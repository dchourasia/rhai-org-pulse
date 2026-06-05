---
repository: "opendatahub-io/llama-stack-provider-instructlab-train"
overall_score: 2.1
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No unit tests exist anywhere in the repository"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "Basic server startup smoke test only; no functional or API-level testing"
  - dimension: "Build Integration"
    score: 0.0
    status: "No Dockerfile, no container build, no PR-time build validation"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images are built or tested"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling, thresholds, or reporting configured"
  - dimension: "CI/CD Automation"
    score: 5.0
    status: "Two workflows with concurrency control; limited scope"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, .claude/ directory, or agent guidance exists"
critical_gaps:
  - title: "Zero unit tests for all 224 lines of source code"
    impact: "Regressions in job scheduling, status mapping, and config validation go undetected"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No container image build or testing"
    impact: "This provider cannot be validated as a deployable artifact; runtime failures discovered only in production"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No visibility into what code is tested; no quality gate to prevent coverage regression"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Integration test only validates server startup, not API behavior"
    impact: "Provider registration is checked but no training API endpoints are actually exercised"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "Dependency pinned to a personal fork branch"
    impact: "llama-stack depends on git+https://github.com/astefanutti/llama-stack.git@feat-658-1238 — fragile, unreproducible, and a supply chain risk"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No security scanning of any kind"
    impact: "Vulnerabilities in 15+ dependencies (including numpy, requests, aiohttp) go undetected"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add pytest with basic unit tests for adapter.py"
    effort: "4-6 hours"
    impact: "Cover job scheduling, status mapping, and error handling — the core business logic"
  - title: "Add codecov integration to test-external-providers workflow"
    effort: "1-2 hours"
    impact: "Establish coverage baseline and prevent regression"
  - title: "Add Trivy or Snyk dependency scanning workflow"
    effort: "1-2 hours"
    impact: "Detect known vulnerabilities in 15+ production dependencies"
  - title: "Pin llama-stack dependency to a release or upstream main"
    effort: "1 hour"
    impact: "Eliminate supply chain risk from personal fork dependency"
  - title: "Add mypy or pyright type checking to CI"
    effort: "2-3 hours"
    impact: "Catch type errors at PR time; config.py uses Optional types inconsistently"
recommendations:
  priority_0:
    - "Add pytest unit test suite for adapter.py covering job lifecycle, status mapping, and error cases"
    - "Pin llama-stack dependency to upstream release or official branch instead of personal fork"
    - "Add Dockerfile and basic container build validation to CI"
  priority_1:
    - "Expand integration test to exercise training API endpoints (supervised_fine_tune, get_training_jobs, etc.)"
    - "Add dependency vulnerability scanning (Trivy/Snyk) as PR check"
    - "Add codecov integration with minimum coverage threshold"
    - "Add mypy type checking to CI pipeline"
  priority_2:
    - "Create CLAUDE.md and .claude/rules/ for AI-assisted test generation guidance"
    - "Add contract tests validating provider implements llama-stack PostTraining API correctly"
    - "Add pre-commit hook for mypy/pyright checks"
    - "Consider adding a Dockerfile for containerized deployment and testing"
---

# Quality Analysis: llama-stack-provider-instructlab-train

## Executive Summary

- **Overall Score: 2.1/10**
- **Repository Type**: Python library — Llama Stack external provider for distributed InstructLab training
- **Language**: Python 3.10+
- **Package Manager**: uv
- **Lines of Code**: 224 (4 Python source files)
- **Commits**: 3 (extremely early-stage)
- **License**: Apache 2.0

This repository is in a very early development stage with only 3 commits and a single merged PR. The core training logic (`supervised_fine_tune`) is not yet implemented (contains a TODO stub). While the project has reasonable CI foundations (pre-commit hooks, concurrency control, a server startup smoke test), it critically lacks unit tests, container image builds, coverage tracking, security scanning, and any form of comprehensive test coverage.

**Key Strengths:**
- Pre-commit hooks with Ruff linting and formatting enforced in CI
- Basic integration test validates the provider registers with the Llama Stack server
- Concurrency control on CI workflows to prevent redundant runs

**Critical Gaps:**
- Zero unit tests for all source code
- No container image build or testing pipeline
- No coverage tracking or enforcement
- Dependency pinned to a personal GitHub fork branch (supply chain risk)
- No security scanning

