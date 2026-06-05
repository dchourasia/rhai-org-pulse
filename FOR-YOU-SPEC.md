# "For You" — Personalized AI Factory Dashboard

## Spec for new view in the AI Impact module

**Branch**: `ai-factory-tailored-page`
**Module**: `modules/ai-impact/`
**Status**: MVP spec — approved for implementation

---

## 1. Problem

The AI Factory pipeline has multiple stages (RFE creation, feature review,
test plans, documentation, build & release), each requiring human action from
different roles. Today every view in the AI Impact module is org-wide — users
must manually sift through hundreds of items across multiple pages to find what
needs their attention. This creates friction, delays human review cycles, and
reduces factory adoption.

Production data illustrates the scale of the problem:

- 1,260 RFEs tracked, 617 of which passed quality gating but are stuck because
  they lack a scope label to enter the strategy pipeline.
- 262 features tracked, 168 of which are CI-approved and waiting for a human to
  pull and sign off.

Most of this work is invisible to the people who should be acting on it.

## 2. Goal

A new **"For You"** view that shows the logged-in user only the RFEs and
Features in their Jira component scope, organized by urgency and annotated with
clear, actionable guidance so they know exactly what to do next.

By surfacing the right items to the right people with specific next-step
instructions, we reduce time-to-action and increase factory throughput.

## 3. User Identity & Component Resolution

### 3.1 Identity chain

```
1. useAuth()          -> user.email (e.g. "acorvin@cluster.local")
2. Extract uid        -> strip @domain -> "acorvin"
3. useRoster()        -> scan all roster members, match by `uid` field
4. Read customFields  -> find the component field dynamically
5. Result             -> ["Model Serving", "Model Runtimes"]
```

**Matching on `uid`** (the SSO username) sidesteps the `AUTH_EMAIL_DOMAIN` /
`cluster.local` vs `redhat.com` domain mismatch entirely. The `uid` field is
present on every roster member and equals the SSO username.

### 3.2 Dynamic component field resolution

The person-level component field ID differs between environments (e.g.
`field_d4e5f6` in fixtures, `field_81d38b` in production). The code must
resolve it dynamically:

1. Load field definitions (available on the roster response as
   `fieldDefinitions`).
2. Find the `personFields` entry where `optionsRef === "component"`.
3. Use that field's `id` to read the person's `customFields[id]`.

The field is `multiValue: true` — always treat the value as an array.

### 3.3 Component coverage

Production data: 547 of 558 roster members (98%) have component assignments.
For users without components, show a placeholder:

> Your component assignments haven't been set up yet. Ask your team lead to
> update your profile in the Team Tracker.

Below the placeholder, show all items ungrouped as a read-only fallback so the
page is still useful.

### 3.4 Item matching

An RFE or Feature appears on a user's "For You" page when:

```
intersection(item.components, user.components).length > 0
```

Both sides are arrays of Jira component name strings (e.g. `"Model Serving"`).

---

## 4. Data Pipeline Changes

### 4.1 Add `components` to the RFE fetcher

**File**: `modules/ai-impact/server/jira/rfe-fetcher.js`

Line 100 — change:
```js
const fields = 'summary,status,priority,created,creator,labels,issuelinks';
```
To:
```js
const fields = 'summary,status,priority,created,creator,labels,issuelinks,components';
```

In `processIssue()`, add to the returned object:
```js
components: (issue.fields.components || []).map(c => c.name),
```

This follows the exact pattern already used in `autofix-fetcher.js` (line 52)
and `team-tracker/server/rfe.js` (line 95).

### 4.2 Add `components` to the feature Jira sync

**File**: `modules/ai-impact/server/features/jira-sync.js`

Line 79 — change:
```js
issues = await doFetch(jiraRequest, jql, 'summary,status,priority,labels', { expand: 'changelog' });
```
To:
```js
issues = await doFetch(jiraRequest, jql, 'summary,status,priority,labels,components', { expand: 'changelog' });
```

In `applyJiraFields()`, extract and store:
```js
const components = (fields.components || []).map(c => c.name);
```

Update `latest.components` alongside the other mutable fields.

### 4.3 Add `components` to feature storage

**File**: `modules/ai-impact/server/features/storage.js`

In `getLatestProjection()`, add `components` to the slim projection:
```js
components: entry.latest.components || [],
```

### 4.4 Add `components` to feature validation

