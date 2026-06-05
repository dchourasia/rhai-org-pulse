---
repository: "opendatahub-io/perf_analyzer"
overall_score: 3.5
scorecard:
  - dimension: "Unit Tests"
    score: 6.5
    status: "Substantial C++ (doctest) and Python (pytest) test suites, but C++ tests not run in GitHub CI"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Only 2 Python integration tests, no E2E tests against actual Triton server"
  - dimension: "Build Integration"
    score: 2.0
    status: "C++ build not validated in GitHub CI; relies on opaque external GitLab pipeline"
  - dimension: "Image Testing"
    score: 1.0
    status: "No Dockerfile, no container builds, no image validation or scanning"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "Coverage generated in CI but never uploaded or enforced; no thresholds"
  - dimension: "CI/CD Automation"
    score: 4.5
    status: "Pre-commit hooks are strong; but no caching, single Python version, C++ CI externalized"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no AI agent test guidance"
critical_gaps:
  - title: "C++ tests not executed in GitHub CI"
    impact: "Contributors cannot see C++ test results on PRs; regressions discovered only after GitLab mirror pipeline runs"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "Coverage generated but never uploaded or enforced"
    impact: "No visibility into coverage trends; PRs can silently reduce coverage with no gate"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No E2E tests in the repository"
    impact: "Integration with Triton Inference Server is never validated before merge"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "No container image testing or Dockerfile"
    impact: "Downstream consumers (ODH, Triton SDK) discover build/packaging issues only at their level"
    severity: "MEDIUM"
    effort: "8-16 hours"
  - title: "External GitLab CI is opaque to contributors"
    impact: "Open-source contributors cannot debug CI failures or understand what tests run"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "CodeQL scans Python only, not C++"
    impact: "C++ code (the core analyzer) has no SAST coverage for memory safety, buffer overflows, etc."
    severity: "HIGH"
    effort: "2-4 hours"
quick_wins:
  - title: "Upload coverage to Codecov"
    effort: "2-3 hours"
    impact: "Instant visibility into coverage trends and PR-level coverage diffs"
  - title: "Enable CodeQL for C++ alongside Python"
    effort: "1-2 hours"
    impact: "Catch memory safety issues, buffer overflows, and security vulnerabilities in core C++ code"
  - title: "Add Dependabot for dependency scanning"
    effort: "1 hour"
    impact: "Automated alerts for known vulnerabilities in Python and CMake dependencies"
  - title: "Add concurrency control to workflows"
    effort: "30 minutes"
    impact: "Prevent duplicate CI runs on rapid push sequences"
  - title: "Create basic CLAUDE.md with test patterns"
    effort: "2-3 hours"
    impact: "Improve AI-generated code quality and test consistency"
recommendations:
  priority_0:
    - "Upload pytest coverage reports to Codecov and set minimum thresholds (e.g., 70%)"
    - "Enable CodeQL for C++ in addition to Python to catch memory safety bugs"
    - "Document what the external GitLab CI pipeline tests so contributors understand the full test matrix"
  priority_1:
    - "Add a lightweight CMake build step to GitHub CI (even without GPU) to validate C++ compilation"
    - "Expand Python test matrix to include Python 3.11 and 3.12"
    - "Create E2E test infrastructure using containerized Triton server for smoke tests"
    - "Add Dependabot configuration for automated dependency vulnerability scanning"
  priority_2:
    - "Create CLAUDE.md and .claude/rules/ for AI agent test automation guidance"
    - "Add Trivy or Snyk scanning for dependency vulnerabilities"
    - "Introduce performance regression testing to detect throughput/latency changes between versions"
    - "Add secret detection (gitleaks) to pre-commit hooks and CI"
---

# Quality Analysis: opendatahub-io/perf_analyzer

## Executive Summary

