---
repository: "opendatahub-io/llama-stack-client-python"
overall_score: 3.8
scorecard:
  - dimension: "Unit Tests"
    score: 5.0
    status: "Auto-generated API tests exist but are DISABLED; hand-written lib tests are limited"
  - dimension: "Integration/E2E"
    score: 4.0
    status: "Two integration tests exist but require external Llama Stack server and are skipped by default"
  - dimension: "Build Integration"
    score: 2.0
    status: "CI workflow is dispatch-only, no PR-triggered test or build validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "Only a devcontainer Dockerfile, no image build/test pipeline"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tool integration, no thresholds, no PR reporting"
  - dimension: "CI/CD Automation"
    score: 3.0
    status: "Pre-commit runs on PRs but core CI (lint, test, build) is dispatch-only"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules or test guidance"
critical_gaps:
  - title: "CI workflow does not run on PRs"
    impact: "Lint, test, and build jobs are workflow_dispatch only — PRs merge without any automated checks beyond pre-commit"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "Tests are explicitly disabled"
    impact: "The scripts/test file exits 0 immediately with a message that tests are disabled due to OpenAPI spec issues"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No visibility into which code paths are tested; regressions go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No security scanning (SAST, dependency, container)"
    impact: "Vulnerabilities in dependencies or code are not detected before release"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Mypy is commented out in both lint script and pre-commit"
    impact: "Type safety checks are not enforced despite strict mypy config in pyproject.toml"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Enable CI workflow on pull_request trigger"
    effort: "30 minutes"
    impact: "All PRs will get lint, build, and test validation automatically"
  - title: "Fix or replace the Prism mock server dependency for tests"
    effort: "4-8 hours"
    impact: "Re-enable the 55 auto-generated test files covering all API endpoints"
  - title: "Add pytest-cov and codecov integration"
    effort: "2-3 hours"
    impact: "Immediate visibility into test coverage with PR-level reporting"
  - title: "Uncomment mypy in the lint script"
    effort: "1-2 hours"
    impact: "Enforce type safety that is already configured in pyproject.toml"
recommendations:
  priority_0:
    - "Add pull_request trigger to ci.yml so lint/test/build run on every PR"
    - "Fix the test infrastructure — either fix the OpenAPI spec for Prism or switch to respx-based mock testing"
    - "Add dependency scanning (Dependabot or Renovate) and CodeQL/Semgrep SAST workflow"
  priority_1:
    - "Add pytest-cov coverage tracking with codecov integration and minimum thresholds"
    - "Enable mypy in lint pipeline — config is already in pyproject.toml"
    - "Write unit tests for hand-written lib/ code (agents, CLI, event system) — currently only 1 test file covers this"
    - "Add Trivy or Snyk dependency vulnerability scanning"
  priority_2:
    - "Create CLAUDE.md and .claude/rules/ for agent-assisted test creation"
    - "Add contract tests validating client against Llama Stack OpenAPI spec"
    - "Add multi-Python-version testing matrix (3.12, 3.13)"
    - "Add release automation with changelog generation"
---

# Quality Analysis: llama-stack-client-python

## Executive Summary

- **Overall Score: 3.8/10**
- **Repository Type**: Python SDK/API client library (auto-generated via Stainless with hand-written extensions)
- **Primary Language**: Python (100%)
- **Framework**: httpx-based REST client with pydantic models, CLI, and agent framework

**Key Strengths:**
- Well-structured pre-commit configuration with ruff linting and formatting
- Strong mypy configuration defined (though not enforced)
- Good test architecture with both sync and async test fixtures
- Hand-written integration tests for the agent framework
- Modern Python tooling (uv, hatch, ruff)

**Critical Gaps:**
- CI workflow is **dispatch-only** — does not run on PRs
- Tests are **explicitly disabled** in the test script (`exit 0`)
- Zero coverage tracking or enforcement
- No security scanning whatsoever
- No agent rules for AI-assisted development

**Agent Rules Status:** Missing — no CLAUDE.md, no .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 5.0/10 | 55 auto-generated test files exist but are DISABLED; 1 hand-written lib test file |
| Integration/E2E | 4.0/10 | 2 integration tests exist but require external server and skip in CI |
| **Build Integration** | **2.0/10** | **CI is dispatch-only; no PR-time build or package validation** |
| Image Testing | 1.0/10 | Only a devcontainer Dockerfile; no image build/test pipeline |
| Coverage Tracking | 1.0/10 | No coverage tool, no thresholds, no PR reporting |
| CI/CD Automation | 3.0/10 | Pre-commit runs on PRs; core CI is dispatch-only |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude/ directory, no test automation guidance |

## Critical Gaps

### 1. CI Workflow Does Not Run on PRs
- **Impact**: The `ci.yml` workflow (lint + test + build) uses only `workflow_dispatch` trigger. PRs merge with zero automated validation beyond pre-commit hooks.
- **Severity**: HIGH
- **Effort**: 30 minutes
- **File**: `.github/workflows/ci.yml:3` — change `workflow_dispatch` to include `pull_request` and `push` triggers

