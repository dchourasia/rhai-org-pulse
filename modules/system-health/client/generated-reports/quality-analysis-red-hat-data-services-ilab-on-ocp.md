---
repository: "red-hat-data-services/ilab-on-ocp"
overall_score: 1.9
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No Python unit tests exist for ~2,600 lines of pipeline component code"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Single Go-based E2E test exists but is manual, not CI-integrated, and environment-gated"
  - dimension: "Build Integration"
    score: 4.0
    status: "Konflux PR builds available but label/comment-gated, no automatic PR image validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "No runtime validation, no vulnerability scanning, no SBOM generation"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage generation, no codecov/coveralls integration, no thresholds"
  - dimension: "CI/CD Automation"
    score: 5.0
    status: "Pre-commit on PRs with caching, pipeline.yaml freshness check, Renovate for deps"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules for test automation"
critical_gaps:
  - title: "Zero Python unit tests"
    impact: "~2,600 lines of pipeline component code (SDG, training, eval, utils) have no unit test coverage. Bugs in pipeline parameter handling, component logic, and API interactions go undetected until runtime on expensive GPU clusters."
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No visibility into what code is tested. PRs can merge with zero test coverage. No baseline to measure improvement against."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image security scanning"
    impact: "Images shipped to production without vulnerability assessment. Base images (UBI8/UBI9) and pip-installed dependencies not scanned for CVEs."
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "E2E test not automated in CI"
    impact: "The single E2E test requires manual execution with specific environment setup. Pipeline regressions not caught before merge."
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No SAST or dependency scanning"
    impact: "No static analysis beyond ruff linting. No CodeQL, Semgrep, or Bandit. Dependency vulnerabilities not tracked."
    severity: "MEDIUM"
    effort: "3-4 hours"
  - title: "No image runtime validation"
    impact: "Built images are not tested for startup, import availability, or basic functionality before deployment."
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add pytest infrastructure and initial unit tests for utils/consts.py and pipeline parameter validation"
    effort: "2-4 hours"
    impact: "Establish test infrastructure and begin covering critical pipeline parameters"
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Immediate vulnerability visibility for container images on every PR"
  - title: "Add codecov integration with baseline coverage"
    effort: "2-3 hours"
    impact: "Track and enforce coverage improvement over time"
  - title: "Add CodeQL or Bandit for Python SAST"
    effort: "1-2 hours"
    impact: "Catch security anti-patterns in Python code automatically"
  - title: "Create basic CLAUDE.md with testing guidelines"
    effort: "1-2 hours"
    impact: "Guide AI-assisted development to produce tested code"
recommendations:
  priority_0:
    - "Add Python unit tests for pipeline components (sdg, training, eval, utils modules)"
    - "Integrate codecov with PR-level coverage enforcement (start with 0% floor, ratchet up)"
    - "Add Trivy container scanning to GitHub Actions PR workflow"
  priority_1:
    - "Automate E2E test execution in CI with a periodic or nightly schedule"
    - "Add image runtime validation (import checks, basic health verification)"
    - "Add CodeQL or Bandit SAST scanning to PR workflow"
    - "Create comprehensive CLAUDE.md with testing and development guidelines"
  priority_2:
    - "Add Gitleaks for secret detection in PRs"
    - "Add type checking with mypy for pipeline components"
    - "Add contract tests for KFP component interfaces"
    - "Add SBOM generation for container images"
---

# Quality Analysis: ilab-on-ocp

## Executive Summary