- **Overall Score: 3.5/10**
- **Repository Type**: CLI tool — Triton Performance Analyzer (C++) + GenAI-Perf (Python)
- **Primary Languages**: C++ (core analyzer), Python (genai-perf CLI wrapper)
- **Build Systems**: CMake (C++), Hatchling/setuptools (Python)
- **Key Strengths**: Comprehensive pre-commit hooks, decent unit test coverage for both C++ and Python, well-organized test structure
- **Critical Gaps**: C++ tests invisible in GitHub CI, no coverage enforcement, no E2E tests, no container/image testing, external CI is opaque
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6.5/10 | Substantial C++ (doctest/gmock) and Python (pytest) suites |
| Integration/E2E | 3.0/10 | Only 2 Python integration tests, no E2E |
| **Build Integration** | **2.0/10** | **C++ build not validated in GitHub CI** |
| Image Testing | 1.0/10 | No Dockerfile, no container builds or scanning |
| Coverage Tracking | 2.0/10 | Generated but never uploaded or enforced |
| CI/CD Automation | 4.5/10 | Good pre-commit; weak CI matrix, opaque external pipeline |
| Agent Rules | 0.0/10 | No AI agent guidance exists |

## Critical Gaps

### 1. C++ Tests Not Executed in GitHub CI
- **Impact**: Contributors cannot see C++ test results on PRs; regressions are only caught after the GitLab mirror pipeline runs
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Detail**: The C++ test suite (`perf_analyzer_unit_tests`) is built via CMake with doctest/Google Mock but requires Triton client libraries and potentially CUDA. Only the `trigger_ci.yml` workflow mirrors to GitLab and triggers an external pipeline — the results are not visible on the GitHub PR.

### 2. Coverage Generated but Never Uploaded or Enforced
- **Impact**: No visibility into coverage trends; PRs can silently reduce coverage with zero enforcement
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Detail**: `python-package-genai.yml` generates `--cov-report=xml` output but never uploads it to Codecov, Coveralls, or any service. No `.codecov.yml` exists. No coverage thresholds are configured.

### 3. No E2E Tests Against Triton Server
- **Impact**: The core functionality — profiling models on Triton Inference Server — is never validated end-to-end before merge
- **Severity**: HIGH
- **Effort**: 20-40 hours
- **Detail**: For a performance benchmarking tool, the absence of E2E tests that actually connect to a Triton server instance (even a mock/minimal one) is a significant gap. The 2 "integration" tests in `genai-perf/tests/integration_tests/` are actually mock-based and don't require a running server.

### 4. CodeQL Only Scans Python, Not C++
- **Impact**: The core C++ code handling network I/O, memory management, and data parsing has no static analysis
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Detail**: `codeql.yml` explicitly sets `matrix.language: ['python']` with C++ commented out. For a C++ codebase that handles raw data, HTTP connections, and gRPC, this is a significant security gap.

### 5. External GitLab CI is Opaque
- **Impact**: Open-source contributors cannot see or debug CI results; NVIDIA-internal pipeline results are not surfaced on GitHub PRs
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Detail**: `trigger_ci.yml` mirrors the repo to GitLab and triggers a pipeline via `curl`, but results are never posted back to the GitHub PR. Contributors must wait for NVIDIA maintainers to report pass/fail.

## Quick Wins

### 1. Upload Coverage to Codecov (2-3 hours)
```yaml
# Add to python-package-genai.yml after pytest step:
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: genai-perf/tests/coverage.xml
    fail_ci_if_error: true
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 2. Enable CodeQL for C++ (1-2 hours)
```yaml
# In codeql.yml, change:
matrix:
  language: ['python', 'cpp']
```

### 3. Add Dependabot (1 hour)
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/genai-perf"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 4. Add Concurrency Control (30 minutes)
```yaml
# Add to each workflow:
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (4 workflows, all PR-triggered):**

| Workflow | Trigger | Purpose | Issues |
|----------|---------|---------|--------|
| `codeql.yml` | PR | SAST scanning (Python only) | Doesn't scan C++ |
| `pre-commit.yml` | PR | Code formatting/linting | Good — runs on modified files only |
| `python-package-genai.yml` | PR | Python tests + coverage | Single version (3.10), coverage not uploaded |
| `trigger_ci.yml` | PR (non-docs) | Mirror to GitLab, trigger external CI | Results opaque to contributors |

**Missing CI capabilities:**
- No concurrency control on any workflow
- No caching (pip, CMake builds)
- No workflow status badges
- No release automation
- No nightly/periodic jobs
- Python tests only on Ubuntu 22.04 with Python 3.10 (no matrix)

### Test Coverage

