---
repository: "red-hat-data-services/autox-ci"
overall_score: 4.6
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "No unit tests — repo is exclusively functional/E2E test harness with no tests for its own library code"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Strong parametrized functional tests for AutoRAG and AutoML pipelines with positive and negative scenarios"
  - dimension: "Build Integration"
    score: 1.0
    status: "No CI/CD workflows, no PR-time validation, no build process"
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfiles, no container images, no image testing"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage configuration, no codecov integration, no coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 1.5
    status: "No GitHub Actions workflows; only a PR template and shell runner exist"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "No CI/CD pipeline — tests never run automatically"
    impact: "Regressions in the test framework itself go undetected; broken test configs merge freely"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No unit tests for library code (2,400+ lines in autox_tests/lib/)"
    impact: "Utility functions (KFP client wrappers, S3 helpers, env parsing, pipeline YAML resolution) are untested"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No code coverage tracking"
    impact: "Impossible to measure or enforce test quality over time"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No linting or static analysis"
    impact: "Code quality drifts; type errors and style inconsistencies creep in"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI agents have no guidance for contributing to or using this test framework"
    severity: "LOW"
    effort: "2-3 hours"
quick_wins:
  - title: "Add a GitHub Actions lint + dry-run workflow"
    effort: "2-3 hours"
    impact: "Catches syntax errors, import issues, and config problems on every PR"
  - title: "Add ruff linting configuration"
    effort: "1-2 hours"
    impact: "Enforces consistent Python style and catches common errors"
  - title: "Add unit tests for env.py, clients.py, and pipeline_yaml_sources.py"
    effort: "4-6 hours"
    impact: "Validates the most-used library utilities that every test depends on"
  - title: "Add pre-commit hooks for formatting and linting"
    effort: "1 hour"
    impact: "Prevents style drift and catches issues before push"
recommendations:
  priority_0:
    - "Implement GitHub Actions CI workflow with lint, type-check, and dry-run validation on PRs"
    - "Add unit tests for the 10+ library modules in autox_tests/lib/ (clients, env, settings, s3_data, etc.)"
  priority_1:
    - "Configure ruff or flake8 for linting with pyproject.toml integration"
    - "Add mypy or pyright type checking (the codebase already uses type annotations extensively)"
    - "Set up codecov or coveralls for PR coverage reporting"
  priority_2:
    - "Create CLAUDE.md and .claude/rules/ for AI agent guidance"
    - "Add pre-commit hooks (ruff, mypy, trailing whitespace)"
    - "Consider adding a Makefile for common development tasks"
---

# Quality Analysis: autox-ci

## Executive Summary

- **Overall Score: 4.6/10**
- **Repository Type**: Python test harness / E2E test suite for AutoX components (AutoRAG, AutoML) on RHOAI
- **Primary Language**: Python 3.12+
- **Framework**: pytest + KFP + Kubernetes + S3 (boto3)
- **Agent Rules Status**: Missing

**Key Strengths**: The functional test suite itself is well-designed — parametrized positive/negative scenarios, JSON-driven test configs with tag-based filtering, comprehensive artifact validation (S3, notebooks, KServe deployment), excellent failure diagnostics (pod logs, task-level errors), and strong fixture architecture with session-scoped resource management and cleanup.

**Critical Gaps**: The repository has **zero CI/CD automation** — no GitHub Actions workflows, no linting, no type checking, no coverage tracking. The library code that powers all tests (~2,400 lines across 10+ modules) has no unit tests of its own. There are no agent rules for AI-assisted development.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1.0/10 | No unit tests for library code; repo is E2E-only |
| Integration/E2E | 8.0/10 | Strong parametrized functional tests with positive/negative paths |
| **Build Integration** | **1.0/10** | **No CI/CD workflows, no PR-time validation** |
| Image Testing | 0.0/10 | N/A — no container images in this repo |
| Coverage Tracking | 0.0/10 | No coverage config, no codecov, no thresholds |
| CI/CD Automation | 1.5/10 | Only PR template exists; no automated workflows |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude/ directory |

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: Tests never run automatically; broken test configs, syntax errors, and import failures merge freely. The test framework itself can regress without detection.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The `.github/workflows/` directory does not exist. There are no GitHub Actions, no GitLab CI, no Jenkinsfile, no Makefile. The only automation is `run_tests.sh`, a local shell wrapper.

