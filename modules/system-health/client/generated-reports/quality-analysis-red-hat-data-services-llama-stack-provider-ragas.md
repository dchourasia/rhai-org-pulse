---
repository: "red-hat-data-services/llama-stack-provider-ragas"
overall_score: 4.4
scorecard:
  - dimension: "Unit Tests"
    score: 3.0
    status: "No unit tests — all 4 test files are integration tests requiring live services"
  - dimension: "Integration/E2E"
    score: 6.0
    status: "Good integration test structure with pytest markers, but all require live Llama Stack + Kubeflow cluster"
  - dimension: "Build Integration"
    score: 2.0
    status: "No PR-time image build, no Konflux simulation, no container validation in CI"
  - dimension: "Image Testing"
    score: 1.5
    status: "Two container files exist but no image build or runtime validation in any workflow"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "pytest-cov in dev deps but no coverage generation, no codecov, no thresholds"
  - dimension: "CI/CD Automation"
    score: 4.5
    status: "Pre-commit checks on PRs; release workflow with smoke tests; no test execution in CI"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude directory, no agent rules of any kind"
critical_gaps:
  - title: "No tests execute in CI"
    impact: "PRs merge without any automated test validation — only pre-commit linting/formatting runs"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Zero unit tests"
    impact: "All test files are integration tests requiring live Llama Stack server and Kubeflow cluster; nothing validates core logic in isolation"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No visibility into what code is covered; regressions go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image build or validation in CI"
    impact: "Containerfile and Dockerfile.konflux changes are never tested before merge; broken images discovered post-deployment"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning"
    impact: "No Trivy, Snyk, CodeQL, or dependency scanning; vulnerabilities in 30+ transitive dependencies go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI-generated code has no project-specific quality guardrails"
    severity: "MEDIUM"
    effort: "3-4 hours"
quick_wins:
  - title: "Add unit tests for core logic (config, constants, compat, errors)"
    effort: "4-6 hours"
    impact: "Immediate validation of business logic without external dependencies"
  - title: "Run unit tests in CI workflow"
    effort: "1-2 hours"
    impact: "Every PR gets automated test feedback; currently CI only runs linting"
  - title: "Add codecov integration with pytest-cov"
    effort: "2-3 hours"
    impact: "Visibility into coverage with PR comments; pytest-cov already in dev deps"
  - title: "Add Trivy container scanning to CI"
    effort: "1-2 hours"
    impact: "Automated vulnerability detection for container images"
  - title: "Add basic agent rules (.claude/rules/)"
    effort: "2-3 hours"
    impact: "Consistent AI-generated code quality with project-specific patterns"
recommendations:
  priority_0:
    - "Add unit tests for config.py, constants.py, compat.py, errors.py, logging_utils.py, and provider.py — these modules have zero test coverage and can be tested without external services"
    - "Add a 'test' job to ci.yml that runs pytest with -m 'not integration_test' — the marker infrastructure already exists"
    - "Enable coverage reporting: add pytest-cov to CI, configure codecov.yml, set minimum threshold (e.g., 60%)"
  priority_1:
    - "Add container image build validation to PR workflow — build both Containerfile and Dockerfile.konflux and verify image startup"
    - "Add Trivy or Snyk scanning for container images and Python dependencies"
    - "Add CodeQL or Semgrep SAST scanning to the CI workflow"
    - "Create .claude/rules/ with unit-tests.md and integration-tests.md agent rules"
  priority_2:
    - "Add concurrency control to CI workflow to cancel superseded runs"
    - "Add type checking (mypy) to CI — mypy config exists in pyproject.toml but isn't enforced in workflows"
    - "Add SBOM generation for container images"
    - "Add multi-architecture image builds (amd64/arm64)"
---

# Quality Analysis: llama-stack-provider-ragas

## Executive Summary
- **Overall Score: 4.4/10**
- **Repository Type**: Python library — Ragas evaluation as an out-of-tree Llama Stack provider
- **Primary Language**: Python 3.12
- **Key Strengths**: Good pre-commit configuration (ruff, mypy, pytest), clean project structure with clear inline/remote separation, solid release workflow with smoke tests, well-defined integration test markers
- **Critical Gaps**: No tests run in CI (only linting), zero unit tests, no coverage tracking, no container image validation, no security scanning
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 3.0/10 | No unit tests — all 4 test files are integration tests requiring live services |
| Integration/E2E | 6.0/10 | Good structure with pytest markers but all need live Llama Stack + Kubeflow |
| **Build Integration** | **2.0/10** | **No PR-time image build, no Konflux simulation, no container validation** |
| Image Testing | 1.5/10 | Two container files exist but zero image validation in any workflow |
| Coverage Tracking | 1.0/10 | pytest-cov in deps but never used; no codecov, no thresholds |
| CI/CD Automation | 4.5/10 | Pre-commit on PR, release with smoke tests, but no test execution |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude directory, no test automation guidance |