**File**: `modules/ai-impact/server/features/validation.js`

Accept optional `components` field (array of strings) in `validateFeature()`.
Include in the returned `data` object:
```js
components: Array.isArray(body.components) ? body.components : [],
```

### 4.5 Update fixtures

- `fixtures/ai-impact/rfe-data.json` — add `"components"` array to each issue,
  using values from `fixtures/team-data/field-options/component.json`.
- `fixtures/ai-impact/features.json` — add `"components"` array to each
  feature's `latest` object.
- Ensure at least one fixture roster member's component overlaps with fixture
  RFE/feature components so demo mode works end-to-end.

---

## 5. RFE State Machine

Each RFE in the user's component scope is classified into exactly one state.
States are ordered by action priority (highest first).

### State 1: Needs Revision (RED)

**Condition**: Has `rfe-creator-needs-attention` AND does NOT have
`rfe-creator-autofix-rubric-pass`.

**Card shows**:
- Compact assessment scores: `WHAT:0 WHY:2 HOW:1 TASK:2 SIZE:1 = 6/10`
  with failing criteria (score 0) highlighted in red.
- Click-through to RFE Review detail for full breakdown.

**Action text**: "This RFE failed the quality rubric and auto-fix couldn't
resolve it. Review the scoring breakdown and revise the description."

**Inline guidance** (collapsible "How to fix this"):
1. Check which criteria scored 0 — zeros block progress.
2. Write your business justification in the Jira Description field — that's
   what the AI reads.
3. Use the `rfe-creator` skill in Claude Code to improve it:
   `/rfe.review RHAIRFE-XXXX`
4. Avoid prescribing architecture (HOW criterion) — describe the need, not
   the solution.
5. After editing, the daily pipeline run (4:00 AM UTC) will re-assess
   automatically.

### State 2: Passed with Caveats (AMBER — lower priority)

**Condition**: Has BOTH `rfe-creator-autofix-rubric-pass` AND
`rfe-creator-needs-attention`.

**Action text**: "This RFE passed the rubric but has items the auto-fix
couldn't resolve. Review the flagged issues and decide if revision is needed."

**Inline guidance**: Same as State 1, but prefixed with "This passed overall
scoring. The flagged items are optional improvements — check whether they
affect the business intent."

### State 3: Ready to Advance (AMBER)

**Condition**: Has `rfe-creator-autofix-rubric-pass` (or `tech-reviewed`) AND
has no `linkedFeature` AND is missing the scope label `strat-creator-3.5`.

This is the **highest-value action on the page**. Production data shows 617
RFEs stuck in this state.

**Action text**: "This RFE passed quality scoring but hasn't entered the
strategy pipeline. Add a scope label to make it eligible."

**Inline guidance**:
1. Open this RFE in Jira.
2. Add the label `strat-creator-3.5` to the ticket.
3. Alternatively, set the Target Version to `rhoai-3.5` (or the appropriate
   EA release).
4. Once labeled, the strat-creator CI pipeline will pick it up automatically
   in the next batch run (~10 RFEs per batch).

### State 4: Queued for Pipeline (BLUE — informational)

**Condition**: Has quality gate label (`rfe-creator-autofix-rubric-pass` or
`tech-reviewed`) AND has scope label (e.g. `strat-creator-3.5`) AND has no
`linkedFeature`.

**Action text**: "This RFE is eligible for the strategy pipeline and will be
picked up in a future batch run. No action needed."

### State 5: Strategy Created (GREEN — cross-link)

**Condition**: Has `linkedFeature` (a linked RHAISTRAT key exists).

**Action text**: "A strategy/feature has been created from this RFE. See it
in the Features section below."

The card shows a link to the corresponding Feature card on this same page (or
to the Feature Review detail view).

---

## 6. Feature State Machine

Each Feature (RHAISTRAT) in the user's component scope is classified into
exactly one state.

### State 1: Rejected (RED)

**Condition**: `recommendation === 'reject'`
(Production: 3 features. Score < 3 or 2+ dimension zeros.)

**Card shows**:
- Compact dimension scores: `F:0 T:0 S:1 A:0 = 1/8` with zeros in red.
- Click-through to Feature Review detail.

**Action text**: "This feature was rejected by CI scoring. Pull it locally,
diagnose the root cause, and add architecture overlays or SME input."

