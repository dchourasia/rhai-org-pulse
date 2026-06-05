---
repository: "red-hat-data-services/gpu-observability-dashboard"
overall_score: 1.2
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist. Zero test coverage for 1,512-line application."
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests. No test infrastructure of any kind."
  - dimension: "Build Integration"
    score: 0.0
    status: "No CI/CD pipeline. No PR validation. No build automation."
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfile or Containerfile. No container image build process."
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tool integration. No codecov, coveralls, or pytest-cov."
  - dimension: "CI/CD Automation"
    score: 0.0
    status: "No GitHub Actions workflows. No CI/CD configuration of any kind."
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, .claude/ directory, or agent rules present."
critical_gaps:
  - title: "No test suite of any kind"
    impact: "Every code change is deployed without validation. Regressions are invisible until users report them."
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No CI/CD pipeline"
    impact: "No automated quality gates. PRs merge without any checks — no lint, no test, no build verification."
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No container image or deployment config"
    impact: "No reproducible deployment. Manual setup required on every target environment."
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No code quality tooling (linting, formatting, type checking)"
    impact: "Code style inconsistencies accumulate. Python type errors go undetected. No automated code review."
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No security scanning"
    impact: "Dependency vulnerabilities (streamlit, plotly, pandas, numpy) are never checked. No secret detection."
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Single-file monolith architecture"
    impact: "1,512 lines in one file makes testing, maintenance, and collaboration difficult. Functions are tightly coupled."
    severity: "MEDIUM"
    effort: "8-12 hours"
quick_wins:
  - title: "Add a basic GitHub Actions CI workflow with linting"
    effort: "2-3 hours"
    impact: "Immediate quality gate on all PRs. Catches syntax errors, import issues, and style violations."
  - title: "Add ruff for linting and formatting"
    effort: "1 hour"
    impact: "Automated code quality enforcement. Ruff is fast and covers flake8 + isort + pyupgrade in one tool."
  - title: "Add a Dockerfile for containerized deployment"
    effort: "1-2 hours"
    impact: "Reproducible deployment. Enables container scanning. Required for production/OpenShift deployment."
  - title: "Add pytest with basic smoke tests for data generation functions"
    effort: "3-4 hours"
    impact: "Covers the core data logic. generate_all_gpu_data(), generate_30day_timeseries(), generate_hourly_usage_patterns() are pure functions — easy to test."
  - title: "Pin dependency versions in requirements.txt"
    effort: "30 minutes"
    impact: "Prevents surprise breakage from upstream dependency updates. Currently all versions use >= (minimum floor only)."
recommendations:
  priority_0:
    - "Add a GitHub Actions CI workflow that runs on PRs with at minimum: Python syntax check, ruff lint, and dependency install verification"
    - "Create a basic pytest test suite covering the three data generation functions (pure functions, deterministic with seed — ideal test targets)"
    - "Add a Dockerfile so the app can be containerized and deployed to OpenShift or any container platform"
  priority_1:
    - "Add ruff.toml with a comprehensive rule set and integrate into CI"
    - "Add mypy or pyright for static type checking — app.py has no type annotations"
    - "Add Trivy or Snyk scanning for dependency vulnerabilities in CI"
    - "Add pre-commit hooks (.pre-commit-config.yaml) for local quality enforcement"
    - "Refactor app.py into modules: data generation, visualization functions, and Streamlit layout"
  priority_2:
    - "Add Selenium or Playwright-based E2E tests for the Streamlit dashboard"
    - "Add codecov integration with a coverage threshold (e.g., 60% minimum)"
    - "Create agent rules (.claude/rules/) for test patterns and code standards"
    - "Add CODEOWNERS file for PR review assignment"
    - "Add dependabot.yml for automated dependency updates"
---

# Quality Analysis: gpu-observability-dashboard

## Executive Summary

