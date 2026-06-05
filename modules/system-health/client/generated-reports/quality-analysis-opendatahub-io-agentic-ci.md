---
repository: "opendatahub-io/agentic-ci"
overall_score: 6.8
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test-to-code ratio (65%), pytest with thorough mocking, edge cases covered"
  - dimension: "Integration/E2E"
    score: 4.0
    status: "E2E skill documented but manual; no automated integration tests against real backends"
  - dimension: "Build Integration"
    score: 2.0
    status: "No container build, no Konflux simulation, no PR-time image validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "No Dockerfile, no container image testing — this is a pure Python library"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "No coverage generation, no codecov integration, no coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 7.5
    status: "Well-organized CI with multi-version matrix, lint, format, typecheck; publish workflow with trusted publishing"
  - dimension: "Agent Rules"
    score: 6.0
    status: "AGENTS.md with architecture docs, conventions, and verification checklist; one E2E skill; no .claude/rules/"
critical_gaps:
  - title: "No test coverage tracking or enforcement"
    impact: "Coverage regressions go undetected; no visibility into untested code paths"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No automated integration/E2E tests"
    impact: "Backend integration bugs (Podman, OpenShell) only caught by manual testing"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "cli.py, otel.py, skill.py, and stream.py (ClaudeCode) have no unit tests"
    impact: "~1,395 lines of core source code with zero test coverage"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No security scanning (Trivy, CodeQL, Gitleaks, Dependabot)"
    impact: "Vulnerabilities in dependencies not detected until downstream consumers scan"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add pytest-cov and codecov integration"
    effort: "2-3 hours"
    impact: "Immediate visibility into test coverage gaps; PR-level coverage enforcement"
  - title: "Add Dependabot or Renovate for dependency updates"
    effort: "30 minutes"
    impact: "Automated security patches for transitive dependencies"
  - title: "Add unit tests for cli.py argument parsing"
    effort: "2-3 hours"
    impact: "Cover the main entry point and argument validation paths"
  - title: "Add pre-commit hooks configuration"
    effort: "1 hour"
    impact: "Catch lint/format issues before commit, not just in CI"
recommendations:
  priority_0:
    - "Add pytest-cov to tox.ini and integrate with Codecov for PR-level coverage reporting"
    - "Write unit tests for cli.py, otel.py, skill.py, and stream.py (ClaudeCodeStreamProcessor)"
  priority_1:
    - "Add GitHub Dependabot or Renovate for automated dependency updates"
    - "Add CodeQL or Bandit scanning workflow for SAST"
    - "Create automated integration smoke tests using Podman in CI (with mocked API)"
  priority_2:
    - "Add .claude/rules/ with unit-test and integration-test writing guidelines"
    - "Add pre-commit configuration for ruff lint and format"
    - "Add property-based testing (Hypothesis) for ADF conversion and verdict validation"
---

# Quality Analysis: agentic-ci

## Executive Summary

