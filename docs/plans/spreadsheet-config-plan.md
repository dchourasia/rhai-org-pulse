# Configurable Spreadsheet Settings

**Status**: Draft (rev 3 — addresses Red Team findings)
**Author**: Architect agent
**Date**: 2026-04-10

## Problem

We are deploying a second instance of Team Tracker for a new org. The new org's Google Spreadsheet has a vastly different structure from ours, and the current system's column mapping — while partially configurable — doesn't accommodate these differences without code changes.

## Spreadsheet Structure Comparison

| Aspect | Our Spreadsheet | New Org's Spreadsheet |
|--------|----------------|----------------------|
| **Relevant sheets** | Per-org tabs (e.g., "AI Platform - Team Breakdown") — 29 sheets total, most irrelevant | 2 sheets: "Project Mapping", "Associate Mapping" |
| **Name column** | `Associate's Name` | `Associate Name` |
| **Team grouping** | `Scrum Team Name (miro)` — comma-separated for multi-team | `Project` — one row per person-project assignment |
| **Multi-membership model** | Single row, comma-separated values in team column | Multiple rows for the same person (one per project) |
| **Extra columns** | Manager, PM, Eng Lead, Status, Specialty, Jira Component, Region, Subcomponent | UID, Title, Manager, Group, Goal/KR |
| **Project metadata sheet** | N/A | "Project Mapping" (Deliverable → Goal/KR → Rationale) — **out of scope for v1** |

### Key Differences to Resolve

1. **Sheet selection**: Our spreadsheet has 29 sheets but only ~6 are relevant. The new org has 2 sheets but only 1 is relevant for people data. Currently all sheets are auto-discovered and attempted — admins need to select which sheets to include.

2. **Multi-row team membership**: The new org uses multiple rows per person (one per project) instead of comma-separated values in a single cell. The current merge logic (`sheets.js` + `merge.js`) collects duplicate entries but only uses the primary entry's `_teamGrouping` value. We need to aggregate team grouping values across all rows.

3. **Column names**: Already configurable via `teamStructure` settings (nameColumn, teamGroupingColumn, customFields). No structural change needed — just different admin-entered values.

## Proposed Changes

### 1. Sheet Selection (Admin UI + Config)

**Goal**: Let admins select which sheets to include instead of reading all sheets.

**Config model** — Reuse the existing `sheetNames` field in roster-sync config:

```json
{
  "googleSheetId": "...",
  "sheetNames": ["Associate Mapping"],
  "teamStructure": { ... }
}
```

> **Why `sheetNames` and not a new `selectedSheets` field?** The config already has a `sheetNames` field (persisted via the save handler at `server/index.js:1816`) and `fetchSheetData()` already accepts it as the 2nd parameter — when non-empty, it restricts which sheets are read. However, this field has no UI today and is always empty. Rather than adding a redundant new field, we surface `sheetNames` in the admin settings UI. This avoids confusion about which field controls sheet filtering and avoids adding a 5th parameter to `fetchSheetData()`.

- `sheetNames`: Array of sheet name strings. When non-empty, only these sheets are read. When empty, falls back to current auto-discover-all behavior (backward compatible).
- No changes needed to `fetchSheetData()` signature or `runSync()` call site — `config.sheetNames` is already passed through.

**Admin UI** — Add a sheet picker to `TeamStructureSettings.vue`:

- After the Spreadsheet ID input, add a "Discover Sheets" button
- Clicking it calls a new API endpoint that returns sheet names for the given spreadsheet ID
- Display sheet names as a checklist; admin toggles which to include
- Selected sheets are saved as `sheetNames` in the existing config field
- If the discover call fails (no SA key, invalid ID, no access), show a user-friendly error message — do not crash
- **When the Spreadsheet ID changes**: Clear the discovered sheet list and any selections. Show a hint like "Click Discover Sheets to load sheet names for this spreadsheet."
- **Loading state**: Show a spinner/disabled state on the "Discover Sheets" button while the API call is in progress
- **Zero sheets discovered**: Show an informational message like "No sheets found in this spreadsheet."

**New API endpoint**:

```
GET /api/modules/team-tracker/sheets/discover?spreadsheetId=...
Response: { sheets: ["Sheet1", "Sheet2", ...] }
```

**Auth**: This endpoint MUST use `requireAdmin` middleware. It accepts a user-provided `spreadsheetId` and makes an outbound Google API call with the app's service account — only admins should be able to probe arbitrary spreadsheet IDs.

**Input validation**:
- Reject empty/missing `spreadsheetId` with 400 status
- Validate format: Google Sheet IDs are alphanumeric + hyphens/underscores, ~44 chars. Reject obviously invalid values.
- Catch Google API errors (invalid ID, no access, network errors) and return a meaningful JSON error (e.g., `{ error: "Could not access spreadsheet. Verify the ID and that the service account has read access." }`)