- **Overall Score: 1.9/10**
- **Repository Type**: Python KFP (Kubeflow Pipelines) pipeline project for InstructLab on RHOAI
- **Primary Language**: Python (~2,600 lines across 13 files), Go (E2E test only)
- **Key Strengths**: Well-configured pre-commit hooks with ruff linting/formatting, Konflux multi-arch builds, pipeline.yaml freshness validation, Renovate for automated dependency updates
- **Critical Gaps**: Zero unit tests, no coverage tracking, no security scanning, E2E test not CI-integrated
- **Agent Rules Status**: Missing - No CLAUDE.md, no `.claude/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No Python unit tests for ~2,600 LOC of pipeline components |
| Integration/E2E | 3/10 | Single Go E2E test, manual execution only, env-gated |
| **Build Integration** | **4/10** | **Konflux PR builds (label-gated), no image validation** |
| Image Testing | 1/10 | No runtime validation, no scanning, no SBOM |
| Coverage Tracking | 0/10 | No coverage generation or enforcement |
| CI/CD Automation | 5/10 | Pre-commit on PRs, pipeline validation, Renovate |
| Agent Rules | 0/10 | No agent rules exist |

## Critical Gaps

### 1. Zero Python Unit Tests
- **Impact**: ~2,600 lines of pipeline component code across `sdg/`, `training/`, `eval/`, `utils/` have zero test coverage. This code handles complex operations including SDG data generation, training job configuration, model evaluation benchmarks, and Kubernetes resource management. Bugs in parameter handling, component assembly, or API interactions are only discovered at runtime on expensive GPU clusters.
- **Severity**: HIGH
- **Effort**: 16-24 hours for initial test suite
- **Files needing tests**:
  - `sdg/components.py` (494 lines) - SDG pipeline operations
  - `training/components.py` (392 lines) - Training job orchestration
  - `eval/final.py` (555 lines) - Final evaluation logic
  - `eval/mt_bench.py` (259 lines) - MT-Bench evaluation
  - `utils/components.py` (681 lines) - Utility components
  - `pipeline.py` (628 lines) - Pipeline assembly

### 2. No Coverage Tracking or Enforcement
- **Impact**: Without coverage tracking, there is no visibility into what code is tested, no ability to set improvement targets, and no gate to prevent coverage regression on PRs.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Implementation**:
  ```yaml
  # .github/workflows/pre_commit.yaml - add step
  - name: Run tests with coverage
    run: |
      uv run pytest --cov=. --cov-report=xml
  - name: Upload coverage
    uses: codecov/codecov-action@v4
    with:
      files: coverage.xml
      token: ${{ secrets.CODECOV_TOKEN }}
  ```

### 3. No Container Image Security Scanning
- **Impact**: Container images built from `Dockerfile` and `Dockerfile.konflux` use UBI base images and pip-install numerous dependencies from `requirements.txt` (78KB of pinned dependencies). None of these are scanned for known vulnerabilities before deployment.
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Implementation**:
  ```yaml
  # Add to PR workflow
  - name: Build image for scanning
    run: podman build -t ilab-on-ocp:scan .
  - name: Run Trivy scan
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: 'ilab-on-ocp:scan'
      format: 'sarif'
      severity: 'CRITICAL,HIGH'
  ```

### 4. E2E Test Not Automated in CI
- **Impact**: The Go-based E2E test (`tests/pipeline/e2e/ilab_rhoai_pipeline_runs_test.go`) validates the full pipeline run but requires manual execution with specific env vars (`ENABLE_ILAB_PIPELINE_TEST`, `PIPELINE_SERVER_URL`, `BEARER_TOKEN`). Pipeline regressions are not caught automatically.
- **Severity**: HIGH
- **Effort**: 8-12 hours (requires cluster access, secrets management)

### 5. No SAST or Dependency Scanning
- **Impact**: Beyond ruff's linting (focused on style/imports), no static analysis tool checks for security issues like command injection, unsafe deserialization, or insecure API usage. No dependency vulnerability tracking beyond Renovate's version updates.
- **Severity**: MEDIUM
- **Effort**: 3-4 hours

### 6. No Image Runtime Validation
- **Impact**: Built images are pushed to registries without verifying they can start, import required Python modules, or respond to basic health checks.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours

## Quick Wins

### 1. Add pytest Infrastructure (2-4 hours)
```toml
# pyproject.toml - add test dependency group
[dependency-groups]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]
```
```python
# tests/test_consts.py - basic test to establish infrastructure
from utils.consts import RHELAI_IMAGE, RUNTIME_GENERIC_IMAGE

def test_image_constants_defined():
    assert RHELAI_IMAGE is not None
    assert RUNTIME_GENERIC_IMAGE is not None
    assert "registry" in RHELAI_IMAGE
