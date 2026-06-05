---
repository: "opendatahub-io/training-notebooks"
overall_score: 8.2
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Good Python unit tests with pytest, Go tests for build tooling, but no coverage tracking"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Excellent multi-layer container testing with Testcontainers, Kubernetes integration, and Playwright browser tests"
  - dimension: "Build Integration"
    score: 8.5
    status: "PR builds include full image builds, Testcontainers validation, Kubernetes deployment testing, and Trivy scan"
  - dimension: "Image Testing"
    score: 9.5
    status: "Gold-standard image testing: ELF linkage, FIPS compliance, workbench startup, library smoke tests, accelerator checks"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "No coverage tracking tool (codecov/coveralls), no coverage thresholds or PR reporting"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "Mature CI/CD with matrix builds, concurrency control, caching, Konflux/Tekton pipelines, Renovate"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory — zero AI agent guidance"
critical_gaps:
  - title: "No test coverage tracking or enforcement"
    impact: "Cannot measure or enforce test coverage — regressions in coverage go undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No AI agent rules for test automation"
    impact: "AI-assisted development lacks guidance on test patterns, frameworks, and quality standards"
    severity: "MEDIUM"
    effort: "4-8 hours"
  - title: "No secret detection tooling (Gitleaks/TruffleHog)"
    impact: "Secrets accidentally committed to the repo may go undetected"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add pytest-cov and codecov integration"
    effort: "2-4 hours"
    impact: "Enable coverage tracking, threshold enforcement, and PR-level coverage reporting"
  - title: "Add Gitleaks secret detection to PR workflow"
    effort: "1-2 hours"
    impact: "Prevent accidental secret commits in PRs"
  - title: "Create basic CLAUDE.md with test automation guidance"
    effort: "2-3 hours"
    impact: "Improve AI-generated test quality and consistency for contributors using AI tools"
  - title: "Add CODEOWNERS file"
    effort: "1 hour"
    impact: "Ensure appropriate reviewers are auto-assigned to PRs based on file ownership"
recommendations:
  priority_0:
    - "Add pytest-cov coverage tracking with codecov integration and minimum threshold (e.g., 70%)"
    - "Add Gitleaks or TruffleHog secret detection to the PR workflow"
  priority_1:
    - "Create CLAUDE.md and .claude/rules/ with test automation guidance for Testcontainers patterns"
    - "Add CODEOWNERS for automated review assignment"
    - "Add mutation testing (mutmut) for critical test infrastructure code"
  priority_2:
    - "Add performance regression testing for image startup times"
    - "Create a test coverage dashboard for tracking trends over time"
    - "Add SBOM generation and signing for all published images"
---

# Quality Analysis: opendatahub-io/training-notebooks

## Executive Summary

- **Overall Score: 8.2/10**
- **Repository Type**: Container image build repository (Jupyter notebooks, workbenches, runtimes)
- **Primary Languages**: Python (64 files), Go (5 files), TypeScript (3 files)
- **Key Strengths**: Exceptional image testing infrastructure, multi-layer validation (Testcontainers + Kubernetes + Playwright + FIPS compliance), mature CI/CD with matrix builds and Konflux/Tekton integration
- **Critical Gaps**: No test coverage tracking, no AI agent rules, no secret detection
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Good pytest + Go tests, but no coverage tracking |
| Integration/E2E | 9.0/10 | Excellent Testcontainers + Kubernetes + Playwright tests |
| **Build Integration** | **8.5/10** | **Full PR-time image builds with Testcontainers + K8s testing** |
| Image Testing | 9.5/10 | Gold-standard: ELF linkage, FIPS, workbench startup, accelerator |
| Coverage Tracking | 2.0/10 | No coverage tool, thresholds, or reporting |
| CI/CD Automation | 9.0/10 | Matrix builds, concurrency, caching, Konflux/Tekton |
| Agent Rules | 0.0/10 | No AI agent guidance exists |

## Critical Gaps

