---
repository: "red-hat-data-services/eval-hub-sobha"
overall_score: 7.2
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test-to-code ratio (1.16x), 37 unit test files covering handlers, storage, runtime, server, config, and auth"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Comprehensive BDD/Gherkin FVT suite with godog, 1883 lines across 5 feature files covering full API lifecycle"
  - dimension: "Build Integration"
    score: 5.0
    status: "Tekton/Konflux PR pipeline exists but no PR-time Docker build validation in GitHub Actions; Konflux is comment/label-triggered only"
  - dimension: "Image Testing"
    score: 6.0
    status: "Multi-arch container build with dry-run validation on push; no PR-time image build, no Trivy/vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 7.5
    status: "Codecov integration with unit + FVT coverage, server-side coverage collection via GOCOVERDIR; thresholds set at 50-75%"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Well-organized CI with quality-checks, security-scan, docker-build, commit lint, and Python publishing workflows"
  - dimension: "Agent Rules"
    score: 5.0
    status: "CLAUDE.md exists with comprehensive build/test/arch docs but no .claude/rules/ directory or test-type-specific guidance"
critical_gaps:
  - title: "No container vulnerability scanning (Trivy/Snyk)"
    impact: "CVEs in base images or dependencies not detected until Konflux or production"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time Docker image build validation"
    impact: "Containerfile/Dockerfile.konflux breakages discovered only post-merge"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Gosec runs in no-fail mode"
    impact: "Security findings are uploaded as SARIF but never block a PR merge"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "Coverage thresholds are low (50-75%)"
    impact: "Coverage can regress significantly without failing CI"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add Trivy container scanning to CI workflow"
    effort: "2-3 hours"
    impact: "Detect CVEs in base images and Go dependencies before merge"
  - title: "Enable gosec to fail CI on HIGH severity findings"
    effort: "1 hour"
    impact: "Enforce security standards rather than just reporting"
  - title: "Add PR-time Docker build step (build-only, no push)"
    effort: "3-4 hours"
    impact: "Catch Containerfile and build-arg issues before merge"
  - title: "Create .claude/rules/ for test automation guidance"
    effort: "2-3 hours"
    impact: "Improve AI-generated test quality and consistency with existing patterns"
recommendations:
  priority_0:
    - "Add container vulnerability scanning (Trivy) to PR workflow"
    - "Make gosec fail CI on HIGH/CRITICAL severity findings"
    - "Add PR-time Docker image build validation (build-only step)"
  priority_1:
    - "Raise coverage thresholds to 70-80% range in codecov.yml"
    - "Create .claude/rules/ directory with unit-test and fvt-test rules"
    - "Add golangci-lint with comprehensive linter set (current lint is just go vet)"
  priority_2:
    - "Add SBOM generation to container build workflow"
    - "Add API contract testing against OpenAPI spec in CI"
    - "Add load/performance testing for evaluation endpoints"
    - "Add image signing/attestation (cosign)"
---

# Quality Analysis: eval-hub-sobha