## Critical Gaps

### 1. No Tests Execute in CI
- **Impact**: PRs merge with only pre-commit linting — no functional validation whatsoever
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The `ci.yml` workflow only runs `pre-commit run --all-files`. Despite having 4 test files and a pytest marker system (`integration_test`), no pytest execution occurs in CI. The pre-commit config includes a local pytest hook, but this only runs locally and uses `KUBEFLOW_BASE_IMAGE=dummy` as a workaround.

### 2. Zero Unit Tests
- **Impact**: Core business logic (config parsing, metric mapping, compatibility layer, error handling) has no isolated test coverage
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: All 4 test files (`test_inline_evaluation.py`, `test_remote_evaluation.py`, `test_remote_wrappers.py`, `test_kubeflow_integration.py`) are marked `pytestmark = pytest.mark.integration_test` and require:
  - A running Llama Stack server
  - Kubeflow Pipelines cluster
  - S3 credentials
  - GPU-capable models

  The 15 source files (1,724 LOC) have zero unit test coverage. Modules like `config.py`, `constants.py`, `compat.py`, `errors.py`, and `logging_utils.py` could be tested entirely in isolation.

### 3. No Coverage Tracking or Enforcement
- **Impact**: No visibility into what code is covered; regressions go completely undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `pytest-cov` is listed in dev dependencies but never configured or used. No `.codecov.yml`, no `.coveragerc`, no coverage thresholds. Test-to-code ratio is approximately 0.32:1 (559 test LOC / 1,724 source LOC), but this is misleading since all tests are integration tests that don't run in CI.

### 4. No Container Image Build or Validation in CI
- **Impact**: Broken container images discovered only after merge or in Konflux builds
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The repo has two container files:
  - `Containerfile` — uses `python:3.12` base, installs `.[remote]`
  - `Dockerfile.konflux` — uses `registry.redhat.io/ubi9/python-312` with pinned SHA, installs base package
  
  Neither is built or tested in any CI workflow. The Konflux Dockerfile is particularly concerning as it only installs the base package (not `.[remote]`), and this difference from the development Containerfile is never validated.

### 5. No Security Scanning
- **Impact**: Vulnerabilities in 30+ transitive Python dependencies go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No Trivy, Snyk, CodeQL, Gitleaks, or any SAST/DAST tool is configured. The project has a large dependency tree (aiohttp, cryptography, openai, langchain, etc.) with known CVE surface area. No `.gitleaks.toml`, no `.trivyignore`.

### 6. No Agent Rules
- **Impact**: AI-assisted development has no project-specific guardrails
- **Severity**: MEDIUM
- **Effort**: 3-4 hours
- **Details**: No `CLAUDE.md`, no `AGENTS.md`, no `.claude/` directory. Contributors using AI coding tools receive no guidance on:
  - Test patterns (integration vs unit, marker usage)
  - Pydantic config patterns used throughout
  - The inline/remote provider architecture
  - Kubeflow pipeline component conventions

## Quick Wins

### 1. Run Unit Tests in CI (1-2 hours)
Add a `test` job to `ci.yml` that executes pytest excluding integration tests:

```yaml
test:
  name: Unit Tests
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    - uses: astral-sh/setup-uv@v4
      with:
        version: "0.8.11"
    - run: uv sync --extra dev
    - run: |
        KUBEFLOW_BASE_IMAGE=dummy uv run pytest -v \
          -m "not integration_test" \
          --cov=src/llama_stack_provider_ragas \
          --cov-report=xml \
          --tb=short
```

### 2. Add Codecov Integration (2-3 hours)
`pytest-cov` is already in dev dependencies. Add:
- A `codecov.yml` with minimum coverage threshold
- Upload step in CI after test execution
- PR comment integration for coverage diff

### 3. Add Trivy Container Scanning (1-2 hours)
```yaml
security-scan:
  name: Security Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        severity: 'CRITICAL,HIGH'
```

### 4. Write Unit Tests for Core Modules (4-6 hours)
Priority targets for unit testing:
- `config.py` — validate Pydantic model construction, defaults, SecretStr handling
- `constants.py` — verify metric mappings, provider IDs
- `compat.py` — test compatibility shims
- `errors.py` — test custom exception types
- `logging_utils.py` — test dataframe rendering
- `provider.py` — test provider spec generation with/without remote deps