### 1. No Test Coverage Tracking or Enforcement
- **Impact**: Cannot measure or enforce test coverage — regressions go undetected
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Despite having good test suites (27 Python test files, Go tests, TypeScript browser tests), there is no `pytest-cov`, no `.codecov.yml`, no coverage reporting in CI. Teams cannot see if a PR reduces test coverage.
- **Fix**: Add `pytest-cov` to dev dependencies, configure `.codecov.yml` with thresholds, add coverage upload step to `code-quality.yaml` workflow.

### 2. No AI Agent Rules for Test Automation
- **Impact**: AI-assisted development lacks structured guidance on test patterns and quality standards
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: No `CLAUDE.md`, `AGENTS.md`, or `.claude/` directory exists. Contributors using AI tools get no guidance on the repo's sophisticated Testcontainers patterns, pytest fixtures, or Kubernetes test infrastructure.

### 3. No Secret Detection Tooling
- **Impact**: Secrets accidentally committed may go undetected
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: While the repo uses `git-crypt` for encrypted secrets in `ci/secrets/`, there's no automated scanning (Gitleaks, TruffleHog) to catch accidentally committed secrets in PRs.

## Quick Wins

### 1. Add pytest-cov and Codecov Integration (2-4 hours)
Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "--cov=ci --cov=tests --cov-report=xml"
```
Add codecov upload step to `code-quality.yaml`.

### 2. Add Gitleaks Secret Detection (1-2 hours)
Add to `.github/workflows/code-quality.yaml`:
```yaml
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

### 3. Create Basic CLAUDE.md (2-3 hours)
Document test patterns, framework choices, and Testcontainers conventions for AI agent guidance.

### 4. Add CODEOWNERS File (1 hour)
Based on the existing `OWNERS` file, create `.github/CODEOWNERS` for automated review assignment.

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory** (20+ workflows):
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `build-notebooks-pr.yaml` | PR | Build changed images (matrix), run Testcontainers + K8s tests |
| `build-notebooks-pr-rhel.yaml` | PR (target) | Build RHEL images (contributor-gated) |
| `build-notebooks-push.yaml` | Push/Schedule/Dispatch | Build all images, push to GHCR |
| `build-notebooks-TEMPLATE.yaml` | Reusable | Template: build, test, Trivy scan, FIPS check, Playwright |
| `code-quality.yaml` | Push/PR | Pytest, pre-commit, YAML/JSON lint, Hadolint, Kustomize |
| `security.yaml` | Push/PR | Trivy filesystem scan, SARIF upload |
| `sec-scan.yml` | Schedule/Dispatch | Quay security vulnerability reporting |
| `docs.yaml` | - | Documentation generation |
| `create-release.yaml` | - | Release automation |
| `notebooks-digest-updater.yaml` | - | Digest update automation |

**Strengths**:
- Excellent matrix build strategy: generates build targets dynamically based on changed files
- Concurrency control with `cancel-in-progress: true`
- Build caching via GHCR (`--cache-from`, `--cache-to`)
- Smart path ignoring (skips builds for manifest-only changes)
- Reusable workflow template (`build-notebooks-TEMPLATE.yaml`) — DRY principle
- Contributor-gating for RHEL image builds (security-conscious)
- 69 Tekton pipeline definitions for Konflux integration
- Renovate (MintMaker) for automated dependency updates

**Areas for Improvement**:
- No test timing/performance tracking
- No flaky test detection mechanism

### Test Coverage

**Test Infrastructure** (27 Python test files):

