---
repository: "opendatahub-io/langfuse"
overall_score: 8.1
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "201 test files across web (Jest) and worker (Vitest) with strong domain coverage"
  - dimension: "Integration/E2E"
    score: 7.5
    status: "Server integration tests with real DB/ClickHouse, Playwright E2E on PR, but E2E coverage is thin (3 specs)"
  - dimension: "Build Integration"
    score: 8.0
    status: "PR-time Docker build with health checks, multi-deploy-mode matrix, but no Konflux simulation"
  - dimension: "Image Testing"
    score: 7.0
    status: "Docker compose build test with health checks on PR, Snyk scanning post-merge only"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "No codecov/coveralls integration, no coverage thresholds, no PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "Excellent pipeline with concurrency control, caching, matrix testing, Slack alerts, merge-group support"
  - dimension: "Agent Rules"
    score: 8.0
    status: "Comprehensive CLAUDE.md, AGENTS.md, .claude/ with hooks/skills/agents, plus .cursor/rules/"
critical_gaps:
  - title: "No coverage tracking or enforcement"
    impact: "Cannot detect coverage regressions on PRs; no visibility into untested code paths"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Snyk container scanning runs post-merge only"
    impact: "Vulnerable images can be merged to main before detection"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Thin Playwright E2E test suite"
    impact: "Only 3 spec files (auth, create-project, API) covering a feature-rich application; UI regressions likely undetected"
    severity: "MEDIUM"
    effort: "20-40 hours"
  - title: "No Konflux/RHOAI build simulation on PR"
    impact: "Downstream Red Hat build issues discovered only post-merge"
    severity: "MEDIUM"
    effort: "8-12 hours"
quick_wins:
  - title: "Add codecov integration to CI pipeline"
    effort: "2-4 hours"
    impact: "Immediate visibility into test coverage and PR-level coverage diff reporting"
  - title: "Move Snyk scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catch container vulnerabilities before merge rather than after"
  - title: "Add coverage threshold enforcement"
    effort: "2-3 hours"
    impact: "Prevent coverage regressions by failing PRs that drop below a baseline"
  - title: "Add .claude/rules/ for test creation patterns"
    effort: "2-3 hours"
    impact: "Ensure AI-generated tests follow repo conventions (servertest vs clienttest vs unit test patterns)"
recommendations:
  priority_0:
    - "Implement codecov/coveralls integration with coverage thresholds and PR comments"
    - "Move Snyk container scanning to PR-triggered workflow to block vulnerable merges"
  priority_1:
    - "Expand Playwright E2E suite to cover core user journeys (tracing, evals, prompt management)"
    - "Add .claude/rules/ with test-type-specific guidance (servertest, clienttest, worker unit tests)"
    - "Add Konflux build simulation to PR workflow for Red Hat downstream validation"
  priority_2:
    - "Add performance/load testing for ingestion endpoints"
    - "Add accessibility testing for the web UI"
    - "Consider contract testing between web and worker via shared queue schemas"
---

# Quality Analysis: opendatahub-io/langfuse

## Executive Summary

- **Overall Score: 8.1/10**
- **Repository Type**: Full-stack web application (LLM observability platform)
- **Tech Stack**: Next.js 14 (Pages Router) + Express.js worker, pnpm + Turbo monorepo
- **Languages**: TypeScript throughout
- **Key Strengths**: Exceptionally well-organized CI/CD pipeline with matrix testing across PostgreSQL versions and deploy modes, strong unit/integration test culture with 201 test files, comprehensive agent rules (CLAUDE.md + AGENTS.md + hooks), PR-time Docker build validation with health checks
- **Critical Gaps**: No coverage tracking or enforcement, Snyk scanning only runs post-merge, thin Playwright E2E suite for a feature-rich application
- **Agent Rules Status**: Present and comprehensive

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | 201 test files across web (Jest) and worker (Vitest) |
| Integration/E2E | 7.5/10 | Server integration tests with real DBs, thin Playwright E2E (3 specs) |
| **Build Integration** | **8.0/10** | **PR-time Docker build + health checks, no Konflux simulation** |
| Image Testing | 7.0/10 | Docker compose build validation on PR, Snyk post-merge only |
| Coverage Tracking | 3.0/10 | No codecov, no thresholds, no PR reporting |
| CI/CD Automation | 9.0/10 | Excellent pipeline with concurrency, caching, matrix, Slack alerts |
| Agent Rules | 8.0/10 | CLAUDE.md + AGENTS.md + .claude/ directory with hooks, skills, agents |

## Critical Gaps

### 1. No Coverage Tracking or Enforcement
- **Impact**: Cannot detect coverage regressions on PRs; no visibility into which code paths are untested
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Neither `web` (Jest) nor `worker` (Vitest) has codecov/coveralls integration. The worker `package.json` has a `coverage` script (`vitest run --coverage`) but it's never invoked in CI. No `.codecov.yml` or `.coveragerc` exists. PRs can freely reduce test coverage without any signal.

