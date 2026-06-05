---
repository: "opendatahub-io/autogluon"
overall_score: 5.9
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "206 test files with 1,239+ test functions across 7 packages; pytest with slow/regression markers"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "Smoke tests and regression tests exist but are CI-only; no dedicated E2E framework"
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time image build validation; nightly-only Docker builds on AWS ECR"
  - dimension: "Image Testing"
    score: 3.0
    status: "4 Dockerfiles built nightly but no runtime validation, startup testing, or vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "Only EDA package has coverage config (fail_under=90); 6 of 7 packages have zero coverage tracking"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Comprehensive AWS Batch-based CI with concurrency control and path filtering; uses outdated actions"
  - dimension: "Agent Rules"
    score: 7.0
    status: "CLAUDE.md and AGENTS.md present with build/test/lint commands and architecture docs; no .claude/rules/"
critical_gaps:
  - title: "No coverage tracking for 6 of 7 packages"
    impact: "Test regressions go undetected; no visibility into which code paths are exercised"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No container vulnerability scanning"
    impact: "Known CVEs in base images or dependencies ship to production undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time Docker image build validation"
    impact: "Image build failures discovered only after merge in nightly builds"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No container runtime validation"
    impact: "Import errors, missing dependencies, or startup failures not caught until deployment"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Outdated GitHub Actions versions (v1/v2)"
    impact: "Deprecated Node.js runtimes; potential security exposure from unpatched action versions"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No dependency vulnerability scanning (Dependabot/Renovate)"
    impact: "Known CVEs in Python dependencies not flagged or auto-patched"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add Trivy scanning to nightly image build workflow"
    effort: "1-2 hours"
    impact: "Detect CVEs in all 4 Docker images before they reach ECR"
  - title: "Enable Dependabot for Python dependency updates"
    effort: "30 minutes"
    impact: "Automated PRs for security patches in pip dependencies"
  - title: "Upgrade GitHub Actions to latest versions (v4)"
    effort: "2-3 hours"
    impact: "Fix deprecation warnings and reduce security surface"
  - title: "Add pytest-cov to all package test runs"
    effort: "3-4 hours"
    impact: "Immediate visibility into test coverage across all 7 packages"
  - title: "Add .claude/rules/ for test automation guidance"
    effort: "2-3 hours"
    impact: "AI-generated tests follow project conventions consistently"
recommendations:
  priority_0:
    - "Add pytest-cov and coverage thresholds to all 7 packages (currently only EDA has coverage at 90%)"
    - "Add Trivy container scanning to the build_latest_image workflow before pushing to ECR"
    - "Add PR-time Docker build validation to catch image build failures before merge"
  priority_1:
    - "Upgrade all GitHub Actions from v1/v2 to v4 (checkout, configure-aws-credentials, etc.)"
    - "Enable Dependabot or Renovate for automated dependency security updates"
    - "Add container runtime validation (import checks, model loading) to image build pipeline"
    - "Create .claude/rules/ directory with test patterns for each package type"
  priority_2:
    - "Add Codecov/Coveralls integration with PR coverage reporting"
    - "Consolidate codespell workflow triggers (currently master-only, not matching main CI triggers)"
    - "Add SBOM generation for Docker images"
    - "Add multi-architecture Docker builds (currently amd64-only)"
---

# Quality Analysis: opendatahub-io/autogluon

## Executive Summary

