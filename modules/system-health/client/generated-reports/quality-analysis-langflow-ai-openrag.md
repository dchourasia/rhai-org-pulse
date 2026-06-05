---
repository: "langflow-ai/openrag"
overall_score: 7.2
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "90 unit test files covering backend with pytest; good coverage of services, utils, and APIs but no coverage enforcement"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Strong multi-layer integration tests (core, SDK-Python, SDK-TypeScript) plus Playwright E2E; all automated in CI on PRs"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR-triggered Docker builds in integration tests; operator CI validates manifests and Docker build; no Konflux simulation"
  - dimension: "Image Testing"
    score: 6.5
    status: "Multi-stage Dockerfiles with non-root users; multi-arch (amd64/arm64) release builds; no container scanning in CI"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "pytest-cov in dev dependencies but no codecov integration, no coverage thresholds, no PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "27 well-organized workflows with concurrency control, caching, path-filtered triggers, autofix, and nightly builds"
  - dimension: "Agent Rules"
    score: 5.0
    status: "CLAUDE.md and AGENTS.md present with skill references (install, SDK); no test-specific agent rules or .claude/rules/"
critical_gaps:
  - title: "No coverage tracking or enforcement"
    impact: "Test coverage can silently regress; no visibility into which code paths are untested"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container vulnerability scanning in CI"
    impact: "CVEs in container images go undetected until production; only periodic dependency audits exist"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Frontend has only 2 E2E specs for 254 source files"
    impact: "Frontend regressions caught only through manual testing or downstream E2E failures"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "No test-specific agent rules"
    impact: "AI-generated tests lack consistency; no guardrails for test patterns, mocking strategies, or fixtures"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Codecov integration with PR reporting"
    effort: "2-4 hours"
    impact: "Immediate visibility into coverage trends; enable coverage regression detection on every PR"
  - title: "Add Trivy container scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in container images before merge; complement existing dependency audit"
  - title: "Add coverage threshold to pytest configuration"
    effort: "1-2 hours"
    impact: "Prevent coverage regressions by failing CI when coverage drops below baseline"
  - title: "Create .claude/rules/ with test automation guidance"
    effort: "3-4 hours"
    impact: "Standardize AI-generated test patterns across unit, integration, and E2E layers"
recommendations:
  priority_0:
    - "Integrate Codecov or Coveralls with coverage thresholds and PR annotations"
    - "Add Trivy or Snyk container scanning to Docker build workflows"
    - "Expand frontend E2E test coverage from 2 specs to cover critical user flows"
  priority_1:
    - "Create comprehensive .claude/rules/ with test creation guidelines per test type"
    - "Add contract tests for backend API boundaries (OpenSearch, Langflow, SDKs)"
    - "Add operator envtest integration tests beyond the existing 3 controller tests"
  priority_2:
    - "Add performance regression testing for search and ingest endpoints"
    - "Add SBOM generation to release builds"
    - "Add Gitleaks scanning to PR workflow (complement existing detect-secrets pre-commit hook)"
---

# Quality Analysis: OpenRAG (langflow-ai/openrag)

## Executive Summary

- **Overall Score: 7.2/10**
- **Repository Type**: Full-stack RAG platform (Python FastAPI backend, Next.js frontend, Kubernetes operator, SDKs)
- **Primary Languages**: Python (backend), TypeScript (frontend), Go (operator)
- **Key Strengths**: Comprehensive CI/CD with 27 workflows, strong integration testing with multi-suite strategy, multi-arch Docker builds, automated code formatting
- **Critical Gaps**: No coverage tracking/enforcement, no container vulnerability scanning, extremely thin frontend test coverage
- **Agent Rules Status**: Present (CLAUDE.md + AGENTS.md) but focused on installation/SDK skills, not test automation

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | 90 test files, pytest + pytest-asyncio, good service/util coverage |
| Integration/E2E | 8.0/10 | Multi-suite CI (core, SDK-Python, SDK-TypeScript, Playwright E2E) |
| Build Integration | 7.0/10 | PR-time Docker builds for integration tests; operator CI validates manifests |
| Image Testing | 6.5/10 | Multi-stage Dockerfiles, multi-arch; no vulnerability scanning |
| Coverage Tracking | 3.0/10 | pytest-cov available but unused in CI; no codecov/thresholds |
| CI/CD Automation | 8.5/10 | 27 workflows, concurrency control, caching, autofix, nightly builds |
| Agent Rules | 5.0/10 | CLAUDE.md + AGENTS.md with install/SDK skills; no test rules |

