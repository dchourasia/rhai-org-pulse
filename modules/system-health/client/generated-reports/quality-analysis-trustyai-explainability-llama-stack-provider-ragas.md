---
repository: "trustyai-explainability/llama-stack-provider-ragas"
overall_score: 6.5
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Good unit test suite with mocking and parametrized tests for wrappers and base logic"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Well-structured 3-tier test strategy (unit, integration, e2e) with cluster deployment scripts"
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time container build validation; only release-time PyPI publish"
  - dimension: "Image Testing"
    score: 4.0
    status: "Containerfiles exist but no CI-driven image build, scan, or runtime validation"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "pytest-cov in dev deps but no coverage generation in CI, no thresholds, no reporting"
  - dimension: "CI/CD Automation"
    score: 6.5
    status: "CI runs pre-commit and integration tests on PRs with caching; no E2E in CI"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "No test coverage tracking or enforcement"
    impact: "Coverage can regress silently; no visibility into untested code paths"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image build or scan in CI"
    impact: "Image build failures and vulnerabilities discovered only at release time or in production"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "E2E tests not automated in CI"
    impact: "Cluster-level regressions not caught until manual testing"
    severity: "HIGH"
    effort: "12-20 hours"
  - title: "No security scanning (SAST, dependency, container)"
    impact: "Vulnerabilities in dependencies or code not detected before merge"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI-generated contributions lack project-specific test guidance"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add pytest-cov coverage reporting to CI"
    effort: "1-2 hours"
    impact: "Immediate visibility into test coverage; enables threshold enforcement"
  - title: "Add Trivy container scanning workflow"
    effort: "1-2 hours"
    impact: "Automated vulnerability detection for container images"
  - title: "Add CodeQL / Semgrep SAST scanning"
    effort: "1-2 hours"
    impact: "Automated static analysis catches security issues early"
  - title: "Enable Codecov integration with PR comments"
    effort: "2-3 hours"
    impact: "Coverage reporting on every PR; enforcement via thresholds"
recommendations:
  priority_0:
    - "Add coverage generation and enforcement to CI workflow (pytest --cov with codecov upload)"
    - "Add container build + Trivy scan step to PR workflow for both Containerfiles"
    - "Add dependency scanning (GitHub Dependabot or pip-audit in CI)"
  priority_1:
    - "Automate E2E tests in CI with a periodic or nightly workflow"
    - "Add SAST scanning (CodeQL or Semgrep) as a required PR check"
    - "Create agent rules (.claude/rules/) for test creation patterns"
    - "Add concurrency control to CI workflow to prevent duplicate runs"
  priority_2:
    - "Add multi-architecture image builds (amd64 + arm64)"
    - "Add SBOM generation and image signing for release images"
    - "Pin pre-commit hook versions and add auto-update workflow"
    - "Add secret detection (Gitleaks) as a pre-commit hook"
---

# Quality Analysis: llama-stack-provider-ragas

## Executive Summary

- **Overall Score: 6.5/10**
- **Repository Type**: Python library / Llama Stack evaluation provider
- **Primary Language**: Python 3.12
- **Framework**: Llama Stack provider (inline + remote via Kubeflow Pipelines)
- **Status**: Maintenance mode (final release v0.7.0)

**Key Strengths**: Well-structured 3-tier test strategy (unit, integration with in-process server, E2E on OpenShift), strong pre-commit hooks with ruff + mypy + pytest, clean test architecture with shared helpers and fixture-based mocking, excellent release pipeline with smoke tests.

**Critical Gaps**: No test coverage tracking or enforcement, no container image scanning, no security scanning (SAST/DAST), E2E tests are manual-only, no agent rules for AI-assisted development.

**Agent Rules Status**: Missing - no CLAUDE.md, AGENTS.md, or .claude/ directory.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Good unit tests with mocking, parametrization, and edge cases |
| Integration/E2E | 8.0/10 | Excellent 3-tier strategy with cluster deployment scripts |
| **Build Integration** | **3.0/10** | **No PR-time container build validation** |
| Image Testing | 4.0/10 | Containerfiles exist but no CI-driven build/scan |
| Coverage Tracking | 2.0/10 | pytest-cov available but never used in CI |
| CI/CD Automation | 6.5/10 | PR checks for lint/test but gaps in image and security |
| Agent Rules | 0.0/10 | No agent rules exist |

## Critical Gaps