**Inline guidance** ("How to fix this"):
1. Run `/strategy-pull RHAISTRAT-XXXX` in Claude Code to fetch the strategy.
2. Review which dimensions scored 0 — those are the blockers.
3. Add corrections to the **Staff Engineer Input** section (not the strategy
   body — direct edits get overwritten by the pipeline).
4. Prefer **architecture overlays** for root-cause fixes — they benefit all
   future strategies for this component, not just this one.
5. Run `/strategy-review RHAISTRAT-XXXX` locally to verify your fixes pass.
6. Run `/strategy-push RHAISTRAT-XXXX` to submit back to CI for
   re-evaluation.
7. After CI re-evaluates, check for the `strat-creator-rubric-pass` label.

### State 2: Revise Required (RED)

**Condition**: `recommendation === 'revise'` AND
`humanReviewStatus === 'needs-review'`
(Production: 45 features. Score 3-5, or 1 zero.)

**Card shows**:
- Compact dimension scores with failing dimensions in amber/red.

**Action text**: "This feature needs improvements before it can pass CI.
Review the failing dimensions and add SME input."

**Inline guidance**: Same steps as State 1 (pull, fix input sections, push
back).

### State 3: Awaiting Sign-off (AMBER)

**Condition**: `recommendation === 'approve'` AND
`humanReviewStatus === 'awaiting-review'`
(Production: 168 features — the largest bucket.)

**Card shows**:
- Compact dimension scores (mostly green).
- Jira status badge.

**Action text**: "This feature passed CI scoring and is ready for human
review. Pull it, verify the technical approach, and sign off."

**Inline guidance**:
1. Run `/strategy-pull RHAISTRAT-XXXX` to review the strategy locally.
2. Verify the technical approach aligns with your component's architecture.
3. Optionally add corrections to the Staff Engineer Input section.
4. If everything looks good, run `/strategy-signoff RHAISTRAT-XXXX` to
   approve.
5. The pipeline will push the strategy content to Jira, post a review summary
   as a comment, and apply the `strat-creator-human-sign-off` label.

### State 4: Signed Off (GREEN)

**Condition**: `humanReviewStatus === 'approved'` (derived from
`strat-creator-human-sign-off` label) OR `approvedBy` is set.
(Production: 44 features.)

**Card shows**:
- Score summary (green).
- "Approved by: [name]" badge with approval date.
- Jira status.

**Action text**: "Approved and signed off — ready for backlog grooming and
sprint planning."

This appears in the "Recently Completed" section.

### Edge cases

| Combo | Count | Treatment |
|-------|-------|-----------|
| `revise + awaiting-review` | 1 | Treat as "Revise Required" |
| `revise + approved` | 1 | Treat as "Signed Off" (human overrode CI) |

---

## 7. Navigation & Module Integration

### 7.1 New nav item

Add to `modules/ai-impact/module.json` navItems array, first position:

```json
{ "id": "for-you", "label": "For You", "icon": "UserCircle" }
```

Add `"separatorBefore": true` to the existing AI Factory Guide entry to
visually separate "For You" from the reference pages.

**Do not** set `"default": true` on the new item. AI Factory Guide remains the
default landing page until this view is proven in production.

### 7.2 Client route

Add to `modules/ai-impact/client/index.js`:

```js
'for-you': defineAsyncComponent(() => import('./views/ForYouView.vue')),
```

---

## 8. Page Layout

