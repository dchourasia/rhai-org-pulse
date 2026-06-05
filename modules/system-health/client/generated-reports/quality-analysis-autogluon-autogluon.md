---
repository: "autogluon/autogluon"
overall_score: 6.4
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Strong test coverage across all modules with pytest, markers, and parallel execution"
  - dimension: "Integration/E2E"
    score: 6.0
    status: "Multi-platform nightly tests, GPU/multi-GPU testing, but no explicit integration test suites"
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time Docker image validation; image builds are nightly-only on AWS ECR"
  - dimension: "Image Testing"
    score: 4.0
    status: "Multiple Dockerfiles for CPU/GPU training/inference, but no runtime validation or scanning"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tooling — no codecov, coveralls, .coveragerc, or --cov in any workflow"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Well-structured PR CI with concurrency control, path filters, and AWS Batch offloading"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory — zero AI agent guidance"
critical_gaps:
  - title: "Zero test coverage tracking or enforcement"
    impact: "No visibility into which code is tested; regressions in coverage go undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container image runtime validation"
    impact: "Nightly Docker images pushed to ECR without startup or functional testing"
    severity: "HIGH"
    effort: "6-8 hours"
  - title: "No PR-time Docker build validation"
    impact: "Image build regressions only discovered in nightly builds, not at PR review time"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No dependency vulnerability scanning in CI"
    impact: "Security vulnerabilities in dependencies not caught until manual review"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "Multimodal tests gated behind labels, not run by default"
    impact: "PRs can merge with multimodal regressions if contributor forgets to add label"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add pytest-cov and codecov integration"
    effort: "3-4 hours"
    impact: "Immediate visibility into test coverage with PR-level reporting and threshold enforcement"
  - title: "Add Dependabot or Renovate for dependency updates"
    effort: "1-2 hours"
    impact: "Automated security patches and dependency freshness tracking"
  - title: "Add Trivy container scanning to image build workflow"
    effort: "1-2 hours"
    impact: "Catch known CVEs in Docker images before they reach ECR"
  - title: "Create basic CLAUDE.md with testing guidelines"
    effort: "2-3 hours"
    impact: "Guide AI-assisted development to follow project testing patterns"
recommendations:
  priority_0:
    - "Implement pytest-cov across all modules and integrate with codecov for PR-level coverage reporting"
    - "Add container vulnerability scanning (Trivy/Snyk) to the nightly image build workflow"
    - "Add runtime validation step after Docker image builds to verify images start correctly"
  priority_1:
    - "Run multimodal tests by default on PRs (remove label gate) to prevent silent regressions"
    - "Add Dependabot configuration for automated dependency security updates"
    - "Create integration test suites that test cross-module interactions (tabular+multimodal, etc.)"
  priority_2:
    - "Add agent rules (.claude/rules/) for test creation patterns per module"
    - "Implement performance regression benchmarks as part of CI (not just manual dispatch)"
    - "Add SBOM generation and image signing for published Docker images"
---

# Quality Analysis: autogluon/autogluon

## Executive Summary