### 2. Multi-Row Team Membership (Backend Merge Logic)

**Goal**: Support both patterns — comma-separated values (existing) and multi-row per person (new).

**Current behavior**: When a person appears in multiple rows, `sheets.js:107-116` collects entries into an array. The merge logic in `merge.js:16-48` (`enrichPerson`) picks one "primary" entry and puts the rest in `additionalAssignments`. Only the primary's `_teamGrouping` is used.

**New behavior**: When merging duplicate person entries, aggregate `_teamGrouping` values from ALL entries into a single deduplicated comma-separated string. This way, `deriveRoster()` already handles comma-separated `_teamGrouping` values and will create correct multi-team membership.

**Known limitation — per-row field values**: In the multi-row pattern, non-grouping custom fields (e.g., Goal/KR, Title) may differ across rows for the same person. Only the primary entry's field values are set on the person object. Secondary entries' differing values are stored in `additionalAssignments` but **nothing downstream currently reads `additionalAssignments`** — those values are effectively not surfaced in the UI. This is acceptable for v1 because:
- The user confirmed project-level metadata (Goal/KR) is out of scope
- Fields like Manager, Group, Title are typically the same across all rows for a given person
- If per-project custom field display is needed later, it can be built on top of the existing `additionalAssignments` data without further backend changes

**Changes to `merge.js`**:

```js
function enrichPerson(person, sheetsMap, orgDisplayName) {
  const normalized = normalizeNameForMatch(person.name);
  const ssData = sheetsMap.get(normalized);
  if (!ssData) return;

  const entries = Array.isArray(ssData) ? ssData : [ssData];

  // Pick primary entry (prefer matching org sheet)
  let primary;
  if (entries.length > 1 && orgDisplayName) {
    const orgNameLower = orgDisplayName.toLowerCase();
    const match = entries.find(e =>
      e.sourceSheet && e.sourceSheet.toLowerCase().includes(orgNameLower)
    );
    primary = match || entries[0];
  } else {
    primary = entries[0];
  }

  // Copy fields from primary
  for (const [key, value] of Object.entries(primary)) {
    if (key === 'originalName') continue;
    person[key] = value;
  }

  // Aggregate _teamGrouping from ALL entries (not just primary), deduplicated
  if (entries.length > 1) {
    const allGroupings = [...new Set(
      entries.map(e => e._teamGrouping).filter(Boolean)
    )];
    if (allGroupings.length > 0) {
      person._teamGrouping = allGroupings.join(', ');
    }

    // Keep additionalAssignments for non-grouping fields, but strip _teamGrouping
    // since it's already been aggregated onto the person
    person.additionalAssignments = entries.filter(e => e !== primary).map(e => {
      const assignment = {};
      for (const [key, value] of Object.entries(e)) {
        if (key === 'originalName' || key === 'sourceSheet' || key === '_teamGrouping') continue;
        assignment[key] = value;
      }
      return assignment;
    });
  }
}
```

This is backward compatible: for our spreadsheet (single row, comma-separated), the person only has one entry so the aggregation code doesn't run. For the new org's spreadsheet (multi-row), all `_teamGrouping` values are collected and deduplicated.

### 3. Config Save Endpoint Update

**Changes to `modules/team-tracker/server/index.js`**:

The config save handler at ~line 1698 already destructures `sheetNames` and persists it at ~line 1816. **No changes needed** to the save handler for sheet selection — `sheetNames` is already handled.

The only addition to the server is the new `GET sheets/discover` endpoint (see section 1).

### 4. Frontend `handleSave()` Wiring

**Changes to `TeamStructureSettings.vue`** `handleSave()`:

The current `handleSave()` sends only `{ googleSheetId, teamStructure }` via `saveConfig()`. It must also include `sheetNames`:

```js
await saveConfig({
  googleSheetId: editSheetId.value.trim() || null,
  sheetNames: editSelectedSheets.value,  // new: selected sheet names
  teamStructure
})
```

The `editSelectedSheets` ref tracks the admin's checkbox selections and is initialized from `config.value.sheetNames || []` on mount/config change.

## Backward Compatibility

All changes are backward compatible:

| Change | Existing deployments | New deployments |
|--------|---------------------|-----------------|
| `sheetNames` empty in config | Auto-discovers all sheets (current behavior) | Admin selects sheets via UI |
| Multi-row aggregation in merge.js | No-op for single-row people | Aggregates `_teamGrouping` across rows |
| Sheet discover API | Not called | Called from settings UI |
| Team grouping column name | Unchanged (`Scrum Team Name (miro)`) | Set to `Project` by admin |