- **Overall Score: 1.2/10**
- **Repository Type**: Python Streamlit web application (single-file dashboard)
- **Primary Language**: Python (1,512 lines)
- **Key Strengths**: Good README documentation, clean .gitignore with PII protection, well-structured simulated data functions
- **Critical Gaps**: No tests, no CI/CD, no container image, no linting, no security scanning — essentially zero quality infrastructure
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

This repository is in its earliest stage. It contains a functional Streamlit dashboard for GPU observability with simulated data, but has **no quality practices** in place. Every dimension scores 0/10. The application code itself is reasonably well-structured (functions are separated, caching is used, data generation is deterministic with seeds), which makes it a good candidate for rapid quality improvement — the functions are already testable.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist anywhere in the repository |
| Integration/E2E | 0/10 | No integration or E2E test infrastructure |
| **Build Integration** | **0/10** | **No CI/CD pipeline, no PR validation** |
| Image Testing | 0/10 | No Dockerfile or container config exists |
| Coverage Tracking | 0/10 | No coverage tooling or reporting |
| CI/CD Automation | 0/10 | No GitHub Actions, no workflows at all |
| Agent Rules | 0/10 | No CLAUDE.md or .claude/ directory |

**Weighted Overall: 1.2/10** (bonus for documentation quality and code structure)

## Critical Gaps

### 1. No Test Suite of Any Kind
- **Impact**: Every code change merges without validation. The three data generation functions (`generate_all_gpu_data`, `generate_30day_timeseries`, `generate_hourly_usage_patterns`) use `np.random.seed()` making them deterministic — ideal for unit testing but completely untested.
- **Severity**: HIGH
- **Effort**: 8-16 hours for initial test suite
- **Example**: A change to GPU type weights could silently break all downstream visualizations with no detection.

### 2. No CI/CD Pipeline
- **Impact**: PRs merge without any automated checks. No lint, test, build, or security gates.
- **Severity**: HIGH
- **Effort**: 4-8 hours to set up GitHub Actions
- **Example**: A syntax error in `app.py` would only be discovered when someone runs the app locally.

### 3. No Container Image or Deployment Configuration
- **Impact**: No reproducible deployment path. Manual `pip install` + `streamlit run` is the only option. Cannot deploy to OpenShift, Kubernetes, or any container platform.
- **Severity**: HIGH
- **Effort**: 4-6 hours for Dockerfile + basic container testing
- **Risk**: Production deployment blocked until containerized.

### 4. No Code Quality Tooling
- **Impact**: No linting (ruff/flake8), no formatting (black/ruff format), no type checking (mypy/pyright), no pre-commit hooks. Code quality relies entirely on manual review.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Observation**: `app.py` has zero type annotations across 1,512 lines. Functions like `generate_all_gpu_data()` return `pd.DataFrame` but this isn't declared.

### 5. No Security Scanning
- **Impact**: Dependencies (`streamlit>=1.30.0`, `plotly>=5.18.0`, `pandas>=2.0.0`, `numpy>=1.24.0`) are never scanned for CVEs. No secret detection despite `.gitignore` mentioning `.env` and `.secret` files.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours to add Trivy + dependabot

### 6. Single-File Monolith (1,512 lines)
- **Impact**: All data generation, visualization functions (~15 plot functions), and Streamlit layout logic in one file. Difficult to test individual components, collaborate on, or maintain.
- **Severity**: MEDIUM
- **Effort**: 8-12 hours to refactor into modules

## Quick Wins

### 1. Add GitHub Actions CI Workflow (2-3 hours)
**Impact**: Immediate quality gate on all PRs.

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pip install ruff pytest
      - run: ruff check .
      - run: ruff format --check .
      - run: python -c "import app; print('Import OK')"
      # - run: pytest tests/ -v  # Uncomment after adding tests
```

### 2. Add Ruff Linting (1 hour)
**Impact**: Fast, comprehensive Python linting.

```toml
# ruff.toml
target-version = "py310"
line-length = 120

[lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "RUF"]