- **Overall Score: 5.9/10**
- **Repository Type**: Python ML monorepo (AutoGluon AutoML framework, fork of autogluon/autogluon)
- **Primary Language**: Python
- **Packages**: 7 sub-packages (common, core, features, tabular, multimodal, timeseries, eda)
- **Key Strengths**: Comprehensive unit test suite (206 test files, 1,239+ test functions), well-structured AWS Batch CI pipeline with per-package parallelization, good agent documentation (AGENTS.md), security scanning with CodeQL + Bandit + CodeGuru
- **Critical Gaps**: No coverage tracking for 6/7 packages, no container vulnerability scanning, no PR-time image build validation, outdated GitHub Actions versions
- **Agent Rules Status**: Partial — CLAUDE.md and AGENTS.md present with excellent build/test/lint commands; no `.claude/rules/` directory for test automation patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | 206 test files, 1,239+ test functions; pytest with slow/regression markers |
| Integration/E2E | 5.0/10 | Smoke/regression tests exist (CI-only); no dedicated E2E framework |
| **Build Integration** | **3.0/10** | **No PR-time image build; nightly-only Docker builds on ECR** |
| Image Testing | 3.0/10 | 4 Dockerfiles built nightly; no runtime validation or scanning |
| Coverage Tracking | 2.0/10 | Only EDA has coverage (fail_under=90); 6/7 packages at 0% tracking |
| CI/CD Automation | 7.0/10 | AWS Batch CI with concurrency control; outdated actions (v1/v2) |
| Agent Rules | 7.0/10 | AGENTS.md with commands/architecture; no .claude/rules/ |

## Critical Gaps

### 1. No Coverage Tracking for 6 of 7 Packages
- **Impact**: Test regressions go undetected; no visibility into code path coverage
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Details**: Only the `eda` package (the smallest, now disabled in CI) has `pytest-cov` and `--cov` configured with `fail_under = 90`. The major packages (tabular, multimodal, timeseries, core, common, features) have zero coverage tracking. No Codecov/Coveralls integration exists.

### 2. No Container Vulnerability Scanning
- **Impact**: Known CVEs in base images or Python dependencies ship undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The `build_latest_image.yml` workflow builds 4 Docker images (CPU/GPU × training/inference) and pushes directly to AWS ECR without any vulnerability scanning. No Trivy, Snyk, or Grype integration exists anywhere in the pipeline.

### 3. No PR-Time Docker Build Validation
- **Impact**: Image build failures discovered only in nightly builds, not during PR review
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: Docker images are built only on a nightly schedule (`cron: "59 8 * * *"`) or manual dispatch. PRs that break Dockerfile builds (e.g., by changing dependency structure) are not caught until the next nightly run.

### 4. No Container Runtime Validation
- **Impact**: Import errors, missing system libraries, or model loading failures not caught until deployment
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Docker images are built and pushed but never tested for basic functionality — no `python -c "import autogluon"` startup check, no model loading validation, no inference smoke test.

### 5. Outdated GitHub Actions Versions
- **Impact**: Deprecated Node.js 12/16 runtimes; potential security exposure from unpatched actions
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: `actions/checkout@v2`, `aws-actions/configure-aws-credentials@v1`, `github/codeql-action/init@v2` are all used extensively. Current versions are v4. The deprecated runners will eventually stop working.

### 6. No Dependency Vulnerability Scanning
- **Impact**: Known CVEs in pip dependencies not flagged automatically
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No Dependabot, Renovate, or `pip-audit` integration. The project relies on manual dependency updates.

## Quick Wins

### 1. Enable Dependabot for Python Dependencies (~30 min)
Add `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 2. Add Trivy Scanning to Image Builds (~1-2 hours)
Add a scan step before `docker push` in `build_latest_image.yml`:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'autogluon-nightly-training:cpu-latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
- name: Upload Trivy scan results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-results.sarif'
```

### 3. Upgrade GitHub Actions Versions (~2-3 hours)
Replace across all workflows:
- `actions/checkout@v2` → `actions/checkout@v4`
- `aws-actions/configure-aws-credentials@v1` → `aws-actions/configure-aws-credentials@v4`
- `github/codeql-action/*@v2` → `github/codeql-action/*@v3`
- `dorny/paths-filter@v2` → `dorny/paths-filter@v3`

