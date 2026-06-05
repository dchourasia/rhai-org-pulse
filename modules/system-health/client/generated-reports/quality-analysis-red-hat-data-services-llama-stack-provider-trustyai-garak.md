---
repository: "red-hat-data-services/llama-stack-provider-trustyai-garak"
overall_score: 7.8
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test suite — 11 test files, ~8500 lines, high test-to-code ratio (0.96:1), comprehensive mocking and parameterized tests"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "No integration or E2E tests — all tests are unit-only with mocked dependencies. No cluster-based or live endpoint testing"
  - dimension: "Build Integration"
    score: 8.0
    status: "PR-time container build + import chain validation + garak version parity check in validate-deps workflow"
  - dimension: "Image Testing"
    score: 7.0
    status: "Container build smoke test with full import chain, garak version verification. No runtime functional validation or multi-arch CI testing"
  - dimension: "Coverage Tracking"
    score: 6.0
    status: "pytest-cov configured with fail_under=60, Makefile coverage target. No CI coverage enforcement or codecov/coveralls integration"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "5 well-organized workflows (tests, lint, security, deps, publish). PR + push triggers. Tekton/Konflux for production builds. Dependabot enabled"
  - dimension: "Agent Rules"
    score: 7.0
    status: "Thorough CLAUDE.md and AGENTS.md with architecture, code layout, build/test instructions. No .claude/rules/ directory with test-type-specific rules"
critical_gaps:
  - title: "No integration or E2E tests"
    impact: "Tests only validate unit-level behavior with mocks. Integration bugs between garak subprocess, KFP, Llama Stack, eval-hub, and S3 are undetectable until deployment"
    severity: "HIGH"
    effort: "40-60 hours"
  - title: "No CI-enforced coverage reporting"
    impact: "fail_under=60 in pyproject.toml is not executed in CI. Coverage can silently regress below threshold without blocking PRs"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No concurrency control on CI workflows"
    impact: "Multiple concurrent workflow runs on the same PR waste resources and can produce confusing status checks"
    severity: "LOW"
    effort: "1 hour"
quick_wins:
  - title: "Add coverage enforcement to CI"
    effort: "2-3 hours"
    impact: "Prevents coverage regression below 60% threshold. Add --cov --cov-report=xml --cov-fail-under=60 to run-tests.yml"
  - title: "Add concurrency control to workflows"
    effort: "30 minutes"
    impact: "Cancel in-progress runs for same PR. Add concurrency: group/cancel-in-progress to each workflow"
  - title: "Add codecov integration"
    effort: "2-3 hours"
    impact: "PR-level coverage diffs, trend tracking, and enforcement. Upload XML coverage artifact from CI"
  - title: "Create .claude/rules/ for test patterns"
    effort: "3-4 hours"
    impact: "Codify existing test conventions (pytest fixtures, mocking patterns, async test setup) for AI-assisted development"
recommendations:
  priority_0:
    - "Add coverage enforcement (--cov-fail-under=60) to CI run-tests.yml workflow"
    - "Add codecov/coveralls integration for PR-level coverage reporting"
  priority_1:
    - "Create integration test suite for KFP pipeline submission (can use mocked KFP server)"
    - "Add .claude/rules/ directory with unit-test-patterns.md and integration-test-patterns.md"
    - "Add container runtime functional validation (test actual garak CLI invocation in built image)"
  priority_2:
    - "Add contract tests between provider and Llama Stack API boundaries"
    - "Add S3 integration test with localstack or minio"
    - "Add CodeQL/SAST scanning workflow"
---

# Quality Analysis: llama-stack-provider-trustyai-garak

## Executive Summary

- **Overall Score: 7.8/10**
- **Repository Type**: Python library — out-of-tree Llama Stack eval provider + eval-hub adapter for Garak LLM red-teaming
- **Primary Language**: Python 3.12
- **Key Strengths**: Exceptional unit test suite with near 1:1 test-to-code ratio, comprehensive CI/CD with 5 well-organized workflows, PR-time container build validation, Trivy security scanning, strong agent documentation (CLAUDE.md/AGENTS.md)
- **Critical Gaps**: No integration or E2E tests despite 4 complex execution modes, coverage not enforced in CI, no .claude/rules/ for test-specific guidance
- **Agent Rules Status**: Present (CLAUDE.md + AGENTS.md) but incomplete — no test automation rules in `.claude/rules/`

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent — 11 test files, ~8500 LOC, pytest + pytest-asyncio + parametrize |
| Integration/E2E | 5.0/10 | No integration or E2E tests — all unit-only with mocks |
| **Build Integration** | **8.0/10** | **PR-time container build + import chain + version parity check** |
| Image Testing | 7.0/10 | Container smoke test in CI, no runtime functional validation |
| Coverage Tracking | 6.0/10 | pytest-cov configured locally (fail_under=60), not enforced in CI |
| CI/CD Automation | 8.5/10 | 5 workflows, Tekton/Konflux, Dependabot, pre-commit hooks |
| Agent Rules | 7.0/10 | Strong CLAUDE.md/AGENTS.md, no .claude/rules/ directory |