## Critical Gaps

### 1. No Coverage Tracking or Enforcement
- **Impact**: Test coverage can silently regress with no visibility into untested code paths
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: `pytest-cov` is listed in dev dependencies but no CI workflow generates coverage reports. No `.codecov.yml`, no coverage thresholds, no PR annotations. The operator CI does generate `cover.out` via `go test -coverprofile` but doesn't upload or enforce it.
- **Fix**: Add `--cov=src --cov-report=xml` to pytest invocations in CI, integrate Codecov/Coveralls, set a baseline threshold (e.g., 50%)

### 2. No Container Vulnerability Scanning
- **Impact**: CVEs in base images and dependencies go undetected; only periodic `pip-audit` and `npm audit` exist
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The project has 5 Dockerfiles (opensearch, backend, frontend, langflow, operator) with no Trivy, Snyk, or Grype scanning in any CI workflow. The `dependency-audit.yml` runs npm/pip audit on a schedule but doesn't scan built container images.
- **Fix**: Add Trivy scan step after Docker build in `test-integration.yml` and `operator-ci.yml`

### 3. Frontend Test Coverage is Negligible
- **Impact**: 254 frontend TypeScript source files with only 2 Playwright E2E specs; regressions caught only through manual testing
- **Severity**: HIGH
- **Effort**: 20-40 hours
- **Details**: The frontend has zero unit tests (no Jest/Vitest) and only 2 Playwright specs (`onboarding.spec.ts`, `tasks-unified-panel.spec.ts`). No component testing, no accessibility testing.
- **Fix**: Add Vitest for component unit tests, expand Playwright specs to cover critical flows (document management, search, settings, chat)

### 4. No Test-Specific Agent Rules
- **Impact**: AI-generated tests lack consistency and may not follow project patterns
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: AGENTS.md focuses on install/SDK skills. No `.claude/rules/` directory with test creation guidance. AI agents won't know about pytest-asyncio patterns, fixture conventions, or integration test infrastructure requirements.

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- Add `--cov=src --cov-report=xml` to `test-unit` and `test-integration` pytest runs
- Add Codecov upload step to CI workflows
- Create `.codecov.yml` with baseline thresholds
```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: 50%
    patch:
      default:
        target: 80%
```

### 2. Add Trivy Container Scanning (1-2 hours)
```yaml
- name: Scan backend image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'langflowai/openrag-backend:${{ env.CI_IMAGE_TAG }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 3. Coverage Threshold in pytest (1-2 hours)
```toml
# pyproject.toml addition
[tool.pytest.ini_options]
addopts = "--cov=src --cov-fail-under=50"
```

### 4. Create Agent Test Rules (3-4 hours)
- Create `.claude/rules/unit-tests.md` with pytest patterns, fixture usage, async test conventions
- Create `.claude/rules/integration-tests.md` with infrastructure requirements, conftest patterns
- Create `.claude/rules/e2e-tests.md` with Playwright patterns and page object model

## Detailed Findings

### CI/CD Pipeline (Score: 8.5/10)

**Strengths:**
- 27 well-organized GitHub Actions workflows covering linting, testing, building, releasing
- Smart path-filtering on all workflows (e.g., `lint-backend.yml` only triggers on `src/**/*.py` changes)
- Concurrency control with `cancel-in-progress: true` on lint and autofix workflows
- Automated code formatting via `autofix.ci` (Ruff safe fixes + format) and `biome-autofix.yml` (frontend)
- Nightly builds with multi-arch Docker images and PyPI publishing
- Self-hosted ARM64 runners for integration and E2E tests
- PR title validation with conventional commits (`semantic-pull-request`)
- Operator CI with manifest generation verification, Helm lint, and Docker build check

**Workflow Inventory:**
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pr-checks.yml` | PR | Conventional commit title validation |
| `lint-backend.yml` | PR (Python) | Ruff lint + mypy on changed files |
| `lint-frontend.yml` | PR (frontend) | Biome lint + TypeScript type check |
| `autofix.ci.yml` | PR (Python) | Auto-apply Ruff fixes |
| `biome-autofix.yml` | Push (frontend) | Auto-apply Biome fixes |
| `test-integration.yml` | PR | Build images, run core + SDK integration tests |
| `test-e2e.yml` | PR | Full-stack Playwright E2E tests |
| `codeql.yml` | PR + Schedule | CodeQL SAST for Python and JavaScript |
| `operator-ci.yml` | PR (operator) | Go fmt/vet/lint, manifest check, test, Helm lint, Docker build |
| `dependency-audit.yml` | Schedule | npm audit + pip-audit across all packages |
| `build-multiarch.yml` | Manual | Multi-arch release builds + PyPI publish |
| `nightly-build.yml` | Schedule | Nightly multi-arch Docker + PyPI |
| `add-labels.yml` | PR | Auto-labeling by file paths |
| `community-label.yml` | PR | Community contributor labeling |
| `conventional-labels.yml` | PR | Labels from conventional commit types |
| `auto-delete-branch.yml` | PR merge | Clean up merged branches |
| `deploy-docs-draft.yml` | PR | Draft docs deployment |
| `deploy-gh-pages.yml` | Push (main) | Deploy docs to GitHub Pages |