- **Overall Score: 6.4/10**
- **Repository Type**: Python ML library (monorepo with 7 sub-packages)
- **Primary Language**: Python (3.10-3.13)
- **Framework**: AutoML — tabular, multimodal, time series, EDA
- **Key Strengths**: Well-organized CI with AWS Batch offloading, strong per-module unit testing, multi-platform (Linux/macOS/Windows) nightly validation, active security tooling (CodeQL, CodeGuru, Bandit)
- **Critical Gaps**: Zero test coverage tracking, no container image validation, no dependency scanning in CI, no agent rules
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or `.claude/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Strong test suite across all modules with pytest markers and parallel execution |
| Integration/E2E | 6.0/10 | Multi-platform nightly tests and GPU testing, but no explicit integration suites |
| **Build Integration** | **3.0/10** | **No PR-time Docker build; image builds are nightly-only** |
| Image Testing | 4.0/10 | 8 Dockerfiles for CPU/GPU variants, but zero runtime validation or scanning |
| Coverage Tracking | 1.0/10 | No coverage tooling whatsoever — no codecov, no .coveragerc, no --cov flags |
| CI/CD Automation | 8.0/10 | Well-structured with concurrency control, path filters, AWS Batch offloading |
| Agent Rules | 0.0/10 | No AI agent guidance — no CLAUDE.md, AGENTS.md, or .claude/ directory |

## Critical Gaps

### 1. Zero Test Coverage Tracking or Enforcement
- **Impact**: No visibility into which code is actually tested; coverage regressions go completely undetected. Contributors have no way to know if their PR reduces coverage.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No `.coveragerc`, `codecov.yml`, or `--cov` flags anywhere in the repository. Test scripts use bare `pytest` without coverage collection. This is a significant gap for a project of this size (650+ source files, 280+ test files).

### 2. No Container Image Runtime Validation
- **Impact**: Nightly Docker images (CPU/GPU training/inference) are pushed to AWS ECR without any verification that they start correctly, import AutoGluon successfully, or pass basic smoke tests.
- **Severity**: HIGH
- **Effort**: 6-8 hours
- **Details**: The `build_latest_image.yml` workflow builds 4 Docker images nightly but only runs `docker build` + `docker push`. No `docker run` or health check validation.

### 3. No PR-Time Docker Build Validation
- **Impact**: Dockerfile changes or dependency changes that break image builds are only discovered in nightly builds, not during PR review. This creates a delayed feedback loop.
- **Severity**: HIGH
- **Effort**: 8-12 hours

### 4. No Dependency Vulnerability Scanning in CI
- **Impact**: While Dependabot is mentioned in SECURITY.md, no `dependabot.yml` configuration exists in `.github/`. No Trivy, Snyk, or other dependency scanning runs in CI.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

### 5. Multimodal Tests Gated Behind Labels
- **Impact**: Multimodal tests (`test_multimodal_predictor`, `test_multimodal_others`, `test_multimodal_others_2`) only run on PRs when the `run-multimodal` label is applied. PRs can merge with multimodal regressions if contributors forget to add the label.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

## Quick Wins

### 1. Add pytest-cov and Codecov Integration (3-4 hours)
Add `--cov` to pytest invocations and configure codecov:
```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: auto
        threshold: 1%
    patch:
      default:
        target: 80%
```
```bash
# In test scripts, add coverage collection:
python -m pytest --cov=autogluon --cov-report=xml --junitxml=results.xml --runslow tests
```

### 2. Add Dependabot Configuration (1-2 hours)
```yaml
# .github/dependabot.yml
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
  - package-ecosystem: "docker"
    directory: "/CI/docker"
    schedule:
      interval: "weekly"
```

### 3. Add Trivy Scanning to Image Builds (1-2 hours)
```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: autogluon-nightly-training:cpu-latest
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 4. Create Basic CLAUDE.md (2-3 hours)
Document testing patterns, module structure, and contribution guidelines for AI-assisted development.

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- **16 workflow files** covering CI, platform tests, benchmarking, image builds, and releases
- **Concurrency control** (`cancel-in-progress: true`) prevents wasted resources on superseded PRs
- **Path filtering** (via `dorny/paths-filter`) skips CI when only docs change
- **AWS Batch offloading** for compute-intensive tests (GPU tests run on actual GPU instances)
- **Multi-platform nightly testing** across macOS, Windows, Ubuntu with Python 3.10-3.13 matrix
- **Automated pre-commit hook updates** via weekly cron workflow
- **Benchmark infrastructure** with slash command dispatch for tabular/timeseries/multimodal