**Agent Rules Status**: Missing — No CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No unit tests exist anywhere in the repository |
| Integration/E2E | 2/10 | Basic server startup smoke test only; no API-level testing |
| **Build Integration** | **0/10** | **No Dockerfile, no container build, no PR-time build validation** |
| Image Testing | 0/10 | No container images are built or tested |
| Coverage Tracking | 0/10 | No coverage tooling, thresholds, or reporting configured |
| CI/CD Automation | 5/10 | Two workflows with concurrency control; limited scope |
| Agent Rules | 0/10 | No CLAUDE.md, .claude/ directory, or agent guidance exists |

## Critical Gaps

### 1. Zero Unit Tests
- **Impact**: All 224 lines of source code — including job scheduling, status mapping (`SchedulerJobStatus` → `JobStatus`), config validation (32 config fields), and error handling — are completely untested
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Key areas needing tests**:
  - `adapter.py`: `supervised_fine_tune()` job scheduling, `get_training_jobs()` response mapping, `get_training_job_status()` status translation (5 status cases + default), `cancel_training_job()` error raising, `get_training_job_artifacts()` with/without checkpoints
  - `config.py`: `InstructLabTrainPostTrainingConfig` default values, `sample_run_config()` returning empty dict
  - `provider.py`: `get_provider_spec()` returns correct `ProviderSpec`

### 2. No Container Image Build or Testing
- **Impact**: There is no Dockerfile or Containerfile in the repository. The provider cannot be validated as a deployable container artifact. Runtime packaging issues (missing dependencies, import errors) are only discovered during production deployment.
- **Severity**: HIGH
- **Effort**: 4-6 hours

### 3. No Coverage Tracking
- **Impact**: Without coverage measurement, there's no visibility into what code is tested and no gate to prevent coverage regression. Given there are zero tests currently, establishing a baseline is critical.
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 4. Integration Test Only Validates Server Startup
- **Impact**: The `test-external-providers.yml` workflow starts the Llama Stack server and checks that the InstructLab Train provider is registered, but it never calls any training API endpoint. The provider could have broken API implementations and CI would still pass.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Current test only checks**: `curl /v1/health` returns "OK" and server log contains the provider name

### 5. Dependency Pinned to Personal Fork
- **Impact**: `llama-stack` is installed from `git+https://github.com/astefanutti/llama-stack.git@feat-658-1238` — a personal fork on a feature branch. This is fragile (branch can be deleted), unreproducible (commit can change), and a supply chain risk (no review process for that fork).
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 6. No Security Scanning
- **Impact**: The project has 15+ production dependencies including `numpy`, `requests`, `aiohttp`, `httpx`, `uvicorn`, `openai`, and `opentelemetry-*` — all of which can have known CVEs. No Trivy, Snyk, CodeQL, Dependabot, or any vulnerability scanning is configured.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours

## Quick Wins

### 1. Add pytest with basic unit tests for adapter.py (4-6 hours)
Cover the core business logic: job creation, status mapping, and error handling.

```python
# tests/test_adapter.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from llama_stack_provider_instructlab_train.adapter import (
    InstructLabTrainPostTrainingImpl,
)
from llama_stack_provider_instructlab_train.config import (
    InstructLabTrainPostTrainingConfig,
)

@pytest.fixture
def config():
    return InstructLabTrainPostTrainingConfig(
        tolerations=[], node_selectors={},
        pytorchjob_output_yaml="out.yaml",
        name_suffix="test", phase_num=1,
        base_image="quay.io/test:latest",
    )

@pytest.fixture
def impl(config):
    return InstructLabTrainPostTrainingImpl(config)

@pytest.mark.asyncio
async def test_get_training_jobs_empty(impl):
    result = await impl.get_training_jobs()
    assert list(result.data) == []

@pytest.mark.asyncio
async def test_cancel_training_job_not_implemented(impl):
    with pytest.raises(NotImplementedError):
        await impl.cancel_training_job("some-uuid")

@pytest.mark.asyncio
async def test_get_training_job_artifacts_missing(impl):
    result = await impl.get_training_job_artifacts("nonexistent")
    assert result is None
```

