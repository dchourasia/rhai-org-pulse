---
repository: "triton-inference-server/perf_analyzer"
overall_score: 5.2
scorecard:
  - dimension: "Unit Tests"
    score: 6.5
    status: "Good Python test suite with pytest; C++ tests exist but not validated in GitHub CI"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Only 2 integration test files; no E2E test infrastructure; no server-based testing"
  - dimension: "Build Integration"
    score: 2.5
    status: "No PR-time build validation; C++ builds only happen after GitLab mirror; no image testing"
  - dimension: "Image Testing"
    score: 1.0
    status: "No Dockerfile in repo; no container image builds, scanning, or runtime validation"
  - dimension: "Coverage Tracking"
    score: 4.0
    status: "Coverage generated for Python via pytest-cov but no enforcement thresholds or codecov integration"
  - dimension: "CI/CD Automation"
    score: 5.5
    status: "4 PR-triggered workflows but C++ CI is indirect via GitLab mirror; no caching or concurrency control"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No .claude directory, CLAUDE.md, or agent rules of any kind"
critical_gaps:
  - title: "C++ unit tests not validated in GitHub CI"
    impact: "C++ regressions can only be caught after GitLab mirror sync, introducing delay and opaque failure modes"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No coverage enforcement thresholds"
    impact: "Coverage can silently regress with no minimum bar; no PR-level coverage reporting"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image testing or security scanning"
    impact: "No vulnerability scanning, no SBOM, no image validation; security issues in dependencies go undetected"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Minimal integration/E2E testing"
    impact: "Only 2 integration test files; no end-to-end testing against a real Triton server; critical user workflows untested"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "No dependency vulnerability scanning"
    impact: "Python dependencies (30+ packages including transformers, numpy, pandas) not scanned for known CVEs"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add codecov integration with PR comments and thresholds"
    effort: "2-3 hours"
    impact: "Prevent silent coverage regression; visibility into coverage trends on every PR"
  - title: "Add Dependabot or Renovate for dependency updates"
    effort: "1-2 hours"
    impact: "Automated dependency security updates for 30+ Python packages"
  - title: "Add Trivy scanning for Python dependencies"
    effort: "1-2 hours"
    impact: "Early detection of known vulnerabilities in the dependency tree"
  - title: "Create basic CLAUDE.md with testing guidelines"
    effort: "2-3 hours"
    impact: "Guide AI agents to produce consistent, high-quality test code matching project conventions"
recommendations:
  priority_0:
    - "Run C++ unit tests directly in GitHub Actions to eliminate the GitLab mirror delay for test feedback"
    - "Add coverage thresholds (--cov-fail-under) to the Python test workflow to prevent regression"
    - "Add dependency vulnerability scanning (Dependabot, Trivy, or pip-audit) to CI"
  priority_1:
    - "Expand integration test suite to cover core perf_analyzer CLI workflows against a mock/real Triton server"
    - "Add container image build and security scanning workflow for downstream consumers"
    - "Create comprehensive agent rules (.claude/rules/) for unit test, integration test, and C++ test patterns"
  priority_2:
    - "Add performance regression testing to detect throughput/latency measurement accuracy drift"
    - "Implement multi-architecture build validation (aarch64 alongside x86_64)"
    - "Add CodeQL scanning for C++ code (currently only Python is analyzed)"
---

# Quality Analysis: triton-inference-server/perf_analyzer

## Executive Summary

- **Overall Score: 5.2/10**
- **Repository Type**: CLI tool (C++/Python hybrid) - Triton Inference Server benchmarking utility
- **Primary Languages**: C++ (perf_analyzer core), Python (genai-perf sub-project)
- **Key Strengths**: Strong pre-commit hooks with comprehensive linting (8 tools), good Python unit test coverage with organized test structure, CodeQL security scanning on PRs
- **Critical Gaps**: C++ tests not run in GitHub CI, no coverage enforcement, no container/image testing, minimal integration/E2E tests, no agent rules
- **Agent Rules Status**: Missing - no `.claude/` directory or CLAUDE.md

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6.5/10 | Good Python test suite (66 files, 17K lines); C++ tests exist (27 files, 12K lines) but not validated in GitHub CI |
| Integration/E2E | 3.0/10 | Only 2 integration test files in genai-perf; no E2E infrastructure against real servers |
| **Build Integration** | **2.5/10** | **No PR-time C++ build validation; builds are deferred to opaque GitLab pipeline** |
| Image Testing | 1.0/10 | No Dockerfile in repo; no container builds, scanning, or runtime validation |
| Coverage Tracking | 4.0/10 | pytest-cov generates reports but no thresholds, no codecov, no PR-level enforcement |
| CI/CD Automation | 5.5/10 | 4 workflows, all PR-triggered; but C++ CI is indirect; no caching, no concurrency control |
| Agent Rules | 0.0/10 | No .claude directory, no CLAUDE.md, no AGENTS.md, no test automation guidance |

