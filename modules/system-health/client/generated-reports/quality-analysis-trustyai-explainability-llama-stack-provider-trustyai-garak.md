---
repository: "trustyai-explainability/llama-stack-provider-trustyai-garak"
overall_score: 7.6
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test suite with 11 test files, ~8900 LOC, pytest+asyncio, strong coverage of all modules"
  - dimension: "Integration/E2E"
    score: 4.0
    status: "No integration or E2E tests; all tests are pure unit tests with mocks. No cluster/KFP validation."
  - dimension: "Build Integration"
    score: 7.5
    status: "PR-time container build + import chain validation, garak version drift check, requirements auto-sync"
  - dimension: "Image Testing"
    score: 6.5
    status: "Container build on PR with full import chain validation, but no runtime functional testing or multi-arch support"
  - dimension: "Coverage Tracking"
    score: 5.0
    status: "Coverage configured with fail_under=60% in pyproject.toml and make coverage target, but no CI enforcement or codecov integration"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "5 well-organized workflows: unit tests, lint+typecheck, security scan, dependency validation+container build, PyPI publish"
  - dimension: "Agent Rules"
    score: 6.0
    status: "CLAUDE.md and AGENTS.md present with architecture docs, but no .claude/rules/ for test automation guidance"
critical_gaps:
  - title: "No integration or E2E tests"
    impact: "KFP pipeline orchestration, S3 artifact flow, and Llama Stack server interactions are only validated via mocks. Real failures in KFP DAG construction, S3 credential resolution, or garak subprocess behavior would be missed."
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No CI coverage enforcement"
    impact: "Coverage threshold (60%) is configured but only runs locally via make coverage. PRs can merge with reduced coverage without anyone noticing."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No multi-architecture container support"
    impact: "Container image only builds for amd64. ARM/aarch64 deployments (growing in Kubernetes/OpenShift) would require manual builds."
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add pytest-cov to CI workflow"
    effort: "1-2 hours"
    impact: "Enforce the existing 60% coverage threshold on every PR, preventing coverage regression"
  - title: "Add codecov integration"
    effort: "2-3 hours"
    impact: "PR-level coverage reporting with diff coverage, trend visualization, and merge blocking"
  - title: "Create .claude/rules/ for test patterns"
    effort: "2-3 hours"
    impact: "Guide AI agents to generate consistent, framework-aligned tests following existing patterns"
  - title: "Add SBOM generation to container build"
    effort: "1-2 hours"
    impact: "Supply chain transparency for compliance and vulnerability tracking"
recommendations:
  priority_0:
    - "Add pytest-cov to the run-tests.yml CI workflow to enforce the 60% fail_under threshold on every PR"
    - "Create a lightweight integration test that validates KFP pipeline construction (without a real cluster)"
  priority_1:
    - "Add codecov integration for PR-level coverage reporting and diff coverage gating"
    - "Create .claude/rules/ directory with unit test patterns, async test guidelines, and mock fixture conventions"
    - "Add a smoke test that runs garak CLI with a trivial config against a local mock server"
  priority_2:
    - "Add multi-architecture container builds (amd64 + arm64) using docker buildx"
    - "Add SBOM generation (syft or trivy) to the container build workflow"
    - "Consider adding contract tests for the Llama Stack provider API interface"
---

# Quality Analysis: llama-stack-provider-trustyai-garak

## Executive Summary

- **Overall Score: 7.6/10**
- **Repository Type**: Python library (Llama Stack eval provider + Eval-Hub adapter)
- **Primary Language**: Python 3.12
- **Framework**: Llama Stack, KFP (Kubeflow Pipelines), eval-hub SDK
- **Key Strengths**: Excellent unit test coverage (~91% test-to-code LOC ratio), thorough CI/CD with 5 focused workflows, strong security scanning via Trivy, well-documented architecture in CLAUDE.md/AGENTS.md, pre-commit hooks with ruff+mypy
- **Critical Gaps**: No integration/E2E tests, coverage threshold not enforced in CI, no .claude/rules/ for AI agent test guidance
- **Agent Rules Status**: Partial (CLAUDE.md + AGENTS.md present, but no .claude/rules/)

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent: 11 test files, ~8900 LOC, pytest+asyncio, parametrized, strong module coverage |
| Integration/E2E | 4.0/10 | All tests are pure unit with mocks. No KFP, S3, or Llama Stack integration tests |
| **Build Integration** | **7.5/10** | **PR-time container build + import validation, garak version drift check** |
| Image Testing | 6.5/10 | Container build + import chain validation on PR, but no runtime functional tests |
| Coverage Tracking | 5.0/10 | fail_under=60% in pyproject.toml, make coverage target, but not enforced in CI |
| CI/CD Automation | 8.0/10 | 5 well-organized workflows with proper triggers, Trivy security scanning |
| Agent Rules | 6.0/10 | CLAUDE.md + AGENTS.md with architecture docs, but no .claude/rules/ |

