---
repository: "opendatahub-io/llama-stack-provider-ragas"
overall_score: 2.2
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "No unit tests exist; all 4 test files are integration-only requiring live Llama Stack and Kubeflow infrastructure"
  - dimension: "Integration/E2E"
    score: 4.0
    status: "4 integration test files with good pytest fixtures and parametrize, but all require live infrastructure and none run in CI"
  - dimension: "Build Integration"
    score: 1.0
    status: "No PR-time container build, no Konflux simulation, no manifest validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "Basic single-stage Containerfile exists but no image build in CI, no vulnerability scanning, no runtime validation"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "pytest-cov listed in dev dependencies but never configured or executed; no codecov integration or thresholds"
  - dimension: "CI/CD Automation"
    score: 3.0
    status: "Pre-commit checks (ruff, mypy) run in CI but pytest collects 0 tests and silently passes; release workflow has good smoke tests"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules or test automation guidance"
critical_gaps:
  - title: "Zero tests execute in CI"
    impact: "The CI pre-commit pytest step runs with '-m not integration_test' but ALL tests are marked integration_test, so 0 tests run. Exit code 5 (no tests collected) is silently treated as success. Regressions are never caught."
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No unit tests exist"
    impact: "1,754 lines of source code with zero unit test coverage. Core logic (config parsing, metric mapping, evaluation wrappers, pipeline construction) has no fast-feedback testing."
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No container image security scanning"
    impact: "Containerfile uses full python:3.12 base image with no vulnerability scanning. Known CVEs could ship to production undetected."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No way to measure or enforce test coverage. Coverage can silently decrease with every PR."
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No dependency vulnerability scanning"
    impact: "191KB requirements.txt with many transitive dependencies. No Dependabot, Renovate, or Snyk to flag vulnerable packages."
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add unit tests for config.py, constants.py, compat.py, and errors.py"
    effort: "4-6 hours"
    impact: "Immediate test coverage for core modules that need no live infrastructure; pytest will actually collect and run tests in CI"
  - title: "Enable Dependabot for dependency vulnerability scanning"
    effort: "30 minutes"
    impact: "Automatic PRs for vulnerable dependencies across 190+ transitive packages"
  - title: "Add Trivy container scanning to CI workflow"
    effort: "1-2 hours"
    impact: "Detect CVEs in the python:3.12 base image and installed packages before release"
  - title: "Configure codecov integration with pytest-cov"
    effort: "2-3 hours"
    impact: "Coverage tracking already partially set up (pytest-cov in deps); just needs wiring"
  - title: "Add concurrency control to CI workflow"
    effort: "15 minutes"
    impact: "Prevent redundant CI runs on rapid pushes to the same PR"
recommendations:
  priority_0:
    - "Write unit tests for all non-integration modules (config, constants, compat, errors, logging_utils, inline/wrappers_inline) so CI actually tests something"
    - "Fix the CI silent-pass bug: either add real unit tests or remove the false-positive pytest step that masks zero coverage"
    - "Add Trivy or Snyk scanning for the Containerfile to catch CVEs before release"
  priority_1:
    - "Configure codecov with pytest-cov and set minimum coverage thresholds (suggest 60% initially)"
    - "Add Dependabot or Renovate for automated dependency updates and vulnerability alerts"
    - "Improve Containerfile: use multi-stage build, non-root user, and minimal base image"
    - "Add PR-time container build validation to catch build failures before merge"
  priority_2:
    - "Create CLAUDE.md and .claude/rules/ with test creation guidance for AI-assisted development"
    - "Add CodeQL or Semgrep SAST scanning workflow"
    - "Add integration test CI job that runs on a schedule against a test cluster"
    - "Add SBOM generation and image signing to the release workflow"
---

# Quality Analysis: llama-stack-provider-ragas

## Executive Summary

- **Overall Score: 2.2/10**
- **Repository Type**: Python library (out-of-tree Llama Stack evaluation provider using Ragas)
- **Language**: Python 3.12 with uv/hatchling
- **Source**: 1,754 lines across 19 Python modules
- **Tests**: 559 lines across 4 test files + conftest (ALL integration-only)

**Key Strengths:**
- Well-structured pre-commit hooks with ruff, mypy, and formatting checks
- Good CONTRIBUTING.md with clear development workflow documentation
- Release workflow includes wheel and sdist smoke tests
- Integration tests demonstrate thorough understanding of test patterns (parametrize, fixtures, async)