## Executive Summary
- **Overall Score: 7.2/10**
- **Repository**: `red-hat-data-services/eval-hub-sobha` (fork of `opendatahub-io/eval-hub`)
- **Type**: Go REST API service (Evaluation Hub) with Python server wrapper
- **Language**: Go 1.25 (primary), Python 3.11+ (server wrapper)
- **Framework**: Standard library `net/http` + godog BDD + Kubernetes operator patterns
- **Key Strengths**: Excellent test coverage with both unit tests (37 files, 14.6K lines) and BDD functional verification tests (1883 lines of Gherkin), Codecov integration, security scanning with gosec, comprehensive CLAUDE.md
- **Critical Gaps**: No container vulnerability scanning, no PR-time image build validation, gosec runs in no-fail mode, no dedicated linter configuration (golangci-lint)
- **Agent Rules Status**: Partial - CLAUDE.md present with build/test/architecture docs, but no `.claude/rules/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent test-to-code ratio (1.16x), 37 test files covering all major packages |
| Integration/E2E | 8.0/10 | Comprehensive BDD/Gherkin FVT suite with godog, 5 feature files, 1883 lines |
| **Build Integration** | **5.0/10** | **Tekton/Konflux PR pipeline exists but comment/label-triggered; no PR-time Docker build in GHA** |
| Image Testing | 6.0/10 | Multi-arch build with dry-run on push; no PR-time build, no vulnerability scanning |
| Coverage Tracking | 7.5/10 | Codecov with unit + FVT coverage; server-side coverage via GOCOVERDIR; thresholds at 50-75% |
| CI/CD Automation | 8.0/10 | Well-organized workflows with quality-checks, security-scan, docker-build-push, commit lint |
| Agent Rules | 5.0/10 | CLAUDE.md with comprehensive guidance, but no .claude/rules/ or test-type-specific rules |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: CVEs in UBI9 base images or Go/Python dependencies are not detected until Konflux build or production deployment
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Neither the CI workflow nor the Tekton pipeline runs Trivy, Snyk, or any vulnerability scanner against the built images. The `Containerfile` uses `registry.access.redhat.com/ubi9/go-toolset:1.25` (builder) and `ubi9/ubi-minimal:latest` (runtime), which should be scanned for known CVEs

### 2. No PR-Time Docker Image Build Validation
- **Impact**: Breaking changes to `Containerfile` or `Dockerfile.konflux` are only caught after merge (push trigger) or when Konflux pipeline runs (comment/label-triggered)
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The `docker-build-push` job only runs on `push` events (`if: github.event_name == 'push'`). PRs get quality checks but never validate that the container image actually builds. The Tekton pipeline (`.tekton/odh-eval-hub-pull-request.yaml`) exists but is triggered by comment (`/build-konflux`) or label (`kfbuild-all`, `kfbuild-eval-hub`), not automatically on every PR

### 3. Gosec Runs in No-Fail Mode
- **Impact**: Security vulnerabilities are reported as SARIF and uploaded to GitHub Security tab, but they never block a PR from merging
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: The gosec command uses `-no-fail` flag: `args: '-no-fail -fmt sarif -out gosec-results.sarif ./...'`. This means even CRITICAL security findings are informational-only

### 4. Low Coverage Thresholds
- **Impact**: Test coverage can regress from 75% to 50% without failing CI
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: `codecov.yml` sets `range: 50..75` which is relatively permissive. The green threshold starts at 75%, but there's no enforcement that prevents significant regression

## Quick Wins

### 1. Add Trivy Container Scanning (2-3 hours)
Add a Trivy scan step to the CI workflow:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

### 2. Enable Gosec Enforcement (1 hour)
Change gosec args to fail on HIGH/CRITICAL:
```yaml
args: '-severity high -fmt sarif -out gosec-results.sarif ./...'
```

### 3. Add PR-Time Docker Build (3-4 hours)
Add a build-only step to the `quality-checks` or a new job triggered on PR:
```yaml
docker-build-check:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    - uses: docker/setup-buildx-action@v3
    - name: Build (no push)
      uses: docker/build-push-action@v6
      with:
        context: .
        file: Containerfile
        push: false