### 1. No Test Coverage Tracking or Enforcement
- **Impact**: Coverage can regress silently with each PR; maintainers have no visibility into which code paths are untested
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `pytest-cov` is in dev dependencies and the CONTRIBUTING.md even mentions `--cov=src`, but no CI job actually generates or uploads coverage. No codecov.yml, no .coveragerc, no thresholds.
- **Fix**: Add `--cov=src --cov-report=xml` to the CI pytest step + integrate codecov or coveralls

### 2. No Container Image Build or Scan in CI
- **Impact**: The two Containerfiles (root `Containerfile` for KFP, `tests/cluster-deployment/Containerfile` for E2E distro) are never built in CI. Build breakage is only discovered during manual E2E setup or release.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No workflow builds or tests container images on PRs or pushes. No vulnerability scanning (Trivy, Snyk, Grype). No SBOM generation.

### 3. E2E Tests Not Automated in CI
- **Impact**: Cluster-level regressions in the eval providers are only caught during manual testing
- **Severity**: HIGH
- **Effort**: 12-20 hours
- **Details**: The E2E test suite (`test_e2e.py`) and deployment scripts (`deploy-e2e.sh`) are well-designed but require manual execution with an OpenShift cluster. No periodic CI job exercises these tests.

### 4. No Security Scanning
- **Impact**: Vulnerabilities in code or dependencies are not detected before merge
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No CodeQL, Semgrep, or gosec. No Dependabot or pip-audit. No Gitleaks or TruffleHog for secret detection. No container vulnerability scanning.

### 5. No Agent Rules
- **Impact**: AI-assisted contributions (via Claude Code, Copilot, etc.) lack project-specific guidance for test patterns, provider architecture, and quality standards
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`. The project has strong testing patterns that would benefit from being codified as agent rules.

## Quick Wins

### 1. Add pytest-cov Coverage to CI (1-2 hours)
Add to the integration-tests job in `.github/workflows/ci.yml`:
```yaml
    - name: Run integration tests
      run: |
        uv run pytest -m "lls_integration" -v --tb=short --maxfail=3 \
          --cov=src --cov-report=xml --cov-report=term-missing
```

### 2. Add Trivy Container Scanning (1-2 hours)
Add a new workflow step or job:
```yaml
  container-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build image
      run: docker build -t test-image -f Containerfile .
    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'test-image'
        severity: 'CRITICAL,HIGH'
        exit-code: '1'
```

### 3. Add CodeQL Scanning (1-2 hours)
```yaml
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
    - uses: actions/checkout@v4
    - uses: github/codeql-action/init@v3
      with:
        languages: python
    - uses: github/codeql-action/analyze@v3