## Critical Gaps

### 1. C++ Unit Tests Not Validated in GitHub CI
- **Impact**: C++ regressions can only be caught after GitLab mirror sync, introducing delay and opaque failure modes for contributors
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Detail**: The `trigger_ci.yml` workflow mirrors the repo to GitLab and triggers a pipeline there. Contributors cannot see C++ test results directly in the GitHub PR checks. The 27 C++ test files (12,448 lines) using doctest + googletest are effectively invisible to the open-source contribution workflow.

### 2. No Coverage Enforcement Thresholds
- **Impact**: Coverage can silently regress; no minimum bar enforced on PRs
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Detail**: The `python-package-genai.yml` runs `pytest --cov=genai_perf --cov-report=xml --cov-report=html` but does NOT use `--cov-fail-under` to enforce a minimum. No codecov integration means no PR-level comments or trend tracking.

### 3. No Container Image Testing or Security Scanning
- **Impact**: No vulnerability scanning, SBOM generation, or image validation; security issues in the 30+ Python dependencies go undetected
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Detail**: The repository has no Dockerfile (container images are built externally in the Triton ecosystem). However, there is no dependency vulnerability scanning (no Dependabot, no pip-audit, no Trivy). The genai-perf package depends on transformers, numpy, pandas, pillow, and many other packages with known CVE histories.

### 4. Minimal Integration/E2E Testing
- **Impact**: Critical user workflows (profiling against Triton, GenAI model benchmarking) are not tested in CI
- **Severity**: HIGH
- **Effort**: 20-40 hours
- **Detail**: Only 2 integration test files exist (`test_multiturn.py`, `test_telemetry.py`) and they use mocks rather than real server interactions. No E2E test infrastructure exists to validate the CLI against a running Triton Inference Server. For a benchmarking tool, accuracy of measurements is mission-critical.

### 5. No Dependency Vulnerability Scanning
- **Impact**: Python dependencies (30+ packages) not scanned for known CVEs
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Detail**: No Dependabot, Renovate, pip-audit, or Trivy scanning configured. The dependency list includes packages with histories of security vulnerabilities (pillow, transformers, numpy).

## Quick Wins

### 1. Add Codecov Integration with PR Comments (2-3 hours)
- **Impact**: Prevent silent coverage regression; visibility into trends
- **Implementation**: Add `.codecov.yml` and upload coverage XML from the existing pytest workflow:
```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: ./genai-perf/tests/coverage.xml
    fail_ci_if_error: true
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 2. Add Dependabot for Dependency Updates (1-2 hours)
- **Impact**: Automated PRs for security updates across 30+ Python packages
- **Implementation**: Create `.github/dependabot.yml`:
```yaml
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

### 3. Add pip-audit or Trivy for Dependency Scanning (1-2 hours)
- **Impact**: Catch known CVEs in Python dependencies before they reach production
- **Implementation**: Add a step to the existing Python test workflow:
```yaml
- name: Audit dependencies
  run: |
    pip install pip-audit
    pip-audit --requirement genai-perf/requirements.txt
```

### 4. Create Basic CLAUDE.md (2-3 hours)
- **Impact**: Guide AI agents to produce consistent, high-quality tests matching the project's conventions
- **Implementation**: Document the dual C++/Python structure, testing frameworks (doctest for C++, pytest for Python), and coding standards.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (4 workflows, all PR-triggered):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `codeql.yml` | `pull_request` | CodeQL analysis for Python only |
| `pre-commit.yml` | `pull_request` | Pre-commit hooks (isort, black, flake8, clang-format, mypy, codespell) |
| `python-package-genai.yml` | `pull_request` | Python unit tests with pytest + coverage generation |
| `trigger_ci.yml` | `pull_request` (paths-ignore README, .github) | Mirrors to GitLab, triggers C++ CI pipeline |

**Strengths**:
- All workflows trigger on PRs (good shift-left approach)
- Pre-commit runs only on modified files (efficient)
- Python test workflow generates JUnit XML and coverage reports

**Weaknesses**:
- No concurrency control (`concurrency:` key not used) - duplicate workflows can run simultaneously
- No caching of pip dependencies or build artifacts
- No GitHub Actions version pinning (uses `@v3`, `@v2` - should pin to commit SHAs for supply chain security)
- C++ CI is opaque - mirrors to internal GitLab, results not visible in GitHub
- `trigger_ci.yml` uses `self-hosted` runner - not accessible to external contributors
- No workflow for periodic/nightly runs
- No workflow dispatch for manual triggering
- Single Python version tested (3.10 only)

