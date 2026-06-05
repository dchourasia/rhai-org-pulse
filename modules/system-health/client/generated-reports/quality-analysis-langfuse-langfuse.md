---
repository: "langfuse/langfuse"
overall_score: 8.4
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "325 test files across monorepo with Vitest, strong server/client/worker coverage"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Multi-matrix integration tests (Postgres 12/15, Azure/Redis-Cluster modes), Docker build health checks"
  - dimension: "Build Integration"
    score: 9.0
    status: "PR-time Docker build with health checks, multi-service compose validation, full-stack startup test"
  - dimension: "Image Testing"
    score: 8.0
    status: "Multi-arch (amd64/arm64) builds, multi-stage Dockerfiles, health check validation in CI"
  - dimension: "Coverage Tracking"
    score: 5.0
    status: "V8 coverage provider configured in Vitest but no codecov integration or PR reporting"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "19 workflows, smart skip-duplicate, concurrency control, Turbo/pnpm caching, Slack alerts"
  - dimension: "Agent Rules"
    score: 9.5
    status: "Best-in-class .agents/ setup with 15 skills, per-package AGENTS.md, verification matrix"
critical_gaps:
  - title: "No coverage tracking or enforcement"
    impact: "Coverage regressions go undetected; no visibility into test health over time"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No pre-commit secret detection"
    impact: "Secrets could be committed to repository before CI catches them"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Snyk container scanning is post-merge only"
    impact: "Vulnerable images can be merged to main before scanning detects issues"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Limited Playwright E2E coverage"
    impact: "Only 2 browser E2E specs; UI regressions may not be caught automatically"
    severity: "MEDIUM"
    effort: "16-24 hours"
quick_wins:
  - title: "Add Codecov integration to pipeline"
    effort: "2-4 hours"
    impact: "Immediate visibility into coverage trends and PR-level coverage diffs"
  - title: "Add Gitleaks secret detection to pre-commit and CI"
    effort: "1-2 hours"
    impact: "Prevent accidental secret commits before they reach the repository"
  - title: "Move Snyk container scanning to PR workflow"
    effort: "2-3 hours"
    impact: "Catch container vulnerabilities before merge instead of after"
  - title: "Add Dependabot or Renovate for dependency updates"
    effort: "1-2 hours"
    impact: "Automated security patches for npm dependencies"
recommendations:
  priority_0:
    - "Add Codecov or Coveralls integration with PR-level coverage reporting and minimum thresholds"
    - "Move Snyk container scanning to run on PRs (shift-left vulnerability detection)"
  priority_1:
    - "Expand Playwright E2E test suite to cover critical user flows (tracing, scoring, prompt management)"
    - "Add Gitleaks or TruffleHog for pre-commit secret detection"
    - "Add contract tests between web/worker/shared API boundaries"
  priority_2:
    - "Add performance regression testing for ingestion and query endpoints"
    - "Enable SBOM generation in Docker image builds"
    - "Add mutation testing (Stryker) for critical business logic"
---

# Quality Analysis: Langfuse

## Executive Summary

- **Overall Score: 8.4/10**
- **Repository Type**: TypeScript monorepo (Next.js web app + worker + shared packages)
- **Primary Language**: TypeScript (Node.js 24)
- **Framework**: Next.js, Vitest, Prisma, ClickHouse, Redis
- **Key Strengths**: Exceptional CI/CD automation with 19 workflows, best-in-class agent rules, strong multi-matrix testing across deployment modes and Postgres versions, PR-time Docker build validation with health checks
- **Critical Gaps**: No coverage tracking/enforcement, Snyk scanning only post-merge, limited browser E2E coverage
- **Agent Rules Status**: **Exemplary** - comprehensive `.agents/` directory with 15 skills, per-package AGENTS.md files, verification matrix, and maintenance contract

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | 325 test files across monorepo with Vitest, strong server/client/worker coverage |
| Integration/E2E | 8.0/10 | Multi-matrix integration tests (PG 12/15, Azure/Redis-Cluster), Docker build health checks |
| **Build Integration** | **9.0/10** | **PR-time Docker build with compose health checks, multi-service startup validation** |
| Image Testing | 8.0/10 | Multi-arch (amd64/arm64) builds, multi-stage Dockerfiles, health check validation |
| Coverage Tracking | 5.0/10 | V8 coverage provider configured but no codecov/coveralls integration or PR reporting |
| CI/CD Automation | 9.5/10 | 19 workflows, smart skip-duplicate, concurrency control, Turbo/pnpm caching |
| Agent Rules | 9.5/10 | Best-in-class .agents/ with 15 skills, per-package guides, verification matrix |