**Weaknesses:**
- **Outdated action versions**: Uses `actions/checkout@v2` throughout (current is v4), `aws-actions/configure-aws-credentials@v1` (current is v4)
- **Commented-out workflows**: Multiple sections disabled (EDA tests, Pyodide tests, package_diff) — indicates abandoned or deferred features
- **No caching**: No pip/conda caching in CI workflows (though AWS Batch may handle this internally)
- **Label-gated tests**: Multimodal and multi-GPU tests require manual labels, creating a risk of missed regressions

**Workflow Inventory:**
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `continuous_integration.yml` | push, PR | Main CI — lint + module tests |
| `continuous_integration_multigpu.yaml` | PR (labeled) | Multi-GPU multimodal tests |
| `platform_tests-command.yml` | schedule (daily), dispatch | Cross-platform matrix tests |
| `benchmark-command.yml` | dispatch | Performance benchmarks |
| `build_latest_image.yml` | schedule (daily), dispatch | Nightly Docker image builds |
| `codeql.yml` | push, PR, schedule | CodeQL security analysis |
| `codeguru-reviewer.yml` | push to master | AWS CodeGuru review |
| `codespell.yml` | push/PR to master | Spelling checks |
| `check_hf_model_list.yml` | PR (labeled) | HuggingFace model list validation |
| `update-pre-commit.yml` | schedule (weekly) | Auto-update ruff hooks |
| `pypi_release.yml` | dispatch | PyPI release workflow |
| `pythonpublish.yml` / `pythonpublish_testpypi.yml` | dispatch | Package publishing |
| `slash_command_dispatch.yml` | issue_comment | Slash command routing |

### Test Coverage

**280 test files across 7 modules** with a test-to-source ratio of **0.43:1** (280 tests / 650 sources):

| Module | Source Files | Test Files | Ratio | Notes |
|--------|-------------|------------|-------|-------|
| common | 48 | 24 | 0.50 | Good coverage |
| core | 91 | 41 | 0.45 | Includes testing utilities |
| features | 48 | 27 | 0.56 | Strong coverage |
| tabular | 194 | 67 | 0.35 | Lower ratio, large module |
| multimodal | 147 | 45 | 0.31 | Lowest ratio, most complex module |
| timeseries | 93 | 50 | 0.54 | Strong coverage with deep model testing |
| eda | 28 | 26 | 0.93 | Highest ratio but tests are disabled in CI |

**Testing Patterns:**
- **Framework**: pytest with custom markers (`@pytest.mark.slow`, `@pytest.mark.gpu`, `@pytest.mark.regression`, `@pytest.mark.pyodide`, `@pytest.mark.multi_gpu`)
- **Fixtures**: 12 `conftest.py` files across modules with shared fixtures
- **Parametrization**: Extensive use of `@pytest.mark.parametrize` for model variants
- **Parallel execution**: `pytest-xdist` used for timeseries tests (`--numprocesses 4`)
- **Mocking**: ~991 mock/patch references — heavy mocking, especially in timeseries
- **JUnit XML reporting**: All test scripts produce `results.xml`

**Notable gaps:**
- **EDA module tests are disabled** — commented out in CI workflows
- **No explicit integration tests** — no cross-module test suites
- **No coverage measurement** — tests run but coverage is never collected

### Code Quality

**Strengths:**
- **Ruff** for formatting and linting (configured in `pyproject.toml`, enforced via pre-commit and CI)
- **Bandit** security linter for the multimodal module (`bandit -r multimodal/src -ll`)
- **Codespell** for spelling checks
- **Pre-commit hooks** with auto-update via weekly cron job
- **Pyright** type checking configured for timeseries module
- **CodeGuru Reviewer** (AWS) on pushes to master

**Weaknesses:**
- **Ruff linting is minimal** — only `--select I` (isort) in pre-commit; many categories disabled
- **Ruff ignores broad rules**: `E501` (line length), `E731` (lambda assignment), `E722` (bare except) all ignored
- **Pyright only covers timeseries** — other modules have no type checking
- **No mypy** — no `mypy.ini` or mypy integration for type safety
- **Bandit only covers multimodal** — other modules not scanned

### Container Images