```

### 2. Add Trivy Scanning (1-2 hours)
Add a new workflow or step to `pre_commit.yaml` that builds the Docker image and scans it with Trivy on every PR.

### 3. Add Codecov Integration (2-3 hours)
Add `pytest-cov` to test dependencies, generate coverage XML in CI, and upload to Codecov. Set an initial threshold of 0% and ratchet up as tests are added.

### 4. Add CodeQL for Python (1-2 hours)
```yaml
# .github/workflows/codeql.yml
name: CodeQL
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
```

### 5. Create CLAUDE.md (1-2 hours)
Add basic development and testing guidelines so AI-assisted contributions include tests.

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `build-main.yml` | Push to main | Build & push image to quay.io |
| `pre_commit.yaml` | PR + push to main | Pre-commit hooks, pipeline freshness, requirements validation |

**Tekton/Konflux:**
- `odh-ml-pipelines-runtime-generic-pull-request.yaml` - Builds multi-arch (x86_64, arm64, ppc64le) container images via Konflux on PRs
- Triggered by labels (`kfbuild-all`, `kfbuild-ilab-on-ocp`) or comment (`/build-konflux`)
- Hermetic build with prefetch for RPMs and pip packages
- Uses centralized `konflux-central` pipeline definition

**Strengths:**
- Concurrency control on main build (cancel-in-progress)
- Pipeline.yaml freshness check in PR workflow (ensures `make pipeline` was run)
- Requirements.txt consistency validation against pyproject.toml
- Renovate configured for Dockerfile digest, Tekton, and RPM updates with automerge
- Pre-commit caching for performance

**Gaps:**
- No PR-triggered tests (only linting/formatting)
- Image build on main only (not on PRs) via GitHub Actions
- Konflux PR builds are label/comment-gated, not automatic
- No test stage in any workflow
- No nightly or periodic test runs
- No deployment validation

### Test Coverage

**Unit Tests: NONE**
- Zero Python test files across the entire repository
- No `pytest.ini`, `conftest.py`, or test configuration
- No test dependency group in `pyproject.toml` (only `lint` group exists)
- No test targets in `Makefile`
- The `.gitignore` includes pytest/coverage patterns suggesting tests were once planned but never created

**E2E Tests: Minimal**
- Single Go test file: `tests/pipeline/e2e/ilab_rhoai_pipeline_runs_test.go`
- Uses testify/require for assertions
- Uses spf13/viper for parameter configuration
- REST utility (`tests/pipeline/e2e/util/rest.go`) for KFP API interaction
- Test flow: Retrieve pipeline ID → Load parameters → Trigger run → Wait for success (2h10m timeout)
- **Gate**: Requires `ENABLE_ILAB_PIPELINE_TEST=true` env var
- **Requirements**: Live cluster with pipeline server, bearer token authentication
- **Not CI-integrated**: Manual execution only per README

**Test-to-Code Ratio**: ~0.03 (76 lines of test code / ~2,600 lines of Python source)

### Code Quality

**Pre-commit Hooks (Good):**
- `trailing-whitespace` - Whitespace cleanup
- `end-of-file-fixer` - Ensure files end with newline
- `check-yaml` - YAML syntax validation (allows multiple documents)
- `check-merge-conflict` - Detect merge conflict markers
- `detect-private-key` - Prevent committing private keys
- `ruff` - Python linting with import sorting (`--fix --select I`)
- `ruff-format` - Python code formatting check
- `yamllint` - YAML linting with strict mode

**Missing:**
- No type checking (mypy, pyright)
- No complexity checks (radon, mccabe)
- No dead code detection (vulture)
- No docstring enforcement
- No Gitleaks for comprehensive secret detection

### Container Images

**Dockerfiles:**
1. `Dockerfile` - Standard build from `ubi8/python-312:1`, installs skopeo + pip requirements
2. `Dockerfile.konflux` - Konflux build from `ubi9/python-312:1` with pinned digest, similar structure
3. `manifests/model_downloader/container_file/Containerfile` - Model download utility from `ubi9/ubi`

**Analysis:**
- Single-stage builds (no multi-stage optimization)
- UBI base images (good for Red Hat ecosystem)
- `requirements.txt` with hashes (good for supply chain security)
- Root user operations properly scoped and dropped back to `default`
- Skopeo installed for image operations
- `.dockerignore` present but minimal (only `.git`, `.github`, `.venv`, `Dockerfile`)

**Gaps:**
- No image startup validation after build
- No vulnerability scanning
- No SBOM generation
- No image signing or attestation
- No health check configuration in Dockerfile
- No image size optimization (single-stage build)

### Security

**Present:**
- `detect-private-key` in pre-commit hooks
- Hermetic Konflux builds with prefetch
- Requirements pinned with hashes for supply chain security
- Renovate for automated dependency updates

**Missing:**
- No SAST (CodeQL, Bandit, Semgrep)
- No container scanning (Trivy, Snyk, Grype)
- No dependency vulnerability scanning (pip-audit, safety)
- No secret detection (Gitleaks, TruffleHog)
- No SBOM generation
- No image signing

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test type rules exist
- **Quality**: N/A
- **Gaps**: 
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory
  - No `.claude/rules/` for test creation guidance
  - No `.claude/skills/` for custom automation
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator`. At minimum, create `CLAUDE.md` with:
  - Project overview and architecture
  - Testing requirements and patterns
  - KFP component testing guidelines
  - Pre-commit and CI requirements

## Recommendations

### Priority 0 (Critical)

1. **Add Python unit test infrastructure and initial tests**
   - Add `pytest`, `pytest-cov` to `pyproject.toml` dependency groups
   - Create `conftest.py` with common fixtures
   - Write initial tests for `utils/consts.py`, `utils/kfp_client.py`
   - Add `pytest` step to `pre_commit.yaml` workflow
   - Target: 30% coverage within first sprint