### 2. Tests Are Explicitly Disabled
- **Impact**: `scripts/test` prints a message that tests are disabled due to OpenAPI spec issues and immediately exits with code 0. Even if CI ran on PRs, no tests would execute.
- **Severity**: HIGH
- **Effort**: 4-8 hours (need to fix mock server or adopt alternative approach)
- **Root Cause**: The auto-generated tests rely on a Prism mock server against the OpenAPI spec, but the spec reportedly has issues preventing mock server operation.

### 3. No Coverage Tracking
- **Impact**: No visibility into test coverage. No codecov/coveralls integration. No minimum coverage thresholds. Regression detection is impossible.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Note**: pytest-cov is not even in dev dependencies

### 4. No Security Scanning
- **Impact**: No SAST (CodeQL, Semgrep), no dependency scanning (Dependabot alerts, Snyk), no secret detection (Gitleaks). As an SDK distributed via PyPI, supply chain security is critical.
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 5. Mypy Type Checking Disabled
- **Impact**: Despite a comprehensive mypy configuration in `pyproject.toml` (strict mode, disallow_untyped_defs, etc.), mypy is commented out in both `scripts/lint` and `.pre-commit-config.yaml`.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours (may need to fix type errors before enabling)

## Quick Wins

### 1. Enable CI on Pull Requests (30 minutes)
Add `pull_request` trigger to `ci.yml`:
```yaml
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
```

### 2. Add Coverage Tracking (2-3 hours)
Add `pytest-cov` to dev dependencies and create `.codecov.yml`:
```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: 60%
    patch:
      default:
        target: 80%
```

### 3. Uncomment Mypy (1-2 hours)
In `scripts/lint`, uncomment:
```bash
echo "==> Running mypy"
uv run mypy .
```