```

### 4. Create Agent Rules for Test Automation (2-3 hours)
Create `.claude/rules/` directory with test-type-specific rules following existing patterns. Use `/test-rules-generator` to bootstrap.

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push (main, develop), PR (main, develop) | Quality checks, security scan, Docker build+push |
| `commitlint.yml` | PR (main) | Conventional commit enforcement via commitizen |
| `publish-python-server.yml` | push (main), tags, workflow_dispatch | Multi-platform binary build + Python wheel publishing |
| `sync-branch-stable.yaml` | push (incubation) | Auto-sync incubation to stable branch |
| `sync-branch-incubation.yaml` | push (main) | Auto-sync main to incubation branch |

**Strengths:**
- CI runs lint, vet, format check, all tests (unit + FVT), and coverage in a single job
- Codecov upload with `fail_ci_if_error: true` (skipped for Dependabot PRs)
- API documentation generation verified in CI
- Commit message enforcement with commitizen
- Security scanning with gosec + SARIF upload to GitHub Security tab
- Multi-architecture Docker builds (amd64 + arm64)
- Image dry-run validation: `docker run --rm "${IMAGE_REF}" /app/eval-hub --local --help`
- Python wheel publishing with TestPyPI for dev builds and PyPI for releases
- CodeRabbit configured for AI-assisted code reviews

**Weaknesses:**
- No concurrency control on workflows (duplicate runs possible)
- No build caching for Go modules in CI (relies on setup-go default caching)
- Docker build/push only on push events, not on PRs
- No parallel test execution
- Gosec in no-fail mode

### Test Coverage

**Unit Tests (37 files, ~14,639 lines):**
- **Test-to-code ratio**: 1.16x (14,639 test lines / 12,611 source lines) - excellent
- **Framework**: Standard Go `testing` package
- **Coverage areas**:
  - `auth/` - Authorization rules testing
  - `internal/eval_hub/handlers/` - All HTTP handlers (evaluations, collections, providers, health, openapi, benchmarks)
  - `internal/eval_hub/config/` - Configuration loading and parsing
  - `internal/eval_hub/runtimes/k8s/` - Kubernetes runtime (job builders, config, helpers)
  - `internal/eval_hub/runtimes/local/` - Local runtime
  - `internal/eval_hub/server/` - Server, middleware, CORS, execution context
  - `internal/eval_hub/storage/sql/` - SQL storage (evaluations, collections, providers, export)
  - `internal/eval_hub/validation/` - Input validation
  - `internal/eval_hub/serviceerrors/` - Error handling
  - `internal/eval_runtime_sidecar/` - Sidecar config, handlers, proxy (auth, HTTP client, OCI auth), termination watcher
  - `pkg/api/` - API types
- **Python tests**: 1 test file (`python-server/tests/test_main.py`) with 3 unit tests covering the setuptools entrypoint

**FVT/Integration Tests (5+2 feature files, ~1,883+ lines):**
- **Framework**: godog (Cucumber/Gherkin for Go)
- **Feature files**:
  - `evaluations.feature` (904 lines) - Full evaluation job lifecycle (create, read, update, delete, error cases, pagination, filtering)
  - `providers.feature` (534 lines) - Provider CRUD operations, system vs tenant scope
  - `collections.feature` (405 lines) - Collection management
  - `health.feature` (21 lines) - Health check endpoint
  - `metrics.feature` (19 lines) - Prometheus metrics endpoint
  - `kubernetes/features/kubernetes_resources.feature` - Kubernetes resource testing
  - `mlflow/features/experiments.feature` - MLflow integration testing
- **Quality**: Scenarios include proper setup/teardown, JSON schema validation, JSONPath assertions, variable substitution, asset cleanup
- **Coverage collection**: FVT tests collect server-side binary coverage via `-cover -covermode=atomic` build + `GOCOVERDIR`

**Coverage Tracking:**
- Codecov integration with `fail_ci_if_error: true`
- Three coverage profiles uploaded: `coverage.out`, `coverage-fvt.out`, `coverage-init.out`
- Coverage range: 50-75% (yellow to green thresholds)
- HTML coverage reports generated locally

### Code Quality

**Linting:**
- `go vet` used as the primary linter (via `make lint` and `make vet`)
- No `golangci-lint` configuration (`.golangci.yaml`) found
- This is a significant gap - `go vet` catches a limited subset of issues compared to a full golangci-lint setup

**Pre-commit Hooks:**
- `.pre-commit-config.yaml` with comprehensive hooks:
  - Ruff (Python linting and formatting)
  - Standard hooks (trailing whitespace, end-of-file, YAML/JSON/TOML check, merge conflict detection, large file check)
  - Commitizen for commit message format
  - MyPy type checking for Python code
  - Pytest for Python unit tests
  - Go unit and integration tests on commit
- No-commit-to-branch protection for `main` (on pre-push stage)

**Static Analysis:**
- Gosec security scanner with SARIF output + GitHub Security integration
- No CodeQL configuration (dedicated workflow)
- No dependency scanning (Dependabot or Renovate for Go)
- Renovate configured (`.github/renovate.json`) for dependency updates

**API Documentation:**
- OpenAPI 3.1.0 specification maintained in `docs/src/openapi.yaml`
- Redocly CLI for bundling, linting, and HTML generation
- CI validates documentation is up-to-date (drift detection via `git diff --exit-code`)

### Container Images

**Build Process:**
- **Containerfile** (development): Multi-stage build from UBI9 Go toolset, builds 3 binaries (eval-hub, eval-runtime-sidecar, eval-runtime-init), multi-arch support (`$BUILDPLATFORM`/`$TARGETARCH`), non-root user (UID 1000)
- **Dockerfile.konflux** (production/Konflux): Pinned base image SHA digests, FIPS-compliant build (`GOEXPERIMENT=strictfipsruntime`), `CGO_ENABLED=1`, Red Hat component labels
- **Lighteval container**: Python-based Dockerfile for KFP pipeline component

**Runtime Validation:**
- Dry-run validation on push: `docker run --rm "${IMAGE_REF}" /app/eval-hub --local --help`
- No PR-time image build validation

**Security:**
- Non-root user in container (UID 1000 in Containerfile, named user in Konflux)
- Pinned SHA digests in Dockerfile.konflux (good supply chain practice)
- No Trivy/Snyk/Grype scanning
- No SBOM generation
- No image signing/attestation

### Security Practices

| Practice | Status | Details |
|----------|--------|---------|
| SAST (Gosec) | Partial | Runs but in no-fail mode |
| CodeQL | Missing | No CodeQL workflow |
| Dependency scanning | Partial | Renovate configured for updates |
| Container scanning | Missing | No Trivy/Snyk |
| Secret detection | Missing | No Gitleaks/TruffleHog |
| Image signing | Missing | No cosign/sigstore |
| SBOM generation | Missing | No SBOM tool configured |
| FIPS compliance | Present | Dockerfile.konflux uses `GOEXPERIMENT=strictfipsruntime` |

### Agent Rules (Agentic Flow Quality)

- **Status**: Partial
- **CLAUDE.md**: Present and comprehensive (210 lines) - covers build commands, testing strategy, architecture overview, configuration patterns, key design patterns (ExecutionContext, routing, metrics), important implementation notes
- **`.claude/` directory**: Not present
- **`.claude/rules/`**: Not present
- **AGENTS.md**: Not present

**Quality Assessment of CLAUDE.md:**
- Excellent build/development command reference
- Good architecture overview with code examples
- Documents testing strategy (unit tests vs FVT)
- Explains key patterns (ExecutionContext, Two-Tier Configuration, Structured Logging)
- Missing: Test-type-specific rules for AI-assisted test generation

**Gaps:**
- No `.claude/rules/unit-tests.md` - No guidance on Go unit test patterns, table-driven tests, mocking strategies
- No `.claude/rules/fvt-tests.md` - No guidance on Gherkin scenario writing, step definition patterns
- No `.claude/rules/integration-tests.md` - No guidance on testing with actual database or Kubernetes
- No quality gates or checklists for AI-generated tests

**Recommendation:** Generate missing rules with `/test-rules-generator` to provide AI agents with test-type-specific patterns matching this repository's conventions

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning to PR workflow**
   - Add Trivy or Grype scanning against the Go module dependencies and Dockerfiles
   - Block PRs with CRITICAL or HIGH severity CVEs
   - Effort: 2-4 hours

2. **Make gosec enforce security standards**
   - Remove `-no-fail` flag or set severity threshold
   - Configure to fail on HIGH/CRITICAL findings
   - Effort: 1 hour

3. **Add PR-time Docker image build validation**
   - Add a `docker build` (no push) step for PRs to catch Containerfile breakages early
   - Consider building both `Containerfile` and `Dockerfile.konflux`
   - Effort: 4-6 hours

### Priority 1 (High Value)

4. **Add golangci-lint with comprehensive configuration**
   - Replace bare `go vet` with golangci-lint including linters like errcheck, gosimple, staticcheck, unused, ineffassign, gocritic
   - Effort: 3-4 hours

5. **Raise Codecov thresholds**
   - Update `codecov.yml` range from `50..75` to at least `65..80`
   - Add patch coverage enforcement (prevent coverage regression on new code)
   - Effort: 1-2 hours

6. **Create `.claude/rules/` for test automation guidance**
   - Add rules for unit tests (Go table-driven patterns, handler testing with mock storage/runtime)
   - Add rules for FVT tests (Gherkin scenario patterns, step definition conventions)
   - Add rules for Kubernetes runtime testing
   - Effort: 2-3 hours

7. **Add CI workflow concurrency control**
   - Prevent duplicate workflow runs for the same PR
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
     cancel-in-progress: true
   ```
   - Effort: 30 minutes