```

### 4. Enable Codecov Integration (2-3 hours)
Add codecov upload step after test execution, create `.codecov.yml` with coverage thresholds.

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory**:
| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| CI | `ci.yml` | push/PR to main, develop | Pre-commit + integration tests |
| Release | `release.yaml` | Release published | Build + publish to PyPI |
| Docs | `docs.yml` | Push/PR touching docs/ | Antora docs build + deploy |

**Strengths**:
- CI runs on both push and PR events for `main` and `develop` branches
- Good use of uv dependency caching with `actions/cache@v3`
- Integration tests matrix includes llama-stack version testing (currently 0.6.0)
- Release pipeline has excellent smoke tests: tests both wheel and sdist locally, then verifies PyPI install

**Weaknesses**:
- No concurrency control on the CI workflow (duplicate runs on push + PR)
- No E2E test automation in CI
- Only tests against one Python version (3.12) and one llama-stack version
- No container build step in PR workflow
- Pre-commit check runs twice (all files + staged files) which is redundant in CI

### Test Coverage

**Test Architecture** (1,144 lines of tests vs. 1,788 lines of source = 0.64 test-to-code ratio):

| File | Marker | Type | Description |
|------|--------|------|-------------|
| `test_base.py` | `unit` | Unit | Tests `_get_metrics()` on `RagasEvaluatorBase` |
| `test_remote_wrappers.py` | `unit` | Unit | Tests LangChain-compatible wrappers (LLM + Embeddings) |
| `test_inline_evaluation.py` | `lls_integration` | Integration | In-process server tests via `LlamaStackAsLibraryClient` |
| `test_e2e.py` | `e2e` | E2E | Full cluster tests on OpenShift |
| `base_eval_tests.py` | — | Shared helpers | `SmokeTester` + `EvalTester` classes |
| `conftest.py` | — | Fixtures | Shared fixtures, data, registration helpers |

**Strengths**:
- 3-tier test strategy: unit (mocked) -> integration (in-process server) -> E2E (OpenShift cluster)
- Excellent mocking strategy with `--no-mock-inference` and `--no-mock-client` flags to run against real services
- Well-structured shared test helpers (`SmokeTester`, `EvalTester`) to avoid duplication
- Good use of pytest fixtures, markers, and indirect parametrization
- Integration tests build an entire Llama Stack config in fixtures (providers, models, storage)
- E2E deployment scripts are production-quality with error handling and wait loops
- Test documentation (`TESTING.md`) with model configuration matrix

**Weaknesses**:
- No coverage generation or reporting
- Only ~0.64 test-to-code ratio (moderate)
- Unit tests cover `base.py` and `wrappers_remote.py` well, but no unit tests for `ragas_inline_eval.py`, `ragas_remote_eval.py`, `config.py`, `kubeflow/pipeline.py`, `kubeflow/components.py`
- Integration tests only exercise the inline provider path (no remote/Kubeflow integration tests in CI)
- E2E tests are purely manual

### Code Quality

**Linting & Formatting**:
- **Ruff**: Well-configured in `pyproject.toml` with E, W, F, I, B, C4, UP rule sets
- **MyPy**: Configured with moderate strictness (`check_untyped_defs=true`, `warn_return_any=true`, but `disallow_untyped_defs=false`)
- **Pre-commit hooks**: Comprehensive setup with:
  - `pre-commit-hooks`: trailing whitespace, end-of-file, YAML check, large files, merge conflicts, debug statements
  - `ruff-pre-commit`: ruff-check with auto-fix + ruff-format
  - `mirrors-mypy`: mypy with additional type stubs
  - Local `pytest` hook: runs unit + integration tests on every commit

**Strengths**:
- Pre-commit hooks enforced in CI via `pre-commit run --all-files`
- Pytest runs as a pre-commit hook (unusual but ensures tests pass before commit)
- Good ruff rule selection covering common bug patterns (flake8-bugbear, pyupgrade)

**Weaknesses**:
- No SAST tools (CodeQL, Semgrep)
- No secret detection (Gitleaks, TruffleHog)
- No dependency vulnerability scanning
- MyPy is moderate rather than strict (`disallow_untyped_defs=false`)

### Container Images

**Containerfiles**:

1. **Root `Containerfile`** (for KFP remote provider):
   - Simple single-stage build from `python:3.12`
   - Installs package in editable mode with `[remote]` extras
   - No multi-stage build, no security hardening
   - No health check, no non-root user

2. **`tests/cluster-deployment/Containerfile`** (E2E distro image):
   - Better structure: uses `python:3.12-slim` base
   - Installs `uv` from official image
   - Pre-downloads HF model for offline operation
   - Proper layer caching (heavy deps first, source code last)
   - Exposes port 8321

**Weaknesses**:
- Neither Containerfile is built in CI
- No vulnerability scanning (Trivy/Snyk/Grype)
- No SBOM generation or image signing
- Root Containerfile uses full `python:3.12` (larger attack surface)
- No multi-architecture builds
- No `.trivyignore` for known vulnerability management
- No health check or runtime validation in CI

### Security

**Current State**: Minimal security tooling.

| Category | Tool | Status |
|----------|------|--------|
| SAST | CodeQL/Semgrep | Missing |
| Dependency Scanning | Dependabot/pip-audit | Missing |
| Container Scanning | Trivy/Snyk | Missing |
| Secret Detection | Gitleaks/TruffleHog | Missing |
| SBOM | Syft/Trivy | Missing |
| Image Signing | Cosign/Sigstore | Missing |

**Mitigating Factor**: The `.dockerignore` properly excludes `.env` files and `.git` directory. The `.pre-commit-config.yaml` includes `check-added-large-files` and `debug-statements` hooks.

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: N/A
- **Quality**: N/A
- **Gaps**: No `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Recommendation**: Generate rules with `/test-rules-generator` covering:
  - Unit test patterns (mocking LlamaStackClient, parametrized metrics tests)
  - Integration test patterns (library client config fixtures, inference mocking)
  - E2E test patterns (cluster fixtures, smoke tester usage)
  - Provider architecture (inline vs remote, base class extension)

## Recommendations

### Priority 0 (Critical)