- **Overall Score: 6.8/10**
- **Repository Type**: Python library/CLI tool for running AI coding agents in sandboxed CI environments
- **Primary Language**: Python 3.10+ (5,977 source lines, 3,901 test lines)
- **Key Strengths**: Excellent unit test coverage for tested modules (65% test-to-code ratio), clean CI pipeline with multi-version Python matrix testing, strong code quality tooling (ruff lint + format, mypy), comprehensive AGENTS.md
- **Critical Gaps**: No coverage tracking/enforcement, several core modules completely untested (cli.py, otel.py, skill.py), no automated integration/E2E tests, no security scanning
- **Agent Rules Status**: Present (AGENTS.md with architecture docs and conventions); no `.claude/rules/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent test-to-code ratio for covered modules; pytest with thorough mocking |
| Integration/E2E | 4.0/10 | E2E test skill documented but fully manual; no automated integration tests |
| **Build Integration** | **2.0/10** | **No container build, no Konflux simulation, no PR-time image validation** |
| Image Testing | 1.0/10 | N/A — pure Python library, no container image to test |
| Coverage Tracking | 2.0/10 | No coverage generation, no codecov, no thresholds |
| CI/CD Automation | 7.5/10 | Well-organized CI with matrix testing; trusted PyPI publishing |
| Agent Rules | 6.0/10 | Good AGENTS.md with architecture and conventions; one E2E skill; no rules directory |

## Critical Gaps

### 1. No Test Coverage Tracking or Enforcement
- **Impact**: Coverage regressions go undetected. No visibility into which code paths are tested.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `.gitignore` lists coverage artifacts (`.coverage`, `coverage.xml`, `htmlcov/`) suggesting coverage was considered, but no `pytest-cov` dependency exists in `pyproject.toml` or `tox.ini`, and no `--cov` flags are passed to pytest. No Codecov/Coveralls integration.

### 2. No Automated Integration/E2E Tests
- **Impact**: Podman and OpenShell backend behavior only verified by manual E2E testing documented in `.claude/skills/test-e2e-podman/SKILL.md`.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The E2E skill is thorough (4 sections × multiple steps, Vertex AI + API key + Claude + OpenCode combos) but requires a human operator with Podman installed and API credentials. No CI job runs these tests.

### 3. Core Modules Without Unit Tests (~1,395 lines)
- **Impact**: The most critical runtime code paths are untested.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Untested modules**:
  - `cli.py` (251 lines) — Main entry point, argument parsing, subcommand dispatch
  - `otel.py` (281 lines) — OTLP HTTP receiver, token/cost tracking, summary
  - `skill.py` (307 lines) — Generic skill runner framework (SkillConfig, run_skill)
  - `stream.py` ClaudeCodeStreamProcessor half (556 lines total, OpenCode tested) — Parsed stream output for Claude Code harness
  - `backend.py` process_stream (124 lines) — Base class stream processing
  - `backends/openshell/` gateway.py, sandbox.py, __init__.py (265 lines) — OpenShell lifecycle

### 4. No Security Scanning
- **Impact**: Vulnerabilities in `requests`, `tenacity`, and optional dependencies (`PyJWT`, `cryptography`) not detected.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: No CodeQL, Bandit, Snyk, Trivy, or Dependabot configuration. No `.gitleaks.toml` despite the project implementing gitleaks as a gate.

## Quick Wins

### 1. Add pytest-cov and Codecov Integration (2-3 hours)
Add `pytest-cov` to test dependencies and configure coverage collection:

```toml
# pyproject.toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.11",
]
```

```ini
# tox.ini [testenv] section
commands = pytest --cov=agentic_ci --cov-report=xml {posargs:tests/}
```

Add a `.codecov.yml`:
```yaml
coverage:
  status:
    project:
      default:
        target: 70%
    patch:
      default:
        target: 80%