### 4. Add Dependabot (30 minutes)
Create `.github/dependabot.yml`:
```yaml
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

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory:**

| Workflow | Trigger | Jobs | Status |
|----------|---------|------|--------|
| `ci.yml` | `workflow_dispatch` only | lint, build, test | Not running on PRs |
| `pre-commit.yml` | `pull_request`, `push:main` | pre-commit checks | Active |
| `publish-pypi.yml` | `release:published`, `workflow_dispatch` | publish to PyPI | Active |

**Key Issues:**
- The `ci.yml` workflow has **no PR trigger** — it only runs when manually dispatched. This means lint, build, and test jobs never run automatically.
- The `pre-commit.yml` is the only workflow running on PRs, providing only basic formatting/linting via ruff (scoped to `src/llama_stack_client/lib/` only).
- No caching of dependencies in `ci.yml` (though uv is fast enough this is minor).
- No concurrency control on any workflow.
- Build job uploads artifacts to Stainless package registry, suggesting upstream sync workflow.

### Test Coverage

**Test Structure:**
- **55 test files** total across `tests/` directory
- **~18,100 lines of test code** vs **~43,700 lines of source code** (test-to-source ratio: 0.41)
- Most tests are auto-generated by Stainless from the OpenAPI spec

**Test Categories:**

| Category | Files | Status |
|----------|-------|--------|
| API resource tests (auto-generated) | 38 files in `tests/api_resources/` | DISABLED (Prism mock server broken) |
| Client infrastructure tests | 10 files (`test_client.py`, `test_streaming.py`, etc.) | DISABLED |
| Hand-written lib tests | 1 file (`tests/lib/agents/test_agent_responses.py`) | Likely runs but CI doesn't trigger |
| Integration tests | 2 files in `tests/integration/` | Skip unless external server available |

**Critical Finding:** `scripts/test` contains:
```bash
echo "Tests are currently disabled because the OpenAPI spec has quite a few 'issues'..."
exit 0
```
This means **no tests run in CI**, period.

**Testing Framework:** pytest with pytest-asyncio, pytest-xdist (parallel), respx (HTTP mocking), time-machine, dirty-equals.

**Hand-Written Tests:** `tests/lib/agents/test_agent_responses.py` (206 lines) provides thorough unit tests for the Agent class using fake client objects. This is well-designed and tests session management, client tools, and server tool event streams.

**Integration Tests:** Two files test against a live Llama Stack server:
- `test_agent_responses_e2e.py` — Tests streaming, follow-up turns, vector store integration
- `test_agent_turn_step_events.py` — Tests turn/step event model with file_search and function tools

Both are skipped unless `LLAMA_STACK_TEST_MODEL` and `TEST_API_BASE_URL` environment variables are set.

### Code Quality

**Linting:**
- **ruff** configured in `pyproject.toml` with isort, bugbear, unused imports, type checking rules
- Line length: 120
- Pre-commit runs ruff check and ruff-format (scoped to `lib/` directory only)
- `blacken-docs` for code examples in docstrings

**Type Checking:**
- **pyright** (v1.1.399) in dev dependencies but not run in CI
- **mypy** configured with strict settings in `pyproject.toml` but commented out everywhere it could run
- Strong type annotations throughout the codebase (typed library per classifiers)

**Pre-commit Hooks:**
- check-merge-conflict
- check-added-large-files (1MB max)
- end-of-file-fixer
- ruff (check + format, lib/ only)
- blacken-docs
- Commented out: mypy, pydoclint, markdown-link-check

**Static Analysis:**
- No SAST tools (CodeQL, Semgrep, Bandit)
- No secret detection (Gitleaks, TruffleHog)
- No dependency vulnerability scanning

### Container Images

- **Devcontainer only**: `.devcontainer/Dockerfile` provides a development environment (Python 3.9 + uv)
- No production Dockerfile — this is a library, not a deployable service
- No image testing pipeline — appropriate for a library, but the devcontainer is untested
- **Score rationale**: As a Python library distributed via PyPI, container image testing is less critical. Score reflects minimal devcontainer presence.

### Security

- **No security scanning** of any kind
- No Dependabot/Renovate for dependency updates
- No CodeQL or Semgrep workflows
- No secret detection
- `SECURITY.md` exists (standard Meta security policy)
- PyPI token stored as GitHub secret (appropriate)
- **Supply chain risk**: As a library installed by downstream users, dependency security is critical but unmonitored

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no CLAUDE.md, no .claude/ directory
- **Quality**: N/A
- **Gaps**: 
  - No test creation rules for any test type
  - No coding standards for agent-assisted development
  - No framework-specific guidance (pytest patterns, async testing, mock strategies)
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering unit tests, integration tests, and the Stainless auto-generated test patterns

## Recommendations

### Priority 0 (Critical)

1. **Add PR triggers to CI workflow** — Change `ci.yml` to run on `pull_request` and `push:main`. This is a 30-minute fix that immediately improves quality gates.

2. **Fix or replace the broken test infrastructure** — The Prism mock server approach is non-functional. Options:
   - Fix the OpenAPI spec issues that prevent Prism from working
   - Switch to respx-based mocking (already a dev dependency) for auto-generated tests
   - At minimum, ensure hand-written tests in `tests/lib/` and `tests/integration/` can run

3. **Add security scanning** — Create CodeQL workflow, enable Dependabot, add `pip-audit` or `safety` to CI for dependency vulnerability detection.

### Priority 1 (High Value)

4. **Add coverage tracking** — Add pytest-cov, configure codecov, set minimum thresholds (start at 40% given current state, increase over time).

5. **Enable mypy** — The configuration is already comprehensive in `pyproject.toml`. Uncomment in lint script and pre-commit. Fix any type errors.

6. **Write tests for hand-written lib/ code** — The `lib/` directory contains ~60 hand-written Python files (agents, CLI, inference, tools) but only 1 test file covers them. Priority targets:
   - `lib/agents/event_synthesizer.py`
   - `lib/agents/tool_parser.py`
   - `lib/cli/` (command tests)
   - `lib/agents/react/` (ReAct agent)

7. **Add Trivy/pip-audit for dependency scanning** — As a library with 13+ runtime dependencies, monitoring for vulnerabilities is essential.

### Priority 2 (Nice-to-Have)

8. **Create CLAUDE.md and .claude/rules/** — Add agent rules for test creation, covering pytest patterns, async test conventions, the Stainless auto-gen patterns, and integration test guidelines.

9. **Add contract tests** — Validate the client against the Llama Stack OpenAPI spec as a CI step to catch spec drift.

10. **Multi-Python-version CI matrix** — Currently targets Python 3.12+ only. Test across 3.12 and 3.13 in CI matrix.

11. **Add release automation** — Automate changelog generation, version bumping, and release workflows.

## Comparison to Gold Standards

| Dimension | llama-stack-client-python | odh-dashboard | notebooks | kserve |
|-----------|--------------------------|---------------|-----------|--------|
| Unit Tests | 5/10 (exist but disabled) | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 4/10 (skip in CI) | 9/10 | 8/10 | 9/10 |
| Build Integration | 2/10 (dispatch-only) | 8/10 | 7/10 | 8/10 |
| Image Testing | 1/10 (devcontainer only) | 8/10 | 10/10 | 7/10 |
| Coverage Tracking | 1/10 (none) | 8/10 | 6/10 | 9/10 |
| CI/CD Automation | 3/10 (pre-commit only) | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 (none) | 7/10 | 4/10 | 3/10 |
| **Overall** | **3.8/10** | **8.5/10** | **7.5/10** | **8.0/10** |

## File Paths Reference

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Main CI (lint, build, test) — dispatch-only |
| `.github/workflows/pre-commit.yml` | Pre-commit hooks on PRs |
| `.github/workflows/publish-pypi.yml` | PyPI release publishing |
| `pyproject.toml` | Project config, ruff, mypy, pytest settings |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `scripts/test` | Test runner — currently exits immediately |
| `scripts/lint` | Linter — ruff only, mypy commented out |
| `scripts/bootstrap` | Dev environment setup |
| `tests/conftest.py` | Shared test fixtures (sync/async clients) |
| `tests/api_resources/` | Auto-generated API endpoint tests |
| `tests/lib/agents/test_agent_responses.py` | Hand-written agent framework tests |
| `tests/integration/` | E2E tests requiring live server |
| `src/llama_stack_client/lib/` | Hand-written library code (agents, CLI, tools) |
| `.devcontainer/Dockerfile` | Development container definition |