## Critical Gaps

### 1. No Integration or E2E Tests
- **Impact**: KFP pipeline orchestration, S3 artifact flow, Llama Stack server interactions, and garak subprocess behavior are only validated via mocks. Real failures in pipeline DAG construction, S3 credential resolution, or subprocess timeout handling would be missed until production.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Recommendation**: Create a `tests/integration/` directory with:
  - KFP pipeline construction test (validates DAG without submitting to cluster)
  - Garak CLI subprocess test with a minimal probe against a mock server
  - S3 upload/download test using moto or localstack

### 2. No CI Coverage Enforcement
- **Impact**: The 60% coverage threshold in `pyproject.toml` is only triggered locally via `make coverage`. PRs can merge with reduced coverage, and there is no codecov/coveralls integration for PR-level diff coverage reporting.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Recommendation**: Add `--cov=llama_stack_provider_trustyai_garak --cov-report=term-missing --cov-fail-under=60` to the pytest command in `run-tests.yml`

### 3. No Multi-Architecture Container Support
- **Impact**: Only builds for amd64. ARM deployments require manual builds.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours

## Quick Wins

### 1. Add pytest-cov to CI Workflow (1-2 hours)
Add coverage enforcement to `.github/workflows/run-tests.yml`:
```yaml
- name: Run tests with coverage
  run: |
    pytest tests -v \
      --cov=llama_stack_provider_trustyai_garak \
      --cov-report=term-missing \
      --cov-fail-under=60
```

### 2. Add Codecov Integration (2-3 hours)
Add codecov step to CI:
```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    fail_ci_if_error: true
```

### 3. Create .claude/rules/ for Test Patterns (2-3 hours)
Create rules files to guide AI agent test generation:
- `.claude/rules/unit-tests.md` - pytest patterns, async fixtures, mock conventions
- `.claude/rules/testing-standards.md` - coverage expectations, parametrization patterns

