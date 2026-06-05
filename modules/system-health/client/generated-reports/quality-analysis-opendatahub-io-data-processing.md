---
repository: "opendatahub-io/data-processing"
overall_score: 4.3
scorecard:
  - dimension: "Unit Tests"
    score: 2.0
    status: "No unit tests for Python source modules; only notebook validation tests exist"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "GPU-based notebook execution and KFP local runner tests on EC2, but not triggered on PRs for pipelines"
  - dimension: "Build Integration"
    score: 3.0
    status: "KFP pipeline compilation verified on PR, but no container image build or Konflux simulation"
  - dimension: "Image Testing"
    score: 2.0
    status: "Single Containerfile exists but no image build CI, no runtime validation, no scanning"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tool integration, no thresholds, no PR reporting"
  - dimension: "CI/CD Automation"
    score: 6.0
    status: "Well-structured workflows with path filtering and matrix strategy, but gaps in PR-time E2E"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules or test guidance"
critical_gaps:
  - title: "No unit tests for KFP components or utility scripts"
    impact: "Python logic in kubeflow-pipelines/common/, scripts/subset_selection/ has zero test coverage"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No code coverage tracking or enforcement"
    impact: "No visibility into test coverage; regressions go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image build or scanning in CI"
    impact: "Containerfile changes not validated until downstream; vulnerabilities undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning (SAST, dependency, secret detection)"
    impact: "Vulnerabilities in dependencies and code not caught before merge"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "KFP local runner tests only run on upstream repo, not fork PRs"
    impact: "Contributors cannot validate pipeline changes before submitting to upstream"
    severity: "MEDIUM"
    effort: "4-8 hours"
quick_wins:
  - title: "Add pytest-cov and Codecov integration"
    effort: "2-3 hours"
    impact: "Immediate visibility into test coverage with PR annotations"
  - title: "Add Trivy container scanning to CI"
    effort: "1-2 hours"
    impact: "Detect vulnerabilities in Containerfile and dependencies automatically"
  - title: "Add CodeQL or Semgrep SAST workflow"
    effort: "1-2 hours"
    impact: "Automated static analysis for security issues in Python code"
  - title: "Create CLAUDE.md with basic agent rules"
    effort: "2-3 hours"
    impact: "Guide AI agents to generate consistent, quality-aligned code and tests"
  - title: "Add ruff lint checks (not just formatting) to CI"
    effort: "1 hour"
    impact: "Catch bugbear, pyflakes, and pyupgrade issues beyond formatting"
recommendations:
  priority_0:
    - "Add unit tests for KFP component functions (import_pdfs, create_pdf_splits, docling_chunk, download_docling_models)"
    - "Add unit tests for scripts/subset_selection modules"
    - "Integrate Codecov with coverage thresholds and PR gating"
    - "Add Trivy or Snyk scanning for the Containerfile"
  priority_1:
    - "Add container image build step to PR workflow to catch Containerfile regressions"
    - "Add CodeQL or Semgrep SAST workflow for Python"
    - "Enable Dependabot security alerts (not just version updates)"
    - "Create comprehensive agent rules (.claude/rules/) for test patterns"
    - "Add ruff linting (not just formatting) to validate-python workflow"
  priority_2:
    - "Add pre-commit hook for ruff linting (currently only ruff-format)"
    - "Add contract tests for KFP component interfaces"
    - "Add notebook output regression testing (compare outputs against baselines)"
    - "Add type checking with mypy or pyright"
    - "Implement Gitleaks or TruffleHog for secret detection"
---

# Quality Analysis: opendatahub-io/data-processing

## Executive Summary

- **Overall Score: 4.3/10**
- **Repository Type**: Python data-processing library with Kubeflow Pipelines, Jupyter notebooks, and utility scripts
- **Primary Language**: Python 3.12
- **Framework**: Kubeflow Pipelines (KFP), Jupyter/Papermill, Docling
- **Key Strengths**: Good CI workflow structure with path filtering, notebook execution tests on GPU hardware, KFP pipeline compilation validation, pre-commit hooks, Dependabot integration
- **Critical Gaps**: No unit tests for Python modules, zero coverage tracking, no container security scanning, no SAST, no agent rules
- **Agent Rules Status**: Missing - No CLAUDE.md, no .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 2.0/10 | No unit tests for source modules; only notebook validation |
| Integration/E2E | 5.0/10 | GPU notebook execution + KFP local runners, but limited PR-time coverage |
| **Build Integration** | **3.0/10** | **KFP compile check on PR, but no container build or Konflux simulation** |
| Image Testing | 2.0/10 | Containerfile exists but no build CI, no runtime validation |
| Coverage Tracking | 0.0/10 | No coverage tools, no thresholds, no reporting |
| CI/CD Automation | 6.0/10 | Well-structured workflows with matrix strategy, but gaps |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude/ directory, no test guidance |