```

### 2. Add Dependabot for Dependency Updates (30 minutes)
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

### 3. Add Unit Tests for cli.py (2-3 hours)
Test argument parsing, subcommand dispatch, and error handling. The module uses argparse which is highly testable with `parse_args()` calls.

### 4. Add Pre-commit Configuration (1 hour)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (2 total)**:

1. **`ci.yml`** — Triggered on push and pull_request
   - Matrix strategy: `[py310, py311, py312, py313, lint, check-format, typecheck]`
   - Uses `fedora-python/tox-github-action` for execution
   - Runs on `ubuntu-latest`
   - No concurrency control (multiple CI runs for same PR can overlap)
   - No caching configured (tox environments rebuilt each run)

2. **`publish.yml`** — Triggered on version tags (`[0-9]+.[0-9]+.[0-9]+`)
   - Uses `uv build` for sdist and wheel
   - Trusted publishing to PyPI via `pypa/gh-action-pypi-publish`
   - Properly scoped permissions (`contents: read`, `id-token: write`)
   - Repository owner check (`github.repository_owner == 'opendatahub-io'`)

**Strengths**:
- Multi-version Python testing (3.10, 3.11, 3.12, 3.13)
- Separate lint, format-check, and typecheck envs
- Action versions pinned to commit SHAs (supply chain security)
- Trusted PyPI publishing (no API tokens stored)

**Gaps**:
- No concurrency control for PRs (stale runs may waste resources)
- No dependency caching (tox env rebuild every time)
- No coverage reporting in CI
- No security scanning workflow

### Test Coverage

**Test files**: 18 test files (excluding `__init__.py`) covering 15 of ~22 source modules.

**Test-to-code ratio**: 3,901 test lines / 5,977 source lines = **65%** (strong)

**Coverage by module**:

| Source Module | Test File | Coverage Depth |
|---------------|-----------|---------------|
| `backends/__init__.py` | `test_backend.py` | Full (factory, params, errors) |
| `backends/podman.py` | `test_podman.py` | Strong (credentials, env, volumes, API key) |
| `backends/openshell/policy.py` | `test_policy.py` | Full (resolution priority) |
| `harness.py` | `test_harness.py` | Excellent (both harnesses, auth modes, all methods) |
| `gates.py` | `test_gates.py`, `test_gate_registry.py` | Excellent (all gates, registry, env validation) |
| `verdict.py` | `test_verdict.py` | Full (valid, invalid, missing, malformed) |
| `pipeline.py` | `test_pipeline.py` | Full (distribution, noop, generation, edge cases) |
| `jira/client.py` | `test_jira_client.py` | Excellent (CRUD, retry, pagination, 429 handling) |
| `jira/acli.py` | `test_acli_client.py` | Full (all operations, fallback to REST) |
| `jira/adf.py` | `test_adf.py` | Full (markdown→ADF, ADF→text, roundtrip) |
| `stream.py` (OpenCode) | `test_stream_opencode.py` | Excellent (all event types, formatting, edge cases) |
| `git.py` | `test_git_credentials.py` | Partial (credential setup only) |
| `forge/__init__.py` | `test_forge_init.py` | Full (detection, URL parsing) |
| `forge/cli.py` | `test_forge_cli.py` | Excellent (all subcommands, token passthrough) |
| `forge/github.py` | `test_forge_github.py` | Excellent (CRUD, GraphQL, pipeline status) |
| `forge/gitlab.py` | `test_forge_gitlab.py` | Excellent (CRUD, threads, diff position) |
| `forge/session.py` | `test_forge_session.py` | Full (adapters, auth, error extraction) |
| **`cli.py`** | **None** | **0% — main entry point untested** |
| **`otel.py`** | **None** | **0% — OTLP receiver untested** |
| **`skill.py`** | **None** | **0% — skill runner framework untested** |
| **`stream.py` (Claude)** | **None** | **0% — ClaudeCodeStreamProcessor untested** |
| **`backend.py`** | **Partial** | **_process_stream helper untested** |
| **`backends/openshell/`** | **None** | **0% — gateway, sandbox lifecycle untested** |

**Testing Frameworks**: pytest (standard), unittest.mock (mocking), monkeypatch (env vars), tmp_path (temp files), capsys (stdout capture), caplog (log capture), parametrize (parameterized tests)

**Testing Patterns**: Well-structured test classes grouped by feature, proper use of fixtures, consistent error testing with `pytest.raises`, good edge case coverage (empty inputs, missing keys, invalid formats).

### Code Quality

**Linting**:
- **Ruff**: Configured in `pyproject.toml` with `line-length = 100`
- Selected rule sets: `F` (pyflakes), `E` (pycodestyle errors), `W` (warnings), `I` (isort), `N` (naming)
- Could add: `S` (bandit/security), `B` (bugbear), `UP` (pyupgrade), `SIM` (simplify)
- Runs in CI via `tox -e lint`

**Formatting**:
- Ruff format with CI check via `tox -e check-format`
- Auto-fix available via `tox -e format`

**Type Checking**:
- mypy configured in `pyproject.toml` with `allow_redefinition = true`, `warn_unused_ignores = true`
- Runs in CI via `tox -e typecheck`
- Checks `src/` only (not tests)

**Pre-commit Hooks**: None configured

**Static Analysis**: No SAST tools (CodeQL, Bandit, Semgrep)

### Container Images

Not applicable — `agentic-ci` is a pure Python library/CLI tool distributed via PyPI. It does not build container images itself (it *uses* container images provided by consumers). No Dockerfile or Containerfile exists in the repository.

### Security

**Current State**:
- No vulnerability scanning (Trivy, Snyk, Grype)
- No SAST/CodeQL integration
- No dependency scanning (Dependabot, Renovate)
- No secret detection in repo (`.gitleaks.toml` absent)
- Action versions pinned to commit SHAs (good practice)
- Publish workflow uses trusted publishing (no stored API tokens)
- Runtime dependencies are minimal (`requests`, `tenacity`)

**Irony**: The project *implements* a gitleaks gate for its consumers but doesn't run gitleaks on itself.

### Agent Rules (Agentic Flow Quality)

**Status**: Present and functional

**AGENTS.md** (symlinked as `CLAUDE.md`):
- Architecture overview with module descriptions
- CLI commands for all development tasks (test, lint, format, typecheck)
- Verification checklist: "run all four checks before reporting task as done"
- Conventions section: Python 3.10+, ruff, pytest, no `# noqa`
- Quality: **Good** — clear, actionable, covers development workflow

