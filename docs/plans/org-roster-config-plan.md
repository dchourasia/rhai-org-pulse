# Org-Roster Module: Configurable Spreadsheet Support

**Status**: Draft (rev 3 — addresses Reviewer + Red Team findings)
**Author**: Architect agent
**Date**: 2026-04-10

## Problem

The org-roster module syncs team metadata (team names, Jira board URLs, component mappings) from two hardcoded Google Sheets tabs: "Scrum Team Boards" and "Summary: components per team". A new org's spreadsheet has neither of these tabs — it only has "Project Mapping" and "Associate Mapping". The module currently errors out when these tabs don't exist.

## Spreadsheet Structure Comparison

| Aspect | Our Spreadsheet | New Org's Spreadsheet |
|--------|----------------|----------------------|
| **Relevant tabs** | "Scrum Team Boards" (team metadata), "Summary: components per team" (component mapping) | "Project Mapping" (deliverable→goal mapping), "Associate Mapping" (people→project assignments) |
| **Team source** | Explicit team list in "Scrum Team Boards" with Organization, Scrum Team Name, JIRA Board columns | No explicit team list — teams (projects) are derived from the "Project" column in "Associate Mapping" |
| **Org grouping** | "Organization" column in "Scrum Team Boards" tab | No org column — org assignment comes from LDAP ancestry (person's `orgKey` in `org-roster-full.json`) |
| **Component mapping** | "Summary: components per team" tab with multi-org Team→Component pairs | No component data |
| **Board URLs** | JIRA Board column in "Scrum Team Boards" | None |

### Key Insight

People data (including `orgKey` and `_teamGrouping` fields) is already processed by the team-tracker's roster-sync and stored in `org-roster-full.json`. The org-roster module already reads this file via `getAllPeople(storage)` and groups people by `orgKey → orgDisplayName :: _teamGrouping`. **The team list can be derived entirely from this people data without needing a separate "Scrum Team Boards" tab.**

The "Scrum Team Boards" tab currently provides three things beyond the team list:
1. **Jira board URLs** — nice-to-have metadata, not essential
2. **Organization grouping** — already available from LDAP via `orgKey`
3. **Team name list** — derivable from people's `_teamGrouping` values

## Proposed Changes

### 1. Make Team Boards Tab Optional (Backend — `sync.js`)

**Goal**: When no team-boards tab is configured (or the tab doesn't exist), derive the team list from people data instead of erroring out.

**New import required in `sync.js`**:
```js
const { getAllPeople } = require('../../../shared/server/roster');
```

**New export** — `deriveTeamsFromPeople` must be added to `module.exports` for direct unit testing:
```js
module.exports = {
  runSync,
  parseTeamBoardsTab,
  parseComponentsTab,
  calculateHeadcountByRole,
  deriveTeamsFromPeople,  // new
};
```

**Changes to `sync.js` `runSync()`**:

Make `sheetId` optional — it's only needed when a tab is configured. When both tabs are empty, the entire sync runs from people data alone.

```js
async function runSync(storage, sheetId, config) {
  const teamBoardsTab = config?.teamBoardsTab || null;  // was: 'Scrum Team Boards'
  const componentsTab = config?.componentsTab || null;   // was: 'Summary: components per team'
  // ...

  // 1. Fetch team boards tab IF configured AND sheetId is available
  let rawTeams = [];
  if (teamBoardsTab && sheetId) {
    try {
      const boardData = await fetchRawSheet(sheetId, teamBoardsTab);
      const allTeams = parseTeamBoardsTab(boardData.headers, boardData.rows);
      // ... existing org filtering + orgNameMapping logic ...
      rawTeams = filteredTeams;
    } catch (err) {
      console.warn(`[org-roster sync] Failed to fetch team boards tab: ${err.message}`);
    }
  }

  // 2. If no teams from sheet, derive from people data
  if (rawTeams.length === 0) {
    rawTeams = deriveTeamsFromPeople(storage);
    console.log(`[org-roster sync] Derived ${rawTeams.length} teams from people data`);
  }

  // 3. Resolve board names ONLY if any teams have board URLs
  let boardNames = {};
  if (rawTeams.some(t => t.boardUrls.length > 0)) {
    try {
      boardNames = await resolveBoardNames(rawTeams);
    } catch (err) {
      console.warn(`[org-roster sync] Failed to resolve board names: ${err.message}`);
    }
  }

  // 4. Fetch components tab IF configured AND sheetId is available
  let componentMap = {};
  if (componentsTab && sheetId) {
    try {
      const compData = await fetchRawSheet(sheetId, componentsTab);
      // ... existing parsing logic ...
    } catch (err) {
      console.warn(`[org-roster sync] Failed to fetch components tab: ${err.message}`);
    }
  }
  // ...
}
```

**New helper `deriveTeamsFromPeople(storage)`**:

Reads `org-roster-full.json` via `getAllPeople()`, groups by orgDisplayName + `_teamGrouping`, and returns `[{ org, name, boardUrls: [] }]`. This produces the same shape as `parseTeamBoardsTab()` output, so all downstream logic (metadata writes, enrichment, API responses) works unchanged.

```js
function deriveTeamsFromPeople(storage) {
  const allPeople = getAllPeople(storage);
  const orgDisplayNames = getOrgDisplayNames(storage);
  const teamSet = new Map(); // "org::team" -> { org, name }

  for (const person of allPeople) {
    const org = orgDisplayNames[person.orgKey] || '';
    if (!org) continue;
    const grouping = person._teamGrouping || person.miroTeam || '';
    const teamNames = grouping.split(',').map(t => t.trim()).filter(Boolean);
    for (const teamName of teamNames) {
      const key = `${org}::${teamName}`;
      if (!teamSet.has(key)) {
        teamSet.set(key, { org, name: teamName, boardUrls: [] });
      }
    }
  }

  return [...teamSet.values()];
}
```

**Note on `orgNameMapping`**: When teams are derived from people data, the org comes directly from LDAP via `orgDisplayNames[person.orgKey]` — no `orgNameMapping` needed. The mapping is only relevant when reading orgs from the spreadsheet's team-boards tab. The implementation should skip the org name mapping step when in derived mode. The Settings UI should hide or grey out the "Org Name Mapping" section when `teamBoardsTab` is empty.

### 2. Make Components Tab Optional (Backend — `sync.js`)

**Goal**: Skip component mapping and RFE features when no components tab is configured.

The components tab fetch is already inside a try/catch in `runSync()`. The change is to skip the fetch entirely when `componentsTab` is not configured (empty/null), rather than attempting to fetch and catching the error. Also requires `sheetId` to be available.

When `componentMap` is empty, the existing downstream behavior is correct:
- `components.json` is saved with `{ components: {} }`
- RFE sync sees no components and skips
- UI shows no component/RFE data (graceful degradation)

### 3. Update Sync Triggers to Allow Derived Mode (Backend — `index.js`)

**Critical**: All three sync entry points in `index.js` currently gate on `if (sheetId)` and return 400 when no Google Sheet ID is configured. This blocks derived-mode sync entirely, since deployments using derived teams may not have a Google Sheet at all.

**Changes to sync trigger endpoints** (`POST /sync/trigger`, `POST /sync/sheets/trigger`):

Replace the hard `sheetId` requirement with a check that either a `sheetId` exists OR both tabs are empty (derived mode):

```js
router.post('/sync/trigger', requireAdmin, async function(req, res) {
  if (isSyncInProgress()) {
    return res.status(409).json({ error: 'Sync already in progress' });
  }

  const sheetId = getSheetId();
  const config = getModuleConfig();
  const needsSheet = config.teamBoardsTab || config.componentsTab;

  if (needsSheet && !sheetId) {
    return res.status(400).json({
      error: 'No Google Sheet ID configured. Configure it in Team Tracker settings, or clear tab names to derive teams from people data.'
    });
  }

  setSyncInProgress(true);
  res.json({ status: 'started' });

  try {
    const result = await runSync(storage, sheetId, config);  // sheetId may be null
    // ... existing RFE refresh logic ...
  } catch (err) {
    // ... existing error handling ...
  } finally {
    setSyncInProgress(false);
  }
});
```

The same pattern applies to `POST /sync/sheets/trigger`.

**Changes to startup sync and daily scheduler** (lines 1327-1393):

The startup block is currently gated on `if (sheetId)`. It must also trigger when in derived mode (both tabs empty). Additionally, the daily scheduler closure captures `sheetId` at startup and reuses it — it must re-read `getSheetId()` dynamically to pick up config changes.

```js
if (!DEMO_MODE) {
  setTimeout(function() {
    const sheetId = getSheetId();
    const config = getModuleConfig();
    const needsSheet = config.teamBoardsTab || config.componentsTab;
    const canSync = sheetId || !needsSheet;

    if (canSync) {
      // Run initial sync (existing logic, pass sheetId which may be null)
      if (!isSyncInProgress()) {
        const rosterData = readFromStorage('org-roster-full.json');
        if (rosterData) {
          setSyncInProgress(true);
          runSync(storage, sheetId, config)
            // ... existing .then/.catch/.finally ...
        }
      }

      // Schedule daily recurring sync — re-read sheetId dynamically
      scheduleDaily(async function() {
        if (isSyncInProgress()) return;
        setSyncInProgress(true);
        try {
          const currentSheetId = getSheetId();  // re-read, not captured
          const currentConfig = getModuleConfig();
          await runSync(storage, currentSheetId, currentConfig);
          // ... existing RFE refresh logic ...
        } catch (err) {
          console.error('[org-roster] Scheduled sync error:', err.message);
        } finally {
          setSyncInProgress(false);
        }
      });
    }
  }, 5 * 60 * 1000);
}
```

### 4. Change Default Tab Values (Config — `index.js`)

**Current defaults** (in `getModuleConfig()` and `OrgRosterSettings.vue`):
```js
teamBoardsTab: 'Scrum Team Boards',
componentsTab: 'Summary: components per team',
```

**New defaults**:
```js
teamBoardsTab: '',  // empty = derive teams from people data
componentsTab: '',  // empty = skip components
```

For backward compatibility, existing deployments that already have `org-roster/config.json` saved with values will continue to use their saved values. Only new deployments (no config file yet) get the empty defaults.

**Migration path**: Existing deployments don't need any changes — their saved config already has the tab names. New deployments start with empty defaults and the admin can configure tab names if their spreadsheet has relevant tabs.

### 5. Config Save Endpoint Update (Backend — `index.js`)

The `POST /config` endpoint needs to handle empty string values for **all four** string fields (currently all skip falsy values with `if (value)`):

```js
// Change from:
if (teamBoardsTab) config.teamBoardsTab = teamBoardsTab;
if (componentsTab) config.componentsTab = componentsTab;
if (jiraProject) config.jiraProject = jiraProject;
if (rfeIssueType) config.rfeIssueType = rfeIssueType;

// To:
if (teamBoardsTab !== undefined) config.teamBoardsTab = teamBoardsTab;
if (componentsTab !== undefined) config.componentsTab = componentsTab;
if (jiraProject !== undefined) config.jiraProject = jiraProject;
if (rfeIssueType !== undefined) config.rfeIssueType = rfeIssueType;
```

This allows saving empty strings to clear any of these fields.

### 6. Update Sheet-Orgs Endpoint (Backend — `index.js`)

The `GET /sheet-orgs` endpoint currently reads the team-boards tab to extract org names. When no team-boards tab is configured, it should derive org names from the configured org roots instead.

```js
router.get('/sheet-orgs', requireAdmin, async function(req, res) {
  try {
    const config = getModuleConfig();
    const tabName = config.teamBoardsTab;

    if (tabName) {
      // Existing logic: read orgs from sheet
      const sheetId = getSheetId();
      if (!sheetId) return res.status(400).json({ error: 'No Google Sheet ID configured.' });
      const boardData = await fetchRawSheet(sheetId, tabName);
      const teams = parseTeamBoardsTab(boardData.headers, boardData.rows);
      const sheetOrgs = [...new Set(teams.map(t => t.org))].sort();
      return res.json({ sheetOrgs });
    }

    // No tab configured: return configured org display names
    const displayNames = getOrgDisplayNames(storage);
    const sheetOrgs = Object.values(displayNames).sort();
    res.json({ sheetOrgs });
  } catch (error) {
    // ...
  }
});
```

### 7. Update Settings UI (Frontend — `OrgRosterSettings.vue`)

**Changes to `OrgRosterSettings.vue`**:

- Change placeholders for Team Boards Tab and Components Tab inputs to indicate they're optional:
  - Team Boards Tab: placeholder `"(optional) e.g. Scrum Team Boards"`
  - Components Tab: placeholder `"(optional) e.g. Summary: components per team"`
- Add helper text below each input explaining the behavior when empty:
  - Team Boards Tab: "Leave empty to derive teams from people data"
  - Components Tab: "Leave empty to skip component/RFE tracking"

**UX adjustments for derived mode** (when `teamBoardsTab` is empty):
- Change "Detect from Sheet" button label to "Detect Orgs" (since orgs come from LDAP roots, not the sheet)
- Hide the "Org Name Mapping" section with a note: "Org mapping is not needed when teams are derived from people data"
- Hide the "Component Name Mapping" section when `componentsTab` is also empty

## Backward Compatibility

All changes are backward compatible:

| Change | Existing deployments | New deployments |
|--------|---------------------|-----------------|
| Empty `teamBoardsTab` default | Saved config still has `'Scrum Team Boards'` | Derives teams from people data |
| Empty `componentsTab` default | Saved config still has `'Summary: components per team'` | Skips components/RFE |
| `deriveTeamsFromPeople()` | Never called (tab name is configured) | Called as fallback |
| Config save accepting empty strings | No change if admin doesn't clear the fields | Admin can clear fields to switch to derived mode |
| `sheet-orgs` fallback | Returns orgs from sheet (existing behavior) | Returns configured org names |
| Sync trigger without `sheetId` | Still requires `sheetId` (tabs are configured) | Allows sync without sheet |
| Daily scheduler re-reads `sheetId` | Functionally identical (value doesn't change) | Picks up config changes dynamically |

No breaking changes to:
- API request/response shapes (team objects still have `{ org, name, boardUrls, boards, ... }`)
- `teams-metadata.json` format (derived teams just have empty `boardUrls`)
- `components.json` format (empty `{ components: {} }` when no tab)
- `org-roster/config.json` schema (same fields, just nullable)
- Shared module exports (`shared/API.md`)

**Demo mode**: `runSync()` is not called in demo mode. No demo-mode guard needed.

## Files to Modify

| File | Change | Scope |
|------|--------|-------|
| `modules/org-roster/server/sync.js` | Add `getAllPeople` import from `shared/server/roster`; add `deriveTeamsFromPeople()` helper and export it; make `sheetId` optional; make team-boards and components tabs optional; skip fetch when tab name is empty; skip `resolveBoardNames()` when all boardUrls are empty | Backend |
| `modules/org-roster/server/index.js` | Update `getModuleConfig()` defaults to empty strings; fix config save to accept empty strings for all four string fields; update `sheet-orgs` endpoint fallback; update sync trigger guards to allow derived mode without `sheetId`; fix daily scheduler to re-read `sheetId` dynamically instead of capturing at startup | Backend |
| `modules/org-roster/client/components/OrgRosterSettings.vue` | Update default values to empty strings; add placeholder text and helper hints for optional tab fields; conditionally hide org/component mapping sections and update button label when in derived mode | Frontend |
| `modules/org-roster/__tests__/server/sync.test.js` | Add tests for `deriveTeamsFromPeople()` and optional tab behavior | Tests |

**Files NOT modified**:
- `shared/server/roster-sync/` — No changes. Org display names and people data are already correct.
- `shared/server/google-sheets.js` — No changes needed.
- `modules/org-roster/client/composables/useOrgRoster.js` — No new API calls needed.
- `modules/org-roster/server/rfe.js` — No changes. RFE logic already handles empty component lists.
- `modules/org-roster/server/scheduler.js` — No changes. The scheduler function itself is unchanged; the callback closure in `index.js` is what needs updating.

## Implementation Plan

### Phase 1: Backend — Optional tabs + derived teams
1. Add `deriveTeamsFromPeople()` to `sync.js` with `getAllPeople` import; export it
2. Update `runSync()` to: make `sheetId` optional; skip team-boards/components fetch when tab names are empty or no `sheetId`; fall back to `deriveTeamsFromPeople()` when no teams from sheet; skip `resolveBoardNames()` when all boardUrls are empty
3. Update `getModuleConfig()` defaults to empty strings
4. Fix `POST /config` to accept empty string values for all four string fields (`!== undefined`)
5. Update `GET /sheet-orgs` to fall back to configured org names when no tab configured
6. Update sync trigger endpoints (`POST /sync/trigger`, `POST /sync/sheets/trigger`) to allow sync without `sheetId` when both tabs are empty
7. Update startup sync gate from `if (sheetId)` to `if (sheetId || !needsSheet)`
8. Fix daily scheduler callback to re-read `getSheetId()` dynamically instead of using captured `sheetId`

### Phase 2: Frontend — Settings UI updates
1. Update `OrgRosterSettings.vue` defaults to empty strings
2. Add placeholder text and helper hints for optional tab fields
3. Hide "Org Name Mapping" section when `teamBoardsTab` is empty
4. Hide "Component Name Mapping" section when `componentsTab` is empty
5. Change "Detect from Sheet" button label to "Detect Orgs" when `teamBoardsTab` is empty
6. Verify org detection flow works with empty team-boards tab

### Phase 3: Testing
1. Unit tests for `deriveTeamsFromPeople()` — people with various org/team combinations
2. Unit tests for `runSync()` with empty tab names and null `sheetId` — verify fallback behavior
3. Regression: `runSync()` with both tabs configured and valid `sheetId` still works
4. Unit test for config save with empty string values
5. Manual test with both spreadsheets

## Required Test Cases

| # | Scenario | Expected |
|---|----------|----------|
| 1 | `deriveTeamsFromPeople` — people across multiple orgs and teams | Returns unique `{ org, name, boardUrls: [] }` per org::team combo |
| 2 | `deriveTeamsFromPeople` — person with no `_teamGrouping` | Skipped (no team entry created) |
| 3 | `deriveTeamsFromPeople` — comma-separated `_teamGrouping` | Creates separate team entries for each |
| 4 | `deriveTeamsFromPeople` — person with `orgKey` not in configured orgs | Skipped |
| 5 | `runSync` — empty `teamBoardsTab`, null `sheetId` | Calls `deriveTeamsFromPeople()`, writes valid metadata, skips board name resolution |
| 6 | `runSync` — empty `componentsTab` | Writes `{ components: {} }`, no fetch attempted |
| 7 | `runSync` — both tabs configured, valid `sheetId` (regression) | Existing behavior unchanged |
| 8 | Config save — empty tab names for all four fields | Saves empty strings, not ignored |
| 9 | `sheet-orgs` — no tab configured | Returns configured org display names |
| 10 | Sync trigger — no `sheetId`, both tabs empty | Sync runs successfully (derived mode) |
| 11 | Sync trigger — no `sheetId`, tab configured | Returns 400 error |

### Test Implementation Notes

`runSync()` integration tests require mocking:
- `fetchRawSheet` (from `shared/server/google-sheets`) — mock Google Sheets API responses
- `resolveBoardNames` (internal) — mock Jira API for board name resolution
- `storage` object — use a simple in-memory `{ readFromStorage, writeToStorage }` test double
- `getAllPeople` (from `shared/server/roster`) — mock to return test people data

`deriveTeamsFromPeople()` unit tests only require mocking `storage` (for `getAllPeople` and `getOrgDisplayNames`), which is simpler. These should be the primary test focus.

## Open Questions

None — all requirements are confirmed.