## Critical Gaps

### 1. No Unit Tests for Python Source Modules
- **Impact**: The 16 Python source files (~2,700 lines) in `kubeflow-pipelines/common/`, `kubeflow-pipelines/docling-standard/`, `kubeflow-pipelines/docling-vlm/`, and `scripts/subset_selection/` have **zero unit tests**. The existing 2 test files (220 lines) only validate notebook structure and execution.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: Functions like `import_pdfs()`, `create_pdf_splits()`, `docling_chunk()`, `download_docling_models()`, and the subset selection CLI have no isolated tests. Bugs in these core components are only caught through slow, GPU-requiring notebook execution tests.

### 2. No Code Coverage Tracking
- **Impact**: No visibility into what percentage of code is tested. No thresholds to prevent coverage regression. No PR annotations.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `pyproject.toml` configures pytest but has no coverage settings. No `.codecov.yml`, no `--cov` flags, no coverage reporting in any workflow.

### 3. No Container Image Security Scanning
- **Impact**: The `kubeflow-pipelines/docling-standard/Containerfile` installs system packages and pip packages without vulnerability scanning. No Trivy, Snyk, or Grype integration.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The Containerfile installs `tesseract`, `leptonica`, `docling`, and PyTorch packages. None are scanned for CVEs. No `.trivyignore`, no SBOM generation, no image signing.

### 4. No SAST or Secret Detection
- **Impact**: No automated static analysis for security vulnerabilities in Python code. No secret detection to prevent credential leaks.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No CodeQL, Semgrep, Bandit, or gosec workflows. No Gitleaks or TruffleHog integration. The code handles S3 credentials and AWS access which makes secret detection especially important.

### 5. KFP Local Runner Tests Not Available on Fork PRs
- **Impact**: The `execute-kfp-localrunners.yml` workflow has `if: github.repository == 'opendatahub-io/data-processing'` which means fork contributors cannot validate pipeline changes.
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: While this is understandable for cost (EC2 GPU runners), it means contributors get no pipeline validation feedback until their PR is submitted upstream.

## Quick Wins

### 1. Add pytest-cov and Codecov Integration (2-3 hours)
Add coverage reporting to the existing pytest setup:
```toml
# pyproject.toml addition
[tool.pytest.ini_options]
addopts = ["--tb=short", "-v", "--cov=kubeflow-pipelines", "--cov=scripts", "--cov-report=xml"]
```
```yaml
# Add to validate-python.yml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
```

### 2. Add Trivy Container Scanning (1-2 hours)
```yaml
# New workflow: .github/workflows/trivy-scan.yml
name: Trivy Scan
on:
  pull_request:
    paths: ["**/Containerfile", "**/Dockerfile", "**/requirements*.txt"]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
```

### 3. Add CodeQL SAST Workflow (1-2 hours)
```yaml
# New workflow: .github/workflows/codeql.yml
name: CodeQL
on:
  pull_request:
    paths: ["**/*.py"]
  schedule:
    - cron: '0 6 * * 1'
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
```

### 4. Create Basic Agent Rules (2-3 hours)
Create `CLAUDE.md` and `.claude/rules/` directory with test patterns for notebooks, KFP components, and Python modules.