### Test Coverage

**Python (genai-perf)**: 
- **66 test files** across 10 directories, **17,232 lines of test code**
- **600 source files**, **33,400 lines of source code**
- **Test-to-code ratio**: 0.52 (decent but room for improvement)
- **Framework**: pytest with pytest-cov, pytest-timeout, pytest-mock
- **Organization**: Well-structured by module (test_converters/, test_data_parser/, test_exporters/, test_metrics/, test_retrievers/, test_statistics/, test_collectors/)
- **Integration tests**: 2 files in `tests/integration_tests/` but use mocks, not real server interactions
- **Coverage generation**: pytest-cov with XML and HTML output, but no threshold enforcement

**C++ (perf_analyzer core)**:
- **27 test files**, **12,448 lines of test code**
- **143 non-test source files**, **30,940 lines of source code**
- **Test-to-code ratio**: 0.40 (moderate)
- **Framework**: doctest (header-only, bundled as `src/doctest.h`) + googletest (fetched via CMake FetchContent)
- **Notable**: Tests are compiled into a `perf_analyzer_unit_tests` binary via CMake
- **Coverage**: No C++ coverage generation configured

### Code Quality

**Pre-commit Hooks** (8 tools, comprehensive):
| Tool | Purpose | Scope |
|------|---------|-------|
| isort | Import sorting | Python |
| black | Code formatting | Python |
| flake8 | Linting | Python |
| clang-format | C/C++ formatting | C, C++, CUDA, Proto, Java |
| codespell | Spelling checker | All |
| mypy | Static type checking | Python |
| pre-commit-hooks | File hygiene (trailing whitespace, line endings, JSON/YAML validation) | All |
| add-license | Copyright headers | All |

**Additional Quality Tools**:
- `.clang-format` config (Google-based style with customizations)
- `ruff.toml` config for Python (via pyproject.toml)
- `pyproject.toml` with isort and codespell configuration

**Strengths**: Very comprehensive linting pipeline covering both languages with formatting and type checking.

**Weaknesses**: 
- Pre-commit hooks are not enforced in CI beyond the pre-commit workflow (hooks can be skipped locally)
- No `ruff` in pre-commit config (uses older black + flake8 combo instead)

### Container Images

**Status**: No container infrastructure in this repository.
- No Dockerfile or Containerfile
- No docker-compose.yml
- No container scanning (Trivy, Snyk, Grype)
- No SBOM generation
- No image signing or attestation

**Context**: Container images are built externally as part of the Triton Inference Server ecosystem. The `.devcontainer/devcontainer.json` references an internal NVIDIA image (`gitlab-master.nvidia.com:5005/dl/dgx/tritonserver:master-py3-base`) for development.

### Security

**Present**:
- CodeQL analysis on PRs (Python only, `security-and-quality` query suite)
- SECURITY.md with NVIDIA PSIRT reporting process
- Pre-commit hooks prevent common issues (merge conflicts, bad file formats)

**Missing**:
- CodeQL not configured for C++ analysis
- No dependency vulnerability scanning (Dependabot, Renovate, pip-audit)
- No container scanning
- No secret detection (Gitleaks, TruffleHog)
- No SBOM generation
- GitHub Actions not pinned to commit SHAs (supply chain risk)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no `.claude/` directory, no CLAUDE.md, no AGENTS.md
- **Quality**: N/A
- **Gaps**: No test automation guidance for AI agents; no documentation of testing patterns, conventions, or quality gates
- **Recommendation**: Generate rules with `/test-rules-generator` covering:
  - Python pytest patterns (parametrize, fixtures, mocking conventions)
  - C++ doctest patterns (TEST_CASE, SUBCASE conventions)
  - Integration test patterns (mock server setup, fixture management)
  - Code formatting requirements (black, clang-format standards)

## Recommendations

### Priority 0 (Critical)

1. **Run C++ unit tests in GitHub Actions** - Add a workflow that builds and runs `perf_analyzer_unit_tests` on PRs. This eliminates the opaque GitLab mirror dependency and gives immediate feedback to contributors. Consider using the devcontainer image or a minimal CMake build setup.

2. **Add coverage enforcement** - Add `--cov-fail-under=70` (or appropriate threshold) to the pytest command in `python-package-genai.yml`. Integrate codecov for PR-level reporting and trend tracking.

3. **Add dependency vulnerability scanning** - Enable Dependabot for Python and GitHub Actions dependencies. Add `pip-audit` or `safety` to the CI pipeline to catch known CVEs in the 30+ Python packages.