## Critical Gaps

### 1. No Coverage Tracking or Enforcement
- **Impact**: Coverage regressions go undetected; no visibility into test health over time
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Vitest is configured with `coverage.provider: "v8"` in `worker/vitest.config.ts`, but there is no Codecov/Coveralls integration, no coverage artifacts uploaded in CI, no minimum thresholds, and no PR-level coverage diff reporting.

### 2. Snyk Container Scanning is Post-Merge Only
- **Impact**: Vulnerable container images can be merged to main before scanning detects issues
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: `snyk-web.yml` and `snyk-worker.yml` only trigger on `push` to `production`/`main` branches. PRs are not scanned, meaning vulnerability detection is reactive rather than preventative.

### 3. No Pre-Commit Secret Detection
- **Impact**: Secrets could be committed to the repository before CI catches them
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No Gitleaks, TruffleHog, or similar secret detection tool is configured. Husky pre-commit hooks run `format:check` and `lint` only.

### 4. Limited Browser E2E Coverage
- **Impact**: Only 2 Playwright specs (`auth.spec.ts`, `create-project.spec.ts`); UI regressions may not be caught
- **Severity**: MEDIUM
- **Effort**: 16-24 hours
- **Details**: The web app has extensive server-side E2E tests (144 servertest files) but minimal browser-level E2E testing. The frontend-browser-review skill exists for agent-driven manual review but does not replace automated E2E suites.

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- **Impact**: Immediate visibility into coverage trends and PR-level diffs
- **Implementation**: Add `--coverage` flag to Vitest runs in CI, upload coverage artifacts, configure `.codecov.yml` with minimum thresholds
```yaml
# Add to tests-web and tests-worker jobs
- name: Upload coverage
  uses: codecov/codecov-action@v5
  with:
    files: coverage/coverage-final.json
    flags: web  # or worker
```

### 2. Add Gitleaks Secret Detection (1-2 hours)
- **Impact**: Prevent accidental secret commits
```yaml
# .github/workflows/gitleaks.yml
name: Gitleaks
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

### 3. Move Snyk to PR Workflow (2-3 hours)
- **Impact**: Shift-left vulnerability detection for container images
- **Implementation**: Add `pull_request` trigger to `snyk-web.yml` and `snyk-worker.yml`

### 4. Add Dependabot Configuration (1-2 hours)
- **Impact**: Automated security patches for npm dependencies
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Detailed Findings

### CI/CD Pipeline

**Score: 9.5/10** - Exceptional

Langfuse has one of the most well-engineered CI/CD pipelines analyzed:

**19 Workflows:**
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pipeline.yml` | PR, push, merge_group | Main CI - lint, typecheck, test, Docker build |
| `codeql.yml` | PR, push, schedule | SAST analysis for JavaScript/TypeScript |
| `semgrep.yml` | PR | Security scanning with baseline diff |
| `snyk-web.yml` | push (main/prod) | Container vulnerability scanning (web) |
| `snyk-worker.yml` | push (main/prod) | Container vulnerability scanning (worker) |
| `zizmor.yml` | PR, push, merge_group | GitHub Actions security audit |
| `claude-code-security-review.yml` | PR | AI-powered security review (Claude Opus) |
| `claude-review-maintainer-prs.yml` | PR | AI code review for maintainer PRs |
| `validate-pr-title.yml` | PR | Conventional Commits enforcement |
| `licencecheck.yml` | PR, push, merge_group | License compliance check |
| `codespell.yml` | PR, push | Spelling error detection |
| `sdk-api-spec.yml` | ? | SDK/API specification validation |
| `deploy.yml` | ? | Deployment workflow |
| `release.yml` | ? | Release automation |
| `promote-main-to-production.yml` | ? | Production promotion |
| `_deploy_ecs_service.yml` | reusable | ECS deployment helper |
| `stale_issues.yml` | schedule | Stale issue management |
| `dependabot-rebase-stale.yml` | ? | Dependabot PR management |
| `cla-assistant.yml` | ? | CLA management |

**Pipeline Architecture Highlights:**
- **Smart skip-duplicate**: Custom tree-SHA deduplication replaces `fkirc/skip-duplicate-actions` — skips runs when the exact git tree was already tested
- **Concurrency control**: `cancel-in-progress` for PRs, grouped by workflow + ref
- **Fork PR security**: Disables cache restores for fork PRs (`CI_CACHE_ALLOWED`)
- **Multi-layer caching**: pnpm cache, Turbo cache, Next.js build cache
- **All-CI-passed gate**: Branch protection via aggregate job that checks all required jobs
- **Slack failure notifications**: Alerts on main/tag CI failures
- **Blacksmith runners**: Custom high-performance runners (4 vCPU)