No breaking changes to:
- API request/response shapes
- `org-roster-full.json` format
- `roster-sync-config.json` (reuses existing `sheetNames` field)
- `fetchSheetData()` function signature (no new parameters)
- Shared module exports (`shared/API.md`)

**Demo mode**: `fetchSheetData` is not called in demo mode (uses fixture-backed storage). No demo-mode guard needed.

**Local dev without Google SA key**: The discover endpoint will fail with a Google API error. The UI handles this gracefully by showing the error message returned by the endpoint (see validation in section 1).

## Files to Modify

| File | Change | Scope |
|------|--------|-------|
| `shared/server/roster-sync/merge.js` | Aggregate + deduplicate `_teamGrouping` across multi-row entries; strip `_teamGrouping` from `additionalAssignments` | Backend |
| `modules/team-tracker/server/index.js` | Add `GET sheets/discover` endpoint with `requireAdmin` + input validation | Backend |
| `modules/team-tracker/client/components/TeamStructureSettings.vue` | Add sheet picker checklist UI with discover button, loading state, error handling, stale-clearing on ID change; wire `sheetNames` into `handleSave()` | Frontend |
| `modules/team-tracker/client/composables/useRosterSync.js` | Add `discoverSheets(spreadsheetId)` API call | Frontend |
| `modules/team-tracker/__tests__/server/` | Tests for sheet discover endpoint | Tests |
| `shared/server/roster-sync/__tests__/` | Tests for merge aggregation (see test cases below) | Tests |

**Files NOT modified** (clarification):
- `shared/server/roster-sync/sheets.js` — No changes needed. `fetchSheetData()` already accepts and uses `sheetNames` to filter.
- `shared/server/roster-sync/index.js` — No changes needed. Already passes `config.sheetNames` to `fetchSheetData()`.
- Config save handler in `modules/team-tracker/server/index.js` — Already destructures and persists `sheetNames`.

## Implementation Plan

### Phase 1: Multi-row merge support (backend)
1. Update `merge.js` `enrichPerson()` to aggregate and deduplicate `_teamGrouping` across all entries
2. Strip `_teamGrouping` from `additionalAssignments` entries
3. Add unit tests (see test cases below)
4. Verify existing comma-separated tests still pass

### Phase 2: Sheet selection (backend + frontend)
1. Add `GET /api/modules/team-tracker/sheets/discover` endpoint with `requireAdmin`, spreadsheetId validation, and error handling
2. Add `discoverSheets(spreadsheetId)` to `useRosterSync.js` composable
3. Add sheet picker UI to `TeamStructureSettings.vue`:
   - "Discover Sheets" button with loading state
   - Checklist of discovered sheets
   - Clear discovered list when spreadsheet ID changes
   - Handle zero sheets / error states
   - Wire `sheetNames` into `handleSave()` payload

### Phase 3: Testing and validation
1. Write tests for sheet discover endpoint (auth, validation, error handling)
2. Test with both spreadsheets (our org's and new org's)
3. Verify backward compatibility (config with empty `sheetNames`)

## Required Test Cases for Multi-Row Merge

| # | Scenario | Input | Expected |
|---|----------|-------|----------|
| 1 | Two different projects | Person in rows with `_teamGrouping: "Alpha"` and `_teamGrouping: "Beta"` | `person._teamGrouping === "Alpha, Beta"` |
| 2 | Same project, two rows | Person in two rows both with `_teamGrouping: "Alpha"` | `person._teamGrouping === "Alpha"` (deduplicated) |
| 3 | One entry with grouping, one without | Person in rows with `_teamGrouping: "Alpha"` and `_teamGrouping: null` | `person._teamGrouping === "Alpha"` |
| 4 | Single-row person | Person appears once with `_teamGrouping: "Alpha"` | `person._teamGrouping === "Alpha"` (unchanged, regression test) |
| 5 | Single-row comma-separated | Person appears once with `_teamGrouping: "Alpha, Beta"` | `person._teamGrouping === "Alpha, Beta"` (unchanged, regression test) |

## UI Design Notes

The sheet picker is a simple addition to the existing `TeamStructureSettings.vue` component — it fits naturally below the "Spreadsheet ID" input. The interaction is:

1. Admin enters spreadsheet ID
2. Clicks "Discover Sheets" button (shows spinner while loading)
3. Sheet names appear as checkboxes (or an error/empty message)
4. Admin selects relevant sheets
5. If admin changes the spreadsheet ID, the sheet list clears and shows "Click Discover Sheets to load sheet names"
6. Selection is saved with the rest of the config as `sheetNames`

This is simple enough that it does not warrant a separate UX review.

## Open Questions

None — all requirements are confirmed.
