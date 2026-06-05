---
repository: "red-hat-data-services/rhai-org-pulse"
overall_score: 6.8
scorecard:
  - dimension: "Unit Tests"
    score: 8.0
    status: "222 test files for 492 source files (45% ratio); Vitest + @vue/test-utils; well-organized per-module structure"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Playwright smoke + module integration tests against containers; dynamic matrix for changed modules"
  - dimension: "Build Integration"
    score: 8.0
    status: "PR builds Docker images and runs Playwright smoke tests; kustomize and OpenAPI validation"
  - dimension: "Image Testing"
    score: 6.0
    status: "Multi-stage builds with UBI9; runtime smoke tests; no vulnerability scanning or SBOM"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tracking, thresholds, or reporting configured anywhere"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "Smart path filtering, concurrency control, Socket Security, automated deploys, Claude code review"
  - dimension: "Agent Rules"
    score: 9.0
    status: "Comprehensive AGENTS.md + CLAUDE.md; automated Claude review and issue triage; AI config guard"
critical_gaps:
  - title: "No test coverage tracking or enforcement"
    impact: "Cannot measure coverage trends, detect regressions, or enforce minimum thresholds; no visibility into untested code"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container image vulnerability scanning"
    impact: "Known CVEs in base images or dependencies could ship to production undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No SAST or CodeQL integration"
    impact: "Security vulnerabilities in application code may not be caught before merge"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No SBOM generation or image signing"
    impact: "Cannot verify supply chain integrity or audit component inventory"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Vitest coverage reporting and Codecov integration"
    effort: "3-4 hours"
    impact: "Immediate visibility into test coverage with PR comments and trend tracking"
  - title: "Add Trivy container scanning to build-images workflow"
    effort: "1-2 hours"
    impact: "Catches known CVEs in container images before deployment"
  - title: "Add CodeQL or Semgrep workflow for SAST"
    effort: "2-3 hours"
    impact: "Automated detection of security anti-patterns in JavaScript code"
  - title: "Add .claude/rules/ test automation guidelines"
    effort: "2-3 hours"
    impact: "Standardize AI-generated test quality across unit, integration, and smoke tests"
recommendations:
  priority_0:
    - "Add Vitest coverage with --coverage flag, set minimum threshold at 60%, integrate with Codecov for PR reporting"
    - "Add Trivy scanning for both backend and frontend container images in build-images.yml"
  priority_1:
    - "Add CodeQL or Semgrep SAST workflow for JavaScript/Node.js security analysis"
    - "Add SBOM generation (Syft or Trivy SBOM mode) for supply chain visibility"
    - "Create .claude/rules/ with test patterns for Vitest unit tests and Playwright integration tests"
  priority_2:
    - "Add multi-architecture builds (amd64 + arm64) for developer parity"
    - "Add performance/load testing for API endpoints"
    - "Add contract tests between frontend API client and backend routes"
    - "Add accessibility testing with axe-core in Playwright tests"
---

# Quality Analysis: rhai-org-pulse (Org Pulse)

## Executive Summary

- **Overall Score: 6.8/10**
- **Repository Type**: Web application (Vue 3 SPA + Express backend)
- **Language**: JavaScript (no TypeScript, by design)
- **Framework**: Vue 3 + Vite + Tailwind CSS (frontend), Express (backend)
- **Deployment**: OpenShift via ArgoCD, dual containers (frontend nginx + backend Express)

### Key Strengths
1. **Excellent CI/CD pipeline** — Smart path-based filtering, concurrency control, Socket Security, automated deployments with image tag PRs, and comprehensive PR validation including Docker builds
2. **Strong test culture** — 222 test files covering frontend components, backend routes, stores, and utilities with Vitest + Playwright
3. **Industry-leading agent integration** — Claude Code review with autofix, issue triage bot, AI config guardrails, comprehensive AGENTS.md and CLAUDE.md

### Critical Gaps
1. **No coverage tracking** — Zero coverage reporting, thresholds, or trend analysis
2. **No security scanning** — No Trivy, Snyk, CodeQL, or any vulnerability scanning
3. **No SBOM or image signing** — No supply chain verification