### 4. Add SBOM Generation (1-2 hours)
Add syft or trivy SBOM generation to `validate-deps.yml`:
```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: provider-smoke-test:ci
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (5 total):**

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| `run-tests.yml` | PR + push to main | Unit tests with smoke-test imports |
| `lint.yml` | PR + push to main | Ruff lint + format check + mypy typecheck |
| `security.yml` | PR + push to main | Trivy filesystem + dependency scan, SARIF upload to GitHub Security |
| `validate-deps.yml` | PR + push to main | Auto-sync requirements.txt, garak midstream version drift check, container build + import validation |
| `build-and-publish.yaml` | Release published | Build + publish to PyPI with trusted publisher |

**Strengths:**
- All PR-blocking workflows trigger on both `pull_request` and `push` to main
- Garak midstream version drift detection prevents silent dependency skew
- Container build validates full import chain (numpy, pandas, garak, sdg-hub, provider)
- Trivy scans with CRITICAL exit code 1 (blocks on critical vulns) and SARIF upload
- Auto-sync requirements.txt on pyproject.toml changes via pre-commit hook + CI

**Gaps:**
- No concurrency control on any workflow (could have redundant runs)
- No caching of pip dependencies (every run does fresh install)
- No test coverage reporting in CI
- `setup-python@v4` used in some workflows while `v5` used in others (inconsistent)

### Test Coverage

**Test Infrastructure:**
- **Framework**: pytest + pytest-asyncio + pytest-cov
- **Test Files**: 11 test files + conftest.py (12 total)
- **Test LOC**: ~8,900 lines
- **Source LOC**: ~9,758 lines
- **Test-to-Code Ratio**: 0.91 (excellent)
- **Coverage Threshold**: 60% (configured in `pyproject.toml`, not enforced in CI)

**Test Modules:**

| Test File | Lines | Scope |
|-----------|-------|-------|
| `test_evalhub_adapter.py` | ~3,771 | Eval-hub adapter alignment, KFP mode, S3, intents, MLflow |
| `test_pipeline_steps.py` | ~822 | Core pipeline steps, API key resolution, config validation |
| `test_utils.py` | ~700 | XDG functions, HTTP client TLS, result parsing, Vega data |
| `test_intents.py` | ~416 | Taxonomy dataset loading, intent generation, sanitization |
| `test_remote_provider.py` | ~880 | Remote KFP adapter creation, job lifecycle, shield availability |
| `test_config.py` | ~500 | Pydantic config validation, deep merge, scan profiles |
| `test_version.py` | ~344 | Version extraction from metadata, pyproject.toml fallbacks |
| `test_shield_scan.py` | ~305 | Shield orchestrator, violation detection, client lifecycle |
| `test_inline_provider.py` | ~146 | Inline provider spec, creation, intents fail-fast |
| `test_intents_with_shields.py` | ~422 | Intents + shields integration, validation, full workflow |
| `test_sdg_params.py` | ~207 | SDG concurrency, flow block overrides, parameter plumbing |

**Strengths:**
- Thorough parametrized tests for framework/scan profiles
- Async test support with proper fixtures
- Excellent edge case coverage (empty datasets, invalid JSON, missing configs)
- Tests for error paths and validation failures
- Deep merge behavior verified with nested dict structures
- Funnel property verification for intents pipeline

**Gaps:**
- All tests are pure unit tests with mocks; no integration with real garak, KFP, or S3
- No test for the HTML report generation (`result_utils.generate_art_report` test opens browser, not a real assertion)
- Some test duplication in `test_config.py` (duplicate method names: `test_scan_dir_respects_garak_scan_dir_env`, etc.)
- No performance/load testing for concurrent scan job management

### Code Quality

**Linting & Formatting:**
- **Ruff**: Configured in `pyproject.toml` with E, F, W rules, line-length 120
- **Per-file ignores**: Appropriate ignores for `__init__.py`, tests, and specific modules
- **Mypy**: Configured for Python 3.12, but many error codes disabled (union-attr, assignment, no-any-return, arg-type, etc.)
- **Pre-commit hooks**: ruff (check + format), mypy, requirements.txt sync
- **Format check**: `ruff format --check` in CI

**Strengths:**
- Pre-commit hooks enforce quality before commits
- CI runs both ruff lint and format check
- Mypy typecheck in both pre-commit and CI
- Consistent code style enforced via ruff formatter

**Gaps:**
- Mypy has 11 error codes disabled, reducing type safety
- No complexity checks (cyclomatic complexity, cognitive complexity)
- `check_untyped_defs = false` means untyped functions aren't checked

### Container Images

**Containerfile:**
- Base image: `registry.access.redhat.com/ubi9/python-312:latest` (Red Hat UBI)
- Multi-stage: No (single stage)
- Non-root user: Yes (USER 1001 after install)
- XDG environment variables set for writable directories
- Garak installed from midstream git with version derived from pyproject.toml

**PR-time Validation (validate-deps.yml):**
- Container build on every PR
- Full import chain verification (numpy, pandas, garak, sdg-hub, provider)
- Garak version consistency check (container vs. pyproject.toml)

**Strengths:**
- UBI base image for enterprise compatibility
- Non-root runtime
- CPU-only torch for smaller image size
- Import chain validation catches dependency conflicts early

**Gaps:**
- No multi-architecture support (amd64 only)
- No SBOM generation
- No image signing/attestation
- No runtime functional testing (only import verification)
- No `.dockerignore` for tests directory (increases build context)

### Security

**Trivy Integration (security.yml):**
- Filesystem scan (all severities, SARIF output)
- Dependency vulnerability scan (vuln scanner, SARIF output)
- Critical vulnerability gate (exit-code: 1 for CRITICAL)
- SARIF upload to GitHub Security tab for PRs

**Dependabot:**
- Weekly pip dependency updates configured

**Strengths:**
- Comprehensive Trivy scanning with SARIF integration
- Critical vulnerability blocking
- Automated dependency updates via Dependabot
- Pinned Trivy action to specific SHA

**Gaps:**
- No SAST/CodeQL integration
- No secret detection (Gitleaks, TruffleHog)
- No `.trivyignore` for known false positives
- Security scan uses `exit-code: 0` for non-critical (doesn't block PR)
- No license compliance scanning

### Agent Rules (Agentic Flow Quality)

**Status**: Partial

**Present:**
- `CLAUDE.md` (root) - Comprehensive architecture documentation with code layout, conventions, build/install, testing, debugging
- `AGENTS.md` (root) - Identical content to CLAUDE.md (agent-agnostic documentation)
- `CONTRIBUTING.md` - Contribution guidelines
- `ARCHITECTURE.md` - Architecture documentation
- `.github/PULL_REQUEST_TEMPLATE.md` - PR template with testing checklist

**Missing:**
- No `.claude/` directory
- No `.claude/rules/` for test creation guidance
- No test pattern documentation for AI agents
- No framework-specific testing rules (pytest-asyncio patterns, mock conventions)

**Recommendation**: Generate test automation rules with `/test-rules-generator` to create:
- `.claude/rules/unit-tests.md` - pytest patterns, parametrization, async fixtures
- `.claude/rules/testing-standards.md` - coverage expectations, mock vs. real patterns
- `.claude/rules/mock-patterns.md` - MagicMock, AsyncMock, monkeypatch conventions

## Recommendations

### Priority 0 (Critical)
1. **Add pytest-cov to CI workflow** - Enforce the existing 60% fail_under threshold in `run-tests.yml` to prevent coverage regression on every PR
2. **Fix duplicate test methods** in `test_config.py` - Methods `test_scan_dir_respects_garak_scan_dir_env` and `test_scan_dir_uses_xdg_cache_home_when_no_override` are duplicated, which silently shadows earlier definitions

### Priority 1 (High Value)
1. **Add codecov integration** for PR-level coverage reporting with diff coverage visualization
2. **Create .claude/rules/** with comprehensive test automation guidance for AI agents
3. **Add a lightweight integration test** that validates KFP pipeline construction without a real cluster
4. **Add concurrency control** to CI workflows to cancel redundant runs
5. **Add pip caching** to CI workflows for faster builds

### Priority 2 (Nice-to-Have)
1. **Add multi-architecture container builds** (amd64 + arm64) using docker buildx
2. **Add SBOM generation** for supply chain transparency
3. **Add CodeQL/SAST** for static application security testing
4. **Add secret detection** (Gitleaks) to prevent credential leaks
5. **Tighten mypy configuration** - Gradually re-enable disabled error codes
6. **Add contract tests** for the Llama Stack provider API interface boundaries
7. **Standardize GitHub Actions versions** (some use v4, others v5)

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 8.5 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 4.0 | 9.0 | 8.0 | 9.5 |
| Build Integration | 7.5 | 8.5 | 7.0 | 8.0 |
| Image Testing | 6.5 | 7.0 | 9.5 | 7.5 |
| Coverage Tracking | 5.0 | 8.5 | 5.0 | 9.0 |
| CI/CD Automation | 8.0 | 9.0 | 8.5 | 9.0 |
| Agent Rules | 6.0 | 8.5 | 3.0 | 4.0 |
| **Overall** | **7.6** | **8.8** | **7.0** | **8.5** |

**Key Takeaway**: This repository has excellent unit test foundations and strong CI/CD infrastructure. The main gaps are the lack of integration/E2E testing and CI-enforced coverage tracking. Compared to gold standards, the unit test quality is nearly on par, but the integration testing gap is the most significant divergence.

## File Paths Reference

### Configuration
- `pyproject.toml` - Project config, dependencies, pytest/coverage/ruff/mypy settings
- `Makefile` - Build targets (test, coverage, lint, format, typecheck, build)
- `.pre-commit-config.yaml` - Pre-commit hooks (ruff, mypy, requirements sync)
- `Containerfile` - Container image build
- `.dockerignore` - Docker build context exclusions
- `.github/dependabot.yml` - Dependabot config for weekly pip updates

### CI/CD
- `.github/workflows/run-tests.yml` - Unit tests (Tier 1)
- `.github/workflows/lint.yml` - Ruff + mypy
- `.github/workflows/security.yml` - Trivy security scanning
- `.github/workflows/validate-deps.yml` - Dependency validation + container build
- `.github/workflows/build-and-publish.yaml` - PyPI publish on release

### Testing
- `tests/conftest.py` - Shared fixtures (mock APIs, temp directories)
- `tests/test_config.py` - Configuration validation tests
- `tests/test_intents.py` - Taxonomy/intents dataset tests
- `tests/test_inline_provider.py` - Inline provider tests
- `tests/test_remote_provider.py` - Remote KFP adapter tests
- `tests/test_shield_scan.py` - Shield orchestrator tests
- `tests/test_evalhub_adapter.py` - Eval-hub adapter tests (largest, ~3771 LOC)
- `tests/test_pipeline_steps.py` - Core pipeline step tests
- `tests/test_version.py` - Version management tests
- `tests/test_utils.py` - Utility + result parsing tests
- `tests/test_sdg_params.py` - SDG parameter resolution tests
- `tests/test_intents_with_shields.py` - Intents + shields integration tests

### Agent Rules
- `CLAUDE.md` - AI agent context and architecture documentation
- `AGENTS.md` - Agent-agnostic context documentation
- `ARCHITECTURE.md` - Architecture documentation
- `CONTRIBUTING.md` - Contribution guidelines