### 2. Snyk Container Scanning Runs Post-Merge Only
- **Impact**: Vulnerable container images are merged to `main`/`production` before detection
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `snyk-web.yml` and `snyk-worker.yml` only trigger on `push` to `production` and `main`. They also use `continue-on-error: true`, meaning even when they run, vulnerabilities don't block the pipeline.

### 3. Thin Playwright E2E Test Suite
- **Impact**: Only 3 spec files (707 lines total) covering auth, project creation, and one API test for a feature-rich application with tracing, evaluations, prompt management, datasets, and more
- **Severity**: MEDIUM
- **Effort**: 20-40 hours
- **Details**: The E2E suite has `auth.spec.ts` (193 lines), `create-project.spec.ts` (199 lines), and `api.servertest.ts` (315 lines). Core user flows like trace exploration, evaluation configuration, prompt versioning, and dashboard analytics have no E2E coverage.

### 4. No Konflux/RHOAI Build Simulation
- **Impact**: Red Hat downstream build issues discovered only after merge
- **Severity**: MEDIUM
- **Effort**: 8-12 hours
- **Details**: This is the `opendatahub-io` fork, which will be consumed by Konflux/RHOAI builds. There is no PR-time simulation of Konflux build constraints.

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- Add `--coverage` flag to Jest and Vitest CI runs
- Add codecov upload action to `pipeline.yml`
- Create `.codecov.yml` with coverage targets

### 2. Move Snyk to PR Workflow (1-2 hours)
- Add `pull_request` trigger to `snyk-web.yml` and `snyk-worker.yml`
- Remove `continue-on-error: true` to make it a blocking check
- Or add Trivy scanning as a lighter-weight alternative on PRs

### 3. Add Coverage Threshold Enforcement (2-3 hours)
- Configure Jest `coverageThreshold` in `jest.config.mjs`
- Configure Vitest `coverage.thresholds` in worker config
- Start with current baseline and ratchet up over time

### 4. Add .claude/rules/ for Test Patterns (2-3 hours)
- Create rules for servertest, clienttest, and worker unit test conventions
- Document the Jest project selection (server vs client vs e2e-server)
- Reference existing `.cursor/rules/tests.mdc` patterns

## Detailed Findings

### CI/CD Pipeline

**Score: 9.0/10** - Excellent

The `pipeline.yml` is a best-in-class CI workflow:

- **Concurrency control**: `cancel-in-progress` on PRs prevents wasted resources
- **Duplicate skip**: Uses `fkirc/skip-duplicate-actions@v5` to avoid re-running unchanged code
- **Path filtering**: `dorny/paths-filter@v3` selectively triggers LLM connection tests only when relevant files change
- **Matrix testing**: Tests against PostgreSQL 12 and 15, three deploy modes (default, Azure, Redis cluster), and 3 shards for parallelization
- **Turbo cache**: Both Turbo remote cache and Next.js build cache are persisted across runs
- **Docker build validation**: Full compose build + health checks on every PR
- **Merge group support**: `merge_group` event enabled for merge queue compatibility
- **Gate job**: `all-ci-passed` aggregation job provides single status check for branch protection
- **Slack notifications**: Failure alerts on push to main/tags