[lint.isort]
known-first-party = ["app"]
```

### 3. Add a Dockerfile (1-2 hours)
**Impact**: Containerized deployment, enables image scanning.

```dockerfile
FROM registry.access.redhat.com/ubi9/python-311:latest

WORKDIR /opt/app-root/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 4. Add Basic pytest Tests (3-4 hours)
**Impact**: Validates core data generation logic.

```python
# tests/test_data_generation.py
import pandas as pd
from app import generate_all_gpu_data, generate_30day_timeseries, generate_hourly_usage_patterns

def test_generate_all_gpu_data_returns_dataframe():
    df = generate_all_gpu_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_generate_all_gpu_data_has_required_columns():
    df = generate_all_gpu_data()
    required = {"cloud", "gpu_type", "team", "workload_type", "total_gpus",
                "allocated_gpus", "used_pct", "utilization_pct", "idle_pct"}
    assert required.issubset(set(df.columns))

def test_generate_all_gpu_data_deterministic():
    df1 = generate_all_gpu_data()
    df2 = generate_all_gpu_data()
    pd.testing.assert_frame_equal(df1, df2)

def test_generate_all_gpu_data_valid_ranges():
    df = generate_all_gpu_data()
    assert (df["used_pct"] >= 0).all() and (df["used_pct"] <= 100).all()
    assert (df["utilization_pct"] >= 0).all() and (df["utilization_pct"] <= 100).all()
    assert (df["idle_pct"] >= 0).all() and (df["idle_pct"] <= 100).all()
    assert (df["total_gpus"] > 0).all()
    assert (df["allocated_gpus"] >= 0).all()

def test_generate_30day_timeseries_has_31_days():
    df = generate_30day_timeseries()
    assert len(df["date"].unique()) == 31  # 30-day range inclusive

def test_generate_hourly_usage_patterns_coverage():
    df = generate_hourly_usage_patterns()
    assert set(df["day_of_week"].unique()) == set(range(7))
    assert set(df["hour"].unique()) == set(range(24))
```

### 5. Pin Dependency Versions (30 minutes)
**Impact**: Reproducible builds.

```txt
# requirements.txt (pinned)
streamlit==1.45.0
pandas==2.2.3
numpy==2.2.6
plotly==6.1.1
```

## Detailed Findings

### CI/CD Pipeline

**Status: Non-existent**

- No `.github/workflows/` directory
- No Makefile
- No `.gitlab-ci.yml`
- No Jenkinsfile
- No CI/CD configuration of any kind

The repository has 2 commits total (initial commit + README PR merge). There is no evidence any CI/CD was ever planned or configured.

### Test Coverage

**Status: Zero**

- No `test_*.py` or `*_test.py` files
- No `tests/` or `test/` directory
- No `pytest.ini`, `pyproject.toml`, or `setup.cfg` with test configuration
- No `conftest.py`
- No testing dependencies in `requirements.txt`

**Positive note**: The three data generation functions are deterministic (use `np.random.seed()`) and return `pd.DataFrame` objects — they are ideal candidates for unit testing without any mocking needed.

### Code Quality

**Status: No tooling**

- No `.flake8`, `ruff.toml`, or `.pylintrc`
- No `mypy.ini` or `pyrightconfig.json`
- No `.pre-commit-config.yaml`
- No `pyproject.toml` for tool configuration
- No type annotations in the codebase

**Code observations**:
- Functions are well-named and documented with docstrings
- Constants are defined at module level (PLOTLY_TEMPLATE, CLOUD_COLORS)
- Streamlit caching (`@st.cache_data`) is correctly applied
- Code uses f-strings consistently
- No obvious security issues in the simulated data code

### Container Images

**Status: Non-existent**

- No Dockerfile or Containerfile
- No docker-compose.yml
- No `.dockerignore`
- No container build or test workflow
- No multi-architecture support
- No SBOM generation
- No image signing

### Security

**Status: Minimal**