### 5. Add Ruff Linting to CI (1 hour)
Currently only `ruff format --check` runs in CI. Add `ruff check` to catch bugbear, pyflakes, and other issues:
```makefile
# Add to Makefile
lint-python:
	ruff check $(ALL_PYTHON_FILES)
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (5 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate-python.yml` | PR (*.py changes) | Ruff format check only |
| `validate-notebooks.yml` | PR + push (*.ipynb) | nbstripout check + notebook parameter validation |
| `compile-kfp.yml` | PR + push (kubeflow-pipelines/**) | Compile KFP YAML and diff against committed version |
| `execute-all-notebooks.yml` | push to main + manual | Execute all notebooks on EC2 GPU instance |
| `execute-kfp-localrunners.yml` | PR + push + manual | Run KFP local Docker runners on EC2 GPU instance |

**Strengths:**
- Path-based filtering avoids unnecessary CI runs
- Matrix strategy for KFP compilation (docling-standard, docling-vlm)
- EC2 self-hosted runners with GPU for realistic notebook testing
- KFP compile-and-diff ensures committed YAML matches code
- Dependabot for GitHub Actions and pip dependencies (weekly)
- Mergify auto-merge with review requirements
- CODEOWNERS file enforces review routing

**Gaps:**
- No concurrency control on any workflow (no `concurrency:` key)
- `validate-python.yml` only checks formatting, not linting
- Notebook execution only runs on push to main, not on PRs
- KFP local runner tests skip fork PRs entirely
- No caching for pip dependencies in most workflows (only `validate-notebooks.yml` uses `cache: pip`)
- No test result artifacts uploaded on success (only failure logs for KFP runners)

### Test Coverage

**Test Files: 2 files, 220 lines**

| Test File | Type | What It Tests |
|-----------|------|---------------|
| `test_notebook_parameters.py` | Validation | Notebooks have `parameters` cell tag for papermill |
| `test_notebook_execution.py` | Integration | Full notebook execution via papermill on GPU |

**Test-to-Code Ratio**: 220 / 2,705 = **0.08** (extremely low; gold standard is 1.0+)

**What's Tested:**
- Notebook parameter cell presence (structural validation)
- Notebook full execution with papermill (integration)
- Custom test parameters per notebook (subset-selection.ipynb)

**What's NOT Tested:**
- `kubeflow-pipelines/common/components.py` - Core KFP components (import_pdfs, create_pdf_splits, docling_chunk, download_docling_models) - **0 unit tests**
- `kubeflow-pipelines/common/constants.py` - Configuration constants
- `kubeflow-pipelines/docling-standard/standard_components.py` - Standard conversion component
- `kubeflow-pipelines/docling-vlm/vlm_components.py` - VLM conversion component
- `scripts/subset_selection/` - Entire subset selection module (CLI, encoders, utils)

### Code Quality

**Linting:**
- Ruff configured in `pyproject.toml` with rules: E, F, I, B, W, UP
- Ruff format (black-compatible) enforced in CI via `ruff format --check`
- `ruff check` (linting) is **NOT** run in CI - only formatting

**Pre-commit Hooks:**
- `ruff-format` for Python formatting
- `nbstripout` for cleaning notebook outputs
- Missing: `ruff` linting hook, type checking, secret detection

**Static Analysis:**
- No CodeQL, Semgrep, or Bandit
- No mypy or pyright type checking
- No secret detection (Gitleaks, TruffleHog)

**Dependency Management:**
- Dependabot configured for GitHub Actions and pip (weekly, Saturday)
- Major version updates ignored for pip (conservative)
- `requirements-dev.txt` pins minimum versions with `>=`

### Container Images

**Containerfile Analysis (`kubeflow-pipelines/docling-standard/Containerfile`):**
- Base image: `quay.io/sclorg/python-311-c9s:c9s` (CentOS Stream 9)
- Multi-stage: No (single stage)
- Non-root user: Yes (USER 1001)
- System packages: tesseract, leptonica, glib2
- Python packages: docling, tesserocr, PyTorch (CPU-only)
- Model pre-download: Yes (layout, tableformer models baked into image)
- .dockerignore: Missing

**Gaps:**
- No container image build in CI (Containerfile changes not validated on PR)
- No vulnerability scanning (Trivy, Snyk, Grype)
- No SBOM generation
- No image signing/attestation
- No multi-architecture support
- No runtime startup validation
- Single stage build (no build/runtime separation)

### Security

**Current State: Minimal**
- No SAST (CodeQL, Semgrep, Bandit)
- No dependency vulnerability scanning (only Dependabot version updates)
- No container scanning
- No secret detection
- No signed commits enforcement
- Code handles sensitive data (S3 credentials, AWS roles) but has no secret scanning

**Positive:**
- Workflows use pinned action SHAs (e.g., `aws-actions/configure-aws-credentials@61815dcd...`)
- Minimal permissions in workflows (`contents: read`, `pull-requests: read`)
- OIDC-based AWS auth (no long-lived credentials)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Does not exist
- **Test automation guidance**: None
- **Coverage**: No test type rules at all
- **Quality**: N/A
- **Gaps**: All test types lack agent guidance. No patterns for KFP component testing, notebook validation, or Python module testing.
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering unit tests for KFP components, notebook validation patterns, and integration test guidance.

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests for KFP component functions** - Test `import_pdfs()`, `create_pdf_splits()`, `docling_chunk()`, and `download_docling_models()` in isolation using mocks for external dependencies (S3, HTTP, filesystem)
2. **Add unit tests for subset_selection modules** - Test CLI, encoders, and utility functions
3. **Integrate Codecov** with a minimum coverage threshold (start at 40%, increase over time)
4. **Add Trivy or Snyk scanning** for the Containerfile and Python dependencies

### Priority 1 (High Value)

5. **Add container image build to PR workflow** - Build the Containerfile on PRs to catch regressions early
6. **Add CodeQL or Semgrep SAST** workflow for Python security analysis
7. **Enable Dependabot security alerts** (separate from version updates)
8. **Create agent rules** (`.claude/rules/`) for test patterns covering KFP components, notebooks, and Python modules
9. **Add ruff linting** (not just formatting) to the CI validation workflow
10. **Add pip caching** to all workflows (currently only `validate-notebooks.yml` uses it)

### Priority 2 (Nice-to-Have)

11. **Add pre-commit hook for ruff linting** (currently only ruff-format)
12. **Add mypy or pyright** for static type checking
13. **Add notebook output regression testing** (compare outputs against baselines)
14. **Implement Gitleaks** for secret detection in pre-commit and CI
15. **Add concurrency control** to workflows to cancel superseded runs
16. **Add .dockerignore** file to reduce image build context
17. **Explore multi-architecture image builds** (amd64/arm64)

## Comparison to Gold Standards

| Dimension | data-processing | odh-dashboard | notebooks | kserve |
|-----------|:-:|:-:|:-:|:-:|
| Unit Tests | 2/10 | 9/10 | 6/10 | 9/10 |
| Integration/E2E | 5/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 3/10 | 8/10 | 7/10 | 8/10 |
| Image Testing | 2/10 | 7/10 | 9/10 | 7/10 |
| Coverage Tracking | 0/10 | 8/10 | 5/10 | 9/10 |
| CI/CD Automation | 6/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **4.3/10** | **8.5/10** | **7.0/10** | **8.0/10** |

**Key Takeaways vs. Gold Standards:**
- **odh-dashboard** has multi-layer testing (unit, integration, contract, E2E), coverage enforcement, and comprehensive agent rules - data-processing has almost none of these
- **notebooks** has 5-layer image validation (build, startup, import, functional, security) - data-processing has no image testing at all
- **kserve** has coverage enforcement with codecov thresholds and multi-version testing - data-processing has zero coverage tracking

## File Paths Reference

| Category | Path | Notes |
|----------|------|-------|
| CI/CD | `.github/workflows/validate-python.yml` | Ruff format check only |
| CI/CD | `.github/workflows/validate-notebooks.yml` | Notebook formatting + parameter validation |
| CI/CD | `.github/workflows/compile-kfp.yml` | KFP pipeline YAML compilation |
| CI/CD | `.github/workflows/execute-all-notebooks.yml` | GPU notebook execution (push to main) |
| CI/CD | `.github/workflows/execute-kfp-localrunners.yml` | KFP Docker local runner tests (PR + push) |
| Tests | `tests/test_notebook_parameters.py` | Notebook parameter cell validation |
| Tests | `tests/test_notebook_execution.py` | Notebook execution via papermill |
| Tests | `tests/conftest.py` | Shared test configuration |
| Config | `pyproject.toml` | Ruff + pytest config |
| Config | `.pre-commit-config.yaml` | ruff-format + nbstripout |
| Config | `Makefile` | Test and format targets |
| Container | `kubeflow-pipelines/docling-standard/Containerfile` | Docling standard image |
| Source | `kubeflow-pipelines/common/components.py` | Core KFP components (untested) |
| Source | `kubeflow-pipelines/common/constants.py` | Base image constants |
| Source | `scripts/subset_selection/` | Subset selection module (untested) |
| Docs | `docs/maintainers/release-strategy.md` | Release strategy documentation |
| GitHub | `.github/mergify.yml` | Auto-merge configuration |
| GitHub | `.github/dependabot.yml` | Dependency updates |
| GitHub | `.github/CODEOWNERS` | Review routing |
