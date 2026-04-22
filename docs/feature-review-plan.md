# Feature Review Implementation Plan

## Overview

Add a "Feature Review" phase to the AI Impact module that visualizes strat creator pipeline activity — the creation, scoring, and human sign-off of Features (RHAISTRAT issues) downstream of approved RFEs.

### Goals

1. **Push-based API** for ingesting feature review data from the strat creator pipeline (mirroring the assessment API pattern)
2. **Feature Review phase** in the AI Impact sidebar (replacing the "Architecture & Design" coming-soon placeholder)
3. **Cross-linking** from features back to source RFEs (both in-app navigation and Jira links)
4. **KPI dashboard** with approval rate, average score, dimension breakdowns, and needs-attention tracking

---

## Data Model

### Feature Schema (`data/ai-impact/features.json`)

Top-level file structure (mirrors `assessments.json`). Note: the counter field is `totalFeatures` (not `totalAssessed` as in assessments) to match the domain terminology:

```json
{
  "lastSyncedAt": "2026-04-21T12:00:00Z",
  "totalFeatures": 75,
  "features": {
    "RHAISTRAT-1168": {
      "latest": { /* full feature object */ },
      "history": [ /* trimmed prior versions */ ]
    }
  }
}
```

#### Full Feature Object (`latest`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | yes | RHAISTRAT issue key (e.g., `"RHAISTRAT-1168"`) |
| `title` | string | yes | Feature title |
| `sourceRfe` | string | yes | Source RFE key (e.g., `"RHAIRFE-262"`) |
| `priority` | string | yes | One of: `"Blocker"`, `"Critical"`, `"Major"`, `"Minor"`, `"Normal"`, `"Undefined"` |
| `status` | string | yes | Jira status (e.g., `"Refined"`) |
| `size` | string\|null | no | T-shirt size: `"S"`, `"M"`, `"L"`, `"XL"`, or `null` |
| `recommendation` | string | yes | Pipeline recommendation: `"approve"`, `"revise"`, `"reject"` |
| `needsAttention` | boolean | yes | Flagged by pipeline for human review |
| `humanReviewStatus` | string | yes | Derived from labels: `"pending"`, `"reviewed"`, `"not-required"` |
| `scores` | object | yes | `{ feasibility: 0-2, testability: 0-2, scope: 0-2, architecture: 0-2, total: 0-8 }` |
| `reviewers` | object | yes | `{ feasibility, testability, scope, architecture }` — each `"approve"`, `"revise"`, or `"reject"` |
| `labels` | string[] | yes | Raw Jira labels array |
| `runId` | string | no | Pipeline run ID (e.g., `"20260419-013035"`) |
| `runTimestamp` | string | no | Pipeline run ISO timestamp |
| `reviewedAt` | string | yes | ISO 8601 timestamp of this review. **See [Field Mapping](#field-mapping-summary-json--api)** for how this is synthesized. |

#### Trimmed History Entry

```json
{
  "scores": { "feasibility": 1, "testability": 1, "scope": 2, "architecture": 2, "total": 6 },
  "recommendation": "approve",
  "needsAttention": false,
  "humanReviewStatus": "pending",
  "reviewedAt": "2026-04-19T01:30:35Z"
}
```

History capped at `MAX_HISTORY = 20` entries per feature. This matches assessments and provides ~5 months of history at one pipeline run per week. The strat creator pipeline typically runs daily but many runs produce identical results (unchanged features), which are deduplicated by the idempotency check on `reviewedAt`. If actual change velocity turns out higher, the cap can be increased later without migration — it only affects how many old entries are retained.

#### `humanReviewStatus` Derivation

During validation, derive from the `labels` array:
- Labels contain `"tech-reviewed"` → `"reviewed"`
- Labels contain `"needs-tech-review"` → `"pending"`
- Neither label present → `"not-required"`

#### Field Mapping: `summary.json` → API

The strat creator pipeline produces `summary.json` with snake_case fields. The API accepts camelCase. **Normalization happens in `validation.js`** — the validator accepts BOTH snake_case and camelCase for all fields, normalizing to camelCase internally.

| `summary.json` (snake_case) | API field (camelCase) | Notes |
|------------------------------|----------------------|-------|
| `strat_id` | `key` | Renamed, not just cased |
| `title` | `title` | Same |
| `source_rfe` | `sourceRfe` | |
| `priority` | `priority` | Same |
| `status` | `status` | Same |
| `size` | `size` | Same |
| `recommendation` | `recommendation` | Same |
| `needs_attention` | `needsAttention` | |
| `scores` | `scores` | Sub-fields are already camelCase-compatible |
| `reviewers` | `reviewers` | Sub-fields are already camelCase-compatible |
| `labels` | `labels` | Same |
| `run_id` | `runId` | |
| `run_timestamp` | `runTimestamp` | |
| *(no field)* | `reviewedAt` | **Synthesized from `run_timestamp`**. If `run_timestamp` is present and `reviewedAt` is absent, validation copies `run_timestamp` → `reviewedAt`. If neither is present, validation fails. |

**Implementation in `validateFeature()`**: Before field-level validation, apply a normalization pass:
1. If `body.strat_id` exists and `body.key` does not, set `body.key = body.strat_id`
2. If `body.source_rfe` exists and `body.sourceRfe` does not, set `body.sourceRfe = body.source_rfe`
3. If `body.needs_attention` exists and `body.needsAttention` is undefined, set `body.needsAttention = body.needs_attention`
4. If `body.run_id` exists and `body.runId` is undefined, set `body.runId = body.run_id`
5. If `body.run_timestamp` exists and `body.runTimestamp` is undefined, set `body.runTimestamp = body.run_timestamp`
6. **If `body.reviewedAt` is undefined and `body.runTimestamp` is a valid ISO string, set `body.reviewedAt = body.runTimestamp`**

This means the pipeline can push `summary.json` data directly (with minimal transformation — just unwrap from the `strategies` array into the `features` array) and validation handles the rest.

---

## Backend

### File Structure

```
modules/ai-impact/server/features/
  validation.js    # validateFeature() — input validation + humanReviewStatus derivation
  storage.js       # readFeatures(), writeFeaturesAtomic(), upsertFeature(), getLatestProjection()
  routes.js        # registerFeatureRoutes(router, context)
```

### `validation.js`

Validate incoming feature data with the following rules:

| Field | Validation |
|-------|-----------|
| `key` | Required string, must start with `RHAISTRAT-` |
| `title` | Required non-empty string |
| `sourceRfe` | Required string, must start with `RHAIRFE-` |
| `priority` | Required, enum: `Blocker`, `Critical`, `Major`, `Minor`, `Normal`, `Undefined` |
| `status` | Required non-empty string |
| `size` | Optional, enum: `S`, `M`, `L`, `XL`, or `null` |
| `recommendation` | Required, enum: `approve`, `revise`, `reject` |
| `needsAttention` | Required boolean |
| `scores` | Required object with `feasibility`, `testability`, `scope`, `architecture` (each integer 0-2) and `total` (integer 0-8). **Sum check**: `total` must equal `feasibility + testability + scope + architecture`. Validation fails with an explicit error message if mismatched (mirrors `assessment validation.js:30-38`). |
| `reviewers` | Required object with `feasibility`, `testability`, `scope`, `architecture` (each enum: `approve`, `revise`, `reject`) |
| `labels` | Required array of strings, max 50 items |
| `runId` | Optional string |
| `runTimestamp` | Optional valid ISO 8601 string |
| `reviewedAt` | Required valid ISO 8601 string |

**On valid input**, return normalized data with `humanReviewStatus` derived from labels.

### `storage.js`

Mirror `modules/ai-impact/server/assessments/storage.js` exactly:

- `STORAGE_KEY = 'ai-impact/features.json'`
- `MAX_HISTORY = 20`
- `readFeatures(readFromStorage)` — read with null guard, returns `{ lastSyncedAt: null, totalFeatures: 0, features: {} }` if missing/malformed
- `writeFeaturesAtomic(data)` — atomic write (temp + rename)
- `trimForHistory(feature)` — keep only `scores` (the full `{ feasibility, testability, scope, architecture, total }` object — note that `total` is nested inside `scores`, unlike assessments where `total` is top-level), `recommendation`, `needsAttention`, `humanReviewStatus`, `reviewedAt`
- `upsertFeature(data, key, feature)` — idempotent upsert with history rotation, returns `'created' | 'updated' | 'unchanged'`. **Idempotency check**: if `existing.latest.reviewedAt === feature.reviewedAt`, returns `'unchanged'` (same as assessments using `assessedAt`)
- `getLatestProjection(data)` — slim projection for list views. Returns `{ lastSyncedAt, totalFeatures, features: { [key]: slimFeature } }`. Strips `labels`, `runId`, `runTimestamp` from each entry; keeps `key`, `title`, `sourceRfe`, `priority`, `status`, `size`, `recommendation`, `needsAttention`, `humanReviewStatus`, `scores`, `reviewers`, `reviewedAt`
- `countHistoryEntries(data)` — total history entries across all features

### `routes.js`

Register on the existing module router (called from `server/index.js`). All routes are under `/api/modules/ai-impact/features/...`.

| Method | Path | Auth | Handler |
|--------|------|------|---------|
| GET | `/features/status` | Admin | Return `{ lastSyncedAt, totalFeatures, totalHistoryEntries }` |
| POST | `/features/bulk` | Admin | Bulk upsert (cap at 5000). Request body: `{ "features": [ { key, title, ... }, ... ] }`. Each entry identified by `entry.key`. Return `{ created, updated, unchanged, errors }` |
| DELETE | `/features` | Admin | Clear all feature data. Writes empty state: `{ lastSyncedAt: null, totalFeatures: 0, features: {} }` |
| GET | `/features` | Public | List all features (slim projection). Returns `{ lastSyncedAt, totalFeatures, features: { [key]: slimFeature } }` |
| GET | `/features/:key` | Public | Single feature + history. Returns `{ latest, history }` |
| PUT | `/features/:key` | Admin | Upsert single feature. Returns `{ status: 'created' | 'updated' | 'unchanged' }` |

**Route registration order**: Static routes (`/status`, `/bulk`) BEFORE parameterized (`/:key`), same as assessments.

**Demo mode**: Bulk, PUT, and DELETE return `{ status: 'skipped', message: '...' }`.

**Body-parsing middleware**: Like assessment routes, create `const jsonLimit = express.json({ limit: '10mb' })` at module scope and apply it as middleware on POST `/features/bulk` and PUT `/features/:key` handlers (same pattern as `assessments/routes.js:12`).

**Bulk entry identifier**: Each entry in the `features` array uses `entry.key` (the RHAISTRAT key) as the identifier, consistent with the feature data model. This differs from assessments which use `entry.id` — features use `key` because the RHAISTRAT key is the natural identifier. The bulk handler also accepts `entry.strat_id` as a fallback (via the same normalization logic in `validateFeature`).

### Wiring (`server/index.js`)

Add one line after the existing assessment routes registration:

```js
const registerFeatureRoutes = require('./features/routes');
registerFeatureRoutes(router, context);
```

---

## Frontend

### New Components

| File | Purpose |
|------|---------|
| `modules/ai-impact/client/components/FeatureReviewContent.vue` | Main content area for the Feature Review phase (analogous to `PhaseContent.vue`) |
| `modules/ai-impact/client/components/FeatureMetricsRow.vue` | KPI cards row |
| `modules/ai-impact/client/components/FeatureList.vue` | Filterable/sortable feature table |
| `modules/ai-impact/client/components/FeatureListItem.vue` | Single row in the feature list |
| `modules/ai-impact/client/components/FeatureDetailPanel.vue` | Right-side detail panel (analogous to `RFEDetailPanel.vue`) |
| `modules/ai-impact/client/components/FeatureCharts.vue` | Score distribution + dimension breakdown charts |

### New Composable

| File | Purpose |
|------|---------|
| `modules/ai-impact/client/composables/useFeatures.js` | Data fetching for features (mirrors `useAssessments.js`) |

#### `useFeatures.js` API

```js
export function useFeatures() {
  // Reactive state
  const features = ref({})        // Map<key, SlimFeature>
  const featureMeta = ref({ lastSyncedAt: null, totalFeatures: 0 })
  const featureLoading = ref(false)
  const featureError = ref(null)
  const detailCache = ref({})

  // Methods
  async function loadFeatures()           // GET /features (slim)
  async function loadFeatureDetail(key)   // GET /features/:key (full + history)

  return { features, featureMeta, featureLoading, featureError, loadFeatures, loadFeatureDetail, detailCache }
}
```

### View Changes (`AIImpactView.vue`)

1. **Update phases array**: Change `architecture` phase from `status: 'coming-soon'` to `status: 'active'` and rename to `'Feature Review'` with `id: 'feature-review'`.

2. **Import and use**: Import `FeatureReviewContent`, `FeatureDetailPanel`, and `useFeatures`. Call `loadFeatures()` on mount.

3. **Template branching**: The current template uses a single `v-if="isPhase && activePhase?.status === 'active'"` that renders `<PhaseContent>` for ALL active phases. This must be replaced with explicit phase-specific branching:

   ```html
   <!-- RFE Review phase -->
   <template v-if="selectedPhase === 'rfe-review'">
     <PhaseContent ... />
     <RFEDetailPanel v-if="selectedRFE" ... />
   </template>

   <!-- Feature Review phase -->
   <template v-else-if="selectedPhase === 'feature-review'">
     <FeatureReviewContent ... />
     <FeatureDetailPanel v-if="selectedFeature" ... />
   </template>

   <!-- Workflow views -->
   <AutofixContent v-else-if="isWorkflow && selectedPhase === 'autofix'" ... />

   <!-- Coming soon placeholder for inactive phases -->
   <ComingSoonPlaceholder v-else-if="isPhase" ... />
   ```

   This replaces the generic `isPhase && activePhase?.status === 'active'` guard with explicit phase ID checks, ensuring each active phase renders its own content component.

4. **Cross-link support**: Pass `assessments` data to `FeatureDetailPanel` so it can link back to source RFE assessment data.

5. **Pass `jiraHost`**: `FeatureReviewContent` and `FeatureDetailPanel` need `jiraHost` for constructing Jira links (both for RHAISTRAT feature keys and RHAIRFE source RFE keys). Source it from `rfeData.jiraHost` (already available in `AIImpactView.vue`) and pass as a prop.

6. **New state**: Add `selectedFeature` ref (analogous to `selectedRFE`) for tracking the currently selected feature in the detail panel.

### KPI Cards (`FeatureMetricsRow.vue`)

Computed from the features list:

| Card | Value | Description |
|------|-------|-------------|
| Total Features | `totalFeatures` | Count of features reviewed |
| Approval Rate | `approved / total * 100` | % with `recommendation === 'approve'` |
| Avg Score | `sum(total) / count` | Mean of `scores.total` across all features |
| Needs Attention | count | Features with `needsAttention === true` |

### Feature List (`FeatureList.vue`)

Filters:
- **Search**: by key, title, or source RFE key
- **Recommendation**: all / approve / revise / reject
- **Priority**: derived from data (like existing `availablePriorities`)
- **Human Review**: all / pending / reviewed / not-required
- **Needs Attention**: all / yes / no

Sort options:
- Default (by key)
- Score: Low to High
- Score: High to Low

### Feature Detail Panel (`FeatureDetailPanel.vue`)

Sections:
1. **Header**: Feature key (Jira link), title
2. **Metadata grid**: Priority, Status, Size, Recommendation badge, Needs Attention badge, Human Review Status
3. **Source RFE**: Show `sourceRfe` as both:
   - A Jira hyperlink (`{jiraHost}/browse/{sourceRfe}`)
   - An in-app navigation link that switches to the RFE Review phase and selects the source RFE
4. **Dimension Scores**: 4 dimension cards showing score (0-2) + reviewer verdict (approve/revise/reject) with color coding
5. **Labels**: Display raw labels as badges
6. **History**: Score history chart (reuse pattern from `AssessmentHistory.vue`)

### Cross-Link Navigation

When the user clicks the in-app source RFE link in `FeatureDetailPanel`:
1. Set `selectedPhase` to `'rfe-review'`
2. Clear any active search/filter state (reset `filter`, `searchQuery`, `passFailFilter`, `priorityFilter`, `statusFilter` to defaults, set `timeWindow` to `'3months'`) to maximize the chance of finding the RFE
3. Find the matching RFE in the full `rfeData.issues` array (NOT `filteredRFEs`, which may exclude the target due to active filters)
4. Set `selectedRFE` to that RFE object
5. If not found (RFE not in cached data), show a toast/notification: "Source RFE not found in current data" and fall back to opening the Jira link

This requires lifting the navigation handler to `AIImpactView.vue` and passing it down as a prop or event.

### Charts (`FeatureCharts.vue`)

Two charts (using Chart.js + vue-chartjs, same as existing):
1. **Score Distribution**: Histogram of `scores.total` values (0-8)
2. **Dimension Breakdown**: Stacked bar chart showing pass/partial/fail counts per dimension (feasibility, testability, scope, architecture), where pass=2, partial=1, fail=0

### Settings (`AIImpactSettings.vue`)

Add a "Feature Reviews" section below the existing "Assessments" section:
- Show `lastSyncedAt`, `totalFeatures`, `totalHistoryEntries` (from GET `/features/status`)
- "Clear Feature Data" button (DELETE `/features`)

---

## Fixtures and Demo Mode

### New Fixture File

`fixtures/ai-impact/features.json` — 10-15 sample features covering:
- Mix of approve/revise/reject recommendations
- Various scores across dimensions
- Some with `needsAttention: true`
- Different `humanReviewStatus` values
- **At least 3 features must link to RFE keys that exist in `fixtures/ai-impact/rfe-data.json`** to make cross-linking testable in demo mode
- Some with history entries

The fixture must match the production `features.json` format exactly.

### Demo Storage

No changes needed — `demo-storage.js` already reads from `fixtures/` by key, and the features storage uses `readFromStorage('ai-impact/features.json')`.

---

## Testing Strategy

### Server Tests

| File | Coverage |
|------|----------|
| `modules/ai-impact/__tests__/server/feature-validation.test.js` | All validation rules, humanReviewStatus derivation from labels, snake_case → camelCase normalization (including `strat_id` → `key`, `run_timestamp` → `reviewedAt` synthesis), labels array cap, edge cases |
| `modules/ai-impact/__tests__/server/feature-storage.test.js` | Read/write, upsert (create/update/unchanged/idempotent), history rotation, trimming, projection, history counting |
| `modules/ai-impact/__tests__/server/feature-routes.test.js` | All 6 endpoints, auth checks, demo mode, bulk cap, error handling |

Mirror the existing assessment test patterns (`assessment-validation.test.js`, `assessment-storage.test.js`, `assessment-routes.test.js`).

### Client Tests

| File | Coverage |
|------|----------|
| `modules/ai-impact/__tests__/client/useFeatures.test.js` | Loading, error handling, detail caching, 404 handling |
| `modules/ai-impact/__tests__/client/FeatureReviewContent.test.js` | Rendering states (loading, error, empty, data), KPI computation |
| `modules/ai-impact/__tests__/client/AIImpactView.test.js` | Add test case for cross-link navigation: switching from feature-review to rfe-review phase and selecting the source RFE (extends existing test file) |

### Test Approach

- Mock `fs` for storage tests (same as assessment tests)
- Use the `createRouter`/`mockReqRes`/`callHandler` pattern from `assessment-routes.test.js`
- Mock `apiRequest` for client composable tests

---

## Documentation Updates

### `docs/DATA-FORMATS.md`

Add new section **"AI Impact — Features (`data/ai-impact/features.json`)"** after the Assessments section. Document the full schema, history trimming rules, humanReviewStatus derivation, and atomic write behavior.

### `.claude/CLAUDE.md`

Add to the API Routes section:

```
- `/api/modules/ai-impact/features` — list all features (slim projection)
- `/api/modules/ai-impact/features/:key` — single feature + history
- `/api/modules/ai-impact/features/status` — feature data status (admin)
- `/api/modules/ai-impact/features/bulk` — bulk upsert features (admin)
- `/api/modules/ai-impact/features/:key` — upsert single feature (admin, PUT)
- `/api/modules/ai-impact/features` — clear all feature data (admin, DELETE)
```

---

## Files to Create/Modify

### New Files

| File | Type | Description |
|------|------|-------------|
| `modules/ai-impact/server/features/validation.js` | Backend | Feature validation + humanReviewStatus derivation |
| `modules/ai-impact/server/features/storage.js` | Backend | Atomic-write storage with history |
| `modules/ai-impact/server/features/routes.js` | Backend | Express route handlers |
| `modules/ai-impact/client/composables/useFeatures.js` | Frontend | Data fetching composable |
| `modules/ai-impact/client/components/FeatureReviewContent.vue` | Frontend | Main phase content view |
| `modules/ai-impact/client/components/FeatureMetricsRow.vue` | Frontend | KPI cards row |
| `modules/ai-impact/client/components/FeatureList.vue` | Frontend | Filterable/sortable table |
| `modules/ai-impact/client/components/FeatureListItem.vue` | Frontend | Single feature row |
| `modules/ai-impact/client/components/FeatureDetailPanel.vue` | Frontend | Detail panel with cross-links |
| `modules/ai-impact/client/components/FeatureCharts.vue` | Frontend | Score distribution + dimension charts |
| `fixtures/ai-impact/features.json` | Fixture | Demo mode data |
| `modules/ai-impact/__tests__/server/feature-validation.test.js` | Test | Validation tests |
| `modules/ai-impact/__tests__/server/feature-storage.test.js` | Test | Storage tests |
| `modules/ai-impact/__tests__/server/feature-routes.test.js` | Test | Route tests |
| `modules/ai-impact/__tests__/client/useFeatures.test.js` | Test | Composable tests |
| `modules/ai-impact/__tests__/client/FeatureReviewContent.test.js` | Test | View tests |

### Modified Files

| File | Change |
|------|--------|
| `modules/ai-impact/server/index.js` | Import and register feature routes (1 line) |
| `modules/ai-impact/client/views/AIImpactView.vue` | Add feature-review phase, import useFeatures, render FeatureReviewContent + FeatureDetailPanel, add cross-link navigation handler |
| `modules/ai-impact/client/components/AIImpactSettings.vue` | Add Feature Reviews status/clear section |
| `docs/DATA-FORMATS.md` | Add Features schema documentation |
| `.claude/CLAUDE.md` | Add feature API routes |

---

## Testability

### Local Dev

1. Start with `npm run dev:full`
2. Push feature data via the bulk endpoint (accepts both snake_case and camelCase):
   ```bash
   # camelCase format:
   curl -X POST http://localhost:3001/api/modules/ai-impact/features/bulk \
     -H 'Content-Type: application/json' \
     -d '{"features": [{"key":"RHAISTRAT-1168","title":"GPU-as-a-Service Observability","sourceRfe":"RHAIRFE-262","priority":"Major","status":"Refined","size":null,"recommendation":"approve","needsAttention":false,"scores":{"feasibility":1,"testability":1,"scope":2,"architecture":2,"total":6},"reviewers":{"feasibility":"approve","testability":"revise","scope":"approve","architecture":"approve"},"labels":["strat-creator-auto-created","strat-creator-rubric-pass"],"reviewedAt":"2026-04-19T01:30:35Z"}]}'

   # Or pipe summary.json strategies directly (snake_case — validator normalizes):
   jq '{features: .summary.strategies}' summary.json | \
     curl -X POST http://localhost:3001/api/modules/ai-impact/features/bulk \
       -H 'Content-Type: application/json' -d @-
   ```
3. Or run in demo mode (`DEMO_MODE=true VITE_DEMO_MODE=true`) to use fixture data
4. Navigate to AI Impact > Feature Review in the sidebar

### Preprod

1. Deploy to preprod overlay (uses `:latest` images)
2. Push data via the bulk API using a script that transforms strat creator `summary.json` output
3. Verify KPIs, filters, sorting, detail panel, cross-links

### Prod

1. Strat creator pipeline pushes data via `POST /features/bulk` after each run
2. Data persists in PVC-mounted `data/` directory
3. Admin can clear via Settings > AI Impact > Feature Reviews

---

## Backward Compatibility

- **No breaking changes**: All new routes are additive under `/api/modules/ai-impact/features/`
- **No existing data changes**: The `assessments.json` file and all existing routes are untouched
- **Sidebar change**: The "Architecture & Design" coming-soon phase is replaced with "Feature Review" (active). This is intentional — there was no functionality behind it.
- **Demo mode**: Works automatically via `demo-storage.js` reading from `fixtures/ai-impact/features.json`
- **No new environment variables**: Feature data is pushed by the pipeline, not pulled
- **`module.json` unchanged**: The AI Impact module manifest does not reference individual phases or views — phase definitions are in `AIImpactView.vue` only. No manifest update needed.
- **Phase id change**: The `architecture` phase id becomes `feature-review`. No existing code persists the selected phase id to localStorage (the `selectedPhase` ref defaults to `'rfe-review'` on every page load), so there is no migration concern. The guide modal dismiss key (`tt_cache:ai-impact-guide-dismissed`) is unrelated.

---

## Phased Implementation Order

### Phase 1: Backend (storage + validation + routes)

1. Create `fixtures/ai-impact/features.json` (must exist before demo mode is testable — do this first to avoid demo crashes if the feature-review phase is activated before the backend is complete)
2. `modules/ai-impact/server/features/validation.js` + tests (includes snake_case normalization)
3. `modules/ai-impact/server/features/storage.js` + tests
4. `modules/ai-impact/server/features/routes.js` + tests
5. Wire into `modules/ai-impact/server/index.js`

**Deliverable**: Working API that can receive and serve feature data. Testable with `curl`.

### Phase 2: Frontend composable + settings

6. `modules/ai-impact/client/composables/useFeatures.js` + tests
7. Update `AIImpactSettings.vue` with feature status/clear section

**Deliverable**: Data fetching layer ready. Settings page shows feature data status.

### Phase 3: Frontend views + components

8. `FeatureMetricsRow.vue` — KPI cards
9. `FeatureListItem.vue` — single row component
10. `FeatureList.vue` — filterable/sortable list
11. `FeatureCharts.vue` — score distribution + dimension breakdown
12. `FeatureDetailPanel.vue` — detail panel with cross-links
13. `FeatureReviewContent.vue` — main content area wiring everything together + test
14. Update `AIImpactView.vue` — activate feature-review phase, wire data + navigation

**Deliverable**: Full Feature Review phase visible and functional in the UI.

### Phase 4: Documentation

15. Update `docs/DATA-FORMATS.md` with features schema
16. Update `.claude/CLAUDE.md` with API routes