### Test Coverage

**Score: 8.5/10** - Strong

**Test Distribution:**
| Package | Test Files | Framework | Types |
|---------|-----------|-----------|-------|
| web | 211 | Vitest | 144 servertest, 67 clienttest, 2 E2E spec |
| worker | 107 | Vitest | 6 unit, 3 integration, 1 E2E, 97 general |
| shared | 7 | Vitest | Unit tests |
| eslint-plugin | ? | Vitest | Plugin rule tests |

**Test-to-Code Ratio**: 117 test files / 2028 source files = ~5.8% (reasonable for a web app with integration tests)

**Vitest Configuration:**
- **Web**: 5 test projects (in-source, client/jsdom, server, server-unit, e2e-server)
- **Worker**: V8 coverage provider configured, forks pool, CI retry (3 attempts)
- **Custom CI reporter**: `VitestCiReporter` for enhanced CI output

**Multi-Matrix Testing:**
- PostgreSQL versions: 12, 15
- Deploy modes: default, Azure, Redis-Cluster
- Node.js: v24
- Total matrix: 6 combinations for web, 6 for worker

**LLM Connection Testing:**
- Conditional job triggered only when LLM-related files change
- Uses real API secrets (cache-cold, secret-bearing job)
- Separate from main test matrix for cost efficiency

### Code Quality

**Score: 8.5/10** - Strong

**Linting:**
- ESLint configured per-package (`web/eslint.config.mjs`, `worker/eslint.config.mjs`, `ee/eslint.config.mjs`)
- Custom ESLint plugin (`packages/eslint-plugin`) with project-specific rules
- Prettier with `trailingComma: "all"` - checked on changed files only (incremental)
- Codespell for spelling error detection

**Pre-commit Hooks (Husky):**
- `pre-commit`: Runs `format:check` and `lint`, with main branch protection prompt
- `pre-push`: Main branch push protection prompt
- No secret detection in hooks

**Static Analysis:**
- CodeQL: Scheduled (weekly) + PR + push for JavaScript/TypeScript
- Semgrep: PR-only with baseline diff scanning (`p/default` rules)
- zizmor: GitHub Actions security auditing
- Claude Code: AI-powered security review on PRs (using Claude Opus)

**Type Safety:**
- TypeScript strict mode with dedicated `typecheck` CI job
- Separate from lint - runs as independent pipeline step
- Turbo task caching for incremental typechecking

**License Compliance:**
- `license-checker` with copyleft detection
- Blocks `WeakCopyleft`, `StrongCopyleft`, `NetworkCopyleft` licenses

### Container Images

**Score: 8.0/10** - Strong

**Dockerfile Quality (Web):**
- Multi-stage build (7 stages: alpine, build-base, runtime-base, migrate-builder, pruner, builder, runner)
- Turbo prune for minimal Docker context
- Non-root user (`nextjs:nodejs`, UID/GID 1001)
- `dumb-init` for proper signal handling
- Alpine-based with explicit security updates (`apk upgrade --no-cache libcrypto3 libssl3`)
- Cross-compilation for golang-migrate (built from source to avoid CVEs from pre-built binaries)
- Package manager removal in runtime stage (npm, corepack, yarn removed)

**Dockerfile Quality (Worker):**
- Similar multi-stage pattern optimized for worker
- `pnpm deploy --legacy --prod` for minimal production dependencies
- All build tools stripped from runtime image

**Multi-Architecture:**
- amd64 + arm64 builds
- Separate platform-specific builds then multi-platform manifest creation
- Dual registry publishing (GHCR + Docker Hub)

**CI Docker Validation:**
- `test-docker-build` job builds and starts full compose stack on every PR
- Health checks for web (`:3000/api/public/health`) and worker (`:3030/api/health`)
- 180-second startup timeout with retry
- Docker diagnostics captured on failure (logs, inspect, events)

**Missing:**
- No Trivy/Grype scanning in CI (only Snyk post-merge)
- No SBOM generation
- No image signing/attestation

### Security

**Score: 8.0/10** - Strong

