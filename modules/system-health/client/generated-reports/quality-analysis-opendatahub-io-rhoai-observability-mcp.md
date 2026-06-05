---
repository: "opendatahub-io/rhoai-observability-mcp"
overall_score: 6.9
scorecard:
  - dimension: "Unit Tests"
    score: 8.0
    status: "112 tests across 19 files, near 1:1 test-to-code ratio, multi-Python matrix (3.11-3.13)"
  - dimension: "Integration/E2E"
    score: 7.0
    status: "Kind-based E2E validates deployment and Prometheus scraping; smoke tests require manual cluster access"
  - dimension: "Build Integration"
    score: 6.0
    status: "PR-time Docker build and Kustomize validation; no Konflux simulation"
  - dimension: "Image Testing"
    score: 5.0
    status: "Multi-stage UBI9 build with attestation but no vulnerability scanning, SBOM, or multi-arch"
  - dimension: "Coverage Tracking"
    score: 6.0
    status: "Codecov integration present but fail_ci_if_error is false and no threshold enforcement"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "3 well-organized workflows with concurrency control, path filters, and matrix testing"
  - dimension: "Agent Rules"
    score: 1.0
    status: "No CLAUDE.md, .claude/ directory, or AI agent test guidance; only human-oriented TESTING.md"
critical_gaps:
  - title: "No container vulnerability scanning"
    impact: "CVEs in base image or dependencies go undetected until deployment"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "No coverage threshold enforcement"
    impact: "Coverage can regress silently; Codecov errors are ignored"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No SAST or dependency scanning"
    impact: "Security vulnerabilities in code and dependencies not detected pre-merge"
    severity: "HIGH"
    effort: "3-4 hours"
  - title: "E2E tests don't validate MCP tool functionality"
    impact: "Deployment works but individual tools could be broken without detection"
    severity: "MEDIUM"
    effort: "8-12 hours"
quick_wins:
  - title: "Add Trivy scanning to container-build workflow"
    effort: "1-2 hours"
    impact: "Catches CVEs in base images and Python dependencies before merge"
  - title: "Enforce coverage threshold via pytest --cov-fail-under=80"
    effort: "30 minutes"
    impact: "Prevents coverage regression; matches TESTING.md recommendation"
  - title: "Add pre-commit hooks for ruff and mypy"
    effort: "1-2 hours"
    impact: "Catches linting/type issues before push, faster feedback loop"
  - title: "Create basic CLAUDE.md with test patterns"
    effort: "2-3 hours"
    impact: "AI agents generate consistent, high-quality tests matching project conventions"
recommendations:
  priority_0:
    - "Add Trivy or Snyk container scanning to the container-build workflow"
    - "Enforce coverage thresholds in CI (--cov-fail-under=80) and set fail_ci_if_error: true in Codecov"
    - "Add CodeQL or Semgrep SAST scanning workflow"
  priority_1:
    - "Add functional E2E tests that exercise MCP tools against mock backends in Kind"
    - "Create .claude/rules/ with unit and E2E test patterns for AI agent consistency"
    - "Add multi-architecture builds (amd64 + arm64)"
    - "Add dependency scanning (Dependabot or Renovate) for Python packages"
  priority_2:
    - "Add SBOM generation to container builds"
    - "Add pre-commit hooks configuration"
    - "Add integration tests for backend error handling with realistic scenarios"
    - "Add health check endpoint (HTTP GET) instead of TCP socket probes"
---

# Quality Analysis: rhoai-observability-mcp

## Executive Summary

- **Overall Score: 6.9/10**
- **Repository Type**: Python MCP (Model Context Protocol) server for RHOAI observability
- **Primary Language**: Python 3.11+ (1,762 lines of source, 1,712 lines of test code)
- **Framework**: FastMCP with async httpx backends, pydantic-settings configuration

**Key Strengths:**
- Near 1:1 test-to-code ratio with 112 well-structured unit tests
- Clean CI/CD pipeline with lint, typecheck, and multi-version test matrix
- Kind-based E2E testing validates real deployment with mock observability backends
- Build provenance attestation for container images
- Excellent developer documentation (TESTING.md, CONTRIBUTING.md)

**Critical Gaps:**
- No container vulnerability scanning (Trivy, Snyk, or equivalent)
- No SAST or dependency scanning in CI
- Coverage threshold not enforced (Codecov errors silently ignored)
- No AI agent rules (.claude/, CLAUDE.md) for test automation guidance