### Agent Rules Status: **Strong** — AGENTS.md, .claude/CLAUDE.md, review instructions, and two Claude workflows (review + issues). Missing `.claude/rules/` for test-specific patterns.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8/10 | 222 test files, 45% test-to-source ratio, Vitest + vue/test-utils |
| Integration/E2E | 8/10 | Playwright smoke + module integration against containers |
| Build Integration | 8/10 | PR-time Docker builds, smoke tests, kustomize & OpenAPI validation |
| Image Testing | 6/10 | UBI9 multi-stage builds, runtime smoke tests; no vuln scanning |
| Coverage Tracking | **1/10** | **No coverage tracking, thresholds, or reporting** |
| CI/CD Automation | 9/10 | Smart path filtering, concurrency, Socket Security, auto-deploy |
| Agent Rules | 9/10 | Comprehensive AGENTS.md, Claude review + issues, AI config guard |

## Critical Gaps

### 1. No Test Coverage Tracking or Enforcement
- **Impact**: Cannot measure coverage trends, detect regressions, or enforce minimum thresholds
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Vitest has built-in coverage via `@vitest/coverage-v8`, but it's not configured. No `--coverage` flags, no codecov integration, no thresholds. With 222 test files, coverage is likely reasonable but unmeasured.
- **Fix**: Add coverage config to `vitest.config.mjs`, set thresholds, integrate Codecov

### 2. No Container Image Vulnerability Scanning
- **Impact**: Known CVEs in UBI9 base images or npm dependencies could ship undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `build-images.yml` builds and pushes images without any scanning step. No Trivy, Snyk, or equivalent.
- **Fix**: Add `aquasecurity/trivy-action` step after image build, before push

### 3. No SAST / CodeQL Integration
- **Impact**: Security vulnerabilities in application code (injection, XSS, etc.) not caught systematically
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: While Claude review checks for OWASP top 10 (per review instructions), there's no deterministic SAST tool. AI review is good but not a substitute for static analysis.
- **Fix**: Add `github/codeql-action` workflow for JavaScript analysis

### 4. No SBOM Generation or Image Signing
- **Impact**: Cannot verify supply chain integrity or audit dependency inventory
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: No Syft, Trivy SBOM, cosign, or attestation in the build pipeline.
- **Fix**: Add SBOM generation step and cosign signing to build-images.yml

## Quick Wins

### 1. Add Vitest Coverage Reporting (3-4 hours)
```bash
npm install -D @vitest/coverage-v8
```

Add to `vitest.config.mjs`:
```javascript
test: {
  coverage: {
    provider: 'v8',
    reporter: ['text', 'lcov'],
    thresholds: {
      lines: 60,
      functions: 60,
      branches: 50,
    },
  },
}
```

Add to `ci.yml`:
```yaml
- name: Run tests with coverage
  run: npm test -- --coverage

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 2. Add Trivy Container Scanning (1-2 hours)
Add to `build-images.yml` after image build:
```yaml
- name: Scan backend image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.BACKEND_IMAGE }}:${{ github.sha }}
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

### 3. Add CodeQL Workflow (2-3 hours)
Create `.github/workflows/codeql.yml`:
```yaml
name: CodeQL
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 8 * * 1'
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript
      - uses: github/codeql-action/analyze@v3
```