**Minor Gaps:**
- No workflow-level dependency caching for Python (uv has built-in caching but explicit cache key would be more reliable)
- Integration test workflow could benefit from test result upload (JUnit XML)

### Test Coverage (Score: 7.5/10 Unit, 8.0/10 Integration/E2E)

**Backend Unit Tests (90 files, ~16K lines):**
- Framework: pytest + pytest-asyncio + pytest-mock
- Test-to-code ratio: 0.30 (16,357 test lines / 54,893 source lines) — adequate
- Well-organized in `tests/unit/` with subdirectories: `api/`, `config/`, `connectors/`, `db/migrations/`, `dependencies/`, `services/`, `utils/`
- Shared `conftest.py` with test fixtures
- Good coverage areas: encryption, ACL, JWT, OpenSearch security, document processing, task service, settings, connectors

**Backend Integration Tests (19 files):**
- Core integration suite (7 tests): API endpoints, startup ingest, group ACL/DLS, MCP URL ingest, onboarding, runtime migration
- SDK integration suite (9 tests): auth, chat, documents, e2e, errors, filters, models, search, settings
- Infrastructure: Full Docker Compose stack (OpenSearch, Langflow, backend, frontend, docling)
- CI matrix strategy: `core`, `sdk-python`, `sdk-typescript` suites run in parallel

**E2E Tests:**
- Playwright-based with 2 specs (onboarding, tasks-unified-panel)
- Runs against full Docker Compose stack
- CI retries (2x), artifact upload for reports
- Good failure diagnostics: service log collection on failure

**Operator Tests (3 files):**
- Go test with race detection and coverage profile
- Controller test, env tests, env example tests
- Uses envtest (controller-runtime test framework)

**SDK Tests:**
- Python SDK: integrated via pytest in `tests/integration/sdk/`
- TypeScript SDK: npm test with separate integration test file

### Code Quality (Score: 8.0/10)

**Backend (Python):**
- **Ruff**: Configured with `E`, `F`, `I`, `B`, `UP` rule sets; line-length 100; Python 3.13 target
- **mypy**: Configured with `ignore_missing_imports`, `warn_unused_ignores`; per-module overrides for FastAPI return types
- **autofix.ci**: Auto-applies safe Ruff fixes (excluding F401) and formatting on PRs
- **Isort**: Custom section ordering to keep bootstrap import first

**Frontend (TypeScript):**
- **Biome**: Lint and format checking on PRs
- **TypeScript**: Strict type checking via `tsc --noEmit`
- **Biome autofix**: Auto-applies formatting on push to non-main branches
- **Knip**: Dead code detection configured

**Operator (Go):**
- **golangci-lint**: v2.11.4 with golangci-lint-action
- **gofmt**: Enforced in CI
- **go vet**: Standard Go static analysis

**Pre-commit:**
- `detect-secrets` hook for secret detection (Yelp/detect-secrets v1.5.0)
- `.secrets.baseline` with comprehensive plugin list (AWS, Azure, GitHub, GitLab, etc.)

### Build Integration (Score: 7.0/10)