### 2. Add codecov integration (1-2 hours)
```yaml
# Add to test-external-providers.yml or a new test workflow
- name: Run tests with coverage
  run: |
    uv run pytest --cov=src --cov-report=xml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
```

### 3. Add Trivy dependency scanning (1-2 hours)
```yaml
# .github/workflows/security.yml
name: Security Scan
on: [pull_request, push]
jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'HIGH,CRITICAL'
```

### 4. Pin llama-stack to upstream (1 hour)
Replace the personal fork dependency in `pyproject.toml`:
```toml
# Before (risky):
"llama-stack @ git+https://github.com/astefanutti/llama-stack.git@feat-658-1238"
# After (stable):
"llama-stack>=0.1.0"  # or pin to a specific release
```

### 5. Add mypy type checking (2-3 hours)
```yaml
# Add to pre-commit-config.yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.8.0
  hooks:
    - id: mypy
      additional_dependencies: [pydantic]
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (2 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pre-commit.yml` | PR + push to main | Runs pre-commit hooks (Ruff lint/format, merge conflict check, trailing whitespace, large files, EOF fixer) |
| `test-external-providers.yml` | PR + push to main | Installs provider, starts Llama Stack server, validates provider registration via health check |

**Strengths:**
- Concurrency control on pre-commit workflow (`cancel-in-progress: true`)
- pip caching configured for pre-commit workflow
- Log artifact upload on test failure

**Weaknesses:**
- No test execution in any workflow (no pytest, no coverage)
- No build validation (no Docker/container build)
- No security scanning workflow
- No dependency update automation (Dependabot/Renovate)
- test-external-providers lacks concurrency control
- No matrix testing across Python versions

### Test Coverage

**Unit Tests: None**
- Zero test files exist (`*_test.py`, `test_*.py`, `tests/`)
- No pytest configuration in `pyproject.toml`
- No test dependencies declared
- Test-to-code ratio: 0:224

**Integration Tests: Minimal**
- `test-external-providers.yml` starts the server and checks health endpoint
- Validates provider is registered but does not call any API
- No API-level testing (POST /v1/post-training/supervised-fine-tune, etc.)
- No mock training job submission or status polling

**E2E Tests: None**
- No end-to-end training workflow tests
- No multi-node training simulation
- No PyTorchJob integration testing

**Coverage Tracking: None**
- No `.coveragerc` or `[tool.coverage]` in pyproject.toml
- No codecov/coveralls integration
- No coverage thresholds
- No PR coverage reporting

### Code Quality

**Linting: Good (for the scope)**
- Ruff configured with `extend-exclude = ["*.ipynb"]`
- Pre-commit hooks enforce Ruff lint + format on every commit
- Additional hooks: merge conflict detection, trailing whitespace, large file detection, EOF fixer

**Type Checking: Missing**
- No mypy, pyright, or pytype configuration
- `config.py` has `chat_tmpl_path: str = None` — should be `Optional[str] = None`
- No type stubs for dependencies

**Static Analysis: Missing**
- No CodeQL, Semgrep, or gosec
- No Bandit (Python security linter)

### Container Images

**Status: Not Applicable / Missing**
- No Dockerfile or Containerfile exists
- No container build workflow
- No multi-architecture support
- No image signing or attestation
- No SBOM generation
- For a provider intended to run distributed training on Kubernetes, the absence of container packaging is a significant gap

### Security

**Vulnerability Scanning: None**
- No Trivy, Snyk, or Grype integration
- No GitHub Dependabot alerts configured
- No secret detection (Gitleaks, TruffleHog)

**Supply Chain Risk: HIGH**
- Primary dependency (`llama-stack`) pinned to a personal fork: `git+https://github.com/astefanutti/llama-stack.git@feat-658-1238`
- This fork could be modified, deleted, or force-pushed without notice
- No verification of the fork's integrity

**Dependency Count**: 15+ production dependencies including networking libraries (aiohttp, httpx, requests, urllib3), ML libraries (numpy, datasets), and observability (opentelemetry-*) — all potential CVE vectors with no scanning

### Agent Rules (Agentic Flow Quality)

**Status**: Missing
- No `CLAUDE.md` or `AGENTS.md` in repository root
- No `.claude/` directory
- No `.claude/rules/` for test creation guidance
- No `.claude/skills/` for custom workflows
- No testing documentation or standards