### 4. Add `.claude/rules/` Test Guidelines (2-3 hours)
Create test automation rules for AI agents to improve generated test quality.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (7 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR | Lint, test, build, kustomize validate, smoke tests |
| `build-images.yml` | Push to main/preprod | Build/push images, update tags, auto-merge deploy PRs |
| `integration-tests.yml` | PR (path-filtered) | Module-specific Playwright tests with dynamic matrix |
| `claude-review.yml` | PR | AI code review with autofix capability |
| `claude-issues.yml` | Issue/comment | AI issue triage and bug fixing |
| `guard-ai-configs.yml` | PR/review | Protect AI config files from unauthorized changes |
| `sync-preprod.yml` | Weekly cron | Sync main → preprod branch |

**Notable Practices**:
- Path-based change detection (`dorny/paths-filter`) for integration tests — only tests changed modules
- Concurrency control on build and integration workflows with `cancel-in-progress`
- Socket Security firewall for npm installs
- `npm audit --omit=dev --audit-level=high` on PRs
- Kustomize overlay validation for all environments
- OpenAPI spec validation as a required check
- Module manifest validation
- Automated image tag update PRs with auto-merge
- Fork-safe Claude review (read-only mode for forks)

**CI Score: 9/10** — One of the strongest CI/CD setups seen. Smart, efficient, and comprehensive.

### Test Coverage

**Unit Tests (Vitest)**:
- **222 test files** across all areas: src, shared, server, and all 5 modules
- **Test-to-source ratio**: 0.45 (222 test files / 492 source files)
- Framework: Vitest with `@vue/test-utils` for Vue components, `jsdom` for browser env
- Smart environment selection: `jsdom` for client code, `node` for server code
- Path aliases configured (`@shared`, `@modules`)

**Test Organization by Area**:
- `src/__tests__/` — App shell tests (6 files)
- `shared/server/__tests__/` — Shared server utilities (17 files)
- `shared/client/__tests__/` — Shared client utilities (3 files)
- `shared/server/roster-sync/__tests__/` — Roster sync (4 files)
- `server/__tests__/` and `server/*/\_\_tests\_\_/` — Server tests (13 files)
- `modules/ai-impact/__tests__/` — AI Impact module (22 files)
- `modules/releases/__tests__/` — Releases module (47 files — most tested)
- `modules/team-tracker/__tests__/` — Team Tracker module (48 files)
- `modules/upstream-pulse/__tests__/` — Upstream Pulse module (3 files)
- `modules/product-builds/__tests__/` — Product Builds module (3 files)

**Smoke Tests (Playwright)**:
- `tests/smoke/app-loads.spec.js` — 5 comprehensive tests:
  - Load without JS errors
  - Core layout structure
  - No stuck loading states
  - Client-side routing
  - Basic accessibility (semantic landmarks)
- Runs in official Playwright container (`mcr.microsoft.com/playwright:v1.60.0`)
- Runs against production container images in demo mode

**Integration Tests (Playwright)**:
- `tests/integration/` — 5 module-specific test files
- Tag-based filtering (`@module-name`) for selective execution
- Dynamic CI matrix tests only changed modules
- Reusable composite action for consistent execution

**Coverage**: No coverage tracking configured.

### Code Quality

**Linting**:
- ESLint 10 with flat config (`eslint.config.mjs`)
- `eslint-plugin-vue` (essential rules)
- Two custom rules:
  - `no-cross-module-imports` — Enforces module isolation
  - `no-module-process-env` — Enforces secrets system
- `no-unused-vars` with `_` prefix pattern

**Pre-commit Hooks**:
- Husky with `lint-staged`
- Auto-runs ESLint `--fix` on staged `.js`, `.mjs`, `.cjs`, `.vue` files

**Dependency Management**:
- Dependabot for npm (weekly, 10 PRs) and GitHub Actions (weekly, 5 PRs)
- Socket Security firewall in CI
- `npm audit --omit=dev --audit-level=high` on PRs

**Missing**:
- No TypeScript (by design, documented constraint)
- No `.pre-commit-config.yaml` (uses Husky instead — this is fine)
- No SAST tools (CodeQL, Semgrep, gosec)
- No secret detection (Gitleaks, TruffleHog)

### Container Images

**Build Process**:
- **Backend**: Single-stage, UBI9 Node.js 20 minimal, production deps only, non-root (UID 1001)
- **Frontend**: Multi-stage — build stage (npm + vite build) → serve stage (UBI9 nginx 124)
- Build args for traceability: `GIT_SHA`, `BUILD_DATE`
- Internal CA trust configured for corporate proxy
- `.dockerignore` present

**Runtime Testing**:
- Backend: Process liveness check (HTTP + kill -0 fallback)
- Frontend: Full Playwright smoke tests against running containers
- Demo mode for deterministic test data

**Missing**:
- No Trivy/Snyk vulnerability scanning
- No SBOM generation
- No image signing (cosign)
- No multi-architecture support (amd64 only)
- No Dockerfile linting (hadolint)

### Security

**Present**:
- Socket Security dependency firewall (npm ci)
- npm audit on PRs (high severity)
- Dependabot for automated dependency updates
- OpenShift OAuth proxy for production auth
- Storage abstraction prevents path traversal
- DOMPurify for HTML sanitization
- Guard AI configs workflow (team approval required)
- Review instructions include OWASP top 10 checklist
- Non-root containers (UID 1001)
- Structured JSON output from Claude review (verdict + blocking issues)

**Missing**:
- No SAST/CodeQL
- No container vulnerability scanning
- No secret detection
- No SBOM
- No image signing

### Agent Rules (Agentic Flow Quality)

**Status**: Present and comprehensive

**Files**:
| File | Purpose | Quality |
|------|---------|---------|
| `AGENTS.md` | Vendor-neutral conventions, 8 hard constraints | Excellent |
| `.claude/CLAUDE.md` | Architecture, API routes, deployment, testing | Excellent |
| `.github/instructions/review.instructions.md` | Shared review checklist with verdict rules | Strong |
| `.claude/commands/pr-review.md` | Manual PR review command | Good |
| `.claude/commands/create-module.md` | Module scaffolding command | Good |
| `.cursor/rules/upstream-pulse-module.mdc` | Cursor rules for one module | Basic |

**CI Integration**:
- `claude-review.yml` — Automated review on every PR with autofix capability, structured PASS/FAIL verdict, fork-safe (read-only for forks)
- `claude-issues.yml` — Issue triage, labeling, bug fixing, feature proposals (with approval gate)
- `guard-ai-configs.yml` — Protects AGENTS.md, .claude/, review instructions, and the guard workflow itself from unauthorized changes

**Strengths**:
- Hard constraints are enforced by both CI and AI review
- Documentation is layered (AGENTS.md for all tools, CLAUDE.md for Claude-specific)
- Review criteria explicitly cover security, correctness, conventions, performance, and API docs
- Issue bot has approval gate for features (won't implement without explicit go-ahead)
- "Claimed" label system prevents AI and human work from colliding

**Gaps**:
- No `.claude/rules/` directory with test-specific patterns
- No test automation guidance beyond what's in AGENTS.md
- Could benefit from `/test-rules-generator` to create Vitest/Playwright test patterns

## Recommendations

### Priority 0 (Critical)

1. **Add test coverage tracking with Codecov** (4-6 hours)
   - Install `@vitest/coverage-v8`
   - Configure coverage thresholds in `vitest.config.mjs` (start at 60% lines, ratchet up)
   - Add Codecov upload to `ci.yml`
   - Add `.codecov.yml` with PR comment settings
   - This is the single biggest gap for a repo with 222 test files

2. **Add container vulnerability scanning** (2-4 hours)
   - Add Trivy scanning to `build-images.yml` for both backend and frontend images
   - Set exit-code 1 for CRITICAL/HIGH severities
   - Consider `.trivyignore` for known acceptable CVEs
   - Block image push if critical CVEs found

### Priority 1 (High Value)

3. **Add SAST/CodeQL workflow** (2-4 hours)
   - Add `.github/workflows/codeql.yml` for JavaScript analysis
   - Run on PRs and weekly schedule
   - Complements Claude review with deterministic static analysis

4. **Add SBOM generation** (4-6 hours)
   - Use Trivy SBOM mode or Syft in build-images.yml
   - Attach SBOM as build artifact
   - Consider cosign for image signing

5. **Create `.claude/rules/` test patterns** (2-3 hours)
   - Unit test patterns for Vitest (component tests, store tests, route tests)
   - Integration test patterns for Playwright module tests
   - Smoke test patterns for new features
   - Run `/test-rules-generator` to bootstrap these

### Priority 2 (Nice-to-Have)

6. **Add multi-architecture builds** (6-8 hours) — Enable arm64 for developer parity on Apple Silicon
7. **Add accessibility testing with axe-core** (4-6 hours) — Extend Playwright smoke tests with `@axe-core/playwright`
8. **Add API contract tests** (8-12 hours) — Validate frontend API client against backend OpenAPI spec
9. **Add performance testing** (8-12 hours) — Load testing for API endpoints with k6 or similar
10. **Add Hadolint for Dockerfile linting** (1-2 hours)

## Comparison to Gold Standards

| Dimension | rhai-org-pulse | odh-dashboard (Gold) | notebooks (Gold) | Gap |
|-----------|---------------|---------------------|------------------|-----|
| Unit Tests | Vitest, 222 files, 45% ratio | Jest, comprehensive, 80%+ | pytest, good | Coverage tracking |
| Integration/E2E | Playwright containers, matrix | Cypress + Playwright, multi-env | Python scripts | Multi-browser |
| Build Integration | Docker + smoke on PR | Konflux + multi-mode | Multi-arch + validation | Similar quality |
| Image Testing | UBI9, runtime smoke | Multi-stage, Testcontainers | 5-layer validation | Vuln scanning |
| Coverage Tracking | **None** | Codecov, 80% threshold | Coverage reports | **Major gap** |
| CI/CD Automation | Path filter, Socket, auto-deploy | Comprehensive CI/CD | Image matrix CI | Comparable |
| Security Scanning | Socket, npm audit | Trivy, CodeQL, Snyk | Trivy | SAST + container |
| Agent Rules | Excellent (9/10) | Strong (8/10) | Minimal | Leading |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` — PR validation pipeline
- `.github/workflows/build-images.yml` — Image build and deployment
- `.github/workflows/integration-tests.yml` — Module integration tests
- `.github/workflows/claude-review.yml` — AI code review
- `.github/workflows/claude-issues.yml` — AI issue assistant
- `.github/workflows/guard-ai-configs.yml` — AI config protection
- `.github/workflows/sync-preprod.yml` — Branch sync
- `.github/actions/test-org-pulse-module/action.yml` — Reusable test action
- `.github/dependabot.yml` — Dependency updates

### Testing
- `vitest.config.mjs` — Unit test configuration
- `playwright.config.js` — E2E test configuration
- `tests/smoke/app-loads.spec.js` — Smoke tests
- `tests/integration/*.spec.js` — Integration tests
- `*/__tests__/**/*.test.js` — Unit tests (222 files)

### Code Quality
- `eslint.config.mjs` — ESLint flat config with custom rules
- `eslint-rules/no-cross-module-imports.js` — Module isolation rule
- `eslint-rules/no-module-process-env.js` — Secrets enforcement rule
- `.husky/pre-commit` — Lint-staged hook
- `scripts/validate-modules.js` — Module manifest validation
- `scripts/validate-openapi.js` — OpenAPI annotation validation

### Container Images
- `deploy/backend.Dockerfile` — Backend container (UBI9 Node.js 20)
- `deploy/frontend.Dockerfile` — Frontend container (UBI9 nginx 124)
- `.dockerignore` — Build context exclusions
- `deploy/nginx.conf` — Nginx configuration
- `deploy/nginx-entrypoint.sh` — Container entrypoint

### Agent Rules
- `AGENTS.md` — Vendor-neutral conventions (8 hard constraints)
- `.claude/CLAUDE.md` — Claude Code reference (architecture, APIs, deployment)
- `.claude/commands/pr-review.md` — PR review slash command
- `.claude/commands/create-module.md` — Module scaffolding command
- `.github/instructions/review.instructions.md` — Shared review checklist
- `.cursor/rules/upstream-pulse-module.mdc` — Cursor IDE rules

### Deployment
- `deploy/openshift/base/` — Base Kubernetes manifests
- `deploy/openshift/overlays/{dev,preprod,prod,local}/` — Environment overlays
- `Makefile` — Build and test commands