## Critical Gaps

### 1. No Integration or E2E Tests
- **Impact**: The provider has 4 execution modes (inline, remote KFP, eval-hub simple, eval-hub KFP) with complex interactions between garak subprocess, KFP pipelines, S3 artifact flow, and Llama Stack APIs. All tests mock these boundaries — integration bugs are invisible until deployment.
- **Severity**: HIGH
- **Effort**: 40-60 hours
- **Examples of untested integration paths**:
  - Actual garak subprocess invocation and output parsing
  - KFP pipeline DAG construction and submission
  - S3 artifact upload/download flow
  - Llama Stack Files API interaction (upload scan results)
  - eval-hub SDK FrameworkAdapter lifecycle

### 2. No CI-Enforced Coverage Reporting
- **Impact**: `pyproject.toml` sets `fail_under = 60` but CI's `run-tests.yml` runs `pytest tests -v` without `--cov`. The threshold is only checked when running `make coverage` locally.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

### 3. No Concurrency Control on Workflows
- **Impact**: Multiple pushes to the same PR trigger overlapping workflow runs. Wasted compute and confusing status checks.
- **Severity**: LOW
- **Effort**: 1 hour

## Quick Wins

### 1. Enforce Coverage in CI (2-3 hours)
Update `run-tests.yml` to run with coverage:
```yaml
- name: Run tests with coverage
  run: |
    pytest tests -v --cov=llama_stack_provider_trustyai_garak \
      --cov-report=xml --cov-report=term-missing \
      --cov-fail-under=60
```

### 2. Add Concurrency Control (30 minutes)
Add to each workflow file:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

### 3. Add Codecov Integration (2-3 hours)
Add after the test step in `run-tests.yml`:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
    fail_ci_if_error: false
