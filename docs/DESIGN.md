# Technical Design Document — AI Platform People & Teams (rhai-org-pulse)

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Frontend Tier](#3-frontend-tier)
4. [Backend Tier](#4-backend-tier)
5. [Data Tier](#5-data-tier)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Module System](#7-module-system)
8. [Built-In Modules](#8-built-in-modules)
9. [Integration Tier](#9-integration-tier)
10. [Roster Sync Pipeline](#10-roster-sync-pipeline)
11. [Deployment Architecture](#11-deployment-architecture)
12. [CI/CD Pipeline](#12-cicd-pipeline)
13. [Key Design Patterns](#13-key-design-patterns)

---

## 1. System Overview

**People & Teams** is an internal Red Hat engineering dashboard that aggregates delivery metrics across Jira, GitHub, and GitLab for AI Platform teams. It provides org-level visibility into sprint health, individual contributor metrics, feature traffic, AI impact assessments, and team roster management.

### Primary Use Cases

| Use Case | Description |
|----------|-------------|
| Delivery Metrics | Per-person and per-team Jira issue resolution, story points, cycle times |
| Roster Management | Automated org roster from Red Hat IPA LDAP + Google Sheets enrichment |
| Contribution Tracking | GitHub and GitLab contribution counts and monthly history |
| Sprint Tracking | Sprint-by-sprint committed vs. delivered analysis |
| AI Impact Assessment | RFE/feature-level AI adoption scoring across the delivery pipeline |
| Feature Traffic | RHAISTRAT feature delivery tracking across repos and components |
| Release Planning | Big Rock tracking, RFE discovery, release health dashboards |

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 (Composition API, `<script setup>`), Vite 6, Tailwind CSS 3, Chart.js 4 |
| Backend | Node.js 20, Express.js, CommonJS |
| Storage | Local filesystem (PVC-mounted in OpenShift) |
| Auth (prod) | OpenShift OAuth Proxy (sidecar) |
| Build | Vite (frontend), esbuild (backend in CI) |
| Container | UBI9 (backend: nodejs-20-minimal, frontend: nginx-124) |
| Orchestration | OpenShift via ArgoCD + Kustomize |

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          OpenShift Cluster                                │
│                                                                          │
│  ┌──────────────────────────────────────┐                                │
│  │         Frontend Pod                 │                                │
│  │  ┌──────────────┐  ┌─────────────┐  │                                │
│  │  │  OAuth Proxy │  │   nginx     │  │  ◄── User browser              │
│  │  │  (sidecar)   │  │   :8080     │  │                                │
│  │  └──────┬───────┘  └──────┬──────┘  │                                │
│  │         │ X-Forwarded-*   │         │                                │
│  └─────────┼─────────────────┼─────────┘                                │
│            │                 │ /api/*, /modules/*                        │
│            ▼                 ▼                                           │
│  ┌──────────────────────────────────────┐                                │
│  │         Backend Pod                  │                                │
│  │  ┌──────────────────────────────┐   │                                │
│  │  │  Express Server :3001        │   │                                │
│  │  │  ├── authMiddleware          │   │                                │
│  │  │  ├── proxySecretGuard        │   │                                │
│  │  │  ├── module routes           │   │                                │
│  │  │  └── legacy forwards         │   │                                │
│  │  └──────────────────────────────┘   │                                │
│  │  ┌──────────────────────────────┐   │                                │
│  │  │  PVC — ./data/               │   │                                │
│  │  │  JSON flat-file storage      │   │                                │
│  │  └──────────────────────────────┘   │                                │
│  └──────────────────────────────────────┘                                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
          │                  │                   │
          ▼                  ▼                   ▼
   ┌────────────┐   ┌───────────────┐   ┌──────────────────┐
   │ Jira Cloud │   │ GitHub GraphQL│   │ GitLab GraphQL   │
   │ (redhat    │   │ API           │   │ (per-instance)   │
   │ .atlassian)│   │               │   │                  │
   └────────────┘   └───────────────┘   └──────────────────┘
                                                │
                                        ┌───────────────┐
                                        │  IPA LDAP     │
                                        │ (corp VPN)    │
                                        └───────────────┘
                                                │
                                        ┌───────────────┐
                                        │ Google Sheets │
                                        │ (enrichment)  │
                                        └───────────────┘
```

---

## 3. Frontend Tier

### 3.1 Application Shell

The frontend is a Vue 3 Single Page Application with no traditional router. Navigation is entirely hash-based, eliminating the need for server-side route handling.

```
src/
├── components/
│   ├── App.vue              ← root shell, hash routing, sidebar wiring
│   ├── AppSidebar.vue       ← navigation sidebar with module list
│   ├── LandingPage.vue      ← home screen when no module is active
│   └── SettingsView.vue     ← platform settings (admin-only)
├── composables/
│   ├── useModules.js        ← git-static module discovery + enable/disable state
│   ├── useModuleAdmin.js    ← admin enable/disable operations
│   ├── useTheme.js          ← light/dark/system theme (localStorage)
│   └── useApiTokens.js      ← token creation/revocation UI
├── module-loader.js         ← import.meta.glob discovery of built-in modules
└── __tests__/               ← shell-level Vitest tests
```

### 3.2 Hash Routing

All navigation uses `window.location.hash`. The shell owns route parsing; modules never see URLs directly.

```
Hash format:  #/<module-slug>/<view-id>?<query-params>

Examples:
  #/team-tracker/home
  #/team-tracker/team-detail?teamKey=shgriffi::Model%20Serving
  #/team-tracker/person-detail?person=Alice%20Smith
  #/ai-impact/rfe-review
  #/feature-traffic/feature-detail?key=RHOAIENG-1234
```

**Parsing flow:**

```
window.location.hash
        │
        ▼
   parseHash()
        │
        ├── slug = path segments[0]   →  "team-tracker"
        ├── viewId = path segments[1] →  "team-detail"
        └── params = URLSearchParams  →  { teamKey: "shgriffi::Model Serving" }
        │
        ▼
 handleSidebarNavigate()
        │
        ├── Find matching built-in module by slug
        ├── Inject moduleNav { navigateTo, goBack, params } via provide/inject
        └── Render active module's view component
```

**Backward-compatible redirects:** Legacy hashes like `#/org-roster/...` are silently rewritten to `#/team-tracker/...` by the shell.

### 3.3 Module Navigation API

Modules receive navigation capabilities via Vue's `provide/inject`:

```javascript
// In any module view component
const nav = inject('moduleNav')

nav.navigateTo('team-detail', { teamKey: 'shgriffi::Model Serving' })
nav.goBack()
nav.params  // reactive: { teamKey: 'shgriffi::Model Serving' }
```

### 3.4 Shared Client Layer

```
shared/client/
├── index.js                 ← barrel export (stability contract: shared/API.md)
├── services/
│   └── api.js               ← fetch wrapper + stale-while-revalidate cache
└── composables/
    ├── useRoster.js          ← org/team/member data
    ├── useAuth.js            ← current user, isAdmin
    ├── useGithubStats.js     ← GitHub contribution data
    ├── useGitlabStats.js     ← GitLab contribution data (multi-instance)
    ├── useAllowlist.js       ← allowlist CRUD (admin)
    ├── useBackendHealth.js   ← /api/healthz polling
    └── useModuleLink.js      ← cross-module hash link generation
```

### 3.5 Stale-While-Revalidate Cache

All API calls from modules go through the shared `cachedRequest()` function:

```
cachedRequest(cacheKey, fetcherFn, onData)
         │
         ├── 1. Read localStorage["app_cache:<key>"]
         │         │
         │         ├── Hit → call onData(staleData) immediately
         │         └── Miss → skip (no first call)
         │
         └── 2. Fetch fresh data from API
                   │
                   ├── Success → call onData(freshData), update cache
                   └── Error  → if cache hit, swallow error silently
                                if cache miss, propagate error to UI
```

This pattern means UIs appear instantly with cached data while a background refresh runs, with no loading flash on revisits.

**Cache eviction:** When localStorage nears capacity, the oldest 50% of `app_cache:*` entries are evicted.

### 3.6 Module Auto-Discovery (Frontend)

```javascript
// module-loader.js
const manifests = import.meta.glob('/modules/*/module.json', { eager: true })
// Vite resolves this at build time to a static map of all module.json files

// Each module's views are lazy-loaded on demand:
// modules/<slug>/client/index.js exports:
export const routes = {
  'home':        defineAsyncComponent(() => import('./views/HomeView.vue')),
  'team-detail': defineAsyncComponent(() => import('./views/TeamDetailView.vue')),
}
```

---

## 4. Backend Tier

### 4.1 Express Server Structure

```
server/
└── dev-server.js     ← single entry point for both local dev and production
```

The same `dev-server.js` runs in both environments. Environment differences (auth, demo mode, data path) are driven entirely by environment variables.

### 4.2 Middleware Stack

Middleware executes in this order for every request:

```
Incoming Request
      │
      ▼
1. express.json()           ← parse JSON body (10 MB limit)
      │
      ▼
2. CORS (*)                 ← allow all origins (OAuth proxy enforces authn upstream)
      │
      ▼
3. requestTracker           ← log method, path, status, duration
      │
      ▼
4. proxySecretGuard()       ← validate X-Proxy-Secret header OR Bearer tt_ token
      │  (rejects 401 if PROXY_AUTH_SECRET set and neither matches)
      ▼
5. authMiddleware()         ← resolve req.userEmail + req.isAdmin
      │  Priority:
      │    1. Bearer tt_<token> → tokenValidator.validateToken()
      │    2. X-Forwarded-Email (set by OAuth proxy)
      │    3. ADMIN_EMAILS env var or "local-dev@redhat.com"
      ▼
6. Route handlers           ← module routes, legacy forwards, admin routes
```

### 4.3 Module Route Mounting

```
server startup
      │
      ▼
getDiscoveredModules()
  ├── scans modules/*/module.json
  ├── reads persisted enabled/disabled state from storage
  └── validates inter-module requires[] dependencies
      │
      ▼
createModuleRouters(modules, context)
  ├── for each enabled module with server.entry:
  │     require('./modules/<slug>/server/index.js')(router, context)
  │     context = { storage, requireAdmin, isAdmin, requireAuth }
  └── returns Map<slug, router>
      │
      ▼
app.use('/api/modules/<slug>', router)

Legacy forwards (team-tracker backward compat):
  /api/roster        → /api/modules/team-tracker/roster
  /api/person/:name  → /api/modules/team-tracker/person/:name
  /api/github/*      → /api/modules/team-tracker/github/*
  ... (15+ aliases)
```

### 4.4 Module Backend Entry Pattern

Every module's `server/index.js` exports a single function:

```javascript
// modules/<slug>/server/index.js
module.exports = function (router, { storage, requireAdmin, requireAuth, isAdmin }) {
  router.get('/some-endpoint', requireAuth, async (req, res) => {
    const data = await storage.readFromStorage('some-key')
    res.json(data)
  })

  router.post('/admin-endpoint', requireAdmin, async (req, res) => {
    await storage.writeToStorage('some-key', req.body)
    res.json({ ok: true })
  })
}
```

---

## 5. Data Tier

### 5.1 Storage Layer

All persistent state lives under `./data/` (PVC-mounted at `/app/data` in production). The storage API is a thin wrapper over `fs.promises` with path-safety validation:

```javascript
// shared/server/storage.js
readFromStorage(key)                  // reads data/<key>.json
writeToStorage(key, data)             // writes data/<key>.json (atomic rename)
listStorageFiles(dir)                 // lists data/<dir>/*.json filenames
deleteStorageDirectory(dir)           // rm -rf data/<dir>/
```

All keys are validated against `../` traversal. JSON is parsed on read and serialized on write.

**Demo mode** substitutes `shared/server/demo-storage.js`, which reads from `fixtures/` (read-only). All writes are silently no-ops.

### 5.2 Data File Map

```
data/
├── org-roster-full.json          ← canonical org/team/member hierarchy (built by roster sync)
├── jira-name-map.json            ← display name → Jira accountId cache
├── allowlist.json                ← authorized user emails
├── site-config.json              ← { titlePrefix }
├── roster-sync-config.json       ← org roots, Sheet ID, GitLab instances, inference settings
│
├── people/
│   └── {sanitized_name}.json    ← per-person Jira metrics (365-day lookback)
│
├── github-contributions.json     ← { users: { username: { totalContributions, months, fetchedAt } } }
├── github-history.json           ← { users: { username: { months: { "2024-01": 42 } } } }
├── gitlab-contributions.json     ← same shape, per GitLab instance
├── gitlab-history.json           ← same shape
│
├── snapshots/
│   └── {sanitized-teamKey}/
│       └── {YYYY-MM-DD}.json    ← monthly metric snapshot (teamKey: "::" → "--")
│
├── boards.json                   ← Jira board list (for sprint tracking)
├── tokens/                       ← API token store (one file per token)
└── feature-traffic/              ← feature-traffic module data
```

### 5.3 Person Metrics Schema

```json
{
  "jiraDisplayName": "Alice Smith",
  "jiraAccountId": "5e41b8c03df51b0c937390ec",
  "fetchedAt": "2026-03-27T06:02:05.213Z",
  "lookbackDays": 365,
  "resolved": {
    "count": 54,
    "storyPoints": 139,
    "issues": [
      {
        "key": "PROJ-1234",
        "summary": "Fix login bug",
        "status": "Resolved",
        "storyPoints": 3,
        "resolutionDate": "2026-03-26T18:40:28.603+0000",
        "cycleTimeDays": 4.5
      }
    ]
  },
  "inProgress": { "count": 1, "storyPoints": 1, "issues": [...] },
  "cycleTime": { "avgDays": 8.6, "medianDays": 2.4 }
}
```

---

## 6. Authentication & Authorization

### 6.1 Production Auth Flow (OpenShift)

```
Browser
  │
  │ GET /api/roster (no session)
  ▼
OpenShift OAuth Proxy (sidecar on frontend pod)
  │
  ├── No session → redirect to OpenShift OAuth provider
  │       │
  │       └── User logs in with Red Hat SSO
  │
  ├── Session valid → inject headers:
  │       X-Forwarded-Email:              user@redhat.com
  │       X-Forwarded-User:              username
  │       X-Forwarded-Preferred-Username: preferred
  │
  ▼
nginx (frontend container)
  │
  ├── proxy_pass http://backend:3001
  ├── proxy_set_header X-Forwarded-Email  $http_x_forwarded_email
  └── proxy_set_header X-Proxy-Secret    "${PROXY_AUTH_SECRET}"
  │
  ▼
Express Backend
  │
  ├── proxySecretGuard: compare X-Proxy-Secret (timing-safe) → 401 on mismatch
  ├── authMiddleware: set req.userEmail = X-Forwarded-Email (lowercased)
  └── requireAdmin: check req.userEmail in allowlist.json
```

### 6.2 API Token Auth (for automation / CI)

```
Client
  │
  │ Authorization: Bearer tt_<token>
  ▼
Backend authMiddleware
  │
  ├── Detect "tt_" prefix → tokenValidator.validateToken(raw)
  ├── Load token from data/tokens/<id>.json
  ├── Check: not expired, not revoked, hash matches
  ├── Update lastUsedAt
  └── Set req.userEmail = token.ownerEmail, req.isAdmin = token.isAdmin
```

Token lifecycle: `POST /api/tokens` returns the raw value exactly once. The backend stores only a bcrypt hash.

### 6.3 Local Dev Auth

```
ADMIN_EMAILS=deepak@redhat.com npm run dev:server
  │
  └── authMiddleware: req.userEmail = "deepak@redhat.com" (from env)
      req.isAdmin = true (first email in ADMIN_EMAILS is pre-seeded into allowlist)
```

### 6.4 Allowlist Management

```
allowlist.json: ["admin1@redhat.com", "admin2@redhat.com"]

Rules:
  - If empty: first authenticated user is auto-added (bootstrap)
  - Emails stored and compared lowercase
  - Admin cannot remove themselves (prevents lockout)
  - isAdmin is re-checked on every request (not cached in session)
```

---

## 7. Module System

### 7.1 Module Anatomy

```
modules/<slug>/
├── module.json              ← manifest (required)
├── client/
│   ├── index.js             ← exports { routes }  (view-id → AsyncComponent)
│   ├── views/               ← Vue SPA views
│   ├── components/          ← module-private components
│   └── composables/         ← module-private composables
├── server/
│   └── index.js             ← exports function(router, context)
└── __tests__/
    ├── client/              ← Vitest + @vue/test-utils
    └── server/              ← Vitest unit tests
```

### 7.2 module.json Structure

```json
{
  "name": "People & Teams",
  "slug": "team-tracker",
  "description": "Delivery metrics and org roster",
  "icon": "users-round",
  "order": 0,
  "defaultEnabled": true,
  "requires": [],
  "client": {
    "entry": "./client/index.js",
    "navItems": [
      { "id": "home", "label": "Team Directory", "icon": "Users", "default": true },
      { "id": "trends", "label": "Trends", "icon": "TrendingUp" }
    ],
    "settingsComponent": "./client/components/MySettings.vue"
  },
  "server": {
    "entry": "./server/index.js"
  }
}
```

### 7.3 Module Lifecycle

```
Server startup                     Client load
      │                                 │
      ▼                                 ▼
Scan modules/*/module.json        import.meta.glob resolves at build time
      │                                 │
      ▼                                 ▼
Load enabled state from storage   Filter by enabled slugs
      │                                 │
      ▼                                 ▼
Validate requires[] deps          Render sidebar navItems in order
      │                                 │
      ▼                                 ▼
Mount routers at /api/modules/    defineAsyncComponent → lazy load on navigate
<slug>/
```

### 7.4 Shared Code Rules

- Modules import from `@shared` only — never from `modules/<other-slug>/`
- `@shared` alias resolves to `shared/` (Vite alias for client, convention for server)
- Changes to `shared/` exports require a deprecation cycle (documented in `shared/API.md`)

### 7.5 Import Conventions

| Context | Style | Example |
|---------|-------|---------|
| Frontend (modules, src/) | ES Modules | `import { useRoster } from '@shared/client'` |
| Backend (server/, modules/*/server/) | CommonJS | `const { storage } = require('@shared/server')` |

---

## 8. Built-In Modules

### 8.1 team-tracker (People & Teams)

**Order:** 0 (first in sidebar) | **Default:** enabled

The core module. Owns the canonical roster and all delivery metrics.

```
Views:
  home           → Team Directory (org tree + team cards)
  people         → People directory (searchable, filterable)
  trends         → Monthly charts (issues, story points, GitHub, GitLab)
  reports        → Per-team summary reports
  org-dashboard  → Org-wide aggregate view
  team-detail    → Team roster with person metrics, sprint data
  person-detail  → Individual profile (Jira, GitHub, GitLab, cycle time)

Server routes (at /api/modules/team-tracker/):
  GET  /roster                    org/team/member hierarchy
  GET  /person/:name/metrics      individual Jira metrics
  GET  /people/metrics            all people (bulk)
  GET  /team/:key/metrics         team aggregate
  GET  /github/contributions      GitHub counts + history
  GET  /gitlab/contributions      GitLab counts + history
  GET  /trends                    monthly aggregated trends
  POST /refresh                   trigger metrics refresh (admin)
  GET|POST /admin/roster-sync/*   roster sync config + trigger (admin)
  GET|POST /admin/snapshots/*     snapshot management (admin)
```

### 8.2 ai-impact (AI Impact Assessment)

**Order:** 5 | **Default:** enabled

Tracks AI adoption scores for RFEs and features across the RHAI delivery pipeline.

```
Views:
  rfe-review           → RFE assessment list with AI scores
  feature-review       → Feature list with assessments
  implementation       → Implementation-phase assessment view
  qe-validation        → QE/Validation-phase view
  security             → Security-phase view
  documentation        → Documentation-phase view
  build-release        → Build & Release-phase view
  jira-autofix         → Jira AutoFix tooling view

Storage:
  data/ai-impact/assessments/<key>.json    ← per-RFE assessment + history
  data/ai-impact/features/<key>.json       ← per-feature data + history

Routes (at /api/modules/ai-impact/):
  GET|PUT     /assessments/:key    single assessment (PUT = upsert)
  GET         /assessments         all latest assessments
  POST        /assessments/bulk    bulk upsert (admin)
  DELETE      /assessments         clear all (admin)
  GET|PUT     /features/:key       single feature
  GET         /features            all features
  POST        /features/bulk       bulk upsert (admin)
```

### 8.3 feature-traffic (Feature Traffic)

**Order:** 15 | **Default:** enabled

Traffic maps showing RHAISTRAT feature delivery status across repos and components. Data is pulled from GitLab CI artifacts.

```
Views:
  overview        → Feature list with traffic-light health indicators
  feature-detail  → Full feature detail with version breakdown

Data source: GitLab CI pipeline artifacts (refreshed via /api/modules/feature-traffic/refresh)

Routes:
  GET  /features           list with filters (status, version, health, sort)
  GET  /features/:key      full feature detail
  GET  /versions           unique fix versions
  GET  /status             data freshness + staleness warning
  GET|POST /config         fetch configuration (admin)
  POST /refresh            trigger manual refresh from GitLab CI (admin)
```

### 8.4 release-analysis (Release Analysis)

**Order:** 10 | **Default:** enabled

Release-by-release analysis of RHAI deliverables.

```
Views:
  release-analysis     → Summary dashboard per release
  component-breakdown  → Breakdown by component

Data: Jira + Product Pages integration
```

### 8.5 release-planning (Release Planning)

**Order:** 20 | **Default:** enabled

Big Rock tracking and feature/RFE discovery from Jira.

```
Views:
  big-rocks      → Strategic feature planning
  release-health → Release plan health indicators
  audit-log      → Change audit trail
```

### 8.6 allocation-tracker (Allocation Tracker)

**Order:** 10 | **Default:** disabled

Sprint-level allocation tracking against a 40-40-20 model (customer, platform, innovation).

```
Views:
  allocation    → Per-sprint allocation breakdown (default)
  project       → Project-level view
  team-detail   → Team-specific allocation

Has a custom settings component (settingsComponent) for allocation targets.
```

### 8.7 upstream-pulse (Upstream Pulse)

**Order:** 10 | **Default:** disabled

Upstream open-source contribution insights.

```
Views:
  dashboard   → Contribution metrics overview (default)
  insights    → Trend analysis
  portfolio   → Project portfolio view
  strategy    → Strategic alignment
```

---

## 9. Integration Tier

### 9.1 Jira Integration

**Endpoint:** `https://redhat.atlassian.net` (Jira Cloud)
**Auth:** Basic auth — base64(`JIRA_EMAIL:JIRA_TOKEN`)

#### Person Metrics Fetch Flow

```
refreshPersonMetrics(name)
        │
        ├── Look up Jira accountId in jira-name-map.json
        │     └── Miss → search Jira /rest/api/2/user/search?query=<name>
        │           └── Tries: email, firstName+lastName, lastName, full name
        │
        ├── Query resolved issues (JQL):
        │     assignee = "<accountId>"
        │     AND status in (Done, Closed, Resolved)
        │     AND resolutionDate >= <365 days ago>
        │     ORDER BY resolutionDate DESC
        │
        ├── Query in-progress issues (JQL):
        │     assignee = "<accountId>"
        │     AND status NOT IN (Done, Closed, Resolved)
        │
        ├── Compute metrics:
        │     totalResolved, totalStoryPoints, avgCycleTime, medianCycleTime
        │
        └── Write to data/people/{sanitized_name}.json
```

**Cycle time calculation:** First transition into an active status (In Progress, In Review, etc.) → `resolutionDate`. Computed from Jira changelog.

**Pagination:** Cursor-based via `nextPageToken` (`GET /rest/api/3/search/jql`). Fetches all pages automatically.

**Rate limiting:** 3 retries with exponential backoff. Respects `Retry-After` header on 429 responses.

#### Sprint Data Flow

```
GET /api/modules/team-tracker/teams
        │
        ├── Load boards.json (cached Jira board list)
        │     └── Stale? → fetch /rest/agile/1.0/board?maxResults=50
        │
        ├── For each board:
        │     GET /rest/greenhopper/1.0/rapid/charts/sprintreport
        │       ?rapidViewId=<boardId>&sprintId=<id>
        │
        └── Response: { committedPoints, completedPoints, issues[], sprintName }
```

### 9.2 GitHub Integration

**API:** GitHub GraphQL (`https://api.github.com/graphql`)
**Auth:** `Authorization: bearer ${GITHUB_TOKEN}` (classic PAT, `read:user` scope)

#### Contribution Fetch Flow

```
fetchContributions(usernames[])
        │
        ├── Split into batches of 5 users
        │
        └── For each batch:
              │
              ├── Build aliased GraphQL query:
              │     user0: user(login: "alice") { contributionsCollection { ... } }
              │     user1: user(login: "bob")   { contributionsCollection { ... } }
              │     ...
              │
              ├── One HTTP request per batch
              │
              ├── Extract from contributionCalendar:
              │     totalContributions
              │     weeks[].contributionDays[] → derive monthly breakdown
              │
              ├── Write to github-contributions.json
              │
              └── Sleep 2s between batches (rate limit safety)
```

A **single GraphQL query** per batch yields both the total count and the full daily calendar, from which monthly history is derived without a second request.

### 9.3 GitLab Integration

**API:** GitLab GraphQL (`{baseUrl}/api/graphql`)
**Auth:** `Authorization: Bearer <instance-token>` (PAT with `read_api` scope)
**Config:** Multiple instances in `roster-sync-config.json` → `gitlabInstances[]`

#### Contribution Fetch Flow

```
fetchContributions(usernames[], instances[])
        │
        ├── For each instance (in parallel, Promise.allSettled):
        │     5-minute per-instance timeout
        │     │
        │     └── For each group in instance.groups (sequential, 200ms delay):
        │           │
        │           └── Query in 31-day windows (93-day API limit):
        │                 group { contributions(username, from, to) { count } }
        │
        └── Merge per-instance results into gitlab-contributions.json
            (instance label stored alongside totals for profile URL generation)
```

**Instance config schema:**
```json
{
  "gitlabInstances": [
    {
      "label": "GitLab.com",
      "baseUrl": "https://gitlab.com",
      "tokenEnvVar": "GITLAB_TOKEN",
      "groups": ["redhat-et"]
    },
    {
      "label": "Internal",
      "baseUrl": "https://gitlab.cee.redhat.com",
      "tokenEnvVar": "FEATURE_TRAFFIC_GITLAB_TOKEN",
      "groups": ["rhoai"]
    }
  ]
}
```

---

## 10. Roster Sync Pipeline

The roster sync pipeline replaces manual roster maintenance. It runs on a 24-hour schedule and can be triggered manually from Settings.

### 10.1 Pipeline Phases

```
runConsolidatedSync()
        │
        ├── Phase 1: IPA LDAP Traversal
        │     │
        │     ├── Connect to ipa.corp.redhat.com via LDAPS (VPN required)
        │     ├── Bind with IPA_BIND_DN + IPA_BIND_PASSWORD (service account)
        │     ├── For each org root UID in config.orgRoots:
        │     │     traverse manager → direct reports recursively
        │     │     extract: uid, cn, mail, title, manager, rhatSocialUrl
        │     │       rhatSocialUrl → parse GitHub/GitLab usernames
        │     └── Filter excluded job titles (contractors, interns by config)
        │
        ├── Phase 2: Google Sheets Enrichment
        │     │
        │     ├── Authenticate with Google SA key (GOOGLE_SERVICE_ACCOUNT_KEY_FILE)
        │     ├── Auto-discover sheet names from configured spreadsheetId
        │     └── For each sheet row matching an LDAP person:
        │           merge: team grouping, specialty, engineeringLead,
        │                  productManager, jiraComponent, customFields
        │
        ├── Phase 3: Username Inference (optional)
        │     │
        │     ├── For people without GitHub: fuzzy-match against GitHub org members
        │     │     (configured githubOrgs in settings)
        │     └── For people without GitLab: fuzzy-match against GitLab group members
        │           (per-instance, configured in gitlabInstances)
        │
        └── Phase 4: Lifecycle Merge & Write
              │
              ├── Load existing org-roster-full.json
              ├── Merge: detect joined, left, reactivated, changed
              ├── Grace period: departed staff kept for N days before removal
              ├── Compute coverage % (people with full data)
              └── Write org-roster-full.json with updated metadata
```

### 10.2 org-roster-full.json Structure

```json
{
  "lastSyncAt": "2026-04-30T06:00:00Z",
  "coverage": 94.2,
  "orgs": {
    "shgriffi": {
      "displayName": "Scott Griffiths Org",
      "teams": {
        "Model Serving": {
          "members": [
            {
              "uid": "asmith",
              "name": "Alice Smith",
              "email": "asmith@redhat.com",
              "title": "Principal Software Engineer",
              "github": { "username": "alicesmith" },
              "gitlab": { "usernames": ["asmith-rh"] },
              "enrichment": {
                "specialty": "Inference",
                "engineeringLead": "Bob Jones"
              }
            }
          ]
        }
      }
    }
  }
}
```

### 10.3 Data Flow into Roster API

```
org-roster-full.json
        │
        ▼
deriveRoster()          ← server-side transform on every /api/roster request
        │
        ├── Build flat people list
        ├── Attach Jira metrics from data/people/*.json
        ├── Attach GitHub stats from github-contributions.json
        ├── Attach GitLab stats from gitlab-contributions.json
        └── Return structured { orgs, teams, people } response
```

### 10.4 Sync Status API

The sync pipeline exposes phase-level progress for real-time UI feedback:

```json
GET /api/admin/roster-sync/status
{
  "running": true,
  "phase": "sheets",
  "phaseLabel": "Enriching from Google Sheets...",
  "metadataSync": { "startedAt": "2026-04-30T06:00:00Z" },
  "stale": false
}
```

---

## 11. Deployment Architecture

### 11.1 Container Images

**Backend (`quay.io/org-pulse/team-tracker-backend`)**
```
Base:     ubi9/nodejs-20-minimal
Build:    npm ci --omit=dev (production deps only)
Runtime:  node server/dev-server.js
Port:     3001
Mounts:   /app/data (PVC, persistent JSON storage)
User:     1001 (non-root)
```

**Frontend (`quay.io/org-pulse/team-tracker-frontend`)**
```
Stage 1 (build):   node:20-alpine
  npm ci && npm run build → dist/

Stage 2 (serve):   ubi9/nginx-124
  Copy dist/ → /opt/app-root/src/
  Port: 8080
  Config: deploy/nginx.conf
```

### 11.2 nginx Routing (Frontend Container)

```
Request
   │
   ├── /api/*      → proxy_pass http://backend:3001  (120s timeout)
   ├── /modules/*  → proxy_pass http://backend:3001  (120s timeout)
   ├── /healthz    → return 200 "ok"
   ├── /assets/*   → static files, Cache-Control: max-age=31536000 immutable
   └── /*          → try_files $uri $uri/ /index.html  (SPA fallback)
```

### 11.3 OpenShift Kustomize Overlays

```
deploy/openshift/
├── base/                         ← shared manifests
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── service.yaml
│   ├── pvc.yaml                  ← 10Gi RWO for data/
│   └── kustomization.yaml
│
└── overlays/
    ├── dev/                      ← namespace: team-tracker
    │   ├── ADMIN_EMAILS cleared  ← first user auto-becomes admin
    │   └── images: :latest
    │
    ├── preprod/                  ← namespace: ambient-code--team-tracker
    │   └── images: :<sha>        ← auto-updated by CI on preprod branch push
    │
    └── prod/                     ← namespace: prod
        ├── ADMIN_EMAILS set      ← pre-seeded admins
        └── images: :<sha>        ← auto-updated by CI via PR on main push
```

**ConfigMap rollout:** `configMapGenerator` in kustomize produces content-hashed ConfigMap names (e.g., `team-tracker-config-5h2f9k`). Any config change → new name → pod rollout automatically triggered.

### 11.4 ArgoCD Auto-Sync

```
git push to main
      │
      ▼
GitHub Actions builds + pushes images
      │
      ▼
CI creates PR: kustomization.yaml image tag updated
      │  (uses GH_PAT with admin bypass for branch protection)
      ▼
PR auto-merges (squash)
      │
      ▼
ArgoCD detects manifest change in prod overlay
      │
      ▼
ArgoCD applies new kustomization → rolling update
```

### 11.5 Daily CronJob

```yaml
# deploy/openshift/overlays/prod/cronjob-sync-refresh.yaml
schedule: "0 6 * * *"  # 6:00 AM UTC daily

Steps:
  1. POST /api/admin/roster-sync/unified   ← roster + metadata sync
  2. POST /api/roster/refresh              ← all person Jira metrics
  3. POST /api/github/refresh              ← all GitHub contributions
  4. POST /api/gitlab/refresh              ← all GitLab contributions
```

---

## 12. CI/CD Pipeline

### 12.1 CI Workflow (`ci.yml`)

**Trigger:** Every PR + push to `main`

```
PR opened / commit pushed
         │
         ▼
┌────────────────────────────────────────────────┐
│  Job: "Test & Build" (required status check)   │
│                                                │
│  1. npm run validate:modules                   │
│  2. npm run lint                               │
│  3. npm test                                   │
│  4. npm run validate:openapi                   │
│  5. npm run build                              │
│  6. (if deploy/ changed)                       │
│     kustomize build overlays/dev               │
│     kustomize build overlays/preprod           │
│     kustomize build overlays/prod              │
└────────────────────────────────────────────────┘
```

Branch protection on `main`: requires "Test & Build" to pass. Admin role (`GH_PAT`) has bypass for CI auto-merge PRs.

### 12.2 Build & Push Workflow (`build-images.yml`)

**Trigger:** Push to `main` or `preprod` branches (or manual dispatch)

```
Push to main/preprod
         │
         ▼
Detect changed components:
  Backend changed?   src/server/, modules/*/server/, shared/server/, backend.Dockerfile
  Frontend changed?  src/, modules/*/client/, shared/client/, frontend.Dockerfile
         │
         ▼
┌──────────────────────────────────────┐
│  Job: Test (always runs)             │
│   npm test                           │
└────────────────┬─────────────────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
 Build Backend       Build Frontend
 (if changed)        (if changed)
         │                │
         ├── docker build  ├── docker build (multi-stage)
         ├── smoke test    ├── smoke test (/healthz)
         └── push :sha     └── push :sha
             push :latest      push :latest
         │                │
         └───────┬────────┘
                 ▼
  update-prod-image job
    kustomize edit set image <sha>
    Create PR → auto-merge (squash)
```

### 12.3 Claude Code Review (`claude-review.yml`)

**Trigger:** PR opened/updated

Uses Claude via `claude-code-action` to review PRs against the criteria in `.github/instructions/review.instructions.md`. The review checks: security, correctness, code quality, project conventions, and performance.

---

## 13. Key Design Patterns

### 13.1 Stale-While-Revalidate (Client Cache)

Frontend UIs never block on network. Every data-fetching composable uses `cachedRequest(key, fn, onData)` which calls `onData` twice: once immediately with cached data, once with fresh. This pattern eliminates perceived latency on revisits.

### 13.2 Dependency Injection for Modules

Modules never import `storage`, `auth`, or other infrastructure directly. These are passed as a `context` object at mount time. This allows the server to swap in demo storage, mock auth, or alternative implementations without module code changes.

### 13.3 Defense in Depth Auth

Three independent auth layers compose:
1. **OAuth proxy** authenticates the user session
2. **Proxy secret header** ensures requests arrive via nginx (not direct backend access)
3. **Allowlist** authorizes the specific user email

Any layer can be individually tightened or bypassed (for local dev) without breaking the others.

### 13.4 Incremental + TTL-Based Refresh

Data fetches are idempotent and skip-safe:
- Person metrics: skip if `fetchedAt` < 7 days ago (unless `force=true`)
- GitHub/GitLab: skip individual users if `fetchedAt` < 12 hours ago
- Roster sync: full re-traversal each run, but lifecycle merge is additive

This allows the daily CronJob to refresh everything safely without full-rebuilds on every run.

### 13.5 Atomic Writes

`writeToStorage(key, data)` writes to a temp file then renames it atomically. This prevents partial reads during concurrent requests and ensures the data directory is always in a consistent state even if the process is killed mid-write.

### 13.6 Graceful Demo Mode

`DEMO_MODE=true` / `VITE_DEMO_MODE=true` swaps the entire storage backend to read-only fixtures. No auth, no external API calls, no PVC required. Useful for demos and local development without credentials. Fixture files in `fixtures/` must always match production JSON schema (enforced by convention and tested via `docs/DATA-FORMATS.md`).

### 13.7 Module Isolation Boundary

The module system enforces a clear boundary:
- Modules **can** import from `@shared` (stable, versioned API)
- Modules **cannot** import from other modules (no sideways dependencies)
- Breaking changes to `@shared` require explicit deprecation in `shared/API.md`

This prevents coupling between modules and allows any module to be disabled without cascading failures.

---

*Generated: 2026-05-01 | Repository: rhai-org-pulse*