**8 Dockerfiles** organized in `CI/docker/` and `CI/batch/docker/`:

| Dockerfile | Base Image | Purpose |
|------------|-----------|---------|
| `Dockerfile.cpu-training` | PyTorch 2.5.1 CPU SageMaker | Nightly CPU training image |
| `Dockerfile.cpu-inference` | PyTorch CPU SageMaker | Nightly CPU inference image |
| `Dockerfile.gpu-training` | PyTorch 2.5.1 GPU CUDA 12.4 | Nightly GPU training image |
| `Dockerfile.gpu-inference` | PyTorch GPU CUDA SageMaker | Nightly GPU inference image |
| `Dockerfile.cpu` (batch) | AWS Batch CPU | CI batch compute |
| `Dockerfile.gpu` (batch) | AWS Batch GPU | CI GPU batch compute |
| `Dockerfile.pyodide` (batch) | Pyodide environment | WASM testing |
| `Dockerfile` (hf_mirror) | HuggingFace mirror | Model caching |

**Weaknesses:**
- **No multi-stage builds** — single-stage Dockerfiles cloning from GitHub at build time
- **No .dockerignore** — entire repo context sent to Docker daemon
- **No health checks** — no HEALTHCHECK instruction in any Dockerfile
- **No runtime validation** — images pushed without any `docker run` testing
- **No vulnerability scanning** — no Trivy/Snyk integration
- **No SBOM generation** — no software bill of materials
- **No image signing** — no cosign/notation attestation
- **Hardcoded AWS account IDs** in base image references

### Security

**Strengths:**
- **CodeQL** analysis on push, PR, and weekly schedule
- **AWS CodeGuru Reviewer** for AI-powered code review on master pushes
- **Bandit** static analysis for the multimodal module
- **SECURITY.md** with vulnerability reporting process
- **Codespell** for catching accidental credential-like strings

**Weaknesses:**
- **No Dependabot configuration** — SECURITY.md claims Dependabot support but no `.github/dependabot.yml` exists
- **No Snyk integration** — SECURITY.md mentions Docker scanning with Snyk but no evidence in CI
- **No secret detection** — no Gitleaks, TruffleHog, or git-secrets
- **No SAST beyond CodeQL/Bandit** — no Semgrep or SonarQube
- **AWS credentials hardcoded in workflows** — IAM role ARNs and account IDs in plain text in YAML files

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test type rules whatsoever
- **Quality**: N/A — no agent rules exist
- **Gaps**: 
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory
  - No `.claude/rules/` for test creation patterns
  - No `.claude/skills/` for custom automation
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering:
  - Per-module test patterns (tabular, multimodal, timeseries, etc.)
  - pytest marker usage guidelines
  - Fixture patterns and shared conftest conventions
  - GPU test annotation requirements
  - Mock/patch patterns for external service isolation

## Recommendations

### Priority 0 (Critical)

1. **Implement coverage tracking** — Add `pytest-cov` and `codecov` integration. Collect coverage in CI test scripts, upload to codecov, and enforce minimum thresholds on PRs. This is the single highest-impact improvement.

2. **Add container vulnerability scanning** — Integrate Trivy into `build_latest_image.yml` to scan all 4 nightly images before pushing to ECR. Block pushes with CRITICAL/HIGH CVEs.

3. **Add image runtime validation** — After `docker build`, run `docker run --rm <image> python -c "import autogluon; print(autogluon.__version__)"` to verify images start correctly and AutoGluon is importable.

### Priority 1 (High Value)

4. **Remove multimodal test label gate** — Run multimodal tests by default on PRs (at least a subset) to prevent silent regressions. Use path filtering to limit to relevant changes instead of manual labels.

5. **Add Dependabot configuration** — Create `.github/dependabot.yml` for pip, GitHub Actions, and Docker base image updates. This fulfills the claim in SECURITY.md.