### 5. Add Basic Agent Rules (2-3 hours)
Create `.claude/rules/unit-tests.md` and `.claude/rules/integration-tests.md` with patterns specific to this project.

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory**:
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push/PR to main, develop | Pre-commit checks (ruff, mypy, trailing whitespace) |
| `docs.yml` | push/PR to main (docs paths only) | Build and deploy Antora documentation to GitHub Pages |
| `release.yaml` | release published | Build package, smoke test, publish to PyPI |

**Strengths**:
- Release workflow has excellent smoke testing: tests both wheel and sdist before publishing, then verifies PyPI install
- Good use of `uv` for fast, deterministic dependency management
- Dependency caching in CI (`~/.cache/uv`, `.venv`)
- Documentation has its own workflow with path filtering

**Weaknesses**:
- CI only runs pre-commit — no pytest execution
- No concurrency control on CI workflow (PRs can pile up)
- No test matrix (single Python version: 3.12)
- No branch protection verification

**Mergify Configuration**: Automated backport from `main` → `incubation` → `stable` via Mergify. Skips `.tekton/`-only changes for stable sync. This is well-designed for the multi-branch release strategy.

**Pull Sync**: Configured to pull from `trustyai-explainability:main` upstream, indicating this is a downstream fork (`red-hat-data-services` is a downstream of `trustyai-explainability`).

### Test Coverage

**Test Files** (5 files, 559 LOC):
| File | Type | Requirements |
|------|------|-------------|
| `conftest.py` | Fixtures | Llama Stack client, Kubeflow config (env vars) |
| `test_inline_evaluation.py` | Integration | Running Llama Stack server |
| `test_remote_evaluation.py` | Integration | Running Llama Stack + Kubeflow |
| `test_remote_wrappers.py` | Integration | Running Llama Stack + Kubeflow |
| `test_kubeflow_integration.py` | Integration | Running Kubeflow cluster + KFP client |

**Positive Observations**:
- All integration tests properly marked with `pytest.mark.integration_test`
- Good use of parametrized tests for metric validation
- Async test support via `pytest-asyncio`
- Well-structured conftest with reusable fixtures
- Tests validate both sync and async code paths

