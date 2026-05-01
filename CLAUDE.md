# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Full architecture, API routes, deployment, and integration details are in `.claude/CLAUDE.md` (auto-loaded as project instructions). This file covers commands, conventions, and cross-cutting rules that apply to all work.

## Commands

```bash
npm run dev:full          # Start Vite (5173) + Express (3001) together
npm run dev               # Vite frontend only
npm run dev:server        # Express backend only (requires .env)
npm test                  # Run all tests once
npm run test:watch        # Run tests in watch mode
npm run lint              # ESLint — must pass before committing
npm run validate:modules  # Validate all module.json manifests (also runs in CI)
npm run validate:openapi  # Validate OpenAPI spec
npm run build             # Production Vite build
```

**Run a single test file:**
```bash
npx vitest run modules/team-tracker/__tests__/server/jira.test.js
npx vitest run --reporter=verbose src/__tests__/SomeComponent.test.js
```

**Demo mode (no credentials needed):**
```bash
echo "DEMO_MODE=true\nVITE_DEMO_MODE=true" > .env && npm run dev:full
```

## Code Style

- **Frontend**: ES modules (`import`), Vue 3 `<script setup>`, Tailwind CSS utility classes
- **Backend**: CommonJS (`require`), Express router pattern
- **No TypeScript** — plain JavaScript throughout
- `husky` + `lint-staged` auto-runs ESLint on staged files; always verify with `npm run lint` before committing

## Testing

- Vitest + `@vue/test-utils` for frontend and backend unit tests
- Tests live in `modules/*/__tests__/client/` (frontend) and `modules/*/__tests__/server/` (backend)
- Shell-level tests: `src/__tests__/`
- `npm run validate:modules` must pass in CI — run it after any `module.json` change

## Architecture

### Import rules — enforced by convention
- **Modules cannot import from other modules** — only from `@shared` (`@shared/client` or `@shared/server`)
- `@shared` alias resolves to `shared/` (configured in `vite.config.mjs` for frontend; documented convention for backend)
- Breaking changes to `shared/` exports require a deprecation cycle (see `shared/API.md`)

### Module system
Each built-in module lives in `modules/<slug>/` with:
- `module.json` — manifest (name, slug, navItems, entry points)
- `client/index.js` — exports `{ routes }` (view id → `defineAsyncComponent`)
- `server/index.js` — exports `function(router, context)` to register Express routes at `/api/modules/<slug>/`
- `__tests__/client/` and `__tests__/server/`

Auto-discovery: frontend uses `import.meta.glob('/modules/*/module.json')`; backend scans via `server/module-loader.js`.

### Hash routing
Navigation is `#/<module-slug>/<view-id>?key=value`. Modules receive `navigateTo`, `goBack`, and reactive `params` via `inject('moduleNav')`.

### Data layer
- All JSON data stored under `data/` (PVC-mounted in production), accessed via `shared/server/storage.js`
- Demo mode swaps in `shared/server/demo-storage.js` backed by `fixtures/` — **fixtures must always match production format** (schema defined in `docs/DATA-FORMATS.md`)
- Frontend caching: `localStorage` stale-while-revalidate via `cachedRequest(key, fetcher, onData)` — `onData` is called twice (cached, then fresh)

### Key data files
| File | Purpose |
|------|---------|
| `data/org-roster-full.json` | Source of truth for orgs/teams/members |
| `data/people/{name}.json` | Per-person Jira metrics (365-day lookback) |
| `data/jira-name-map.json` | Cache of display name → Jira accountId |
| `data/github-contributions.json` / `data/gitlab-contributions.json` | Contribution counts |
| `data/snapshots/{teamKey}/{date}.json` | Monthly metric snapshots (teamKey: `::` → `--`) |
| `data/roster-sync-config.json` | Org roots, Google Sheet ID, GitLab instances |
| `data/site-config.json` | Platform title prefix |

## Documentation maintenance

When making code changes, keep these docs in sync:

| Change | Update |
|--------|--------|
| Data file format | `docs/DATA-FORMATS.md` + `fixtures/` |
| API route added/removed | API Routes section in `.claude/CLAUDE.md` |
| New `shared/` export | `shared/API.md` |
| Module system changes | `docs/MODULES.md` |
| New data file or storage path | Data Flow in `.claude/CLAUDE.md` + `docs/DATA-FORMATS.md` |