**Critical Gaps:**
- **Zero tests run in CI** — the pytest step silently passes with 0 tests collected
- No unit tests exist for any module
- No container security scanning, no coverage tracking, no dependency scanning
- No agent rules for AI-assisted development

**Agent Rules Status:** Missing — no CLAUDE.md, no `.claude/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1/10 | No unit tests; all tests are integration-only |
| Integration/E2E | 4/10 | 4 test files exist but require live infra; none run in CI |
| **Build Integration** | **1/10** | **No PR-time build, no Konflux simulation** |
| Image Testing | 1/10 | Basic Containerfile, no scanning or runtime validation |
| Coverage Tracking | 1/10 | pytest-cov in deps but never used |
| CI/CD Automation | 3/10 | Pre-commit in CI is good but pytest is a no-op |
| Agent Rules | 0/10 | No agent rules or test automation guidance |

## Critical Gaps

### 1. Zero Tests Execute in CI (Severity: HIGH)

The CI workflow runs pre-commit which includes a pytest hook:

```yaml
# .pre-commit-config.yaml (line 27-34)
- id: pytest
  entry: bash
  args: [-c, 'KUBEFLOW_BASE_IMAGE=dummy uv run pytest -v -m "not integration_test" --tb=short --maxfail=3; ret=$?; [ $ret = 5 ] && exit 0 || exit $ret']
```

**Problem**: ALL 4 test files are marked `pytestmark = pytest.mark.integration_test`, so `pytest -m "not integration_test"` collects **zero tests**. Exit code 5 (no tests) is explicitly treated as success (`[ $ret = 5 ] && exit 0`).

- **Impact**: Regressions are never caught. The CI gives a false sense of safety.
- **Effort**: 8-16 hours to write real unit tests that can run without infrastructure.

### 2. No Unit Tests Exist (Severity: HIGH)

1,754 lines of source code with zero unit test coverage:

| Module | Lines | Testable Without Infra | Current Tests |
|--------|-------|----------------------|---------------|
| `config.py` | Config models | Yes (Pydantic) | None |
| `constants.py` | Metric mappings | Yes (static) | None |
| `compat.py` | Compatibility layer | Yes (pure logic) | None |
| `errors.py` | Error classes | Yes (trivial) | None |
| `logging_utils.py` | DataFrame rendering | Yes (pure logic) | None |
| `inline/wrappers_inline.py` | Inline wrappers | Yes (with mocks) | None |
| `inline/provider.py` | Provider interface | Partially (with mocks) | None |
| `remote/wrappers_remote.py` | Remote wrappers | Partially (with mocks) | None |

- **Impact**: Any change to core logic ships without validation.
- **Effort**: 16-24 hours for initial unit test suite.

### 3. No Container Image Security Scanning (Severity: HIGH)

The `Containerfile` uses `python:3.12` (full Debian-based image) with no vulnerability scanning:

```dockerfile
FROM python:3.12
WORKDIR /usr/local/src/kfp/components
COPY . .
RUN pip install --no-cache-dir -e ".[remote]"
```

**Issues:**
- Full base image (not slim/distroless) includes unnecessary packages and larger attack surface
- No Trivy/Snyk scanning in any workflow
- No multi-stage build to minimize final image size
- No non-root user (`USER` directive missing)
- No `HEALTHCHECK` instruction
- pip used instead of uv (inconsistent with development workflow)

### 4. No Coverage Tracking (Severity: MEDIUM)

`pytest-cov` is listed in `[project.optional-dependencies.dev]` but:
- No `.coveragerc` or `[tool.coverage]` configuration
- No `--cov` flag in CI pytest invocation
- No codecov/coveralls integration
- No coverage thresholds or gates
- No PR coverage reporting

### 5. No Dependency Vulnerability Scanning (Severity: MEDIUM)

The `requirements.txt` is 191KB with hundreds of transitive dependencies (aiohappyeyeballs, aiohttp, cryptography, etc.). No automated scanning:
- No `.github/dependabot.yml`
- No Renovate configuration
- No Snyk or similar tool

## Quick Wins

### 1. Add Unit Tests for Pure-Logic Modules (4-6 hours)

```python
# tests/test_config.py — test config validation without live services
from llama_stack_provider_ragas.config import RagasProviderInlineConfig, KubeflowConfig