### 4. Add pytest-cov to All Packages (~3-4 hours)
Update each package's test runner script to include coverage:
```bash
python -m pytest --cov=autogluon.tabular --cov-report=xml --junitxml=results.xml tests/unittests/
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (13 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `continuous_integration.yml` | push, pull_request_target | Main CI: lint + 8 parallel test jobs + docs build |
| `continuous_integration_multigpu.yml` | PR (labeled) | Multi-GPU multimodal tests |
| `codeql.yml` | push, PR, weekly schedule | CodeQL SAST scanning |
| `codeguru-reviewer.yml` | push to master | AWS CodeGuru automated review |
| `codespell.yml` | push/PR to master | Spell checking |
| `check_hf_model_list.yml` | PR (labeled, paths) | HuggingFace model list validation |
| `build_latest_image.yml` | nightly, dispatch | 4 Docker image builds |
| `benchmark-command.yml` | dispatch | Performance benchmarking |
| `benchmark_master.yml` | schedule/dispatch | Master branch benchmarking |
| `platform_tests-command.yml` | nightly, dispatch | Cross-platform (Mac/Win/Linux × Python 3.10-3.13) |
| `pythonpublish.yml` | dispatch | PyPI release |
| `pythonpublish_testpypi.yml` | dispatch | Test PyPI release |
| `update-pre-commit.yml` | - | Pre-commit hook updates |

**Strengths**:
- Concurrency control (`cancel-in-progress: true`) on main CI and multi-GPU workflows
- Path filtering to skip CI when only docs change
- Per-package test parallelization via AWS Batch (8 parallel jobs on PR)
- Cross-platform testing matrix (macOS, Windows, Ubuntu × Python 3.10-3.13) in nightly
- Benchmark pipeline with dashboard integration

**Weaknesses**:
- All actions use outdated versions (v1/v2)
- No caching strategy for pip dependencies or conda environments in GitHub runners
- EDA package tests are commented out in CI
- `codespell.yml` targets `master` branch but main CI triggers on all branches
- Tests run on AWS Batch, making local reproduction harder
- No workflow for validating Docker builds on PRs

### Test Coverage

**Test File Distribution by Package**:

| Package | Test Files | Source Files | Test Functions | Test-to-Code Ratio |
|---------|-----------|-------------|----------------|-------------------|
| common | 20 | 48 | 80 | 0.42 |
| core | 26 | 91 | 135 | 0.29 |
| features | 21 | 48 | ~80 | 0.44 |
| tabular | 49 | 194 | 236 | 0.25 |
| multimodal | 36 | 147 | 134 | 0.24 |
| timeseries | 34 | 93 | 654 | 0.37 |
| eda | 20 | 28 | ~60 | 0.71 |
| **Total** | **206** | **649** | **1,239+** | **0.32** |

**Test Tiers**:
- **Unit tests** (`tests/unittests/`): Run on every PR via AWS Batch; gated by `@pytest.mark.slow` for expensive tests
- **Regression tests** (`tests/regressiontests/`): Tabular only; require external datasets/infrastructure
- **Smoke tests** (`tests/smoketests/`): Timeseries only; require model downloads and long runtimes
- **Style checks** (`test_check_style.py`): Ruff formatting and import sorting validation

**Coverage Tracking**:
- Only `eda` package has `pytest-cov` configured (`fail_under = 90`, branch coverage enabled)
- The `eda` package is also the **only one commented out in CI** — so the only package with coverage isn't being tested
- No Codecov, Coveralls, or any PR-level coverage reporting
- No coverage thresholds for the 6 active packages

### Code Quality

**Linting**:
- **Ruff**: Configured in `pyproject.toml` with line-length=119, target Python 3.10
  - Format checking (black-compatible)
  - Import sorting (isort-compatible) with first-party/third-party classification
  - Per-file ignores for `__init__.py` F401
  - Ignores E501 (line too long), E731 (lambda), E722 (bare except)
- **Bandit**: Security linting for `multimodal/src` only (medium+ severity, `-ll`)
- **Codespell**: Spell checking on push/PR to master
- **Pyright**: Type checking configured for `timeseries/src/` only

**Pre-commit Hooks**:
- `.pre-commit-config.yaml` present with:
  - `ruff-format` (diff mode, no auto-fix)
  - `ruff` lint (import sorting only)
- Scoped to main package directories
- Uses latest ruff version (v0.15.12)

**Static Analysis**:
- **CodeQL**: Runs on push, PR, and weekly schedule — good coverage
- **AWS CodeGuru Reviewer**: Runs on push to master — cloud-based AI review
- **Bandit**: Only covers `multimodal/src`, not other packages

### Container Images

**Dockerfiles** (4 total in `CI/docker/`):

| Dockerfile | Base Image | Purpose |
|------------|-----------|---------|
| `Dockerfile.cpu-training` | PyTorch 2.5.1 CPU SageMaker | CPU training image |
| `Dockerfile.cpu-inference` | PyTorch CPU SageMaker | CPU inference image |
| `Dockerfile.gpu-training` | PyTorch GPU SageMaker | GPU training image |
| `Dockerfile.gpu-inference` | PyTorch GPU SageMaker | GPU inference image |

**Build Process**:
- Images built nightly via `build_latest_image.yml`
- Pushed to AWS ECR (369469875935.dkr.ecr.us-east-1.amazonaws.com)
- Single-arch only (amd64)
- Full `git clone` + `full_install_image.sh` inside container (no multi-stage builds)

**Missing**:
- No vulnerability scanning (Trivy, Grype, Snyk)
- No SBOM generation
- No image signing/attestation
- No runtime validation after build
- No PR-time build testing
- No multi-architecture builds
- No `.dockerignore` optimization

### Security

**Present**:
- **CodeQL**: Full SAST scanning on push, PR, and weekly schedule
- **CodeGuru Reviewer**: AWS AI-powered code review on master pushes
- **Bandit**: Python security linting (multimodal package only)
- **Codespell**: Catches typos that could indicate code issues

**Missing**:
- No container vulnerability scanning
- No dependency vulnerability scanning (Dependabot/Renovate/pip-audit)
- No secret detection (Gitleaks, TruffleHog)
- No SBOM generation
- Bandit only covers `multimodal/src`, not other packages

### Agent Rules (Agentic Flow Quality)

**Status**: Partial

**Present**:
- `CLAUDE.md` — points to `@AGENTS.md`
- `AGENTS.md` — Comprehensive document with:
  - Monorepo package structure and dependency order
  - Install commands for each package
  - Unit test run commands per package
  - Lint/format commands (check and auto-fix)
  - Test tier documentation (unit/regression/smoke)
  - Architecture table (where to find things)
  - Key conventions (lazy imports, docstring style, small tests)
  - PR conventions

**Missing**:
- No `.claude/` directory
- No `.claude/rules/` for test automation guidance
- No per-test-type rules (unit test patterns, integration test patterns)
- No testing framework examples or templates
- No quality gate checklists

**Quality Assessment**: The AGENTS.md is well-written and actionable — one of the better examples seen. It provides the essential commands an AI agent needs to build, test, and lint code. However, it lacks structured test creation rules that would guide AI agents to generate tests matching project conventions (pytest markers, fixture patterns, slow test gating).

**Recommendation**: Generate `.claude/rules/` with `/test-rules-generator` to codify test patterns per package.

## Recommendations

### Priority 0 (Critical)

1. **Add coverage tracking to all 7 packages** — Currently only the disabled EDA package has `pytest-cov`. Add `--cov=autogluon.{package} --cov-report=xml` to each test runner script. Set initial `fail_under` thresholds based on current coverage, then ratchet up.

2. **Add container vulnerability scanning** — Add Trivy scanning to `build_latest_image.yml` before pushing images to ECR. Upload SARIF results to GitHub Security tab.

3. **Add PR-time Docker build validation** — Add a lightweight PR workflow that does `docker build --target=builder` (or equivalent dry-run) to catch build breakages before merge.

### Priority 1 (High Value)

4. **Upgrade all GitHub Actions to v4** — `actions/checkout@v2` and `aws-actions/configure-aws-credentials@v1` are deprecated. Upgrade across all 13 workflows.

5. **Enable Dependabot** — Configure for both pip and GitHub Actions ecosystems. This catches dependency CVEs automatically.

6. **Add container runtime validation** — After building images, run a quick smoke test: `docker run --rm image python -c "import autogluon; print(autogluon.__version__)"`.

7. **Expand Bandit coverage** — Currently only scans `multimodal/src`. Extend to all package source directories.

8. **Create `.claude/rules/` test automation rules** — Codify pytest patterns, fixture usage, `@pytest.mark.slow` gating, and per-package test conventions.

### Priority 2 (Nice-to-Have)

9. **Add Codecov integration with PR reporting** — Show coverage diff on each PR to prevent coverage regression.

10. **Add secret detection** — Configure Gitleaks or TruffleHog to scan for accidentally committed credentials (especially given AWS IAM role ARNs in workflows).

11. **Add SBOM generation** — Use Syft or `docker sbom` to generate SBOMs for all 4 Docker images.

12. **Add multi-architecture Docker builds** — Support arm64 for Apple Silicon development environments.

13. **Consolidate codespell triggers** — Currently only runs on `master` branch push/PR; should match main CI triggers.

14. **Add pip caching to platform tests** — The `platform_tests-command.yml` workflow reinstalls everything on each run. Add `actions/cache` for conda/pip packages.

## Comparison to Gold Standards

| Dimension | autogluon | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 7.5 — 206 files, pytest | 9.0 — Jest + React Testing Library | 6.0 — Jupyter-based | 9.0 — Go testing + table-driven |
| Integration/E2E | 5.0 — CI-only smoke/regression | 9.0 — Cypress + contract tests | 7.0 — Runtime validation | 9.0 — envtest + Kind |
| Build Integration | 3.0 — Nightly only | 8.0 — PR-time builds | 7.0 — PR image validation | 7.0 — PR operator builds |
| Image Testing | 3.0 — Build only, no validation | 7.0 — Startup testing | 9.0 — 5-layer validation | 7.0 — KServe inference testing |
| Coverage Tracking | 2.0 — 1/7 packages | 9.0 — Codecov with enforcement | 5.0 — Basic coverage | 8.0 — Codecov + thresholds |
| CI/CD Automation | 7.0 — AWS Batch parallelization | 9.0 — Optimized workflows | 8.0 — Matrix builds | 9.0 — Well-organized CI |
| Agent Rules | 7.0 — Good AGENTS.md | 9.0 — Full .claude/rules/ | 3.0 — Minimal | 4.0 — Basic CONTRIBUTING |
| Security | 5.0 — CodeQL + partial Bandit | 7.0 — SAST + dependency scanning | 6.0 — Trivy scanning | 7.0 — SAST + scanning |
| **Overall** | **5.9** | **8.4** | **6.4** | **7.6** |

## File Paths Reference

### CI/CD
- `.github/workflows/continuous_integration.yml` — Main PR CI pipeline
- `.github/workflows/continuous_integration_multigpu.yaml` — Multi-GPU multimodal tests
- `.github/workflows/build_latest_image.yml` — Nightly Docker image builds
- `.github/workflows/codeql.yml` — CodeQL SAST
- `.github/workflows/codeguru-reviewer.yml` — AWS CodeGuru
- `.github/workflows/platform_tests-command.yml` — Cross-platform nightly tests
- `.github/workflows/benchmark-command.yml` — Performance benchmarking
- `.github/actions/submit-job/action.yml` — AWS Batch job submission
- `.github/workflow_scripts/` — Shell scripts for CI test execution

### Testing
- `{common,core,features,tabular,multimodal,timeseries,eda}/tests/unittests/` — Unit tests
- `tabular/tests/regressiontests/` — Regression tests
- `timeseries/tests/smoketests/` — Smoke tests
- `tabular/tests/conftest.py` — Pytest markers (slow, regression, pyodide, multi_gpu)

### Code Quality
- `pyproject.toml` — Ruff, codespell, pyright configuration
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff-format, ruff-lint)
- `setup.cfg` — Flake8 configuration
- `eda/setup.cfg` — Coverage configuration (the only package with coverage)

### Container Images
- `CI/docker/Dockerfile.{cpu,gpu}-{training,inference}` — 4 Docker images
- `CI/docker/login_ecr.sh` — ECR authentication
- `CI/docker/full_install_image.sh` — Image installation script

### Agent Rules
- `AGENTS.md` — Comprehensive build/test/lint commands and architecture
- `CLAUDE.md` — Points to AGENTS.md