1. **Add coverage generation and enforcement to CI** (2-4 hours)
   - Add `--cov=src --cov-report=xml` to pytest commands
   - Integrate codecov with GitHub app
   - Set minimum coverage threshold (e.g., 70%)
   - Enable PR coverage comments

2. **Add container build and scan to PR workflow** (4-6 hours)
   - Build both Containerfiles on every PR
   - Add Trivy vulnerability scanning with CRITICAL/HIGH threshold
   - Fail PR if critical vulnerabilities found

3. **Add dependency scanning** (1-2 hours)
   - Enable GitHub Dependabot for Python dependencies
   - Or add `pip-audit` step to CI workflow

### Priority 1 (High Value)

4. **Automate E2E tests** (12-20 hours)
   - Create a nightly/weekly GitHub Actions workflow
   - Use a self-hosted runner with OpenShift access
   - Or set up a Kind/Minikube-based simplified E2E suite

5. **Add SAST scanning** (1-2 hours)
   - Enable CodeQL for Python analysis
   - Or add Semgrep with Python ruleset

6. **Create agent rules** (2-3 hours)
   - Create `.claude/rules/unit-tests.md` with mocking patterns
   - Create `.claude/rules/integration-tests.md` with library client patterns
   - Create `.claude/rules/e2e-tests.md` with cluster test patterns
   - Create `CLAUDE.md` with project overview and architecture

7. **Add concurrency control** (30 minutes)
   ```yaml
   concurrency:
     group: ci-${{ github.ref }}
     cancel-in-progress: true
   ```

### Priority 2 (Nice-to-Have)

8. **Multi-architecture image builds** (2-4 hours)
   - Add `docker/build-push-action` with `platforms: linux/amd64,linux/arm64`

9. **SBOM generation and image signing** (2-3 hours)
   - Add Syft SBOM generation
   - Add Cosign image signing for releases

10. **Secret detection** (1 hour)
    - Add Gitleaks as a pre-commit hook
    - Or add TruffleHog to CI workflow

11. **Expand test matrix** (2-3 hours)
    - Test against multiple llama-stack versions (0.5.x, 0.6.x)
    - Test against Python 3.13 when supported

## Comparison to Gold Standards

| Dimension | llama-stack-provider-ragas | odh-dashboard | notebooks | kserve |
|-----------|--------------------------|---------------|-----------|--------|
| Unit Tests | 7.5 - Good mocking, gaps in coverage | 9.0 - Comprehensive | 7.0 | 9.0 - High coverage |
| Integration/E2E | 8.0 - 3-tier but manual E2E | 9.5 - Full automation | 8.0 | 9.0 - Multi-version |
| Build Integration | 3.0 - No PR image builds | 8.0 - Konflux integration | 7.0 | 8.0 |
| Image Testing | 4.0 - Containerfiles only | 8.0 - Multi-layer | 9.0 - 5-layer validation | 7.0 |
| Coverage Tracking | 2.0 - Not implemented | 9.0 - Enforced thresholds | 6.0 | 9.0 - Codecov |
| CI/CD Automation | 6.5 - Good PR checks | 9.0 - Full pipeline | 8.0 | 9.0 |
| Agent Rules | 0.0 - None | 8.0 - Comprehensive | 3.0 | 2.0 |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - PR checks (pre-commit + integration tests)
- `.github/workflows/release.yaml` - PyPI publish on release
- `.github/workflows/docs.yml` - Antora documentation build/deploy

### Testing
- `tests/test_base.py` - Unit tests for base evaluator
- `tests/test_remote_wrappers.py` - Unit tests for LangChain wrappers
- `tests/test_inline_evaluation.py` - Integration tests with in-process server
- `tests/test_e2e.py` - E2E tests for OpenShift deployment
- `tests/base_eval_tests.py` - Shared SmokeTester/EvalTester helpers
- `tests/conftest.py` - Shared fixtures
- `tests/TESTING.md` - Test documentation

### Code Quality
- `pyproject.toml` - Ruff, MyPy, pytest configuration
- `.pre-commit-config.yaml` - Pre-commit hooks

### Container Images
- `Containerfile` - KFP remote provider image
- `tests/cluster-deployment/Containerfile` - E2E test distro image
- `tests/cluster-deployment/deploy-e2e.sh` - E2E deployment script
- `.dockerignore` - Docker build exclusions

### Documentation
- `README.md` - Project overview and setup
- `CONTRIBUTING.md` - Development workflow
- `COMPATIBILITY.md` - Version compatibility matrix
- `docs/` - Antora documentation