```

### 4. Create Agent Test Rules (3-4 hours)
Create `.claude/rules/` with files like `unit-tests.md` documenting the existing patterns:
- Use `pytest` + `pytest-asyncio` for async tests
- Mock external dependencies (garak, KFP, S3, Llama Stack APIs) using `unittest.mock`
- Use `monkeypatch` for environment variable manipulation
- Use `conftest.py` fixtures for shared mock objects
- Always test error paths and validation logic

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- **5 well-organized workflows** with clear separation of concerns:
  1. `run-tests.yml` — "Tier 1 - Unit Tests" on PR + push
  2. `lint.yml` — Ruff lint + format + Mypy type check
  3. `security.yml` — Trivy filesystem + dependency scan with SARIF upload
  4. `validate-deps.yml` — Auto-sync requirements.txt + garak version drift detection + container build validation
  5. `build-and-publish.yaml` — PyPI publish on release
- **Tekton/Konflux pipeline** (`.tekton/`) for production container builds with multi-arch support (x86_64, arm64, ppc64le, s390x), hermetic builds, and prefetch mode
- **Dependabot** configured for weekly pip updates
- **Smoke-test imports** step validates the import chain before running tests

**Gaps:**
- No concurrency control on any workflow
- No caching (pip, UV) in CI workflows — each run installs from scratch
- Tests do not run with coverage in CI
- No matrix testing across Python versions (only 3.12)

### Test Coverage

**Strengths:**
- **11 test files** covering all major modules:
  - `test_config.py` — Configuration classes, deep merge logic (500 LOC)
  - `test_pipeline_steps.py` — Core pipeline steps, API key resolution, scan config validation (820+ LOC)
  - `test_evalhub_adapter.py` — Eval-hub adapter with exhaustive intents model overlay testing (3300+ LOC)
  - `test_remote_provider.py` — Remote KFP adapter lifecycle (880 LOC)
  - `test_inline_provider.py` — Inline provider with fail-fast intents check (146 LOC)
  - `test_intents.py` — Taxonomy/intents dataset loading and generation (416 LOC)
  - `test_shield_scan.py` — Shield orchestrator with violation handling (305 LOC)
  - `test_version.py` — Version management with 15+ edge cases (344 LOC)
  - `test_utils.py` — XDG env, TLS, result parsing, Vega data (702 LOC)
  - `test_sdg_params.py` — SDG parameter resolution and flow block overrides (207 LOC)
  - `test_intents_with_shields.py` — Shield integration with intents mode
- **Near 1:1 test-to-code ratio**: ~8500 LOC tests vs ~8800 LOC source
- **Comprehensive mocking**: `conftest.py` provides shared fixtures for Files API, Benchmarks API, Safety API
- **Parameterized tests**: Framework profiles, TLS variants, timeout precedence
- **Error path testing**: Invalid configs, missing fields, validation errors, edge cases

**Gaps:**
- **Zero integration tests**: All external dependencies (garak subprocess, KFP, S3, Llama Stack APIs) are mocked
- **No E2E tests**: No tests that exercise the full eval lifecycle end-to-end
- **No contract tests**: API boundary contracts between provider and Llama Stack/eval-hub are untested
- **Coverage not enforced in CI**: `fail_under=60` exists in config but `make coverage` is not part of CI

### Code Quality

**Strengths:**
- **Ruff** for linting and formatting (target: py312, line-length: 120)
- **Mypy** for type checking (with extensive ignore list — `check_untyped_defs = false`)
- **Pre-commit hooks**: Ruff (lint + format), Mypy, requirements.txt auto-sync
- **Makefile targets**: `test`, `coverage`, `lint`, `format`, `typecheck`, `check` (lint + typecheck + test)

**Gaps:**
- **Mypy is weak**: `check_untyped_defs = false` and 12 error codes disabled. Type checking is largely a no-op.
- **No SAST/CodeQL**: No static analysis beyond Ruff/Mypy
- **No secret detection**: No Gitleaks or TruffleHog configured

### Container Images

**Strengths:**
- **Two Containerfiles**: `Containerfile` (dev/local) and `Dockerfile.konflux` (production)
- **PR-time container build validation** in `validate-deps.yml`:
  - Builds image from `Containerfile`
  - Verifies full import chain (numpy, pandas, garak, sdg-hub, provider)
  - Verifies garak version in container matches `pyproject.toml`
- **UBI9 base image**: `registry.access.redhat.com/ubi9/python-312:latest`
- **Non-root runtime**: Switches to UID 1001 after build
- **XDG env vars**: Set to `/tmp` for writability in restricted environments
- **Multi-arch Konflux builds**: x86_64, arm64, ppc64le, s390x
- **`.dockerignore`** present

**Gaps:**
- **No runtime functional validation**: Container build is tested but actual garak CLI execution inside the container is not validated
- **No vulnerability threshold enforcement**: Trivy scans with `exit-code: '0'` for non-critical (only fails on CRITICAL)
- **No SBOM generation**: No Syft or similar tool
- **No image signing/attestation** (handled by Konflux, not in GitHub CI)

### Security

**Strengths:**
- **Trivy security scanning** on PRs:
  - Filesystem scan (code + configs)
  - Dependency vulnerability scan
  - Critical severity gate (exit-code: 1)
  - SARIF upload to GitHub Security tab
- **Dependabot** for weekly dependency updates
- **garak version drift detection**: CI validates pinned version matches midstream tag
- **API key handling**: `__FROM_ENV__` placeholders, role-based key resolution, volume mount support
- **API key redaction**: `redact_api_keys()` sanitizes configs before logging

**Gaps:**
- **No CodeQL/SAST** workflow
- **No secret detection** (Gitleaks, TruffleHog)
- **Trivy non-critical results don't fail**: Only CRITICAL severity blocks PRs

### Agent Rules (Agentic Flow Quality)

**Strengths:**
- **CLAUDE.md** (113 lines): Comprehensive overview of repository purpose, 4 execution modes, code layout, key conventions, build/install instructions, test running, debugging tips
- **AGENTS.md**: Identical content to CLAUDE.md (well-organized for AI agents)
- **ARCHITECTURE.md**: Detailed architecture documentation
- **CONTRIBUTING.md**: Contribution guidelines
- **BENCHMARK_METADATA_REFERENCE.md**: API reference for benchmark configuration
- **COMPATIBILITY.md**: Version compatibility matrix

**Gaps:**
- **No `.claude/` directory**: No `.claude/rules/` with test-type-specific automation guidance
- **No test pattern rules**: AI agents don't have codified guidance on how to write tests for this repo (fixture patterns, mocking conventions, async test setup)
- **No skill definitions**: No `.claude/skills/` for custom development workflows

## Recommendations

### Priority 0 (Critical)
1. **Enforce coverage in CI** — Add `--cov --cov-fail-under=60` to `run-tests.yml`
2. **Add codecov integration** — Upload coverage XML for PR-level reporting and trend tracking

### Priority 1 (High Value)
1. **Create integration test suite** — Test garak subprocess invocation, KFP client interaction, and S3 artifact flow with mocked services (not full cluster required)
2. **Create `.claude/rules/` directory** — Codify test patterns:
   - `unit-tests.md`: pytest conventions, fixture patterns, mocking strategies
   - `integration-tests.md`: How to write integration tests for each execution mode
3. **Add container runtime functional test** — Execute `garak --help` or a minimal scan inside the built container
4. **Strengthen Mypy** — Enable `check_untyped_defs = true` and remove unnecessary error code suppressions incrementally

### Priority 2 (Nice-to-Have)
1. **Add CodeQL/SAST scanning** — GitHub native CodeQL for Python
2. **Add contract tests** — Validate provider API surface against Llama Stack Eval spec
3. **Add pip caching** — Use `actions/setup-python` cache option to speed up CI
4. **Add S3 integration test** — Use localstack or minio in CI for artifact flow testing
5. **Add secret detection** — Gitleaks pre-commit hook and CI workflow

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 8.5 — Excellent ratio | 9.0 — Jest + RTL | 7.0 — Basic | 9.0 — Go testing |
| Integration/E2E | 5.0 — None | 9.0 — Cypress E2E | 8.0 — Multi-layer | 9.0 — envtest |
| Build Integration | 8.0 — PR container + import validation | 8.0 — Multi-mode | 8.0 — Image matrix | 7.0 — Standard |
| Image Testing | 7.0 — Import smoke only | 6.0 — Basic | 9.0 — 5-layer | 7.0 — Basic |
| Coverage | 6.0 — Local only | 9.0 — Codecov enforced | 6.0 — Basic | 9.0 — Enforced |
| CI/CD | 8.5 — Well-organized | 9.0 — Comprehensive | 8.0 — Matrix | 9.0 — Advanced |
| Agent Rules | 7.0 — Good docs, no rules/ | 8.0 — Full rules | 5.0 — Minimal | 6.0 — Basic |
| Security | 7.5 — Trivy + Dependabot | 7.0 — Basic | 6.0 — Minimal | 8.0 — Multiple scanners |

## File Paths Reference

### CI/CD
- `.github/workflows/run-tests.yml` — Unit tests (PR + push)
- `.github/workflows/lint.yml` — Ruff + Mypy
- `.github/workflows/security.yml` — Trivy scanning
- `.github/workflows/validate-deps.yml` — Dep sync + garak drift + container build
- `.github/workflows/build-and-publish.yaml` — PyPI publish
- `.tekton/odh-trustyai-garak-lls-provider-dsp-pull-request.yaml` — Konflux PR pipeline
- `.github/dependabot.yml` — Weekly pip updates

### Testing
- `tests/conftest.py` — Shared fixtures (mock APIs)
- `tests/test_config.py` — Configuration classes
- `tests/test_pipeline_steps.py` — Core pipeline steps
- `tests/test_evalhub_adapter.py` — Eval-hub adapter (largest test file)
- `tests/test_remote_provider.py` — Remote KFP adapter
- `tests/test_inline_provider.py` — Inline provider
- `tests/test_intents.py` — Taxonomy/intents dataset handling
- `tests/test_shield_scan.py` — Shield orchestrator
- `tests/test_version.py` — Version management
- `tests/test_utils.py` — Utilities and result parsing
- `tests/test_sdg_params.py` — SDG parameter resolution

### Code Quality
- `pyproject.toml` — Ruff, Mypy, pytest, coverage config
- `.pre-commit-config.yaml` — Ruff + Mypy + requirements sync

### Container Images
- `Containerfile` — Dev/local image (UBI9 + garak from git)
- `Dockerfile.konflux` — Production image (BASE_IMAGE arg, prefetched deps)
- `.dockerignore` — Build context exclusions
- `.konflux/cpu-ubi9.conf` — Konflux build args

### Agent Rules
- `CLAUDE.md` — AI agent context (architecture, conventions, debugging)
- `AGENTS.md` — Same as CLAUDE.md
- `ARCHITECTURE.md` — Detailed architecture docs