**Strengths:**
- Integration test workflow builds all 4 Docker images (`ci-build-images`) on PR
- Operator CI does a Docker build check (no push) on PR
- Operator CI validates generated manifests (CRD, RBAC, deepcopy, typed client) are up-to-date
- Helm chart lint and template validation
- CRD symlink verification

**Gaps:**
- No Konflux simulation or production build pipeline testing on PR
- No image startup validation (container health check testing)
- No multi-arch build testing on PR (only release workflow builds multi-arch)

### Container Images (Score: 6.5/10)

**Strengths:**
- Multi-stage Dockerfiles for backend (3 stages: base → builder → runtime)
- Non-root user in all images (opensearch user, appuser, node user)
- Multi-arch support (amd64 + arm64) in release and nightly builds
- Efficient layer caching with BuildKit cache mounts (`--mount=type=cache`)
- UBI9 base image for OpenSearch (OpenShift compatible)
- Graceful shutdown handling (entrypoint wrapper)
- gosu for privilege dropping in backend

**Gaps:**
- No Trivy/Snyk/Grype scanning in any CI workflow
- No SBOM generation
- No image signing or attestation
- No `.trivyignore` configuration
- CVE patching is manual (e.g., `patch-netty.sh` for Netty CVE-2025-58056)

### Security (Score: 7.0/10)

**Strengths:**
- CodeQL SAST scanning for Python and JavaScript (PR + weekly schedule)
- `detect-secrets` pre-commit hook with comprehensive baseline
- Dependency audit workflow (npm audit + pip-audit) on Mon/Thu schedule
- SECURITY.md with responsible disclosure policy
- JWT-based authentication with RSA key management
- RBAC system (opt-in) with permission caching
- OAuth/OIDC integration with OpenSearch

**Gaps:**
- No container image scanning
- No Gitleaks in CI (only detect-secrets in pre-commit)
- Dependency audit runs only on schedule, not on PRs
- No DAST or runtime security testing
- No secret rotation testing

### Agent Rules (Score: 5.0/10)

**Strengths:**
- `CLAUDE.md` present (points to AGENTS.md)
- `AGENTS.md` with comprehensive operational constraints documentation
- Two agent skills: `openrag_install` (installation) and `openrag_sdk` (SDK integration)
- Skills properly symlinked from `.claude/skills/` to `plugins/openrag/skills/`
- Plugin architecture supports Claude Code, Claude Agent SDK, and generic agents

**Gaps:**
- No `.claude/rules/` directory
- No test creation rules for any test type (unit, integration, E2E)
- No testing standards documentation for AI agents
- Skills focus on installation/SDK, not quality or testing
- No guidance on mocking strategies, fixture patterns, or async test conventions
- `AGENTS.md` operational constraints are helpful but don't address test automation

## Recommendations

### Priority 0 (Critical)

1. **Integrate coverage tracking with enforcement**
   - Add `pytest-cov` to CI pytest invocations with XML report output
   - Set up Codecov/Coveralls with PR annotations and coverage thresholds
   - Start with 50% project target, 80% patch target
   - Estimated effort: 4-6 hours

2. **Add container vulnerability scanning**
   - Add Trivy scanning step after Docker image builds in integration test and operator CI
   - Upload SARIF results to GitHub Security tab
   - Set severity threshold: fail on CRITICAL/HIGH
   - Estimated effort: 2-4 hours

3. **Expand frontend test coverage**
   - Add Vitest for component unit testing (hooks, contexts, lib utilities)
   - Expand Playwright E2E specs for critical user flows: document upload, search, chat, settings
   - Target: at least 10-15 E2E specs covering golden paths
   - Estimated effort: 20-40 hours

### Priority 1 (High Value)

4. **Create comprehensive agent test rules**
   - Create `.claude/rules/unit-tests.md` with pytest/pytest-asyncio patterns
   - Create `.claude/rules/integration-tests.md` with Docker infrastructure and conftest patterns
   - Create `.claude/rules/e2e-tests.md` with Playwright best practices
   - Use `/test-rules-generator` skill to bootstrap
   - Estimated effort: 4-6 hours

5. **Add contract tests for API boundaries**
   - Backend ↔ OpenSearch query/response contracts
   - Backend ↔ Langflow API contracts
   - SDK ↔ Backend API contracts (beyond current integration tests)
   - Estimated effort: 12-16 hours