| Test Layer | Files | Framework | Coverage |
|-----------|-------|-----------|----------|
| Unit tests (Python) | `tests/test_main.py` | pytest + pytest-subtests | Pipfile validation, file consistency, Makefile dry-run |
| Container tests | `tests/containers/*.py` | pytest + Testcontainers | Base image: ELF linkage, oc/skopeo, pip, FIPS, permissions |
| Workbench tests | `tests/containers/workbenches/*.py` | pytest + Testcontainers | Entrypoint startup, IPv6, OpenShift deployment |
| JupyterLab tests | `tests/containers/workbenches/jupyterlab/*.py` | pytest + Testcontainers + allure | Spinner HTML, PDF export, mongocli, scikit-learn, MySQL, libraries |
| Runtime tests | `tests/containers/runtimes/*.py` | pytest + Testcontainers | pyzmq import validation |
| Accelerator tests | `tests/containers/workbenches/accelerator_image_test.py` | pytest + K8s | CUDA/ROCm GPU validation on OpenShift |
| Browser tests | `tests/browser/tests/*.spec.ts` | Playwright + Testcontainers | Code-server editor, terminal, file operations |
| Go tests | `scripts/buildinputs/buildinputs_test.go` | Go testing | Dockerfile parsing validation |
| Notebook tests | `jupyter/*/test/test_notebook.ipynb` (13 files) | Papermill | Notebook execution validation per image variant |

**Test Markers** (from `pytest.ini`):
- `openshift` — requires OpenShift cluster
- `cuda` — requires CUDA hardware
- `rocm` — requires ROCm hardware

**Strengths**:
- Multi-layer testing approach covering unit, container, integration, browser, and deployment
- Testcontainers for portable, reproducible container testing
- Allure reporting integration for issue tracking (`@allure.issue`)
- Pytest subtests for granular failure reporting
- Kubernetes deployment testing with kubeadm + cri-o in CI
- Pydantic schemas for test data validation
- Custom fixtures for image type detection (workbench, runtime, cuda, rocm, etc.)

**Weaknesses**:
- No coverage measurement (`pytest-cov` not in dependencies)
- No coverage thresholds or enforcement
- No mutation testing

### Code Quality

**Linting & Static Analysis**:
- **Ruff**: Comprehensive configuration with 25+ rule sets (B, C4, COM, E, W, F, FA, FLY, G, I, INP, INT, ISC, N, PERF, PGH, PIE, PL, PYI, Q, RET, RUF, S102, T10, TCH, TID, UP, YTT)
- **Pyright**: Type checking configured with `typeCheckingMode = "off"` but key checks enabled (`reportMissingImports`, `reportUnboundVariable`, `reportGeneralTypeIssues`)
- **Hadolint**: Dockerfile linting with custom config
- **yamllint**: YAML validation with strict mode
- **json_verify**: JSON syntax validation for `.json`, `Pipfile.lock`, and `.ipynb` files

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- `uv-lock` — Lock file consistency
- `ruff` — Linting with auto-fix
- `ruff-format` — Code formatting
- `pyright` — Type checking

**Code Review**:
- CodeRabbit AI review configured (`.coderabbit.yaml`)
- Auto-review on PRs to `main` and `2024b` branches

**Strengths**:
- Excellent Ruff configuration with many rule categories
- Pre-commit hooks enforced in CI (not just local)
- Hadolint for Dockerfile quality
- CodeRabbit for automated code review
- `.editorconfig` for consistent formatting

### Container Images

**Image Matrix** (38 Dockerfiles):
| Category | Variants | Platforms |
|----------|----------|-----------|
| JupyterLab Minimal | Python 3.11/3.12 | CPU, CUDA, ROCm |
| JupyterLab DataScience | Python 3.11/3.12 | CPU |
| JupyterLab PyTorch | Python 3.11/3.12 | CUDA |
| JupyterLab TensorFlow | Python 3.11/3.12 | CUDA |
| JupyterLab TrustyAI | Python 3.11/3.12 | CPU |
| JupyterLab ROCm PyTorch | Python 3.11/3.12 | ROCm |
| JupyterLab ROCm TensorFlow | Python 3.11 | ROCm |
| Code Server | Python 3.11/3.12 | CPU |
| RStudio | Python 3.11 | CPU, CUDA (c9s + rhel9) |
| Runtime Minimal/DataScience | Python 3.11/3.12 | CPU |
| Runtime PyTorch/TensorFlow | Python 3.11/3.12 | CUDA, ROCm |
| PyTorch+LLMCompressor | Python 3.11 | CUDA |