6. **Update GitHub Actions versions** — Migrate from `actions/checkout@v2` to `v4`, `aws-actions/configure-aws-credentials@v1` to `v4`, etc. Outdated actions miss security patches.

7. **Add cross-module integration tests** — Create test suites that exercise interactions between modules (e.g., tabular using multimodal features, time series with custom transformers).

### Priority 2 (Nice-to-Have)

8. **Add agent rules** — Create `.claude/rules/` with test patterns for each module, pytest marker conventions, and fixture guidelines.

9. **Expand type checking** — Extend Pyright (or add mypy) beyond timeseries to all modules. Type safety reduces bugs significantly in a codebase of this complexity.

10. **Add performance regression CI** — Make benchmark workflow run automatically on PRs that touch core prediction paths, not just manual dispatch.

11. **Add SBOM generation** — Generate software bill of materials for Docker images for supply chain security compliance.

12. **Implement secret detection** — Add Gitleaks or TruffleHog to prevent accidental credential commits.

## Comparison to Gold Standards

| Capability | AutoGluon | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|-----------|-----------|---------------------|-----------------|---------------|
| Unit Tests | pytest with markers | Jest + React Testing Library | pytest per notebook | Go testing + envtest |
| Coverage Tracking | **None** | codecov with enforcement | Coverage per notebook | Codecov with 80%+ |
| Integration Tests | Multi-platform nightly | Cypress E2E | Cross-notebook | Multi-version K8s |
| Image Testing | Nightly build only | Build + validate + scan | 5-layer validation | Multi-arch build |
| Image Scanning | **None in CI** | Trivy integration | Trivy + SBOM | Trivy + signing |
| Pre-commit | ruff (format + isort) | ESLint + Prettier | flake8 + black | golangci-lint |
| Security Scanning | CodeQL + CodeGuru | CodeQL + Snyk | Trivy | CodeQL + gosec |
| Agent Rules | **None** | Comprehensive rules | Basic rules | None |
| CI Caching | AWS Batch (opaque) | npm cache + Docker layer | pip cache | Go mod cache |
| Coverage Enforcement | **None** | PR coverage gates | Per-notebook | Threshold enforcement |

## File Paths Reference

### CI/CD
- `.github/workflows/continuous_integration.yml` — Main PR CI pipeline
- `.github/workflows/continuous_integration_multigpu.yaml` — Multi-GPU CI
- `.github/workflows/platform_tests-command.yml` — Cross-platform nightly tests
- `.github/workflows/build_latest_image.yml` — Nightly Docker image builds
- `.github/workflows/benchmark-command.yml` — Benchmark infrastructure
- `.github/workflows/codeql.yml` — CodeQL security scanning
- `.github/workflows/codeguru-reviewer.yml` — AWS CodeGuru review
- `.github/workflows/codespell.yml` — Spelling checks
- `.github/workflows/update-pre-commit.yml` — Auto-update pre-commit hooks
- `.github/workflow_scripts/` — Shell scripts for test execution

### Testing
- `common/tests/`, `core/tests/`, `features/tests/` — CPU module tests
- `tabular/tests/`, `multimodal/tests/` — GPU module tests
- `timeseries/tests/` — Time series tests (parallel execution)
- `eda/tests/` — EDA tests (disabled in CI)
- `*/tests/conftest.py` — Shared fixtures and markers per module

### Code Quality
- `pyproject.toml` — Ruff, codespell, pyright configuration
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff format + isort)
- `setup.cfg` — pycodestyle/flake8 configuration

### Container Images
- `CI/docker/Dockerfile.{cpu,gpu}-{training,inference}` — Nightly images
- `CI/batch/docker/Dockerfile.{cpu,gpu,pyodide}` — CI batch images
- `CI/hf_mirror/Dockerfile` — HuggingFace model mirror

### Security
- `SECURITY.md` — Security policy and vulnerability reporting
- `.github/workflows/codeql.yml` — CodeQL scanning
- `.github/workflows/codeguru-reviewer.yml` — CodeGuru review