def test_inline_config_defaults():
    config = RagasProviderInlineConfig(embedding_model="test-model")
    assert config.embedding_model == "test-model"

def test_kubeflow_config_validation():
    config = KubeflowConfig(
        pipelines_endpoint="http://localhost",
        namespace="test-ns",
        llama_stack_url="http://localhost:8321",
        base_image="python:3.12",
        results_s3_prefix="s3://bucket/prefix",
        s3_credentials_secret_name="my-secret",
    )
    assert config.namespace == "test-ns"
```

### 2. Enable Dependabot (30 minutes)

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
```

### 3. Add Trivy Scanning (1-2 hours)

```yaml
# Add to ci.yml
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -f Containerfile -t test-image .
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'test-image'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
```

### 4. Configure Codecov (2-3 hours)

```yaml
# Add to ci.yml as a new job
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --extra dev
      - run: uv run pytest -m "not integration_test" --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### 5. Add CI Concurrency Control (15 minutes)

```yaml
# Add to ci.yml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (3):**

| Workflow | Trigger | Purpose | Issues |
|----------|---------|---------|--------|
| `ci.yml` | push/PR to main, develop | Pre-commit checks | No concurrency control; pytest collects 0 tests |
| `docs.yml` | push/PR (docs changes) | Antora docs → GitHub Pages | Well-configured with concurrency |
| `release.yaml` | Release published | Build + publish to PyPI | Good smoke tests (wheel + sdist + install) |

**Strengths:**
- uv dependency caching in CI
- Separate docs workflow with path filtering
- Release workflow validates both wheel and sdist with import checks
- Mergify configured for multi-branch backporting (main → incubation → stable)
- Pull Upstream sync from trustyai-explainability fork

**Weaknesses:**
- CI runs ONLY pre-commit — no dedicated test job
- No concurrency control on main CI workflow
- No matrix testing (single Python version)
- No integration test job (even scheduled)
- No container build validation in CI

### Test Coverage

**Test file inventory:**

| File | Lines | Type | Runs in CI |
|------|-------|------|-----------|
| `conftest.py` | 110 | Fixtures | N/A |
| `test_inline_evaluation.py` | 57 | Integration | No |
| `test_kubeflow_integration.py` | 233 | Integration | No |
| `test_remote_evaluation.py` | 78 | Integration | No |
| `test_remote_wrappers.py` | 86 | Integration | No |
| **Total** | **559** | | **0 tests in CI** |

**Test-to-code ratio:** 559 / 1,754 = 0.32 (low, and effectively 0 since none run)

**Integration test quality (when run manually):**
- Good use of `pytest.fixture` for setup (client, config, data)
- Parametrized metric testing
- Async test support via `pytest-asyncio`
- Proper marker usage (`@pytest.mark.integration_test`)
- Kubeflow pipeline tests include component-level and full pipeline coverage

**Missing test categories:**
- Unit tests (0 files)
- Contract tests
- Snapshot/regression tests
- Performance benchmarks
- Error handling/edge case tests

### Code Quality

**Pre-commit hooks (strong):**
- `pre-commit-hooks` v4.5.0: trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-merge-conflict, debug-statements
- `ruff-pre-commit` v0.12.10: lint (with auto-fix) + format
- `mirrors-mypy` v1.17.1: type checking with error codes
- Local pytest hook (but collects 0 tests)

**Ruff configuration (adequate):**
- 7 rule sets enabled: E, W, F, I, B, C4, UP
- Missing: D (pydocstyle), S (bandit/security), N (naming), SIM (simplify), RUF
- Reasonable ignores for line length and complexity

**Mypy configuration (moderate):**
- Not strict mode (disallow_untyped_defs=false)
- Good: warn_return_any, strict_equality, warn_unreachable, show_error_codes
- Weak: ignore_missing_imports=true, disallow_incomplete_defs=false

### Container Images

**Containerfile analysis:**

| Aspect | Status | Issue |
|--------|--------|-------|
| Base image | `python:3.12` (full) | Should use slim or distroless |
| Multi-stage | No | Larger image, build tools in production |
| Non-root user | Missing | Security risk |
| Health check | Missing | No container health monitoring |
| .dockerignore | Present | Good — excludes .venv, .git, etc. |
| Multi-arch | No | Single platform only |
| Package manager | pip (not uv) | Inconsistent with dev workflow |
| SBOM | No | No software bill of materials |
| Signing | No | No image signing/attestation |