- **Positive**: `.gitignore` excludes `.env`, `*.secret`, `*.token`, `*.local` files
- No dependency scanning (no Trivy, Snyk, or Dependabot)
- No SAST tools (no CodeQL, Bandit, or Semgrep)
- No secret detection (no Gitleaks or TruffleHog)
- Dependencies use minimum version floors (`>=`) rather than pinned versions — vulnerable to supply chain attacks via dependency confusion

### Agent Rules (Agentic Flow Quality)

**Status: Missing**

- No `CLAUDE.md` in repository root
- No `AGENTS.md`
- No `.claude/` directory
- No `.claude/rules/` for test creation guidance
- No `.claude/skills/` for custom skills
- No testing documentation in `docs/`

**Recommendation**: Use `/test-rules-generator` to create comprehensive agent rules for:
- Unit test patterns for Streamlit data functions
- Visualization function testing guidelines
- Integration test patterns for Streamlit apps

## Recommendations

### Priority 0 (Critical — Do These First)

1. **Add a GitHub Actions CI workflow** that runs on PRs with: Python syntax check, ruff lint, dependency install verification, and eventually pytest
2. **Create a pytest test suite** covering the three data generation functions — they're deterministic pure functions, perfect test targets
3. **Add a Dockerfile** for containerized deployment to OpenShift or any platform
4. **Pin dependency versions** in requirements.txt to prevent supply chain issues

### Priority 1 (High Value — Do These Next)

1. **Add ruff.toml** with comprehensive rules and integrate into CI
2. **Add mypy** for static type checking — add type annotations to function signatures
3. **Add Trivy scanning** in CI for dependency vulnerabilities
4. **Add pre-commit hooks** for local development quality enforcement
5. **Refactor app.py** into modules: `data/`, `charts/`, `layout/` to improve testability

### Priority 2 (Nice-to-Have — Longer Term)

1. **Add Selenium/Playwright E2E tests** for the Streamlit dashboard UI
2. **Add codecov integration** with a coverage threshold
3. **Create agent rules** (`.claude/rules/`) for test patterns and code standards
4. **Add CODEOWNERS** for PR review assignment
5. **Add dependabot.yml** for automated dependency updates
6. **Add performance benchmarks** for data generation functions (important if connecting to real Prometheus)

## Comparison to Gold Standards

| Capability | gpu-observability-dashboard | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|---|---|---|---|---|
| Unit Tests | None | Jest + React Testing Library | pytest | Go testing + envtest |
| Integration/E2E | None | Cypress E2E + contract tests | 5-layer image validation | Multi-version E2E |
| CI/CD | None | 15+ GitHub Actions workflows | Automated image pipelines | Comprehensive PR checks |
| Coverage | None | Codecov with thresholds | Per-notebook tracking | 80%+ enforcement |
| Linting | None | ESLint + Prettier + strict TS | Ruff + mypy | golangci-lint (20+ linters) |
| Container | None | Multi-stage Dockerfile | Multi-arch builds + scanning | Distroless images |
| Security | .gitignore only | CodeQL + Snyk + secret scanning | Trivy + SBOM | Multiple SAST tools |
| Agent Rules | None | Comprehensive .claude/rules/ | Basic rules | N/A |
| Pre-commit | None | Husky + lint-staged | pre-commit hooks | pre-commit hooks |
| Dependency Mgmt | >= floors only | Dependabot + lockfile | Pinned + Dependabot | go.sum + Dependabot |

## File Paths Reference

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Entire application — data, charts, layout | 1,512 |
| `requirements.txt` | Python dependencies (4 packages, unpinned) | 4 |
| `README.md` | Comprehensive documentation | 709 |
| `SETUP.md` | Quick setup guide | 52 |
| `GITHUB_SETUP.md` | GitHub repo creation guide | 62 |
| `.gitignore` | Python/IDE/PII exclusions | 30 |

**Notable absent files**: No tests, no CI config, no Dockerfile, no linting config, no type checking config, no pre-commit hooks, no agent rules.