**Negative Observations**:
- Zero unit tests for 15 source files
- All tests require external services — can't run in standard CI
- Test-to-code ratio: 0.32:1 (misleadingly high since tests don't run)
- No mocking of external dependencies for unit-level validation
- Commented-out metrics in tests (`context_precision, faithfulness, context_recall`)

### Code Quality

**Pre-commit Configuration** (Strong):
- `pre-commit-hooks`: trailing-whitespace, end-of-file-fixer, check-yaml, large files, merge conflicts, debug statements
- `ruff`: lint check with auto-fix + formatting (E, W, F, I, B, C4, UP rules)
- `mypy`: type checking with `--ignore-missing-imports`, types-requests
- Local `pytest` hook: runs non-integration tests locally

**Linting (Good)**:
- Ruff configured in `pyproject.toml` with 7 rule categories (pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade)
- Sensible ignores (E501 line length, B008 function calls in defaults, C901 complexity)
- Target version: Python 3.12

**Type Checking (Moderate)**:
- mypy configured with reasonable strictness: `warn_return_any`, `warn_unused_configs`, `check_untyped_defs`, `strict_equality`
- But `disallow_untyped_defs = false` and `disallow_incomplete_defs = false` — so untyped functions pass
- `ignore_missing_imports = true` weakens external type checking
- mypy runs in pre-commit but NOT in CI workflow

### Container Images

**Containerfile** (Development):
- Simple single-stage build from `python:3.12`
- Installs `.[remote]` extra
- No multi-stage build, no user creation, no health check
- No `.dockerignore` optimization (includes `.github`, `.vscode`)

**Dockerfile.konflux** (Production):
- Based on `registry.redhat.io/ubi9/python-312` with pinned SHA digest
- Installs base package only (no `[remote]` extra) — inconsistency with dev Containerfile
- Proper Red Hat labels (component, description, license)
- No health check, no user creation, no multi-stage build

**Critical Issue**: The Konflux Dockerfile installs only the base package (`pip install -e .`) while the development Containerfile installs with remote extras (`pip install -e ".[remote]"`). This difference is never validated in CI.

### Security

**No security scanning of any kind**:
- No Trivy/Snyk for container images
- No CodeQL/Semgrep for static analysis
- No Gitleaks for secret detection
- No dependency vulnerability scanning
- No SBOM generation
- The `requirements.txt` with pinned hashes is good for reproducibility but no automated audit

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test type rules, no development guidelines
- **Quality**: N/A
- **Gaps**: Complete absence — no CLAUDE.md, no AGENTS.md, no `.claude/` directory
- **Recommendation**: Generate comprehensive rules with `/test-rules-generator` covering:
  - Unit test patterns for Pydantic models and provider logic
  - Integration test patterns with pytest markers
  - Kubeflow pipeline component testing conventions
  - Mock patterns for Llama Stack client interactions

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests for core modules** — `config.py`, `constants.py`, `compat.py`, `errors.py`, `logging_utils.py`, `provider.py` can all be tested without external services. Target: 60% coverage of `src/` directory.

2. **Add pytest execution to CI workflow** — Add a `test` job to `ci.yml` that runs `pytest -m "not integration_test"` with coverage reporting. The marker infrastructure already exists.

3. **Enable coverage tracking** — Configure `pytest-cov` (already in deps) with codecov integration and set a minimum coverage threshold to prevent regression.

### Priority 1 (High Value)

4. **Add container image build validation** — Build both `Containerfile` and `Dockerfile.konflux` in PR CI to catch build failures before merge. Verify the Konflux image installs correctly.

5. **Add security scanning** — Trivy filesystem scan for Python dependencies + container image scan. Add to CI workflow.

6. **Add CodeQL or Semgrep** — Static analysis for Python code to catch security anti-patterns.

7. **Create agent rules** — Add `.claude/rules/` with guidelines for unit tests, integration tests, and project-specific patterns.

### Priority 2 (Nice-to-Have)

8. **Add concurrency control** to CI workflow to cancel superseded PR runs.

9. **Run mypy in CI** — It's configured in pyproject.toml and pre-commit but not enforced in the CI workflow itself.

10. **Add SBOM generation** for container images.

11. **Add multi-arch builds** (amd64/arm64) for container images.

12. **Consider adding contract tests** between the inline and remote provider implementations to ensure API compatibility.

## Comparison to Gold Standards

| Dimension | llama-stack-provider-ragas | odh-dashboard | notebooks | kserve |
|-----------|---------------------------|---------------|-----------|--------|
| Unit Tests | 3.0 — None exist | 9.0 — Jest/Vitest, 70%+ | 7.0 — Python unit tests | 8.5 — Go testing, envtest |
| Integration/E2E | 6.0 — Good markers, need infra | 9.0 — Cypress E2E | 8.0 — Multi-version | 9.0 — Multi-version |
| Build Integration | 2.0 — No PR builds | 8.0 — Multi-mode | 7.0 — Image builds | 7.5 — Operator builds |
| Image Testing | 1.5 — Files only | 8.0 — Testcontainers | 9.0 — 5-layer validation | 7.0 — Runtime tests |
| Coverage | 1.0 — Not configured | 9.0 — Codecov + gates | 6.0 — Basic coverage | 8.0 — Enforcement |
| CI/CD | 4.5 — Lint + release | 9.5 — Full pipeline | 8.0 — Matrix builds | 9.0 — Comprehensive |
| Agent Rules | 0.0 — None | 8.0 — Comprehensive | 3.0 — Minimal | 2.0 — Minimal |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` — Pre-commit checks (linting, formatting, type checking)
- `.github/workflows/docs.yml` — Antora documentation build and deploy
- `.github/workflows/release.yaml` — PyPI release with smoke tests
- `.github/pull.yml` — Upstream sync configuration
- `.mergify.yml` — Automated backport rules (main → incubation → stable)

### Testing
- `tests/conftest.py` — Shared fixtures (Llama Stack client, Kubeflow config, sample data)
- `tests/test_inline_evaluation.py` — Inline provider integration tests
- `tests/test_remote_evaluation.py` — Remote provider integration tests
- `tests/test_remote_wrappers.py` — Remote LLM/embeddings wrapper integration tests
- `tests/test_kubeflow_integration.py` — Kubeflow pipeline integration tests

### Code Quality
- `pyproject.toml` — Ruff lint/format config, mypy config, pytest config
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff, mypy, pytest, standard hooks)

### Container Images
- `Containerfile` — Development container (python:3.12 + [remote])
- `Dockerfile.konflux` — Production container (UBI9/python-312)
- `.dockerignore` — Docker build exclusions

### Source Code
- `src/llama_stack_provider_ragas/` — Main package (15 Python files, 1,724 LOC)
- `src/llama_stack_provider_ragas/inline/` — Inline evaluation provider
- `src/llama_stack_provider_ragas/remote/` — Remote evaluation provider (Kubeflow)
- `src/llama_stack_provider_ragas/remote/kubeflow/` — Kubeflow pipeline components
