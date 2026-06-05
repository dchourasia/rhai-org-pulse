---
repository: "opendatahub-io/agent-eval-harness"
overall_score: 5.4
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "309 test functions across 20+ files; good pytest fixtures; but ~7,250 LOC of skill scripts untested"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "E2E tests exist using real Claude API; evalhub has integration tests; but coverage is thin (2 E2E, 1 integration)"
  - dimension: "Build Integration"
    score: 2.0
    status: "No PR-time container build validation; no Containerfile build test; no image startup testing"
  - dimension: "Image Testing"
    score: 2.0
    status: "Containerfile exists for evalhub but no image build in CI; no runtime validation; no multi-arch"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tool configured; no codecov/coveralls; no coverage thresholds; no PR reporting"
  - dimension: "CI/CD Automation"
    score: 6.0
    status: "4 workflows (tests, lint, release, lint-review); semantic-release; but no caching, no E2E in CI"
  - dimension: "Agent Rules"
    score: 8.0
    status: "Comprehensive CLAUDE.md and AGENTS.md with architecture docs; .claude-plugin config; no .claude/rules/ for test patterns"
critical_gaps:
  - title: "No test coverage tracking"
    impact: "Cannot detect coverage regressions; unclear which modules are under-tested"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "7,250 LOC of skill scripts have zero test coverage"
    impact: "Core scoring, execution, collection, and workspace scripts are completely untested"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "No container image build or test in CI"
    impact: "Containerfile breakage discovered only at deployment time"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning (SAST, dependency, container)"
    impact: "Vulnerabilities in dependencies or container image undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No linting or static analysis"
    impact: "No ruff, flake8, mypy, or any Python linter configured; code quality issues go undetected"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add pytest-cov and codecov integration"
    effort: "2-3 hours"
    impact: "Immediate visibility into coverage gaps; PR coverage reporting"
  - title: "Add ruff linting to CI"
    effort: "1-2 hours"
    impact: "Catches common Python bugs, enforces style consistency"
  - title: "Add Trivy container scanning"
    effort: "1-2 hours"
    impact: "Detect vulnerabilities in UBI9 base image and dependencies"
  - title: "Add Containerfile build to PR workflow"
    effort: "1-2 hours"
    impact: "Catch container build failures before merge"
recommendations:
  priority_0:
    - "Add pytest-cov with coverage thresholds and codecov integration"
    - "Add container image build validation to PR workflow"
    - "Add dependency vulnerability scanning (Dependabot or Trivy)"
  priority_1:
    - "Add unit tests for skill scripts (score.py, execute.py, workspace.py, collect.py)"
    - "Add ruff or flake8 linting with CI enforcement"
    - "Add mypy type checking for the agent_eval package"
    - "Run E2E tests in CI (scheduled, not on every PR)"
  priority_2:
    - "Add pre-commit hooks for formatting and linting"
    - "Add SBOM generation for container image"
    - "Create .claude/rules/ with test pattern guidelines"
    - "Add multi-architecture container build support"
---

# Quality Analysis: agent-eval-harness

## Executive Summary

- **Overall Score: 5.4/10**
- **Repository Type**: Python CLI tool / Claude Code plugin / evaluation framework
- **Primary Language**: Python 3.11+
- **Framework**: Claude Code plugin with skills, pytest for testing, MLflow integration
- **Key Strengths**: Strong unit test suite (309 test functions), well-documented architecture (CLAUDE.md/AGENTS.md), semantic versioning with automated releases, skillsaw lint enforcement
- **Critical Gaps**: Zero coverage tracking, no container image testing in CI, no security scanning, no Python linter, 7,250 LOC of skill scripts completely untested
- **Agent Rules Status**: Present (CLAUDE.md, AGENTS.md) — comprehensive architecture docs but no .claude/rules/ for test patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | 309 test functions; good fixtures; but skill scripts untested |
| Integration/E2E | 5.0/10 | E2E tests exist with real API calls; thin coverage (3 tests) |
| **Build Integration** | **2.0/10** | **No PR-time container build; no image validation** |
| Image Testing | 2.0/10 | Containerfile exists but not built/tested in CI |
| Coverage Tracking | 1.0/10 | No coverage tooling configured at all |
| CI/CD Automation | 6.0/10 | 4 workflows; semantic-release; no caching; no E2E in CI |
| Agent Rules | 8.0/10 | Excellent CLAUDE.md/AGENTS.md; no .claude/rules/ |

## Critical Gaps