```
+--------------------------------------------------------------+
|  For You                                   [Stage v] [Pri v]  |
|  Showing items for: Model Serving, Model Runtimes             |
+--------------------------------------------------------------+
|  +------------+  +------------+  +------------+  +----------+ |
|  | 4 Revise   |  | 12 Review  |  | 3 Queued   |  | 2 Done   | |
|  | RFEs       |  | Features   |  | for Strat  |  | This Wk  | |
|  +------------+  +------------+  +------------+  +----------+ |
+--------------------------------------------------------------+
|                                                                |
|  ACTION NEEDED (7)                            sorted by wait   |
|  +----------------------------------------------------------+ |
|  | RHAIRFE-2301  Support for fine-tuning LLMs                | |
|  | Model Serving . RFE Review                                | |
|  |                                                           | |
|  | WHAT:0  WHY:2  HOW:1  TASK:2  SIZE:1  =  6/10            | |
|  |                                                           | |
|  | This RFE failed the quality rubric and auto-fix couldn't  | |
|  | resolve it. Review the scoring breakdown and revise.      | |
|  |                                                           | |
|  | > How to fix this                                         | |
|  |                                                           | |
|  | Waiting: 3 days                [Open in Jira] [Details ->]| |
|  +----------------------------------------------------------+ |
|  | RHAISTRAT-1541  Model Serving Autoscaling                 | |
|  | Model Serving . Feature Review                            | |
|  |                                                           | |
|  | F:1  T:1  S:2  A:1  =  5/8           rec: revise         | |
|  |                                                           | |
|  | Needs improvements before CI pass. Review failing         | |
|  | dimensions, add SME input, then push back.                | |
|  |                                                           | |
|  | > How to fix this                                         | |
|  |                                                           | |
|  | Waiting: 12 days . Critical   [Open in Jira] [Details ->] | |
|  +----------------------------------------------------------+ |
|  | RHAISTRAT-1525  Model Serving Health Checks               | |
|  | Model Serving . Feature Review                            | |
|  |                                                           | |
|  | F:2  T:2  S:2  A:2  =  8/8                               | |
|  |                                                           | |
|  | CI approved -- ready for human review. Pull, verify the   | |
|  | technical approach, and sign off.                         | |
|  |                                                           | |
|  | > How to sign off                                         | |
|  |                                                           | |
|  | Waiting: 5 days . Major       [Open in Jira] [Details ->] | |
|  +----------------------------------------------------------+ |
|                                                                |
|  IN PROGRESS (5)                              [collapsed >]    |
|  (RFEs queued for pipeline, features being processed)          |
|                                                                |
|  RECENTLY COMPLETED (2)                       [collapsed >]    |
|  (Signed-off features, rubric-pass RFEs from last 7 days)      |
+--------------------------------------------------------------+
```

### 8.1 Summary statistics bar

Four stat cards at the top, reflecting the most actionable categories:

| Card | Counts | What it includes |
|------|--------|------------------|
| **Revise RFEs** | RFE states 1+2 | RFEs needing revision or with caveats |
| **Review Features** | Feature states 1+2+3 | Features needing SME input or sign-off |
| **Queued for Strat** | RFE state 3 | RFEs passed but missing scope label |
| **Done This Week** | RFE state 5 + Feature state 4 | Items completed in last 7 days |

### 8.2 Card anatomy

Each item card contains:

1. **Jira key** (linked to Jira instance URL) + **summary** (truncated to
   ~80 chars).
2. **Component badge** (e.g. "Model Serving") + **pipeline stage** label
   ("RFE Review" or "Feature Review").
3. **Inline score summary**:
   - RFEs: `WHAT:0 WHY:2 HOW:1 TASK:2 SIZE:1 = 6/10`
   - Features: `F:2 T:1 S:2 A:1 = 6/8`
   - Each dimension color-coded: 0=red, 1=amber, 2=green.
4. **Action text** — plain-language description of what to do (from state
   machine above).
5. **Collapsible guidance** — "How to fix this" / "How to sign off" expands
   to show step-by-step instructions with CLI commands.
6. **Wait time** — days since the item entered its current state (from
   `reviewedAt` or `created` date).
7. **Priority badge** — shown for Critical/Major items.
8. **Navigation links**:
   - "Open in Jira" — external link to the Jira ticket.
   - "Details" — navigates to the existing detail view
     (`rfe-review?select=KEY` or `feature-review?select=KEY`).

### 8.3 Sections

| Section | Default | Contains | Sort |
|---------|---------|----------|------|
| **Action Needed** | Expanded | RFE states 1-3, Feature states 1-3 | Wait time desc, then priority |
| **In Progress** | Collapsed | RFE state 4, processing features | Wait time desc |
| **Recently Completed** | Collapsed | RFE state 5 (last 7d), Feature state 4 (last 7d) | Completion date desc |

RFEs and Features are interleaved within each section, sorted purely by wait
time (longest waiting first), then by priority as a tiebreaker.

### 8.4 Filters

| Filter | Options | Default |
|--------|---------|---------|
| **Stage** | All / RFEs only / Features only | All |
| **Priority** | All / Critical / Major / Minor | All |

No release/version filter in MVP.

### 8.5 Color coding