### 2. No Unit Tests for Library Code
- **Impact**: The `autox_tests/lib/` directory contains ~2,400 lines of Python across 10+ modules (clients.py, env.py, settings.py, pipeline_yaml_sources.py, s3_data.py, rhoai_support.py, kfp_progress.py, etc.) with zero unit test coverage.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: Functions like `make_kfp_client()`, `load_tests_env()`, `resolve_precompiled_pipeline_yaml()`, `ensure_s3_bucket_exists()`, and `build_temp_kubeconfig()` are critical infrastructure that every test depends on. Bugs in these functions would cascade silently.

### 3. No Coverage Tracking
- **Impact**: No way to measure how much of the library code is exercised, enforce minimums, or track trends.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

### 4. No Linting or Static Analysis
- **Impact**: The codebase uses Python type annotations extensively (good), but there is no mypy/pyright configuration to validate them. No ruff, flake8, or pylint configuration exists.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

### 5. No Agent Rules
- **Impact**: AI agents contributing to this repo have no guidance on test patterns, fixture usage, JSON config schema, or the testing philosophy.
- **Severity**: LOW
- **Effort**: 2-3 hours

## Quick Wins

### 1. Add GitHub Actions CI Workflow (2-3 hours)
```yaml
name: CI
on: [pull_request]
jobs:
  lint-and-dry-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --extra test_autorag
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: ./run_tests.sh --dry-run "autorag and positive"
      - run: ./run_tests.sh --dry-run --suite automl "tabular"
```

### 2. Add Ruff Configuration (1-2 hours)
Add to `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### 3. Add Pre-commit Hooks (1 hour)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
      - id: ruff-format
```

### 4. Add Unit Tests for Core Library Modules (4-6 hours)
Start with:
- `test_env.py` — test `load_tests_env()` and path resolution
- `test_pipeline_yaml_sources.py` — test URL construction and local path resolution
- `test_clients.py` — test client creation with mock configs

## Detailed Findings

### CI/CD Pipeline
- **Workflows**: None (`.github/workflows/` does not exist)
- **PR Template**: Good — `pull_request_template.md` has structured sections and a checklist
- **Test Runner**: `run_tests.sh` is well-designed with `--dry-run`, `--suite`, `--tags`, and `--extras` support
- **Verdict**: The PR template and test runner are good, but without CI nothing runs automatically

### Test Coverage
- **Functional Tests**: 3 test files with parametrized positive and negative scenarios
  - `autorag/test_pipeline_functional.py` — 2 positive + 3 negative AutoRAG scenarios
  - `automl/test_tabular_functional.py` — 3 positive + 6 negative tabular scenarios
  - `automl/test_timeseries_functional.py` — 2 positive + 5 negative timeseries scenarios
- **Test Configs**: JSON-driven (`test_configs.json`, `tabular_test_configs.json`, `timeseries_test_configs.json`)
- **Tag Filtering**: Supports `smoke`, `negative`, `validation`, `storage`, `credentials` tags
- **Artifact Validation**: Comprehensive S3 artifact checks (patterns, notebooks, leaderboard, metrics)
- **Notebook Execution**: Downloads and runs indexing/inference notebooks via papermill
- **Deployment Testing**: Optional KServe InferenceService creation, readiness wait, and v1/v2 scoring
- **Failure Diagnostics**: Pod log fetching, task-level error extraction, formatted reports
- **Unit Tests**: None — the library code powering all of this is untested
- **Coverage**: No `.coveragerc`, no `codecov.yml`, no coverage generation

### Code Quality
- **Linting**: No `.golangci.yaml`, no `ruff.toml`, no `flake8`, no `mypy.ini`
- **Pre-commit**: No `.pre-commit-config.yaml`
- **Type Annotations**: The codebase uses Python 3.12+ type annotations extensively (`str | None`, `list[str]`, `dict[str, Any]`), but there's no mypy/pyright to validate them
- **Code Organization**: Clean separation between test suites (autorag, automl), shared lib, and configs
- **Docstrings**: Thorough module and function docstrings throughout

### Container Images
- **Dockerfiles**: None — this is a pure test harness, not an application
- **Image Testing**: N/A
- **Scoring Note**: The 0.0 score for Image Testing reflects absence but is not a deficiency for this repo type

### Security
- **Container Scanning**: None (N/A)
- **SAST**: No CodeQL, gosec, Semgrep
- **Dependency Scanning**: No automated dependency scanning
- **Secret Detection**: `.gitignore` properly excludes `.env` files; env examples don't contain secrets
- **TLS Handling**: Test code properly supports configurable TLS verification and CA bundles

