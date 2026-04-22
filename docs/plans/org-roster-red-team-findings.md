# Red Team Findings: Org-Roster Configurable Spreadsheet Plan

**Reviewed**: `docs/plans/org-roster-config-plan.md`
**Date**: 2026-04-10

---

## 1. [Critical] `runSync()` still requires `sheetId` but derived-teams mode doesn't need Google Sheets at all

The plan proposes making both tabs optional and falling back to `deriveTeamsFromPeople()`. But `runSync()` still receives `sheetId` as a required parameter, and — more importantly — all three callers in `index.js` (lines 717-762, 792-819, 1330-1384) gate on `if (sheetId)` or return HTTP 400 if no sheetId is configured. If an admin hasn't configured a Google Sheet ID (because they don't have one), sync will never run at all, and `deriveTeamsFromPeople()` is unreachable.

The plan says "no changes to `index.js` sync triggers" but this is architecturally broken for the primary use case: an org that has no relevant spreadsheet tabs and wants to derive everything from people data. Either:
- The trigger endpoints need to allow sync without a sheetId when both tabs are empty, or
- `deriveTeamsFromPeople()` needs to be callable outside of `runSync()` (e.g., on a separate endpoint or as part of roster-sync's post-hook)

## 2. [Critical] `deriveTeamsFromPeople()` is synchronous but plan shows it inside `async runSync()`

The proposed `deriveTeamsFromPeople(storage)` calls `getAllPeople(storage)` which reads `org-roster-full.json` from disk synchronously. This is fine. But the plan places it as a fallback inside `runSync()` which is an async function that also does Google Sheets fetching, Jira board resolution, etc. When both tabs are empty, `runSync()` will:
1. Skip the sheet fetch (good)
2. Call `deriveTeamsFromPeople()` (good)
3. Still call `resolveBoardNames(rawTeams)` on line 340 — but derived teams have `boardUrls: []`, so this is a no-op (OK, but wasteful API call setup)

Not truly critical on its own, but combined with finding #1, the entire `runSync()` flow is overkill for the derived-teams case. A cleaner approach would be a separate `syncFromPeople()` path.

## 3. [Major] `orgNameMapping` filtering is skipped for derived teams, causing inconsistency

In the current `runSync()` (lines 297-315), after fetching teams from the sheet, it applies `orgNameMapping` to map sheet org names to configured org names. The plan's `deriveTeamsFromPeople()` helper uses `getOrgDisplayNames()` directly (which returns LDAP-based display names), so `orgNameMapping` is never consulted.

This means the org name mapping feature in the Settings UI becomes partially dead code when using derived mode. If an admin has previously configured mappings (e.g., for a different sheet), those mappings silently do nothing. The UI will still show the mapping section, and "Detect from Sheet" will return org display names — but there's nothing to map.

This isn't necessarily a bug, but the plan doesn't acknowledge it, and the UX is confusing. The Org Name Mapping section should be hidden or disabled when `teamBoardsTab` is empty.

## 4. [Major] `sheet-orgs` endpoint fallback returns wrong data shape for "Detect from Sheet" button

The plan proposes that when no team-boards tab is configured, `GET /sheet-orgs` returns `getOrgDisplayNames()` values. But the "Detect from Sheet" button in the UI (line 363 of `OrgRosterSettings.vue`) calls both `loadSheetOrgs()` and `loadConfiguredOrgs()` and then cross-references them to build mapping rows. When both return the same list (configured org names), every org will appear as an "exact match" with no mapping needed — which is correct behavior.

However, the button still says "Detect from Sheet" even when there's no sheet involved. This is a UX lie. The plan should either rename the button dynamically or hide the entire Org Name Mapping section when `teamBoardsTab` is empty (see finding #3).

## 5. [Major] The plan claims "Open Questions: None" but doesn't address the sheetId-less deployment scenario end-to-end

The plan focuses on making individual tabs optional but doesn't consider the full deployment scenario where a new org has:
- No "Scrum Team Boards" tab
- No "Summary: components per team" tab
- A Google Sheet that exists but only has unrelated tabs

In this case, the admin must still configure a Google Sheet ID (required by sync triggers). But what if the new org doesn't even have a Google Sheet? The plan's `deriveTeamsFromPeople()` doesn't need one. The plan should explicitly state whether a Google Sheet ID is still required, and if not, update the trigger guards.

## 6. [Major] Daily scheduler captures `sheetId` at startup, ignoring later config changes

In `index.js` lines 1330-1384, the `sheetId` is captured once at startup (inside the `setTimeout`) and then reused in the `scheduleDaily` closure. If an admin later clears the Google Sheet ID or changes it, the daily scheduler still uses the stale value. This is a pre-existing bug, but the plan makes it worse because:
- An admin might start with a sheetId, then switch to derived-teams mode (clearing both tabs)
- The daily sync will still try to fetch from the old sheet

The plan should note this as a known issue or fix it by re-reading `getSheetId()` inside the scheduler callback. (The scheduler callback already re-reads `getModuleConfig()` on line 1371 — it should also re-read `sheetId`.)

## 7. [Minor] `deriveTeamsFromPeople()` uses `person.miroTeam` as fallback but `groupPeopleByOrgTeam()` checks `_teamGrouping || miroTeam`

The plan's proposed code (line 83):
```js
const grouping = person._teamGrouping || person.miroTeam || '';
```

This matches the existing `groupPeopleByOrgTeam()` logic in `index.js` line 46:
```js
const groupingValue = person._teamGrouping || person.miroTeam || '';
```

Good — these are consistent. No issue here on closer inspection.

## 8. [Minor] No test for `runSync()` integration — existing tests only cover parsers

The plan proposes adding tests for `deriveTeamsFromPeople()` and `runSync()` with empty tabs, but `runSync()` currently has zero tests (only the parser functions are tested in `sync.test.js`). Testing `runSync()` requires mocking `fetchRawSheet`, `resolveBoardNames`, and `storage` — the plan doesn't mention this complexity. The test cases listed (table rows 4-6) imply integration-level tests that will need significant mock setup.

## 9. [Minor] Config save still uses truthiness check for `jiraProject` and `rfeIssueType`

The plan correctly identifies that `teamBoardsTab` and `componentsTab` need `!== undefined` checks instead of truthiness. But lines 1152-1153 have the same truthiness problem for `jiraProject` and `rfeIssueType` — you can't clear those fields either. The plan should fix all four fields, not just two, for consistency.

## 10. [Minor] Component Mapping UI section is shown even when `componentsTab` is empty

When `componentsTab` is empty, there are no components to map. But the plan doesn't hide the "Component Name Mapping" section (lines 179-251 of `OrgRosterSettings.vue`). The "Detect & Match" button will call `loadComponents()` which reads `components.json` — this file will have `{ components: {} }` (empty), so the section will show "Click Detect & Match to discover..." with nothing to discover. Not broken, but a confusing UX.

## 11. [Minor] Plan says "Demo mode: No demo-mode guard needed" without verifying

The plan asserts `runSync()` is not called in demo mode, which is true — `DEMO_MODE` gates in `index.js` prevent sync triggers. But `deriveTeamsFromPeople()` calls `getAllPeople(storage)` which calls `storage.readFromStorage('org-roster-full.json')`. In demo mode, `storage` is the demo storage backed by fixtures. If `deriveTeamsFromPeople()` were somehow called in demo mode (e.g., a future code path), it would try to read fixture data. This is not currently a problem since the callers are gated, but the assertion is unverified rather than verified.

---

## Summary

| # | Severity | Finding |
|---|----------|---------|
| 1 | Critical | Sync triggers require sheetId — `deriveTeamsFromPeople()` is unreachable without a Google Sheet |
| 2 | Critical | `runSync()` is overkill for derived-teams-only mode (unnecessary Jira board resolution) |
| 3 | Major | `orgNameMapping` is silently ignored in derived mode; UI should reflect this |
| 4 | Major | "Detect from Sheet" button label is misleading when no sheet tab is configured |
| 5 | Major | Plan doesn't address the sheetId-less deployment scenario end-to-end |
| 6 | Major | Daily scheduler captures stale `sheetId` at startup (pre-existing, worsened by plan) |
| 7 | Minor | `_teamGrouping || miroTeam` fallback is consistent (non-issue on review) |
| 8 | Minor | `runSync()` integration tests need significant mock setup not discussed in plan |
| 9 | Minor | Config save truthiness bug applies to all four string fields, not just two |
| 10 | Minor | Component Mapping UI shown even when components tab is empty |
| 11 | Minor | Demo mode assertion is unverified |