**C++ Test Suite:**
- **Framework**: doctest (lightweight) + Google Mock
- **Test files**: 23 (12,409 lines of test code)
- **Mock files**: 12 (well-structured mock objects)
- **Source files**: 133 (18,938 lines)
- **Test-to-code ratio**: 0.66 (decent)
- **Key test areas**: Command line parser, concurrency manager, data loader, HTTP client, inference profiler, metrics manager, model parser, report writer, request rate manager, sequence manager
- **Build**: Compiled as `perf_analyzer_unit_tests` via CMake with Google Test/Mock
- **NOT run in GitHub CI** — only via external GitLab pipeline

**Python Test Suite (genai-perf):**
- **Framework**: pytest with pytest-mock, pytest-cov
- **Test files**: 65 (17,232 lines)
- **Source files**: ~600 (33,400 lines)
- **Test-to-code ratio**: 0.52 (moderate)
- **Organization**: Well-structured subdirectories:
  - `test_converters/` (11 files) — output format converters
  - `test_data_parser/` (4 files) — profile data parsing
  - `test_exporters/` (5 files) — data export formats
  - `test_metrics/` (4 files) — telemetry metrics
  - `test_retrievers/` (6 files) — data retrieval
  - `test_statistics/` (2 files) — statistical analysis
  - `test_collectors/` — data collectors
  - `integration_tests/` (2 files) — mock-based integration
- **Coverage**: Generated as XML and HTML in CI, but never uploaded

**Integration Tests:**
- Only 2 files: `test_multiturn.py` and `test_telemetry.py`
- These use mocks (`unittest.mock`) and don't require a running Triton server
- More accurately "component integration tests" than true integration tests

**E2E Tests:** None

### Code Quality

**Pre-commit Hooks (Strong — 8 hooks):**

| Hook | Purpose | Status |
|------|---------|--------|
| isort | Python import sorting | Active |
| black | Python code formatting | Active |
| flake8 | Python linting | Active |
| clang-format | C/C++ formatting | Active |
| codespell | Spell checking | Active |
| mypy | Python type checking | Active |
| pre-commit-hooks | General checks (merge conflicts, trailing whitespace, etc.) | Active |
| add-license | Custom copyright header checker | Active |

**Additional tooling:**
- Ruff configured in `genai-perf/pyproject.toml` (minimal — line-length/indent-width only)
- CodeQL for Python SAST (no C++ scanning)
- No Dependabot or Renovate for dependency updates

**Gaps:**
- No golangci-lint equivalent for C++ beyond clang-format
- No cppcheck, clang-tidy, or similar static analysis
- No secret detection (gitleaks/trufflehog)

### Container Images

- **No Dockerfile or Containerfile** in the repository
- **DevContainer** provided for development with NVIDIA Triton base image (`gitlab-master.nvidia.com:5005/dl/dgx/tritonserver:master-py3-base`)
- The C++ binary is built externally and packaged into Triton SDK containers
- **No container scanning, SBOM generation, or image signing** at this level

### Security

| Practice | Status | Detail |
|----------|--------|--------|
| CodeQL (SAST) | Partial | Python only, C++ excluded |
| Dependency scanning | Missing | No Dependabot/Renovate/Snyk |
| Secret detection | Missing | No gitleaks or TruffleHog |
| Container scanning | N/A | No containers built in this repo |
| SBOM generation | Missing | No SBOM tooling |
| License compliance | Good | Pre-commit hook for copyright headers |
| Outdated actions | Present | Uses `actions/checkout@v3` (latest is v4) and `codeql-action@v2` (latest is v3) |

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test types have rules
- **Quality**: N/A
- **Gaps**:
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory
  - No `.claude/rules/` for test creation guidance
  - No `.claude/skills/` for custom workflows
  - No testing documentation for AI agents
- **Recommendation**: Generate rules with `/test-rules-generator` covering:
  - C++ unit test patterns (doctest + Google Mock)
  - Python unit test patterns (pytest + pytest-mock)
  - Integration test patterns for genai-perf
  - CMake build and test configuration patterns

## Recommendations

### Priority 0 (Critical)

1. **Upload pytest coverage to Codecov** — Add codecov-action to `python-package-genai.yml` and set a minimum threshold (start at current level, ratchet up). This is a 2-3 hour fix with immediate ROI.

2. **Enable CodeQL for C++** — Change the language matrix to include `cpp`. The C++ codebase handles network I/O, memory buffers, and data serialization — all high-risk areas for security bugs.