**Agent Rules Status**: Missing - no CLAUDE.md or .claude/ directory exists

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8/10 | 112 tests, near 1:1 ratio, multi-Python matrix (3.11-3.13) |
| Integration/E2E | 7/10 | Kind E2E validates deployment + scraping; smoke tests manual |
| **Build Integration** | **6/10** | **PR Docker build + Kustomize validation; no Konflux sim** |
| Image Testing | 5/10 | Multi-stage UBI9 + attestation; no scanning, SBOM, or multi-arch |
| Coverage Tracking | 6/10 | Codecov present but fail_ci_if_error=false, no threshold |
| CI/CD Automation | 8/10 | 3 workflows, concurrency control, path filters, matrix |
| Agent Rules | 1/10 | No CLAUDE.md, .claude/, or agent-specific test guidance |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: CVEs in the UBI9 base image or Python dependencies (httpx, kubernetes, pydantic) go undetected until production deployment
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: The `container-build.yml` workflow builds and pushes images but never scans them. The project uses `registry.access.redhat.com/ubi9/python-312` which is generally well-maintained, but transitive Python dependencies could introduce vulnerabilities.

### 2. No Coverage Threshold Enforcement
- **Impact**: Code coverage can silently regress; new PRs can merge with decreased coverage
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Details**: The CI workflow generates coverage reports and uploads to Codecov with `fail_ci_if_error: false`. The `TESTING.md` documents `--cov-fail-under=80` but this flag is NOT used in the CI workflow. The actual CI command is:
  ```yaml
  uv run pytest tests/unit -v --tb=short --cov=src/rhoai_obs_mcp --cov-report=xml --cov-report=term
  ```
  Missing: `--cov-fail-under=80`

### 3. No SAST or Dependency Scanning
- **Impact**: Code-level security issues (injection, insecure deserialization) and known-vulnerable dependencies not caught before merge
- **Severity**: HIGH
- **Effort**: 3-4 hours
- **Details**: No CodeQL, Semgrep, Bandit, or safety workflows. No Dependabot or Renovate configuration for automated dependency updates.

### 4. E2E Tests Don't Validate MCP Tool Functionality
- **Impact**: The Kind E2E test (`kind-e2e.yml`) validates deployment, pod readiness, and Prometheus scraping, but never actually invokes any of the 21 MCP tools. A broken tool registration or query formatting issue would not be caught.
- **Severity**: MEDIUM
- **Effort**: 8-12 hours

## Quick Wins

### 1. Add Trivy Scanning to Container Build (1-2 hours)
```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

### 2. Enforce Coverage Threshold (30 minutes)
Change the CI test step from:
```yaml
uv run pytest tests/unit -v --tb=short --cov=src/rhoai_obs_mcp --cov-report=xml --cov-report=term
```
To:
```yaml
uv run pytest tests/unit -v --tb=short --cov=src/rhoai_obs_mcp --cov-report=xml --cov-report=term --cov-fail-under=80
```
And set `fail_ci_if_error: true` in the Codecov upload step.

### 3. Add Pre-commit Hooks (1-2 hours)
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, pydantic-settings]
```

### 4. Create Basic CLAUDE.md (2-3 hours)
Add agent rules for unit test patterns (respx mocking, AsyncMock, tool registration testing).

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- **3 well-defined workflows** with clear separation of concerns:
  - `ci.yml`: Lint (ruff check + format) + Typecheck (mypy) + Test (pytest with multi-Python matrix)
  - `container-build.yml`: Docker build with Buildx, GHA caching, metadata, and attestation
  - `kind-e2e.yml`: Full Kubernetes deployment test with mock backends
- **Concurrency control** on all workflows (`cancel-in-progress: true`)
- **Path-based triggering** on E2E workflow (only runs when deploy/, hack/, Makefile, or Containerfile change)
- **Matrix testing** across Python 3.11, 3.12, 3.13
- **CI gate job** (`ci-status`) aggregates all job results for a single required status check
- **Build provenance attestation** via `actions/attest-build-provenance@v2`