### Priority 2 (Nice-to-Have)

8. **Add SBOM generation to container build**
   - Use Syft or Trivy to generate SBOM alongside the built image
   - Effort: 2-3 hours

9. **Add API contract testing in CI**
   - Validate API responses against the OpenAPI spec in FVT tests
   - The infrastructure for this partially exists (JSON schema validation in step definitions)
   - Effort: 4-6 hours

10. **Add secret detection**
    - Configure Gitleaks or TruffleHog as a pre-commit hook or CI step
    - Effort: 1-2 hours

11. **Add image signing with cosign**
    - Sign built images for supply chain security
    - Effort: 4-6 hours

12. **Add load/performance testing for evaluation endpoints**
    - Benchmark key API endpoints under load
    - Effort: 8-12 hours

## Comparison to Gold Standards

| Dimension | eval-hub-sobha | odh-dashboard | notebooks | kserve |
|-----------|---------------|---------------|-----------|--------|
| Unit Test Coverage | Strong (1.16x ratio) | Strong | Moderate | Strong |
| Integration/E2E | Comprehensive BDD/FVT | Multi-layer | Image-focused | Multi-version |
| Coverage Enforcement | Codecov (50-75%) | Codecov + thresholds | Minimal | Strict enforcement |
| Container Scanning | Missing | Trivy | Multi-layer validation | Trivy |
| Security Scanning | Gosec (no-fail) | CodeQL + gosec | Minimal | CodeQL + gosec |
| Pre-commit Hooks | Comprehensive | Comprehensive | Basic | Moderate |
| Agent Rules | CLAUDE.md only | Full .claude/rules/ | Minimal | Moderate |
| API Doc Validation | Automated (Redocly) | Automated | N/A | Automated |
| Multi-arch Builds | Yes (amd64 + arm64) | Limited | Yes (5 archs) | Yes |
| FIPS Compliance | Dockerfile.konflux | No | No | No |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/commitlint.yml` - Commit message linting
- `.github/workflows/publish-python-server.yml` - Python wheel publishing
- `.github/workflows/sync-branch-stable.yaml` - Branch sync
- `.tekton/odh-eval-hub-pull-request.yaml` - Konflux/Tekton PR pipeline
- `Makefile` - Build, test, and development targets

### Testing
- `tests/features/*.feature` - BDD/Gherkin test scenarios
- `tests/features/suite_test.go` - FVT test suite setup
- `tests/features/step_definitions_test.go` - FVT step implementations
- `tests/kubernetes/` - Kubernetes-specific FVT tests
- `tests/mlflow/` - MLflow integration FVT tests
- `auth/rules_test.go` - Authorization rules unit tests
- `internal/eval_hub/handlers/*_test.go` - Handler unit tests
- `internal/eval_hub/storage/sql/*_test.go` - Storage unit tests
- `internal/eval_hub/runtimes/k8s/*_test.go` - K8s runtime unit tests
- `python-server/tests/test_main.py` - Python entrypoint tests

### Code Quality
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `.cz.toml` - Commitizen configuration
- `.coderabbit.yaml` - CodeRabbit AI review configuration
- `redocly.yaml` - API documentation linting

### Container Images
- `Containerfile` - Development/standard container build
- `Dockerfile.konflux` - Konflux/production container build (FIPS-compliant)
- `containers/lighteval/Dockerfile` - Lighteval KFP component container

### Coverage
- `codecov.yml` - Codecov configuration

### Agent Rules
- `CLAUDE.md` - Claude Code guidance (build, test, architecture)
- No `.claude/` directory
- No `AGENTS.md`