**Build Process**:
- Multi-architecture support (amd64, arm64, s390x, ppc64le via QEMU)
- Build caching via GHCR container cache
- Smart changed-file detection for selective builds
- Sandbox build with `scripts/sandbox.py`
- Go-based Dockerfile dependency analysis (`scripts/buildinputs/`)

**Image Testing Pipeline** (in `build-notebooks-TEMPLATE.yaml`):
1. **Build**: Podman build with caching
2. **Testcontainers**: pytest container tests (base + workbench + runtime)
3. **Kubernetes**: kubeadm cluster → deploy via kustomize → notebook execution with Papermill
4. **OpenShift**: OpenShift-specific container tests
5. **Trivy**: Vulnerability scanning (image or filesystem scan)
6. **FIPS**: check-payload for FIPS compliance
7. **Playwright**: Browser tests for code-server images

**Strengths**:
- **Gold-standard image testing** — among the best in the ODH ecosystem
- Multi-architecture support including s390x
- FIPS compliance validation with `check-payload`
- Runtime validation with actual Kubernetes deployment
- Browser-level testing with Playwright
- Trivy vulnerability scanning integrated into build pipeline

### Security

| Tool | Status | Details |
|------|--------|---------|
| Trivy (filesystem scan) | Active | On push/PR, uploads SARIF to GitHub Security tab |
| Trivy (image scan) | Active | In build pipeline, label-triggered for PRs, scheduled |
| check-payload (FIPS) | Active | FIPS compliance validation on all built images |
| Quay Security Scan | Active | Scheduled vulnerability reporting |
| git-crypt | Active | Encrypted secrets for RHEL subscriptions |
| CodeQL/SAST | Missing | No CodeQL or static security analysis |
| Gitleaks | Missing | No secret detection in PRs |
| SBOM Generation | Partial | Tekton pipelines include SBOM, GHA builds do not |
| Image Signing | Partial | Tekton pipelines include signing, GHA builds do not |

**Strengths**:
- Trivy integration at both filesystem and image level
- FIPS compliance checking — rare and valuable
- Contributor-gating for RHEL builds (security-conscious)
- git-crypt for secret management

**Gaps**:
- No CodeQL or SAST beyond Trivy
- No Gitleaks or TruffleHog for secret detection in PRs
- SBOM and image signing only in Tekton pipelines, not GHA

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**:
  - No test creation rules for Testcontainers patterns
  - No guidance on pytest fixture usage (workbench_image, runtime_image, etc.)
  - No Kubernetes test deployment patterns documented for agents
  - No Playwright test pattern guidance
  - No allure issue annotation conventions
- **Recommendation**: Generate comprehensive agent rules using `/test-rules-generator` covering:
  - Testcontainers container test patterns
  - pytest fixture conventions and markers
  - Kubernetes deployment test patterns
  - Playwright browser test patterns
  - allure reporting conventions

## Recommendations

### Priority 0 (Critical)

1. **Add pytest-cov coverage tracking with codecov integration**
   - Add `pytest-cov` to dev dependencies
   - Configure coverage collection in pytest
   - Add `.codecov.yml` with minimum threshold (e.g., 70%)
   - Add coverage upload to `code-quality.yaml`
   - Effort: 4-6 hours

2. **Add secret detection to PR workflow**
   - Add Gitleaks action to `code-quality.yaml`
   - Create `.gitleaks.toml` to exclude `ci/secrets/` (already encrypted)
   - Effort: 2-3 hours

### Priority 1 (High Value)

3. **Create comprehensive agent rules**
   - Create `CLAUDE.md` documenting repo structure, test patterns, and conventions
   - Create `.claude/rules/` with test creation rules for Testcontainers, Kubernetes, and Playwright patterns
   - Effort: 4-8 hours

4. **Add CODEOWNERS file**
   - Based on existing `OWNERS` file and contributor list in `build-notebooks-pr-rhel.yaml`
   - Effort: 1 hour

5. **Add mutation testing for critical code**
   - Add `mutmut` for Python test infrastructure code (`ci/`, `tests/`)
   - Focus on build matrix generation and test fixtures
   - Effort: 4-6 hours