### 1. No Test Coverage Tracking
- **Impact**: Cannot detect coverage regressions or identify under-tested modules
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No `pytest-cov`, no `.coveragerc`, no codecov/coveralls integration, no coverage thresholds, no PR coverage reports. The `pyproject.toml` has no coverage-related configuration at all.

### 2. 7,250 LOC of Skill Scripts Untested
- **Impact**: Core functionality (scoring, execution, workspace creation, artifact collection, HTML reporting) has zero automated tests
- **Severity**: HIGH
- **Effort**: 20-40 hours
- **Details**: The `skills/` directory contains 17 Python scripts totaling 7,250 LOC. These implement the core eval pipeline (workspace.py, execute.py, collect.py, score.py, report.py, tools.py) but have no corresponding test files. Only the `agent_eval/` package (5,219 LOC) is tested.

### 3. No Container Image Build or Test in CI
- **Impact**: Containerfile breakage discovered only at deployment time
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: `deploy/evalhub/Containerfile` builds a UBI9-based image but no CI workflow builds or tests this image. No `docker build` step in any workflow. No image startup validation. No multi-architecture support.

### 4. No Security Scanning
- **Impact**: Vulnerabilities in dependencies or container images go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No Trivy, Snyk, CodeQL, Dependabot, Gitleaks, or any other security scanning tool configured. No `.trivyignore`, no `codeql-analysis.yml`, no dependency review workflow.

### 5. No Python Linting or Static Analysis
- **Impact**: Code quality issues, type errors, and style inconsistencies go undetected
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No ruff, flake8, pylint, mypy, or any Python linter. The only linting is `skillsaw` which checks skill metadata quality, not Python code quality. No `.pre-commit-config.yaml`.

## Quick Wins

### 1. Add pytest-cov and codecov integration (2-3 hours)
- Install `pytest-cov` as test dependency
- Add `--cov=agent_eval --cov-report=xml` to pytest config
- Add codecov upload step to tests workflow
- Set minimum coverage threshold (e.g., 60% to start)

```yaml
# In pyproject.toml
[tool.pytest.ini_options]
addopts = "-m 'not e2e' --cov=agent_eval --cov-report=xml --cov-fail-under=60"
```

### 2. Add ruff linting to CI (1-2 hours)
```yaml
# Add to lint.yml
- name: Run ruff
  uses: astral-sh/ruff-action@v3
  with:
    args: "check ."
```

### 3. Add Trivy container scanning (1-2 hours)
```yaml
# New workflow step
- name: Build container
  run: docker build -f deploy/evalhub/Containerfile -t eval-harness:test .
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: eval-harness:test
    severity: 'CRITICAL,HIGH'
```