2. **Integrate codecov with coverage enforcement**
   - Generate coverage XML in CI
   - Upload to Codecov
   - Set initial floor at 0%, configure ratchet (no coverage decrease on PRs)
   - Add coverage badge to README

3. **Add Trivy container scanning to PR workflow**
   - Build image in PR workflow
   - Scan with Trivy for CRITICAL and HIGH vulnerabilities
   - Fail PR if critical vulnerabilities found
   - Upload SARIF results for GitHub Security tab integration

### Priority 1 (High Value)

4. **Automate E2E test execution**
   - Create nightly/periodic workflow with cluster credentials
   - Integrate with RHOAI test infrastructure
   - Report results and failures via Slack/email

5. **Add image runtime validation**
   - After image build, verify: container starts, Python imports work, pipeline.yaml is present
   - Add basic smoke test: `podman run --rm image python -c "import kfp; import sdg; import training; import eval"`

6. **Add SAST scanning**
   - CodeQL for Python (free for public repos)
   - Or Bandit for Python-specific security checks
   - Run on PRs and pushes to main

7. **Create CLAUDE.md and agent rules**
   - Document project architecture and pipeline structure
   - Add testing requirements for all contributions
   - Specify KFP component testing patterns
   - Include pre-commit requirements

### Priority 2 (Nice-to-Have)

8. **Add Gitleaks for secret detection**
9. **Add mypy type checking for pipeline components**
10. **Add contract tests for KFP component interfaces**
11. **Add SBOM generation for container images**
12. **Optimize Dockerfiles with multi-stage builds**
13. **Add image signing with cosign**

## Comparison to Gold Standards

| Capability | ilab-on-ocp | odh-dashboard | notebooks | kserve |
|------------|-------------|---------------|-----------|--------|
| Unit Tests | None | Comprehensive (Jest) | Present | Extensive (Go) |
| Integration Tests | None | Contract tests | Image validation | envtest |
| E2E Tests | 1 manual Go test | Cypress + API | Multi-layer | Multi-version |
| Coverage Tracking | None | Codecov enforced | Present | Enforced (90%+) |
| Coverage Threshold | None | Yes | Yes | Yes |
| PR Test Automation | None | Full suite | Full suite | Full suite |
| Container Scanning | None | Trivy | Trivy | Trivy |
| SAST | None | CodeQL | N/A | CodeQL |
| Secret Detection | Basic (pre-commit) | Gitleaks | N/A | Gitleaks |
| Pre-commit Hooks | Good (ruff, yamllint) | Comprehensive | Present | Present |
| Image Runtime Tests | None | Deployment tests | 5-layer validation | Startup tests |
| Agent Rules | None | Comprehensive | None | None |
| Renovate/Dependabot | Renovate (good) | Dependabot | N/A | Dependabot |
| Multi-arch Builds | Konflux (3 archs) | N/A | Yes | Yes |

## File Paths Reference

### CI/CD
- `.github/workflows/build-main.yml` - Main branch image build
- `.github/workflows/pre_commit.yaml` - PR pre-commit checks
- `.github/workflows/renovate.json` - Renovate configuration
- `.tekton/odh-ml-pipelines-runtime-generic-pull-request.yaml` - Konflux PR build
- `Makefile` - Pipeline compilation target

### Source Code
- `pipeline.py` (628 lines) - Main pipeline assembly
- `sdg/components.py` (494 lines) - SDG pipeline components
- `training/components.py` (392 lines) - Training job components
- `eval/final.py` (555 lines) - Final evaluation logic
- `eval/mt_bench.py` (259 lines) - MT-Bench evaluation
- `utils/components.py` (681 lines) - Utility components
- `utils/kfp_client.py` (56 lines) - KFP client utilities
- `utils/consts.py` (21 lines) - Image constants

### Tests
- `tests/pipeline/e2e/ilab_rhoai_pipeline_runs_test.go` - E2E pipeline test
- `tests/pipeline/e2e/util/rest.go` - REST API test utilities
- `tests/pipeline/e2e/resources/pipeline_params.yaml` - Test parameters

### Container Images
- `Dockerfile` - Standard image build
- `Dockerfile.konflux` - Konflux hermetic build
- `manifests/model_downloader/container_file/Containerfile` - Model downloader

### Code Quality
- `.pre-commit-config.yaml` - Pre-commit hooks (ruff, yamllint, detect-private-key)
- `.yamllint.yaml` - YAML lint configuration
- `pyproject.toml` - Project metadata and dependencies
- `.gitignore` - Git ignore patterns (includes pytest/coverage patterns)