3. **Document the GitLab CI pipeline** — At minimum, add a `CONTRIBUTING.md` section explaining what the external pipeline tests and how to interpret results. Ideally, post pipeline status back to GitHub PRs via the GitHub commit status API.

### Priority 1 (High Value)

4. **Add CMake build validation to GitHub CI** — Even without GPU/Triton libraries, a no-GPU build compilation check would catch syntax errors and missing includes before they hit the GitLab pipeline. Use a container with prebuilt Triton client libs.

5. **Expand Python test matrix** — Test against Python 3.10, 3.11, and 3.12. The current single-version testing misses compatibility issues.

6. **Create E2E test infrastructure** — Use a minimal Triton server container (CPU-only) to run smoke tests that validate the perf_analyzer CLI can connect, profile, and report results.

7. **Add Dependabot** — Enable automated dependency vulnerability scanning for both Python (pip) and GitHub Actions.

### Priority 2 (Nice-to-Have)

8. **Create CLAUDE.md and agent rules** — Add `.claude/rules/` with test patterns for both C++ (doctest/gmock) and Python (pytest) to improve AI-generated code quality.

9. **Add static analysis for C++** — Integrate cppcheck or clang-tidy into the pre-commit hooks or CI pipeline.

10. **Add secret detection** — Include gitleaks in pre-commit hooks to prevent accidental credential commits.

11. **Performance regression testing** — For a performance benchmarking tool, regression testing of the tool's own performance characteristics would be valuable.

12. **Update GitHub Actions versions** — Migrate from `actions/checkout@v3` to `v4`, `codeql-action@v2` to `v3`, etc.

## Comparison to Gold Standards

| Capability | perf_analyzer | odh-dashboard | notebooks | kserve |
|------------|--------------|---------------|-----------|--------|
| Unit tests | Moderate (C++ + Python) | Comprehensive (Jest + Cypress) | Moderate | Strong (Go) |
| Integration tests | Minimal (2 mock-based) | Contract tests, API tests | Image startup tests | envtest-based |
| E2E tests | None | Cypress E2E suite | Multi-image validation | Multi-version E2E |
| Coverage tracking | Generated, not uploaded | Codecov enforced | Basic | Codecov enforced |
| Coverage threshold | None | Yes (ratchet) | None | Yes |
| Container testing | None | Build validation | 5-layer image testing | Build + deploy |
| Security scanning | CodeQL (Python only) | CodeQL + Trivy | Trivy | CodeQL + Trivy |
| Dependency scanning | None | Dependabot + Renovate | Dependabot | Dependabot |
| Pre-commit hooks | Strong (8 hooks) | Moderate | Minimal | Moderate |
| CI concurrency | None | Controlled | Controlled | Controlled |
| Agent rules | None | Comprehensive | None | Partial |
| Multi-version testing | None | Multi-browser | Multi-Python | Multi-K8s |

## File Paths Reference

### CI/CD Configuration
- `.github/workflows/codeql.yml` — CodeQL SAST (Python only)
- `.github/workflows/pre-commit.yml` — Pre-commit hook enforcement
- `.github/workflows/python-package-genai.yml` — Python tests + coverage
- `.github/workflows/trigger_ci.yml` — GitLab mirror + external CI trigger
- `.github/workflows/mirror_repo.sh` — GitLab mirror sync script

### Build Configuration
- `CMakeLists.txt` — Root CMake config
- `src/CMakeLists.txt` — Core C++ build + unit test target
- `pyproject.toml` — Root Python package config (perf-analyzer)
- `genai-perf/pyproject.toml` — GenAI-Perf Python package config

### Test Files
- `src/test_*.cc` — 23 C++ unit test files (doctest + gmock)
- `src/mock_*.h` — 12 C++ mock objects
- `src/perf_analyzer_unit_tests.cc` — C++ test runner entry point
- `genai-perf/tests/` — 65 Python test files (pytest)
- `genai-perf/tests/integration_tests/` — 2 integration test files
- `genai-perf/pytest.ini` — Pytest configuration

### Code Quality
- `.pre-commit-config.yaml` — Pre-commit hooks (isort, black, flake8, clang-format, mypy, codespell)
- `genai-perf/pyproject.toml` — Ruff config (minimal)

### Development
- `.devcontainer/devcontainer.json` — VS Code devcontainer with NVIDIA Triton base