**.claude/skills/**:
- `test-e2e-podman/SKILL.md`: Comprehensive manual E2E test plan covering 4 sections (Claude+Vertex, Claude+API Key, OpenCode+Vertex, OpenCode+API Key)
- Quality: **Excellent** — step-by-step instructions with verification criteria

**Gaps**:
- No `.claude/rules/` directory for test creation guidance
- No unit test writing guidelines for AI agents
- No integration test patterns documented
- Missing rules for: mocking patterns, fixture usage, test naming conventions

## Recommendations

### Priority 0 (Critical)

1. **Add test coverage tracking with enforcement** — Add `pytest-cov` to tox.ini, integrate Codecov with a 70% project target and 80% patch target. This will immediately reveal the ~40% of source code with zero tests.

2. **Write unit tests for untested core modules** — `cli.py` (argument parsing), `otel.py` (token tracking), `skill.py` (skill runner lifecycle), and `stream.py` ClaudeCodeStreamProcessor. These are the most critical runtime paths.

### Priority 1 (High Value)

3. **Add GitHub Dependabot** for automated dependency updates. The `cryptography` optional dependency is especially important to keep current.

4. **Add CodeQL or Bandit SAST scanning** — Enable the `S` (bandit) rule set in ruff and/or add a CodeQL workflow for Python.

5. **Create automated integration smoke tests** — Even without real API access, test the Podman backend's `setup()` command construction and subprocess argument building. Use `subprocess.run` mocking at a higher level than current unit tests.

### Priority 2 (Nice-to-Have)

6. **Add `.claude/rules/` directory** with guidelines for writing unit tests, integration tests, and mocking patterns specific to this codebase.

7. **Add pre-commit hooks** with ruff lint and format to catch issues before CI.

8. **Add concurrency control** to CI workflow: `concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }`

9. **Add tox environment caching** in CI to speed up builds.

## Comparison to Gold Standards

| Practice | agentic-ci | odh-dashboard | notebooks | kserve |
|----------|-----------|---------------|-----------|--------|
| Unit test ratio | 65% (strong) | 70%+ | N/A | 60%+ |
| Coverage enforcement | None | Codecov with thresholds | N/A | Codecov required |
| E2E automation | Manual skill | Automated Cypress | Automated notebooks | Automated KServe |
| Security scanning | None | Trivy + SAST | Container scanning | Multiple scanners |
| Pre-commit hooks | None | Configured | N/A | Configured |
| Type checking | mypy in CI | TypeScript strict | N/A | Go vet |
| Multi-version testing | py310-313 | Node matrix | Image matrix | Go version matrix |
| Agent rules | AGENTS.md + 1 skill | Comprehensive rules | N/A | N/A |
| CI concurrency | None | Configured | Configured | Configured |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` — Main CI pipeline
- `.github/workflows/publish.yml` — PyPI publish workflow
- `tox.ini` — Test/lint/format/typecheck orchestration
- `pyproject.toml` — Build system, dependencies, tool config

### Testing
- `tests/` — All unit tests (18 test files)
- `.claude/skills/test-e2e-podman/SKILL.md` — Manual E2E test plan

### Code Quality
- `pyproject.toml` — Ruff lint/format config, mypy config
- No `.pre-commit-config.yaml`
- No `.codecov.yml`

### Agent Rules
- `AGENTS.md` (symlinked as `CLAUDE.md`) — Architecture, commands, conventions
- `.claude/skills/test-e2e-podman/` — E2E test skill

### Source Code
- `src/agentic_ci/` — Main package (27 Python files, 5,977 lines)
- `src/agentic_ci/cli.py` — Entry point
- `src/agentic_ci/backends/` — Podman and OpenShell backends
- `src/agentic_ci/forge/` — GitHub/GitLab forge abstraction
- `src/agentic_ci/jira/` — Jira REST API client