**Weaknesses:**
- No Python dependency caching in CI (relies on uv's speed but still downloads packages each run)
- No artifact upload for test results or coverage on failure
- Container build workflow runs on PRs but only builds (doesn't push) - good practice, but no post-build validation (scanning, smoke test)
- No scheduled/periodic workflows for dependency freshness or long-running tests

### Test Coverage

**Strengths:**
- **112 test functions** across 19 test files
- **Near 1:1 test-to-code ratio** (1,712 test lines vs 1,762 source lines)
- **Every source module has a corresponding test file** (test_auth, test_config, test_server, test_backends_*, test_tools_*)
- **Well-structured test classes** organized by functionality (e.g., `TestTempoBackendGetTrace`, `TestTempoBackendSearch`, `TestRelativeToEpoch`)
- **Good edge case coverage**: unavailable backends, connection errors, invalid input, non-dict responses
- **respx** for HTTP mocking (type-safe, async-native)
- **AsyncMock** patterns for tool testing (no real HTTP in unit tests)
- **Shared fixtures** in conftest.py (settings, auth)
- **Security test**: validates trace ID to prevent path traversal (`../../../etc/passwd` test case)

**Weaknesses:**
- Coverage threshold documented in TESTING.md but not enforced in CI
- No integration tests that test backend+tool together with real HTTP (respx sits between)
- Smoke test (`tests/smoke_test.py`) requires a live cluster - not automatable without infrastructure

**Test Distribution:**
| Module | Tests | Lines |
|--------|-------|-------|
| test_tools_metrics | 15 | 174 |
| test_config | 12 | 91 |
| test_backends_tempo | 12 | 210 |
| test_tools_traces | 9 | 127 |
| test_tempo_unavailable | 8 | 72 |
| test_tools_investigate | 7 | 169 |
| test_loki_unavailable | 6 | 61 |
| test_backends_prometheus | 5 | 103 |
| test_backends_loki | 5 | 98 |
| test_auth | 5 | 45 |
| test_tools_cluster | 4 | 73 |
| test_backends_grafana | 4 | 77 |
| test_backends_alertmanager | 4 | 73 |
| test_tools_logs | 3 | 52 |
| test_tools_alerts | 3 | 45 |
| test_main | 3 | 29 |
| test_backends_openshift | 3 | 93 |
| test_tools_dashboards | 2 | 49 |
| test_server | 2 | 50 |

### Code Quality

**Strengths:**
- **Ruff** for both linting and formatting (fast, comprehensive, replaces flake8 + black + isort)
- **Mypy** for static type checking (run as separate CI job)
- **Modern Python conventions**: `str | None` instead of `Optional[str]`, type hints on public functions
- **Clean code structure**: separation of backends, tools, config, and auth
- **pydantic-settings** for configuration with environment variable support and validation

**Weaknesses:**
- No pre-commit hooks (`.pre-commit-config.yaml` absent)
- Ruff configuration is minimal in pyproject.toml (no explicit rule sets enabled/disabled)
- Mypy configured with `ignore_missing_imports = true` and `warn_return_any = false` (permissive)
- No complexity checks or import ordering enforcement beyond ruff defaults

### Container Images

**Strengths:**
- **Multi-stage build**: builder (uv sync) + runtime (minimal production image)
- **Red Hat UBI9 base** (`registry.access.redhat.com/ubi9/python-312`) - well-maintained, enterprise-grade
- **Non-root user** (`USER 1001`) for security
- **OCI labels** (title, description, license, source)
- **Docker Buildx** with GHA layer caching (`cache-from: type=gha`, `cache-to: type=gha,mode=max`)
- **Build provenance attestation** for supply chain security
- **Proper .dockerignore** (excludes .git, tests, docs, caches)
- **Frozen lockfile** (`uv sync --frozen --no-dev`) for reproducible builds

**Weaknesses:**
- **Single architecture only** (`linux/amd64`) - no arm64 support
- **No vulnerability scanning** (Trivy, Snyk, Grype)
- **No SBOM generation** (Syft, cyclonedx)
- **No image signing** (cosign)
- **No runtime validation** in CI (image starts, healthcheck passes)
- **No image size optimization** tracking

### Security

**Strengths:**
- Build provenance attestation (SLSA Level 1)
- Non-root container execution
- `.env` in `.gitignore` (no credential leaking)
- Input validation on trace IDs (path traversal prevention)
- Token-based auth with ServiceAccount auto-detection
- Proper TLS handling for in-cluster communication

**Weaknesses:**
- No container vulnerability scanning (Trivy/Snyk/Grype)
- No SAST tools (CodeQL, Bandit, Semgrep)
- No dependency scanning (Dependabot, Renovate, safety)
- No secret detection (gitleaks, TruffleHog)
- No security-focused CI workflow
- `GITHUB_TOKEN` is used for GHCR push but no mention of least-privilege scoping

### Agent Rules (Agentic Flow Quality)

**Status**: Missing
**Coverage**: None - no test type rules exist
**Quality**: N/A
**Gaps**: Everything - no `.claude/` directory, `CLAUDE.md`, or `AGENTS.md`

The repository has excellent human-readable documentation:
- `TESTING.md` documents test patterns (respx mocking, tool testing), running tests, and coverage
- `CONTRIBUTING.md` describes development setup, code standards, project structure, and PR process

However, none of this is structured for AI agent consumption:
- No `.claude/rules/` with unit test, E2E test, or backend test creation rules
- No automated test generation guidance (which mocks to use, fixture patterns, assertion conventions)
- An AI agent would need to read TESTING.md + examine multiple test files to infer patterns

**Recommendation**: Generate agent rules with `/test-rules-generator` to create:
- `unit-tests.md` - respx patterns, AsyncMock usage, conftest fixtures
- `e2e-tests.md` - Kind deployment testing patterns
- `backend-tests.md` - HTTP client mocking conventions

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning** - Add Trivy or Snyk to `container-build.yml` to scan the built image before pushing. This catches CVEs in UBI9 base image and Python dependencies.

2. **Enforce coverage threshold in CI** - Add `--cov-fail-under=80` to the pytest command in `ci.yml` and set `fail_ci_if_error: true` in Codecov upload. The project already documents 80% as the threshold in TESTING.md.

3. **Add SAST scanning** - Add a CodeQL or Semgrep workflow. The MCP server handles external input (PromQL queries, trace IDs, namespace names) that flows to backend HTTP calls - SAST tools can detect injection risks.

### Priority 1 (High Value)

4. **Add functional E2E tests** - Extend `kind-e2e.yml` to invoke actual MCP tools (e.g., call `query_prometheus` via the MCP protocol against the mock Prometheus). The current E2E only checks deployment + connectivity.

5. **Create agent rules** - Add `.claude/rules/` directory with test patterns extracted from existing tests. This ensures AI-generated code follows project conventions (respx mocking, shared fixtures, AsyncMock patterns).

6. **Add multi-arch builds** - Extend `container-build.yml` to build `linux/amd64,linux/arm64` for broader deployment support.

7. **Add dependency automation** - Configure Dependabot or Renovate for automated Python dependency updates and vulnerability alerts.

### Priority 2 (Nice-to-Have)

8. **Add SBOM generation** - Generate Software Bill of Materials during container build for supply chain visibility.

9. **Add pre-commit hooks** - Create `.pre-commit-config.yaml` with ruff and mypy hooks for faster local feedback.

10. **Add HTTP health endpoint** - Replace TCP socket liveness/readiness probes with an HTTP GET endpoint that validates backend connectivity.

11. **Add integration test layer** - Tests that exercise backend+tool together with a real HTTP server (e.g., using pytest-httpserver) rather than only respx mocking.

## Comparison to Gold Standards

| Dimension | rhoai-observability-mcp | odh-dashboard | notebooks | kserve |
|-----------|------------------------|---------------|-----------|--------|
| Unit Tests | 112 tests, 1:1 ratio | Multi-layer, contract tests | Image-focused | Coverage enforcement |
| E2E Tests | Kind deployment test | Cypress + API | 5-layer validation | Multi-version K8s |
| Coverage | Codecov (not enforced) | Enforced thresholds | Per-image coverage | Per-PR enforcement |
| Image Scanning | None | Trivy in CI | Multi-layer scanning | Trivy + SBOM |
| SAST | None | CodeQL | N/A | CodeQL + gosec |
| Agent Rules | None | Comprehensive .claude/ | N/A | N/A |
| Multi-arch | amd64 only | amd64 + arm64 | Multi-arch + multi-Python | amd64 |
| Pre-commit | None | Husky + lint-staged | N/A | golangci-lint |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - Lint + typecheck + test pipeline
- `.github/workflows/container-build.yml` - Container build + push + attestation
- `.github/workflows/kind-e2e.yml` - Kind-based E2E deployment testing

### Source Code
- `src/rhoai_obs_mcp/server.py` - FastMCP server creation and tool registration
- `src/rhoai_obs_mcp/config.py` - Settings via pydantic-settings
- `src/rhoai_obs_mcp/auth.py` - Token management
- `src/rhoai_obs_mcp/backends/` - HTTP clients (prometheus, alertmanager, loki, tempo, grafana, openshift)
- `src/rhoai_obs_mcp/tools/` - MCP tool implementations (21 tools across 7 categories)

### Tests
- `tests/unit/conftest.py` - Shared fixtures (settings, auth)
- `tests/unit/test_*.py` - 19 unit test files (112 test functions)
- `tests/smoke_test.py` - Live cluster smoke test (manual)

### Build & Deploy
- `Containerfile` - Multi-stage container build (UBI9 + uv)
- `Makefile` - Build, deploy, and Kind management targets
- `deploy/base/` - Kubernetes base manifests
- `deploy/overlays/kind/` - Kind overlay with mock backends
- `deploy/overlays/openshift/` - OpenShift overlay with Route

### Configuration
- `pyproject.toml` - Python project config (ruff, mypy, pytest, hatch)
- `.gitignore` / `.dockerignore` - Exclusion rules