**Workflows inventory (15 files)**:
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pipeline.yml` | PR, push, merge_group | Main CI (lint, test, build, e2e) |
| `codeql.yml` | PR, push, weekly | SAST analysis |
| `codespell.yml` | PR, push | Spelling checks |
| `validate-pr-title.yml` | PR | Conventional commits enforcement |
| `licencecheck.yml` | PR, push, merge_group | License compliance |
| `snyk-web.yml` | push (main, production) | Container vulnerability scan (web) |
| `snyk-worker.yml` | push (main, production) | Container vulnerability scan (worker) |
| `deploy.yml` | push (main, production) | ECS deployment |
| `release.yml` | tag push | Docker image publish |
| `promote-main-to-production.yml` | manual | Production promotion |
| `sdk-api-spec.yml` | push (main) | SDK/API spec generation |
| `stale_issues.yml` | cron (daily) | Stale issue management |
| `dependabot-rebase-stale.yml` | push (main) | Dependabot PR maintenance |

### Test Coverage

**Score: 8.5/10 (Unit) / 7.5/10 (Integration/E2E)**

**Test files breakdown**:
- `*.servertest.ts`: 90 files (server-side integration tests with real DB)
- `*.test.ts`: 75 files (unit tests across web and worker)
- `*.clienttest.ts`: 34 files (React component/client-side tests)
- `*.spec.ts`: 2 files (Playwright E2E)
- **Total**: 201 test files
- **Source files**: ~1,872 TS/TSX files (non-test, non-generated)
- **Test-to-code ratio**: ~10.7% (201/1872)

**Testing frameworks**:
- **Web**: Jest with separate project configs for `server`, `client`, and `e2e-server` test types
- **Worker**: Vitest with `--pool=forks --singleFork` for isolation
- **E2E**: Playwright for browser tests

**Test infrastructure quality**:
- Server tests run against real PostgreSQL + ClickHouse + Redis + MinIO (not mocked)
- Matrix testing across PostgreSQL 12 & 15
- Multi-deploy-mode testing (default, Azure, Redis cluster)
- Test sharding (3 shards) for parallelization
- LLM connection tests are conditionally triggered and use real API keys
- Worker has separate test commands for excluding/including LLM tests

**Weaknesses**:
- Only 2 Playwright spec files + 1 E2E server test
- No coverage reporting or tracking
- No coverage thresholds

### Code Quality

**Score: 8.0/10**

- **ESLint**: Configured per-package (`web/eslint.config.mjs`, `worker/eslint.config.mjs`, `packages/shared/eslint.config.mjs`, `ee/eslint.config.mjs`) with shared config package
- **Prettier**: `prettier.config.cjs` with format checking on changed files in CI
- **Husky pre-commit**: Runs `format:check` on every commit, with protection prompt for `main` branch
- **Husky pre-push**: Protection prompt for direct pushes to `main`
- **Codespell**: Spell checking in CI on PRs and pushes
- **PR title validation**: Conventional commits enforcement via `amannn/action-semantic-pull-request@v6`
- **License checking**: Automated license compliance verification
- **No pre-commit-config.yaml**: Uses Husky instead (adequate for this project type)

### Container Images

**Score: 7.0/10**

**Dockerfile quality (web)**:
- Multi-stage build (alpine base → pruner → builder → runner)
- `turbo prune --scope=web --docker` for minimal install footprint
- Non-root user (`nextjs:nodejs`)
- `dumb-init` for proper signal handling
- Platform-aware build (`TARGETPLATFORM`)
- Security: `apk upgrade --no-cache libcrypto3 libssl3` for CVE mitigation
- Standalone output tracing for minimal image size

**Build validation**:
- `test-docker-build` job in CI: builds both web and worker images, starts full compose stack, validates health endpoints
- Health check curls for both web (`/api/public/health`) and worker (`/api/health`)
- Failure diagnostics: captures container logs, compose state, docker events on failure

**Weaknesses**:
- Snyk scanning runs post-merge only, not on PRs
- No Trivy scanning
- No SBOM generation
- No image signing/attestation
- Multi-architecture builds (amd64 + arm64) only on tagged releases, not tested on PRs

### Security

**Score: 7.5/10**

- **CodeQL**: Enabled on PRs and pushes to main/production, with weekly scheduled scans
- **Snyk**: Container scanning for both web and worker images (but post-merge only)
- **License checking**: Automated compliance verification on PRs
- **Secrets handling**: `.env.*.example` files with proper gitignore, `SECURITY.md` for vulnerability reporting
- **No Gitleaks/TruffleHog**: No secret detection in CI
- **No dependency scanning**: No Dependabot security updates configured (only rebase automation)

### Agent Rules (Agentic Flow Quality)

**Score: 8.0/10**

**Status**: Present and comprehensive

**CLAUDE.md** (root):
- Comprehensive project overview, architecture, and repo structure
- Development commands with clear instructions
- Technology stack documentation
- Testing guidelines per package (Jest for web, Vitest for worker)
- Code conventions and TypeScript best practices
- Frontend tips (basePath handling)
- Linear MCP integration guidance

**AGENTS.md** (root):
- Monorepo-level architectural guidance
- Dependency direction rules (`web → shared, ee`; `worker → shared`)
- Minimum verification matrix by change scope
- Coding style and naming conventions
- Commit and PR guidelines (conventional commits)
- Release channel documentation
- Maintenance contract (update AGENTS.md when guidance changes)
- Cross-references to package-level AGENTS.md files

**.claude/ directory**:
- `agents/changelog-writer.md` - Specialized changelog generation agent
- `skills/` - 3 custom skills (add-model-price, backend-dev-guidelines, skill-developer) + skills rules
- `hooks/` - 3 hooks (error-handling-reminder, post-tool-use-tracker, skill-activation-prompt)
- `settings.json` - Permissions, MCP servers, hook configuration

**.cursor/rules/**:
- 8 rule files covering authorization/RBAC, entitlements, frontend features, public API, tests, global conventions, and banner positioning

**Gaps**:
- No `.claude/rules/` directory (test creation rules in `.cursor/rules/tests.mdc` instead)
- Cursor test rules are minimal (just 2 bullet points: test independence and no pruneDatabase)
- No framework-specific test creation rules (e.g., how to write servertests vs clienttests vs worker unit tests)
- No rule for Playwright E2E test patterns

## Recommendations

### Priority 0 (Critical)

1. **Implement coverage tracking with enforcement**
   - Add `--coverage` to Jest and Vitest CI runs
   - Integrate codecov with coverage upload
   - Set minimum coverage thresholds (start at current baseline)
   - Enable PR-level coverage diff comments

2. **Move Snyk container scanning to PR-triggered workflow**
   - Add `pull_request` trigger to both Snyk workflows
   - Remove `continue-on-error: true` to make failures blocking
   - Or add Trivy as a lightweight alternative for PR-time scanning

### Priority 1 (High Value)

3. **Expand Playwright E2E test suite**
   - Add specs for core user flows: trace exploration, evaluation setup, prompt management, dataset operations
   - Target 10-15 spec files covering the main feature areas
   - Consider visual regression testing with Playwright screenshots

4. **Add .claude/rules/ for test creation patterns**
   - Migrate and expand `.cursor/rules/tests.mdc` to `.claude/rules/`
   - Create separate rules for: servertest patterns, clienttest patterns, worker unit test patterns
   - Include test file naming conventions, project selection, and fixture patterns

5. **Add Konflux build simulation for downstream validation**
   - Create a PR workflow job that simulates Konflux build constraints
   - Validate that the Dockerfile builds under Red Hat base image restrictions

### Priority 2 (Nice-to-Have)

6. **Add performance testing for ingestion endpoints**
   - The worker handles high-volume trace ingestion; load testing would catch performance regressions
   
7. **Add secret detection to CI**
   - Integrate Gitleaks or TruffleHog to prevent credential leaks

8. **Add accessibility testing**
   - Integrate axe-core with Playwright for automated accessibility checks

9. **Consider contract testing for web-worker boundary**
   - Queue payload schemas in `packages/shared/src/server/queues.ts` could be validated with contract tests

## Comparison to Gold Standards

| Feature | langfuse | odh-dashboard | notebooks | kserve |
|---------|----------|---------------|-----------|--------|
| Unit Tests | 201 files (Jest+Vitest) | Extensive (Jest) | N/A | Extensive (Go) |
| Integration Tests | 90 server tests w/ real DB | Contract tests | N/A | envtest |
| E2E Tests | 3 Playwright specs | Cypress suite | N/A | Multi-version |
| Coverage Tracking | None | Codecov | N/A | Codecov + thresholds |
| CI Matrix | PG12/15 x 3 deploy modes x 3 shards | Multi-env | Multi-arch | Multi-version |
| Docker Build on PR | Yes + health checks | Yes | Yes (5-layer) | Yes |
| Security Scanning | CodeQL + Snyk (post-merge) | Trivy on PR | Trivy | Trivy + gosec |
| Agent Rules | CLAUDE.md + AGENTS.md + .claude/ | CLAUDE.md + rules | None | None |
| Pre-commit Hooks | Husky (format check) | Husky | Pre-commit | Pre-commit |
| License Check | Yes (CI) | No | No | No |

## File Paths Reference

### CI/CD
- `.github/workflows/pipeline.yml` - Main CI pipeline
- `.github/workflows/codeql.yml` - CodeQL SAST
- `.github/workflows/snyk-web.yml` / `snyk-worker.yml` - Container scanning
- `.github/workflows/deploy.yml` - ECS deployment
- `.github/workflows/release.yml` - Docker image publish
- `.github/workflows/validate-pr-title.yml` - Conventional commits

### Testing
- `web/jest.config.mjs` - Jest configuration (3 projects: server, client, e2e-server)
- `web/playwright.config.ts` - Playwright E2E configuration
- `web/src/__tests__/` - Web test files (servertests + clienttests)
- `web/src/__e2e__/` - Playwright E2E specs
- `worker/src/__tests__/` - Worker unit/integration tests

### Code Quality
- `web/eslint.config.mjs` - Web ESLint config
- `worker/eslint.config.mjs` - Worker ESLint config
- `prettier.config.cjs` - Prettier configuration
- `.husky/pre-commit` - Pre-commit hook (format check)
- `.codespellrc` - Spell check configuration

### Container Images
- `web/Dockerfile` - Web application Docker image
- `worker/Dockerfile` - Worker Docker image
- `docker-compose.build.yml` - Full stack build validation
- `.dockerignore` - Docker build exclusions

### Agent Rules
- `CLAUDE.md` - Root project guide for Claude Code
- `AGENTS.md` - Monorepo-level agent guidance
- `.claude/settings.json` - Claude Code settings
- `.claude/agents/changelog-writer.md` - Changelog agent
- `.claude/skills/` - Custom skills
- `.claude/hooks/` - Custom hooks
- `.cursor/rules/tests.mdc` - Test writing rules (Cursor)