**Coverage**: 0/7 test types covered (unit, integration, e2e, contract, image, security, performance)

**Recommendation**: Generate rules with `/test-rules-generator` to establish AI-assisted testing standards. Given the small codebase, this would provide disproportionate value — every new feature PR could get comprehensive test suggestions from AI agents.

## Recommendations

### Priority 0 (Critical)

1. **Add pytest unit test suite** for `adapter.py` covering:
   - Job creation and scheduling via `supervised_fine_tune()`
   - All 5 status mappings in `get_training_job_status()` (new, scheduled, running, completed, failed)
   - Error handling (LoRA config raises `NotImplementedError`, cancel raises `NotImplementedError`)
   - `get_training_job_artifacts()` with and without checkpoints
   - `get_training_jobs()` empty and populated cases

2. **Pin llama-stack dependency** to upstream release or official branch. The current personal fork dependency is a supply chain risk and reproducibility hazard.

3. **Add a Dockerfile** and basic container build validation to CI so the provider can be tested as a deployable artifact.

### Priority 1 (High Value)

4. **Expand integration tests** to exercise the provider's API endpoints through the Llama Stack server (submit a training job, poll status, retrieve artifacts).

5. **Add dependency vulnerability scanning** (Trivy or Snyk) as a required PR check.

6. **Add codecov integration** with a minimum coverage threshold (start at 50%, increase as tests are added).

7. **Add mypy type checking** to CI. The codebase has type annotations but no checker — `config.py` already has a type inconsistency (`str = None` should be `Optional[str] = None`).

### Priority 2 (Nice-to-Have)

8. **Create CLAUDE.md and `.claude/rules/`** for AI-assisted development guidance, especially test generation patterns for the Llama Stack provider API.

9. **Add contract tests** validating that the provider correctly implements the full `PostTraining` API interface from llama-stack.

10. **Add Dependabot or Renovate** for automated dependency updates.

11. **Add Python version matrix testing** (3.10, 3.11, 3.12) since `requires-python = ">=3.10"`.

12. **Expand README.md** — currently a single line with just the repo name. Should document: what this provider does, how to install/configure it, how to run tests, and how to contribute.

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | None (0/10) | Comprehensive Jest suite (9/10) | Pytest suite (7/10) | Go test + envtest (9/10) |
| Integration/E2E | Startup smoke only (2/10) | Cypress E2E + contract tests (9/10) | Multi-notebook validation (8/10) | Multi-version E2E (9/10) |
| Build Integration | No builds (0/10) | PR-time image builds (8/10) | 5-layer image validation (9/10) | Konflux simulation (7/10) |
| Image Testing | No images (0/10) | Container validation (7/10) | Runtime + startup tests (9/10) | Multi-arch builds (8/10) |
| Coverage Tracking | None (0/10) | Codecov enforcement (8/10) | Coverage reports (6/10) | Coverage gates (8/10) |
| CI/CD Automation | 2 workflows (5/10) | 15+ workflows (9/10) | Matrix workflows (8/10) | Comprehensive CI (9/10) |
| Agent Rules | None (0/10) | CLAUDE.md + rules (8/10) | Partial (4/10) | None (1/10) |
| **Overall** | **2.1/10** | **8.5/10** | **7.5/10** | **8.0/10** |

## File Paths Reference

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project config, dependencies, Ruff settings |
| `.pre-commit-config.yaml` | Pre-commit hooks (Ruff lint/format, file checks) |
| `.github/workflows/pre-commit.yml` | CI for pre-commit enforcement |
| `.github/workflows/test-external-providers.yml` | Server startup smoke test |
| `src/llama_stack_provider_instructlab_train/adapter.py` | Core provider implementation (160 lines) |
| `src/llama_stack_provider_instructlab_train/config.py` | Provider configuration model (35 lines) |
| `src/llama_stack_provider_instructlab_train/provider.py` | Provider spec definition (18 lines) |
| `src/llama_stack_provider_instructlab_train/__init__.py` | Package exports (11 lines) |
| `run.yaml` | Llama Stack server configuration |
| `providers.d/inline/post_training/instructlab_train.yaml` | External provider registration |