### 4. Add Containerfile build to PR workflow (1-2 hours)
```yaml
# Add to tests.yml
- name: Build container image
  run: docker build -f deploy/evalhub/Containerfile -t eval-harness:pr-test .
```

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory** (4 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `tests.yml` | push (all branches), PR (main), workflow_call | Run pytest unit tests |
| `lint.yml` | push (main), PR (main) | Run skillsaw linter |
| `lint-review.yml` | workflow_run (lint completed) | Post skillsaw review comments on PRs |
| `release.yml` | push (main), workflow_dispatch | Tests + semantic-release |

**Strengths**:
- Tests run on all branch pushes (good for feature branches)
- Semantic-release with automated versioning across pyproject.toml, plugin.json, marketplace.json
- Lint results posted as PR review comments (nice developer experience)
- Reusable workflow pattern (`workflow_call` on tests.yml)
- Pin-by-SHA on all GitHub Actions (security best practice)

**Weaknesses**:
- No dependency caching (`actions/cache` or `setup-python` cache)
- No concurrency control (duplicate runs on push+PR)
- E2E tests not run in CI (manual only, require ANTHROPIC_API_KEY)
- No matrix testing (only Python 3.12, no 3.11 which is the minimum)
- No artifact upload for test results

### Test Coverage

**Unit Tests** (tests/ directory):
- **Framework**: pytest 8.0+
- **Test files**: 17 unit test files + 1 E2E file
- **Test functions**: 309 total (296 unit + 13 evalhub + 2 E2E)
- **Lines of test code**: 5,373
- **Conftest quality**: Excellent — well-structured fixtures, factory functions, composite fixtures for different stream versions

**Source-to-test mapping**:
- `agent_eval/` package: 5,219 LOC source → well covered by 17 test files
- `skills/` scripts: 7,250 LOC source → **zero test coverage**
- `deploy/evalhub/`: 64 LOC entrypoint + adapters → covered by 6 test files (836 LOC)
- **Test-to-code ratio**: 5,373 tests / 12,832 source = **0.42** (below 0.5 target)

**Modules without direct tests**:
- `agent_eval/agent/claude_code.py` (443 LOC) — the main runner, no unit tests
- `agent_eval/agent/base.py` (82 LOC) — ABC for runners
- `agent_eval/mlflow/experiment.py` (284 LOC) — MLflow integration
- `agent_eval/mlflow/traces.py` (138 LOC)
- `agent_eval/mlflow/datasets.py` (62 LOC)
- `agent_eval/evalhub/adapter.py` (434 LOC) — tested by deploy/ tests, not main suite
- `agent_eval/cli/trace_run.py` (308 LOC) — CLI entry point
- `agent_eval/state.py` (108 LOC)

**E2E Tests**:
- 2 E2E tests in `tests/e2e/test_external_state.py`
- Invoke real Claude API calls (~$0.50/run per CLAUDE.md)
- Test the eval-analyze → eval-dataset pipeline
- Require ANTHROPIC_API_KEY — not run in CI
- Well-structured with workspace initialization fixture

**EvalHub Tests**:
- 6 test files with 13 test functions in `deploy/evalhub/tests/`
- Cover adapter, config translator, results mapper, S3 dataset, entrypoint
- Integration test for adapter pipeline
- Isolated from main test suite (not run by default `make test`)

### Code Quality

**Linting**: 
- **Only skillsaw** — a plugin/skill metadata linter, not a Python code quality tool
- No ruff, flake8, pylint, bandit, or mypy
- No `.pre-commit-config.yaml`
- No type annotations enforcement

**Static Analysis**:
- No CodeQL, Semgrep, or gosec
- No dependency scanning

**Code Organization**:
- Clean package structure with clear separation (agent, judges, mlflow, evalhub, cli)
- Well-documented architecture in CLAUDE.md
- Semantic versioning with conventional commits

### Container Images

**Containerfile** (`deploy/evalhub/Containerfile`):
- Base: `registry.access.redhat.com/ubi9/python-311:latest` (good — Red Hat supported base)
- Multi-stage: No (single stage)
- Size optimization: `--no-cache-dir` on pip install
- Security: No user switching (runs as default user)
- Copies: pyproject.toml → install deps → copy source (reasonable layer ordering)

**Testing**:
- No CI build of the container image
- No image startup validation
- No vulnerability scanning
- No SBOM generation
- No multi-architecture support
- Smoke test directory exists (`deploy/evalhub/smoke-test/`) but not run in CI

### Security

**Current State**: No security scanning infrastructure at all.
- No Trivy / Snyk / Grype
- No CodeQL / Semgrep SAST
- No Dependabot / Renovate for dependency updates
- No Gitleaks / TruffleHog for secret detection
- No dependency review on PRs
- GitHub Actions pinned by SHA (good practice)

### Agent Rules (Agentic Flow Quality)

**Status**: Present and comprehensive

**What exists**:
- `CLAUDE.md` (root): Detailed architecture documentation, usage patterns, design decisions, test commands
- `AGENTS.md` (root): Identical to CLAUDE.md — provides context for all agent-based tools
- `.claude-plugin/plugin.json`: Plugin metadata with SessionStart hook
- `.skillsaw.yaml`: Skill quality linting configuration
- 7 skills with SKILL.md documentation (eval-analyze, eval-dataset, eval-run, eval-review, eval-mlflow, eval-optimize, eval-setup)

**What's missing**:
- No `.claude/rules/` directory with test creation guidelines
- No test pattern documentation (how to write unit tests for this project)
- No agent-specific quality gates or checklists

**Quality**: The CLAUDE.md is among the best I've seen — it documents every module, every skill, every configuration option, and design decisions. It serves both human developers and AI agents effectively. The gap is specifically in test creation guidance.

## Recommendations

### Priority 0 (Critical)

1. **Add pytest-cov with coverage tracking and enforcement**
   - Add `pytest-cov` to test dependencies
   - Configure coverage in pyproject.toml with `--cov-fail-under=60`
   - Add codecov GitHub Action to tests.yml
   - Add `.codecov.yml` for PR comment configuration
   - Effort: 2-4 hours

2. **Add container image build to PR workflow**
   - Add `docker build` step to tests.yml
   - Catch Containerfile breakage before merge
   - Effort: 1-2 hours

3. **Add dependency vulnerability scanning**
   - Enable Dependabot or add `pip-audit` to CI
   - Add Trivy for container image scanning
   - Effort: 2-4 hours

### Priority 1 (High Value)

4. **Add unit tests for skill scripts**
   - Priority scripts: `score.py` (scoring logic), `workspace.py` (workspace creation), `collect.py` (artifact collection)
   - These are the core eval pipeline — currently 7,250 LOC with zero tests
   - Effort: 20-40 hours (phased)

5. **Add ruff linting with CI enforcement**
   - Add `ruff.toml` configuration
   - Add ruff check to lint.yml workflow
   - Effort: 1-2 hours

6. **Add mypy type checking**
   - Configure mypy for `agent_eval/` package
   - Start with `--ignore-missing-imports` and tighten over time
   - Effort: 4-8 hours

7. **Run E2E tests in CI on a schedule**
   - Add cron-triggered workflow for E2E tests
   - Use GitHub secrets for ANTHROPIC_API_KEY
   - Effort: 2-3 hours

### Priority 2 (Nice-to-Have)

8. **Add pre-commit hooks**
   - ruff format, ruff check, trailing whitespace, YAML validation
   - Effort: 1-2 hours

9. **Create .claude/rules/ with test pattern guidelines**
   - Unit test patterns for this project
   - Fixture creation guidelines
   - Mock strategy documentation
   - Effort: 2-3 hours

10. **Add SBOM generation for container image**
    - Use Syft or similar tool
    - Effort: 1-2 hours

11. **Add multi-architecture container build**
    - Support amd64 and arm64
    - Effort: 2-4 hours

12. **Add Python version matrix testing**
    - Test against Python 3.11 and 3.12 (both supported per pyproject.toml)
    - Effort: 1 hour

## Comparison to Gold Standards

| Dimension | agent-eval-harness | odh-dashboard | notebooks | kserve |
|-----------|-------------------|---------------|-----------|--------|
| Unit Tests | 7.5 — 309 tests, good fixtures | 9 — multi-layer, contract tests | 7 — image-focused | 9 — extensive operator tests |
| Integration/E2E | 5.0 — 3 tests, manual only | 9 — comprehensive Cypress E2E | 8 — 5-layer validation | 9 — multi-version E2E |
| Build Integration | 2.0 — no CI builds | 8 — PR-time builds | 7 — image build matrix | 8 — operator manifests |
| Image Testing | 2.0 — Containerfile only | 7 — basic validation | 10 — gold standard | 7 — multi-platform |
| Coverage Tracking | 1.0 — none | 8 — codecov + thresholds | 6 — basic tracking | 9 — strict enforcement |
| CI/CD Automation | 6.0 — basic but functional | 9 — comprehensive | 8 — matrix builds | 9 — multi-stage |
| Agent Rules | 8.0 — excellent CLAUDE.md | 9 — rules + skills | 4 — minimal | 3 — none |

## File Paths Reference

### CI/CD
- `.github/workflows/tests.yml` — Unit tests (pytest)
- `.github/workflows/lint.yml` — Skillsaw linter
- `.github/workflows/lint-review.yml` — PR review comments
- `.github/workflows/release.yml` — Semantic release
- `.releaserc.json` — Semantic release config
- `Makefile` — Test/lint/install targets

### Testing
- `tests/conftest.py` — Shared fixtures and factory functions
- `tests/test_*.py` — 17 unit test files
- `tests/e2e/test_external_state.py` — E2E tests (Claude API)
- `deploy/evalhub/tests/` — 6 evalhub test files

### Source
- `agent_eval/` — Core Python package (5,219 LOC)
- `skills/*/scripts/` — Skill implementation scripts (7,250 LOC)
- `deploy/evalhub/` — EvalHub provider adapter

### Configuration
- `pyproject.toml` — Project config, dependencies, pytest config
- `.skillsaw.yaml` — Skill quality linting rules
- `.claude-plugin/plugin.json` — Claude Code plugin metadata

### Container
- `deploy/evalhub/Containerfile` — UBI9-based container image
- `deploy/evalhub/smoke-test/` — Smoke test config (not automated)

### Agent Rules
- `CLAUDE.md` — Comprehensive architecture + usage documentation
- `AGENTS.md` — Identical to CLAUDE.md (multi-agent support)
- `.claude-plugin/` — Plugin metadata and hooks
