# Red Team Findings -- Spreadsheet Config Plan

**Reviewed**: `docs/plans/spreadsheet-config-plan.md`
**Date**: 2026-04-10

---

## CRITICAL

### 1. The `enrichPerson` rewrite silently drops non-grouping fields from secondary entries

The plan's proposed `enrichPerson` copies all fields from only the `primary` entry (lines 94-97 of proposed code), then aggregates `_teamGrouping` from all entries. But it ignores that secondary entries may have *different* values for other fields (e.g., a different `manager`, `status`, or custom fields per project row). The current code stores these in `additionalAssignments` -- the plan keeps `additionalAssignments` but nothing downstream consumes the differing field values from them. If the new org's spreadsheet has per-project custom fields (Goal/KR, Title, etc.), those values from non-primary rows are effectively lost. The plan doesn't acknowledge this data loss or consider whether it matters.

### 2. The `fetchSheetData` signature change creates confusion with the existing `sheetNames` parameter

The plan proposes adding a 5th parameter `selectedSheets` to `fetchSheetData()` (Section 3), and says to update `index.js` to pass it (Section 4). But the current `index.js:73` call is:

```js
sheetsData = await fetchSheetData(config.googleSheetId, config.sheetNames, config.customFields, config.teamStructure);
```

`config.sheetNames` already exists and is already passed as the 2nd argument -- it restricts which sheets are read. The plan introduces `selectedSheets` as a *separate* concept but doesn't explain the relationship to the existing `sheetNames` field, which does the same thing. Are they redundant? Does `selectedSheets` replace `sheetNames`? The plan is silent on this, and an implementer will be confused about which field to use.

---

## MAJOR

### 3. The config save endpoint destructuring doesn't include `selectedSheets`

The plan says to "Accept `selectedSheets` in config save" (Section 5, Files to Modify table), but the existing config save handler at `server/index.js:1698` destructures a fixed list of fields:

```js
const { orgRoots, googleSheetId, sheetNames, githubOrgs, gitlabGroups, gitlabInstances, teamStructure } = req.body;
```

And then builds the config object at lines 1813-1824 with those exact fields. The plan provides no code for this endpoint -- just says "accept and persist." If the implementer misses the merge logic (lines 1811-1825), `selectedSheets` will be silently dropped on save.

### 4. The sheet discover endpoint doesn't specify `requireAdmin` auth

The plan proposes `GET /api/modules/team-tracker/sheets/discover?spreadsheetId=...` but doesn't specify it needs `requireAdmin`. The spreadsheet ID is user-supplied in the query string -- any authenticated user (not just admins) could probe arbitrary Google spreadsheets that the service account has access to.

### 5. No validation on `selectedSheets` input

The plan doesn't validate `selectedSheets` at all -- no type checking, no length limits, no sanitization. The existing config save handler validates every other field meticulously (orgRoots, gitlabInstances, teamStructure with 100+ lines of validation). An attacker-controlled `selectedSheets` array with arbitrary strings would be persisted directly to disk.

### 6. Multi-row aggregation produces duplicate team names

The plan's aggregation logic joins all `_teamGrouping` values with `', '`. But if a person appears in 3 rows all with `Project: "Alpha"`, the result is `"Alpha, Alpha, Alpha"`. Then `deriveRoster()` at line 127-129 splits on comma and creates 3 identical team assignments. The plan doesn't deduplicate. The existing comma-separated approach wouldn't hit this (a single cell wouldn't repeat values), but multi-row data easily could.

### 7. No error handling for invalid/inaccessible spreadsheet IDs in the discover endpoint

The plan proposes a new API endpoint that calls `discoverSheetNames` with an *arbitrary* `spreadsheetId` from the query string. Currently, `discoverSheetNames` is only called internally with the configured `sheetId`. If the service account doesn't have access to the admin-entered spreadsheet ID, this will fail with an unhelpful Google API error. The plan doesn't address this.

---

## MINOR

### 8. Frontend integration gaps in `TeamStructureSettings.vue`

The plan says to add a sheet picker "below the Spreadsheet ID input" in the same component. But `handleSave()` at line 324-327 only sends `{ googleSheetId, teamStructure }`. The plan doesn't show how `selectedSheets` is added to this payload, how the sheet picker state is initialized from `config.selectedSheets` on load, or how `discoverSheets()` is wired into `useRosterSync.js`.

### 9. The plan dismisses UX review prematurely

The discover-then-select flow has timing dependencies: if the spreadsheet ID changes, the discovered sheets list is stale. The plan doesn't address clearing/re-discovering when the ID changes, showing a loading state during discovery, or handling zero discovered sheets.

### 10. Redundant `sheetNames` config field not addressed

The existing config already has a `sheetNames` field (persisted at line 1816 of server/index.js, passed as 2nd arg to `fetchSheetData`). The plan introduces `selectedSheets` without discussing whether it replaces, supplements, or conflicts with `sheetNames`. This risks two competing mechanisms for the same purpose.