### Priority 1 (High Value)

4. **Expand integration test suite** - Build E2E tests that validate genai-perf against a real Triton Inference Server (containerized in CI). For a benchmarking tool, measurement accuracy is critical and can only be validated end-to-end.

5. **Add container security scanning** - Even without a Dockerfile in this repo, add a workflow that scans the Python dependency tree with Trivy or Grype. This catches vulnerabilities before they propagate to downstream container builds.

6. **Create comprehensive agent rules** - Build `.claude/rules/` with guidelines for:
   - `unit-tests.md`: pytest patterns, fixtures, parametrize usage, mocking conventions
   - `cpp-tests.md`: doctest patterns, TEST_CASE/SUBCASE usage, googletest integration
   - `integration-tests.md`: mock server patterns, test data management
   - `code-quality.md`: formatting, linting, type annotation requirements

7. **Pin GitHub Actions to commit SHAs** - Replace `@v3`, `@v2` with full commit SHAs to prevent supply chain attacks via compromised action tags.

### Priority 2 (Nice-to-Have)

8. **Multi-Python-version testing** - Currently only testing on Python 3.10. Add 3.12 (the other version in classifiers) to the test matrix.

9. **Add performance regression testing** - For a performance analysis tool, benchmark measurement accuracy should be continuously validated. Consider a CI job that runs the tool against a known workload and compares results.

10. **Add CodeQL for C++ code** - The current CodeQL config only analyzes Python. Extending to C++ would catch memory safety, buffer overflow, and other C++-specific vulnerabilities.

11. **Add concurrency control to workflows** - Use `concurrency:` in workflow definitions to cancel redundant runs on updated PRs.

12. **Replace black+flake8 with ruff** - The `ruff` config already exists in `pyproject.toml`. Migrating pre-commit hooks to `ruff` would be faster and reduce tooling complexity.

## Comparison to Gold Standards

| Dimension | perf_analyzer | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|-----------|---------------|---------------------|-------------------|---------------|
| Unit Tests | 6.5 - Good Python coverage, C++ tests exist | 9.0 - Multi-layer with Jest | 7.0 - Notebook validation | 9.0 - Go testing + envtest |
| Integration/E2E | 3.0 - Minimal, mock-based | 9.0 - Cypress E2E + contract tests | 8.0 - Image runtime testing | 9.0 - Multi-version E2E |
| Build Integration | 2.5 - Opaque GitLab mirror | 8.0 - PR-time builds validated | 8.0 - Image builds on PRs | 7.0 - Operator manifest validation |
| Image Testing | 1.0 - No container infra | 7.0 - Testcontainers | 9.0 - 5-layer validation | 7.0 - Deployment testing |
| Coverage | 4.0 - Generated, not enforced | 9.0 - Enforced with thresholds | 6.0 - Basic tracking | 8.0 - Codecov + thresholds |
| CI/CD | 5.5 - 4 workflows, basic | 9.0 - Comprehensive pipeline | 8.0 - Multi-arch builds | 9.0 - Well-organized |
| Agent Rules | 0.0 - None | 8.0 - Comprehensive rules | 3.0 - Basic | 4.0 - Partial |

## File Paths Reference

### CI/CD
- `.github/workflows/codeql.yml` - CodeQL security scanning (Python only)
- `.github/workflows/pre-commit.yml` - Pre-commit hook enforcement
- `.github/workflows/python-package-genai.yml` - Python tests with coverage
- `.github/workflows/trigger_ci.yml` - GitLab mirror + CI trigger
- `.github/workflows/mirror_repo.sh` - GitLab mirror sync script

### Testing
- `genai-perf/tests/` - Python unit tests (66 files)
- `genai-perf/tests/integration_tests/` - Integration tests (2 files)
- `genai-perf/pytest.ini` - Pytest configuration
- `src/test_*.cc` - C++ unit tests (20+ files using doctest)
- `src/perf_analyzer_unit_tests.cc` - C++ test runner
- `src/doctest.h` - Bundled doctest framework

### Code Quality
- `.pre-commit-config.yaml` - 8 pre-commit hooks
- `.clang-format` - C++ formatting config (Google-based)
- `pyproject.toml` - Python tool configs (isort, ruff, codespell)
- `genai-perf/pyproject.toml` - genai-perf package config

### Build
- `CMakeLists.txt` - Top-level CMake (ExternalProject-based)
- `src/CMakeLists.txt` - Core C++ build with test binary
- `.devcontainer/devcontainer.json` - Dev container config

### Security
- `SECURITY.md` - NVIDIA PSIRT vulnerability reporting
- `.github/workflows/codeql.yml` - CodeQL (Python only)