**Security Tooling:**
| Tool | Scope | Trigger | Integration |
|------|-------|---------|-------------|
| CodeQL | SAST | PR, push, weekly schedule | GitHub Security tab |
| Semgrep | SAST | PR (diff-based) | CI blocking |
| Snyk (Web) | Container | push (main/prod) | SARIF → GitHub Security |
| Snyk (Worker) | Container | push (main/prod) | SARIF → GitHub Security |
| zizmor | GitHub Actions | PR, push, merge_group | SARIF → GitHub Security |
| Claude Code | AI Security Review | PR | PR comments |
| License Check | License compliance | PR, push, merge_group | CI blocking |

**Strengths:**
- Multiple overlapping SAST tools (CodeQL + Semgrep)
- AI-powered security review using Claude Opus on every PR
- GitHub Actions security auditing (zizmor) — uncommon and valuable
- Pinned action SHAs throughout all workflows (supply chain security)
- Fork PR cache poisoning protection

**Gaps:**
- No pre-commit secret detection (Gitleaks/TruffleHog)
- Snyk container scanning is post-merge only
- No dependency scanning (Dependabot/Renovate not configured)

### Agent Rules (Agentic Flow Quality)

**Score: 9.5/10** - Exemplary (Best-in-class)

**Status**: Present and comprehensive — one of the most mature agent setups analyzed

**Infrastructure:**
- `.agents/AGENTS.md` - Canonical root guide (10KB+)
- `CLAUDE.md` → `AGENTS.md` → `.agents/AGENTS.md` (symlink chain for tool compatibility)
- `.agents/config.json` - Shared agent/tool configuration
- `.agents/ARCHITECTURE_PRINCIPLES.md` - Architecture handbook
- `.agents/README.md` - Agent setup documentation
- `agents:sync` / `agents:check` scripts for configuration validation

**15 Custom Skills:**
| Skill | Purpose |
|-------|---------|
| `add-model-price` | Model pricing constant management |
| `agent-setup-maintenance` | Agent configuration sync/check |
| `analyze-cloud-costs` | Cloud cost analysis (AWS/ClickHouse/Metabase) |
| `backend-dev-guidelines` | Backend development standards |
| `changelog-writing` | Changelog drafting |
| `clickhouse-best-practices` | ClickHouse schema/query review |
| `code-review` | Code review guidelines |
| `datadog-query-recipes` | Production telemetry research |
| `debug-issue-with-datadog` | Issue debugging with Datadog APM |
| `frontend-browser-review` | Playwright browser review loop |
| `linear-bug-triage` | Bug triage and dedup with Linear |
| `pnpm-upgrade-package` | Dependency upgrade workflow |
| `skill-creator` | Skill creation guidelines |
| `turborepo` | Monorepo/Turbo task graph changes |
| `weekly-production-review` | Production review workflow |

**Per-Package AGENTS.md:**
- `web/AGENTS.md` - Frontend-specific guidance
- `worker/AGENTS.md` - Worker queue guidance
- `packages/shared/AGENTS.md` - Shared contracts
- `ee/AGENTS.md` - Enterprise features

**Verification Matrix:**
- Documented minimum verification per change scope (web-only, worker-only, shared, cross-package)
- Bug fixes require failing test first
- Frontend changes require browser review loop

**Maintenance Contract:**
- Living document with update requirements
- Changes to agent setup require `agents:sync` + `agents:check`
- Durable guidance in AGENTS.md, not tool-specific config

**Only Gap:** No explicit test-type-specific rules (e.g., "how to write unit tests for ClickHouse queries" or "integration test patterns for queue processors")

## Recommendations

### Priority 0 (Critical)

1. **Add Codecov/Coveralls integration with PR-level reporting**
   - Configure coverage thresholds (suggest 70% minimum)
   - Add coverage diff reporting on PRs
   - Upload coverage from both web and worker test jobs
   - Effort: 4-6 hours

2. **Shift Snyk container scanning left to PRs**
   - Add `pull_request` trigger to `snyk-web.yml` and `snyk-worker.yml`
   - Consider adding Trivy as a complementary scanner (faster, runs locally)
   - Effort: 4-6 hours

### Priority 1 (High Value)

3. **Add secret detection to CI and pre-commit**
   - Gitleaks in CI workflow + pre-commit hook
   - Effort: 2-3 hours

4. **Expand Playwright E2E test suite**
   - Cover critical user flows: tracing view, prompt management, scoring, evaluations
   - The `frontend-browser-review` skill provides manual review but doesn't replace automated suites
   - Effort: 16-24 hours

5. **Add contract tests for internal API boundaries**
   - web ↔ shared, worker ↔ shared, web ↔ worker (via Redis queues)
   - Queue payload schemas in `packages/shared/src/server/queues.ts` are a natural contract boundary
   - Effort: 8-12 hours