### Agent Rules (Agentic Flow Quality)
- **Status**: Missing
- **CLAUDE.md**: Not present
- **.claude/ directory**: Not present
- **Rules Coverage**: No rules for any test type
- **Recommendation**: Create rules covering test config JSON schema, fixture usage patterns, negative test design, and library utility conventions. Use `/test-rules-generator` to bootstrap.

## Recommendations

### Priority 0 (Critical)
1. **Implement GitHub Actions CI workflow** — At minimum: lint, format-check, dry-run validation, and JSON config schema validation on every PR
2. **Add unit tests for library modules** — Start with `env.py`, `clients.py`, `pipeline_yaml_sources.py`, `s3_data.py`, and config loaders. These are the foundation everything else depends on.

### Priority 1 (High Value)
3. **Configure ruff for linting** — Add `[tool.ruff]` section to `pyproject.toml`; integrate into CI
4. **Add mypy or pyright type checking** — The codebase already has extensive type annotations; validating them is low-effort/high-value
5. **Set up coverage tracking** — Add `pytest-cov` and `codecov.yml`; report coverage on PRs
6. **Add pre-commit hooks** — Enforce formatting and linting before push

### Priority 2 (Nice-to-Have)
7. **Create agent rules** — Add `CLAUDE.md` and `.claude/rules/` to guide AI-assisted development
8. **Add a Makefile** — Common targets: `lint`, `format`, `test-dry-run`, `test-unit`
9. **Add JSON schema validation for test configs** — Validate `*_test_configs.json` files against a JSON Schema to prevent malformed configs
10. **Consider adding contract tests** — Validate the JSON config schema that downstream repos provide when using autox-ci as a submodule

## Comparison to Gold Standards

| Dimension | autox-ci | odh-dashboard | notebooks | kserve |
|-----------|----------|---------------|-----------|--------|
| Unit Tests | 1.0 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 8.0 | 9.0 | 8.0 | 9.0 |
| Build Integration | 1.0 | 8.0 | 7.0 | 8.0 |
| Image Testing | 0.0 | 7.0 | 9.0 | 7.0 |
| Coverage Tracking | 0.0 | 8.0 | 5.0 | 9.0 |
| CI/CD Automation | 1.5 | 9.0 | 8.0 | 9.0 |
| Agent Rules | 0.0 | 8.0 | 3.0 | 2.0 |
| **Overall** | **4.6** | **8.5** | **7.0** | **8.0** |

**Key Gap vs Gold Standards**: The biggest differentiator is CI/CD automation. Gold standard repos have comprehensive GitHub Actions workflows that run lint, type-check, unit tests, and integration tests on every PR. autox-ci has none of this infrastructure despite having a mature functional test suite.

## File Paths Reference

| File | Purpose |
|------|---------|
| `pyproject.toml` | Dependencies, pytest markers, extras |
| `run_tests.sh` | Test runner wrapper (uv + pytest) |
| `autox_tests/autorag/test_pipeline_functional.py` | AutoRAG functional tests |
| `autox_tests/automl/test_tabular_functional.py` | Tabular AutoML functional tests |
| `autox_tests/automl/test_timeseries_functional.py` | Timeseries AutoML functional tests |
| `autox_tests/autorag/configs/test_configs.json` | AutoRAG test scenarios (5 configs) |
| `autox_tests/automl/configs/tabular_test_configs.json` | Tabular scenarios (9 configs) |
| `autox_tests/automl/configs/timeseries_test_configs.json` | Timeseries scenarios (7 configs) |
| `autox_tests/lib/clients.py` | KFP and S3 client factories |
| `autox_tests/lib/env.py` | .env file loading |
| `autox_tests/lib/settings.py` | Environment-driven settings |
| `autox_tests/lib/pipeline_yaml_sources.py` | Pipeline YAML resolution (local/URL) |
| `autox_tests/lib/s3_data.py` | S3 upload helpers |
| `autox_tests/lib/rhoai_support.py` | OpenShift namespace/secret setup |
| `autox_tests/lib/kfp_progress.py` | KFP run progress polling |
| `.github/pull_request_template.md` | PR template with checklist |
| `autox_tests/.env.rag.example` | AutoRAG env template |
| `autox_tests/.env.ml.example` | AutoML env template |