### Security

| Practice | Status |
|----------|--------|
| Container scanning (Trivy/Snyk) | Missing |
| SAST (CodeQL/Semgrep) | Missing |
| Dependency scanning (Dependabot) | Missing |
| Secret detection (Gitleaks) | Missing |
| SECURITY.md | Missing |
| Supply chain (SLSA/Sigstore) | Missing |

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test type rules exist
- **Quality**: N/A
- **Gaps**: Everything — no CLAUDE.md, no `.claude/` directory, no test creation rules, no coding standards for AI agents
- **Recommendation**: Generate agent rules with `/test-rules-generator` to establish unit test patterns, integration test patterns, and code quality guidelines

## Recommendations

### Priority 0 (Critical)

1. **Write unit tests for pure-logic modules** — `config.py`, `constants.py`, `compat.py`, `errors.py`, `logging_utils.py` can all be tested without live infrastructure. This immediately makes the CI pytest step meaningful.

2. **Fix the CI silent-pass bug** — Either:
   - (a) Add unit tests so pytest actually collects and runs tests, OR
   - (b) Remove the exit-code-5 suppression so CI fails honestly when no tests exist

3. **Add Trivy/Snyk container scanning** — The `python:3.12` full base image has known CVEs. A 15-line workflow addition catches them before release.

### Priority 1 (High Value)

4. **Configure codecov with coverage thresholds** — pytest-cov is already a dependency. Wire it into CI with a 60% initial threshold and ratchet up over time.

5. **Enable Dependabot** — 191KB of pinned transitive dependencies with no automated vulnerability alerts.

6. **Improve the Containerfile** — Multi-stage build, `python:3.12-slim` base, non-root user, and uv instead of pip.

7. **Add PR-time container build validation** — Build the image on PRs to catch Containerfile issues before merge.

8. **Add concurrency control to CI** — Prevent redundant CI runs on rapid pushes.

### Priority 2 (Nice-to-Have)

9. **Create CLAUDE.md and `.claude/rules/`** — Agent rules for unit test patterns, integration test patterns, and code style. Use `/test-rules-generator`.

10. **Add CodeQL or Semgrep SAST** — Static application security testing for the Python codebase.

11. **Add scheduled integration test job** — Run integration tests nightly against a test cluster to catch environmental regressions.

12. **Add SBOM generation and image signing** — Supply chain security for released images.

13. **Expand ruff rule sets** — Add S (security), D (docstrings), SIM (simplification), and RUF rules.

## Comparison to Gold Standards

| Practice | llama-stack-provider-ragas | odh-dashboard | notebooks | kserve |
|----------|--------------------------|---------------|-----------|--------|
| Unit tests in CI | 0 tests run | Comprehensive Jest | Pytest suites | Go testing |
| Integration/E2E | Exist but manual | Cypress E2E | Notebook validation | Multi-version |
| Coverage tracking | Not configured | Codecov enforced | Tracked | Enforced |
| Container scanning | None | Trivy | Multi-layer | Trivy |
| Pre-commit hooks | ruff + mypy | ESLint + Prettier | Varies | golangci-lint |
| Dependency scanning | None | Dependabot | Dependabot | Dependabot |
| Agent rules | None | Comprehensive | Partial | None |
| SAST/Security | None | CodeQL | Varies | CodeQL |
| Multi-arch images | No | N/A | Yes (5 platforms) | Yes |
| Release validation | Smoke tests | E2E gates | Image validation | Integration gates |

## File Paths Reference

| Category | Files |
|----------|-------|
| CI/CD | `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/release.yaml` |
| Tests | `tests/conftest.py`, `tests/test_inline_evaluation.py`, `tests/test_kubeflow_integration.py`, `tests/test_remote_evaluation.py`, `tests/test_remote_wrappers.py` |
| Code Quality | `.pre-commit-config.yaml`, `pyproject.toml` (ruff + mypy config) |
| Container | `Containerfile`, `.dockerignore` |
| Build | `pyproject.toml` (hatchling), `requirements.txt` (pinned deps), `uv.lock` |
| Docs | `README.md`, `CONTRIBUTING.md`, `antora-playbook.yml`, `docs/` |
| Automation | `.mergify.yml` (backporting), `.github/pull.yml` (upstream sync) |