### Priority 2 (Nice-to-Have)

6. **Add SBOM generation to Docker image builds**
   - Currently `sbom: false` in release build — enable for supply chain transparency
   - Effort: 1-2 hours

7. **Enable image signing/attestation**
   - Use Sigstore/cosign for release image provenance
   - Effort: 4-6 hours

8. **Add performance regression testing**
   - Benchmark ingestion endpoint throughput, ClickHouse query latency
   - Effort: 8-16 hours

9. **Add test-type-specific agent rules**
   - Create `.agents/skills/` entries for unit test patterns, integration test patterns, ClickHouse test patterns
   - Use `/test-rules-generator` to bootstrap
   - Effort: 4-6 hours

## Comparison to Gold Standards

| Dimension | Langfuse | odh-dashboard | notebooks | kserve |
|-----------|---------|---------------|-----------|--------|
| Unit Tests | 8.5 | 8.0 | 6.0 | 9.0 |
| Integration/E2E | 8.0 | 9.0 | 7.0 | 9.0 |
| Build Integration | 9.0 | 8.0 | 7.0 | 7.0 |
| Image Testing | 8.0 | 7.0 | 9.0 | 7.0 |
| Coverage Tracking | 5.0 | 8.0 | 5.0 | 9.0 |
| CI/CD Automation | 9.5 | 8.0 | 7.0 | 8.0 |
| Agent Rules | 9.5 | 7.0 | 3.0 | 2.0 |
| **Overall** | **8.4** | **7.9** | **6.3** | **7.6** |

**Notable Observations:**
- Langfuse's CI/CD and Agent Rules are the strongest analyzed — sets a new benchmark
- Coverage tracking is the weakest dimension; the infrastructure exists (V8 provider) but isn't wired to reporting
- Docker build validation in CI (PR-time health checks) is exemplary — ahead of most projects analyzed
- AI-powered security review (Claude Opus on every PR) is innovative and rare

## File Paths Reference

### CI/CD Workflows
- `.github/workflows/pipeline.yml` - Main CI pipeline (lint, test, Docker build)
- `.github/workflows/codeql.yml` - CodeQL SAST
- `.github/workflows/semgrep.yml` - Semgrep security scanning
- `.github/workflows/snyk-web.yml` - Snyk container scanning (web)
- `.github/workflows/snyk-worker.yml` - Snyk container scanning (worker)
- `.github/workflows/zizmor.yml` - GitHub Actions security
- `.github/workflows/claude-code-security-review.yml` - AI security review
- `.github/workflows/validate-pr-title.yml` - PR title validation
- `.github/workflows/licencecheck.yml` - License compliance
- `.github/workflows/codespell.yml` - Spell checking

### Test Configuration
- `vitest.workspace.ts` - Vitest workspace (web, worker)
- `web/vitest.config.mts` - Web test config (5 projects)
- `worker/vitest.config.ts` - Worker test config (V8 coverage)
- `packages/shared/vitest.config.ts` - Shared package tests
- `packages/eslint-plugin/vitest.config.ts` - ESLint plugin tests

### Container Images
- `web/Dockerfile` - Web image (7-stage multi-stage)
- `worker/Dockerfile` - Worker image (multi-stage)
- `docker-compose.build.yml` - Build validation compose
- `docker-compose.dev.yml` - Development compose
- `docker-compose.dev-azure.yml` - Azure mode compose
- `docker-compose.dev-redis-cluster.yml` - Redis cluster mode compose

### Code Quality
- `prettier.config.cjs` - Prettier configuration
- `web/eslint.config.mjs` - Web ESLint config
- `worker/eslint.config.mjs` - Worker ESLint config
- `ee/eslint.config.mjs` - EE ESLint config
- `packages/eslint-plugin/` - Custom ESLint plugin
- `.husky/pre-commit` - Pre-commit hook (format + lint)
- `.husky/pre-push` - Pre-push hook (main branch protection)

### Agent Rules
- `.agents/AGENTS.md` - Root agent guide
- `.agents/ARCHITECTURE_PRINCIPLES.md` - Architecture handbook
- `.agents/config.json` - Agent configuration
- `.agents/skills/` - 15 custom skills
- `web/AGENTS.md` - Frontend agent guide
- `worker/AGENTS.md` - Worker agent guide
- `packages/shared/AGENTS.md` - Shared package guide
- `ee/AGENTS.md` - Enterprise agent guide