6. **Expand operator test coverage**
   - Only 3 Go test files; add tests for reconciliation logic, status updates, error handling
   - Add envtest integration tests for CRD validation and webhook testing
   - Estimated effort: 8-12 hours

### Priority 2 (Nice-to-Have)

7. **Add SBOM generation to release builds**
   - Use Syft or `docker buildx build --sbom` in release workflow
   - Attach SBOMs to GitHub releases
   - Estimated effort: 2-3 hours

8. **Add performance regression testing**
   - Benchmark search latency and ingest throughput
   - Compare against baseline in CI
   - Estimated effort: 8-12 hours

9. **Move dependency audit to PR trigger**
   - Add `pip-audit` and `npm audit` to PR workflows (in addition to schedule)
   - Fail on HIGH/CRITICAL vulnerabilities
   - Estimated effort: 2-3 hours

10. **Add Gitleaks to CI**
    - Complement pre-commit detect-secrets with CI-level Gitleaks scanning
    - Catch secrets that bypass pre-commit hooks
    - Estimated effort: 1-2 hours

## Comparison to Gold Standards

| Practice | OpenRAG | odh-dashboard | notebooks | kserve |
|----------|---------|---------------|-----------|--------|
| Unit Test Coverage | 90 files, no threshold | Extensive + enforced | N/A | Enforced (80%+) |
| Integration Tests | Multi-suite in CI | Contract + integration | Image validation | Multi-version |
| E2E Tests | 2 Playwright specs | Comprehensive Cypress | N/A | E2E suite |
| Coverage Enforcement | None | Codecov + thresholds | N/A | Codecov enforced |
| Container Scanning | None | Trivy | Trivy + SBOM | Trivy |
| Multi-arch | amd64 + arm64 | Single arch | Multi-arch | Multi-arch |
| Code Quality | Ruff + mypy + Biome | ESLint + TS strict | Linters | golangci-lint |
| SAST | CodeQL | CodeQL | N/A | gosec |
| Agent Rules | Skills only | Full rules + skills | N/A | N/A |
| Pre-commit | detect-secrets | Multiple hooks | N/A | Multiple hooks |
| CI Organization | 27 workflows, path-filtered | Well-organized | Comprehensive | Well-organized |

## File Paths Reference

### CI/CD Configuration
- `.github/workflows/lint-backend.yml` - Backend linting (Ruff + mypy)
- `.github/workflows/lint-frontend.yml` - Frontend linting (Biome + TypeScript)
- `.github/workflows/test-integration.yml` - Integration test suite
- `.github/workflows/test-e2e.yml` - Playwright E2E tests
- `.github/workflows/codeql.yml` - CodeQL SAST scanning
- `.github/workflows/operator-ci.yml` - Operator CI (Go lint/test/manifest validation)
- `.github/workflows/dependency-audit.yml` - Periodic dependency audit
- `.github/workflows/build-multiarch.yml` - Multi-arch release builds
- `.github/workflows/nightly-build.yml` - Nightly Docker + PyPI builds
- `.github/workflows/autofix.ci.yml` - Ruff autofix
- `.github/workflows/biome-autofix.yml` - Biome autofix

### Testing
- `tests/unit/` - 90 backend unit test files (pytest)
- `tests/integration/core/` - 7 core integration test files
- `tests/integration/sdk/` - 9 SDK integration test files
- `frontend/tests/` - 2 Playwright E2E specs
- `kubernetes/operator/internal/controller/*_test.go` - 3 operator tests

### Code Quality
- `pyproject.toml` - Ruff, mypy, pytest configuration
- `.pre-commit-config.yaml` - detect-secrets hook
- `.secrets.baseline` - Secret detection baseline

### Container Images
- `Dockerfile` - OpenSearch (multi-stage, UBI9)
- `Dockerfile.backend` - Backend (3-stage, Python 3.13-slim)
- `Dockerfile.frontend` - Frontend (Node 25.9-slim)
- `Dockerfile.langflow` - Langflow
- `kubernetes/operator/Dockerfile` - Operator

### Agent Rules
- `CLAUDE.md` - Points to AGENTS.md
- `AGENTS.md` - Agent instructions with operational constraints
- `.claude/skills/` - Symlinks to install and SDK skills
- `plugins/openrag/skills/install/SKILL.md` - Installation skill
- `plugins/openrag/skills/sdk/SKILL.md` - SDK integration skill