| Color | Usage |
|-------|-------|
| Red (`bg-red-50`) | Rejected or failed items requiring immediate action |
| Amber (`bg-amber-50`) | Items needing human action (review, revision, scope label) |
| Blue (`bg-blue-50`) | Items in progress, no action needed |
| Green (`bg-green-50`) | Completed / signed-off items |

---

## 9. Data Loading

### 9.1 Composables used

| Composable | Endpoint | Purpose |
|------------|----------|---------|
| `useRoster()` | `/api/roster` | User identity + component resolution |
| `useAIImpact(timeWindow)` | `/api/modules/ai-impact/rfe-data` | RFE data with labels |
| `useFeatures()` | `/api/modules/ai-impact/features` | Feature data with scores |
| `useAssessments()` | `/api/modules/ai-impact/assessments` | RFE assessment scores (for inline display) |

### 9.2 Loading strategy

- Load all four composables in parallel via `Promise.allSettled`.
- Render sections progressively as each resolves (skeleton loader per
  section).
- Each composable creates independent state (not singletons). This is an
  accepted tradeoff — data is cached via localStorage stale-while-revalidate.
- Show `lastSyncedAt` timestamp per data source at the bottom of the page.

### 9.3 Client-side filtering

All filtering and state classification happens client-side. No new server
endpoints are needed for MVP. The flow:

1. Resolve user's components (section 3).
2. Filter RFEs where `rfe.components` overlaps user's components.
3. Filter Features where `feature.components` overlaps user's components.
4. Classify each item into its state (sections 5-6).
5. Sort by action priority, then wait time, then Jira priority.

---

## 10. Empty & Error States

| Scenario | Behavior |
|----------|----------|
| **User has no component assignment** | Placeholder message with link to Team Tracker settings. Show all items below as fallback. |
| **User's components match zero items** | Congratulatory "all clear" state: "No items in your component area need attention right now." Link to AI Factory Guide. |
| **Roster fails to load** | Error banner with retry button. Page is non-functional without roster. |
| **RFE/Feature data fails to load** | Per-section error state with retry. Other sections still render. |
| **User not in roster** | "We couldn't find your profile in the roster. Your SSO username (acorvin) didn't match any roster entry." Link to admin contact. |

---

## 11. Scope

### In scope (MVP)

- For You view with component-based filtering
- RFE state machine (5 states) with inline scores and guidance
- Feature state machine (4 states + edge cases) with inline scores and
  guidance
- Summary statistics bar
- Stage and priority filters
- Collapsible action guidance with CLI commands
- Progressive data loading with skeletons
- Fixture updates for demo mode
- Data pipeline changes (add `components` to RFE fetcher and feature sync)

### Out of scope (MVP)

- Test plans, documentation, build & release items
- Admin "browse as" capability (existing user impersonation covers this)
- Notification system integration (Phase 2)
- Release/version filtering
- Making "For You" the default landing page
- Server-side aggregation endpoint

### Future phases

- **Phase 2**: Add test plans and documentation (linked via feature's
  `sourceRfe` or RHAISTRAT key). Add notification provider for new action
  items.
- **Phase 3**: Make "For You" the default landing page. Add release filter
  once `fixVersions` data is reliably available on features. Consider
  server-side aggregation if client-side filtering becomes slow at scale.

---

## 12. Files to Create or Modify

### New files

| File | Purpose |
|------|---------|
| `modules/ai-impact/client/views/ForYouView.vue` | Main view component |
| `modules/ai-impact/client/components/ForYouCard.vue` | Reusable item card with scores, action text, guidance |
| `modules/ai-impact/client/components/ForYouStats.vue` | Summary statistics bar |
| `modules/ai-impact/client/composables/useForYou.js` | Component resolution, item filtering, state classification |

### Modified files

| File | Change |
|------|--------|
| `modules/ai-impact/module.json` | Add `for-you` nav item |
| `modules/ai-impact/client/index.js` | Register `for-you` route |
| `modules/ai-impact/server/jira/rfe-fetcher.js` | Add `components` to fields + processIssue |
| `modules/ai-impact/server/features/jira-sync.js` | Add `components` to JQL fields + applyJiraFields |
| `modules/ai-impact/server/features/storage.js` | Add `components` to slim projection |
| `modules/ai-impact/server/features/validation.js` | Accept optional `components` field |
| `fixtures/ai-impact/rfe-data.json` | Add `components` arrays |
| `fixtures/ai-impact/features.json` | Add `components` arrays |