### Priority 2 (Nice-to-Have)

6. **Add CodeQL static analysis**
   - Enable GitHub CodeQL for Python and Go code
   - Effort: 2-3 hours

7. **Add SBOM generation to GHA builds**
   - Bring GHA builds to parity with Tekton pipeline SBOM generation
   - Effort: 4-6 hours

8. **Track image startup performance**
   - Add timing metrics to Testcontainers workbench startup tests
   - Detect performance regressions in PR builds
   - Effort: 4-6 hours

## Comparison to Gold Standards

| Dimension | training-notebooks | odh-dashboard | notebooks (parent) | Best Practice |
|-----------|--------------------|---------------|-------------------|---------------|
| Unit Tests | pytest + Go testing | Jest + React Testing | pytest | All strong |
| Integration Tests | Testcontainers + K8s | Cypress + API tests | Testcontainers | training-notebooks excels |
| Browser Tests | Playwright | Cypress | None | training-notebooks good |
| Image Testing | 7-layer pipeline | N/A | 5-layer pipeline | **training-notebooks is gold standard** |
| Coverage Tracking | None | Codecov | None | odh-dashboard leads |
| CI Caching | GHCR cache | npm cache | GHCR cache | All adequate |
| Security Scanning | Trivy + FIPS | CodeQL + Snyk | Trivy | training-notebooks strong |
| Pre-commit | ruff + pyright + uv-lock | ESLint + Prettier | ruff | All adequate |
| Agent Rules | None | Comprehensive | None | odh-dashboard leads |
| Dependency Updates | Renovate/MintMaker | Dependabot | Renovate | All adequate |

## File Paths Reference

### CI/CD
- `.github/workflows/build-notebooks-pr.yaml` — PR build workflow
- `.github/workflows/build-notebooks-TEMPLATE.yaml` — Reusable build template (contains 7-layer test pipeline)
- `.github/workflows/code-quality.yaml` — Static analysis, pytest, pre-commit
- `.github/workflows/security.yaml` — Trivy filesystem scan
- `.github/workflows/sec-scan.yml` — Quay vulnerability reporting
- `.tekton/` — 69 Tekton/Konflux pipeline definitions

### Testing
- `tests/test_main.py` — Unit tests for Pipfiles, file consistency, Makefile
- `tests/containers/conftest.py` — Core Testcontainers fixtures and image metadata
- `tests/containers/base_image_test.py` — Base image tests (ELF, oc, FIPS, permissions)
- `tests/containers/workbenches/workbench_image_test.py` — Workbench startup and IPv6 tests
- `tests/containers/workbenches/jupyterlab/` — JupyterLab-specific tests (spinner, PDF, libraries)
- `tests/containers/workbenches/accelerator_image_test.py` — CUDA/ROCm GPU tests
- `tests/containers/runtimes/runtime_test.py` — Runtime image tests
- `tests/browser/tests/codeserver.spec.ts` — Playwright browser tests for code-server
- `scripts/buildinputs/buildinputs_test.go` — Go tests for Dockerfile parser

### Code Quality
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff, pyright, uv-lock)
- `pyproject.toml` — Ruff and Pyright configuration
- `ci/hadolint-config.yaml` — Dockerfile linting
- `ci/yamllint-config.yaml` — YAML linting
- `.coderabbit.yaml` — CodeRabbit AI review configuration
- `.editorconfig` — Editor consistency settings

### Container Images
- `jupyter/*/Dockerfile.*` — JupyterLab image definitions
- `runtimes/*/Dockerfile.*` — Runtime image definitions
- `codeserver/*/Dockerfile.*` — Code-server image definitions
- `rstudio/*/Dockerfile.*` — RStudio image definitions
- `.dockerignore` — Build context exclusions

### Security
- `.github/workflows/security.yaml` — Trivy scan configuration
- `ci/secrets/` — git-crypt encrypted secrets
- `scripts/check-payload/` — FIPS compliance tooling
- `.github/renovate.json` — Dependency update configuration
