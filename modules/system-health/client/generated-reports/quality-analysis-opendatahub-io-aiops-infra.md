---
repository: "opendatahub-io/aiops-infra"
overall_score: 2.7
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No unit tests exist — zero test files across 54 scripts (7,654 LOC)"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests — all scripts are untested"
  - dimension: "Build Integration"
    score: 1.0
    status: "No container builds, no PR-time validation beyond skillsaw lint"
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfiles, no container images built or tested"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tool configured — no codecov, coveralls, or coverage reports"
  - dimension: "CI/CD Automation"
    score: 3.0
    status: "Only skillsaw lint on PRs — no test jobs, no security scanning, no dependency checks"
  - dimension: "Agent Rules"
    score: 6.0
    status: "17 Claude Code skills with SKILL.md files, but no test rules, CLAUDE.md, or .claude/rules/"
critical_gaps:
  - title: "Zero test coverage across entire codebase"
    impact: "54 scripts (33 shell, 21 Python) with 7,654 LOC have no tests — regressions are undetectable"
    severity: "HIGH"
    effort: "40-60 hours"
  - title: "No Python linting or static analysis"
    impact: "21 Python scripts have no ruff, flake8, mypy, or pylint configured — type errors and style issues go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No ShellCheck linting for 33 shell scripts"
    impact: "Shell scripting bugs (quoting, word splitting, undefined vars) are not caught in CI"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No security scanning (SAST, dependency, secret detection)"
    impact: "Scripts handle GITHUB_TOKEN, GITLAB_TOKEN, JIRA_API_TOKEN — no automated secret leak detection"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No CLAUDE.md or agent testing rules"
    impact: "17 skills exist but no test automation guidance — AI agents cannot write or verify tests"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add ShellCheck to CI workflow"
    effort: "1-2 hours"
    impact: "Catch shell scripting bugs across all 33 scripts with zero false-positive cost"
  - title: "Add ruff linting for Python scripts"
    effort: "1-2 hours"
    impact: "Immediate detection of Python bugs, unused imports, and style issues across 21 scripts"
  - title: "Add pytest skeleton with tests for validate_yaml_schema.py"
    effort: "2-3 hours"
    impact: "Establish testing pattern for the most critical script — schema validation is the pipeline entry point"
  - title: "Add gitleaks secret scanning to CI"
    effort: "1-2 hours"
    impact: "Prevent accidental credential leaks in a repo that handles multiple API tokens"
recommendations:
  priority_0:
    - "Add unit tests for all Python scripts — start with validate_yaml_schema.py, parse scripts, and Jira/GitHub API wrappers"
    - "Add ShellCheck and ruff linting to CI — immediate low-effort quality improvement"
    - "Add secret detection scanning (gitleaks) — this repo handles GITHUB_TOKEN, GITLAB_TOKEN, JIRA_API_TOKEN"
  priority_1:
    - "Add integration tests for the pipeline orchestration flow (mock API responses, verify state machine transitions)"
    - "Create CLAUDE.md with project conventions and testing requirements"
    - "Add .claude/rules/ with test creation guidelines for Python and shell scripts"
    - "Add mypy type checking for Python scripts (most already have type hints in docstrings)"
  priority_2:
    - "Add pre-commit hooks (.pre-commit-config.yaml) for shellcheck, ruff, gitleaks"
    - "Add CodeQL or Semgrep SAST scanning"
    - "Add BATS testing framework for shell script unit tests"
    - "Add dependency scanning for Python inline dependencies (uv audit)"
---

# Quality Analysis: aiops-infra

## Executive Summary

- **Overall Score: 2.7/10**
- **Repository Type**: Infrastructure automation toolkit (Python + Shell scripts)
- **Primary Languages**: Bash (33 scripts), Python (21 scripts) — 7,654 LOC total
- **Purpose**: Automates ODH/RHOAI component onboarding onto the Konflux CI/CD platform via Claude Code skills

### Key Strengths
- **Excellent skill architecture**: 17 well-documented Claude Code skills with a sophisticated master orchestrator
- **Strong shell scripting discipline**: All 33 shell scripts use `set -euo pipefail` (100% strict mode)
- **Modern Python practices**: 16 of 21 Python scripts use `uv run --script` with inline dependency declarations
- **Schema validation**: JSON Schema (Draft 2020-12) for input validation with comprehensive conditional logic
- **Idempotent design**: Pipeline orchestrator is fully idempotent with state tracking via JSON and Jira labels

### Critical Gaps
- **Zero test coverage**: Not a single test file exists in the entire repository
- **No Python or shell linting**: No ruff, mypy, shellcheck, or any static analysis in CI
- **No security scanning**: Scripts handle sensitive tokens with no secret detection or SAST
- **CI is lint-only**: Only skillsaw (skill metadata lint) runs on PRs — no code quality checks

### Agent Rules Status: **Partial**
- 17 Claude Code skills present with SKILL.md files
- No CLAUDE.md, AGENTS.md, or `.claude/rules/` directory
- No test automation guidance for AI agents

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist anywhere in the repository |
| Integration/E2E | 0/10 | No integration or end-to-end test infrastructure |
| **Build Integration** | **1/10** | **Only skillsaw metadata lint on PRs — no code validation** |
| Image Testing | 0/10 | No container images are built (pure script repo) |
| Coverage Tracking | 0/10 | No coverage tools configured |
| CI/CD Automation | 3/10 | Minimal — skillsaw lint only, no test/security/quality jobs |
| Agent Rules | 6/10 | Rich skill library but no test rules or project-level agent config |

## Critical Gaps

### 1. Zero Test Coverage
- **Impact**: 54 scripts totaling 7,654 lines of code have no automated tests. Regressions in pipeline orchestration, Jira API interactions, GitHub/GitLab PR creation, YAML schema validation, and state machine transitions are completely undetectable.
- **Severity**: HIGH
- **Effort**: 40-60 hours (incremental)
- **Why it matters**: This repo automates production onboarding workflows that touch Jira, GitHub, GitLab, Quay, and OpenShift. A bug in any script could silently break the component onboarding pipeline for ODH/RHOAI.

### 2. No Python Linting or Static Analysis
- **Impact**: 21 Python scripts with no ruff, flake8, mypy, or pylint. Type errors, unused imports, undefined variables, and style inconsistencies go undetected.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Files affected**: All `scripts/*.py`

### 3. No Shell Linting
- **Impact**: 33 shell scripts with no ShellCheck integration. While all scripts use `set -euo pipefail` (a positive sign), common shell bugs like unquoted variables, word splitting, and POSIX compatibility issues are not caught.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Files affected**: All `scripts/*.sh`

### 4. No Security Scanning
- **Impact**: Scripts directly reference and use `GITHUB_TOKEN`, `GITLAB_TOKEN`, `JIRA_API_TOKEN`, and `EXT_OC_TOKEN`/`INT_OC_TOKEN`. No gitleaks, trufflehog, CodeQL, or Semgrep scanning exists.
- **Severity**: HIGH
- **Effort**: 4-6 hours

### 5. No CLAUDE.md or Test Automation Rules
- **Impact**: The repo has 17 Claude Code skills but no project-level `CLAUDE.md` or `.claude/rules/` directory. AI agents using this repo have no guidance on testing conventions, coding standards, or quality requirements.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours

## Quick Wins

### 1. Add ShellCheck to CI (1-2 hours)
```yaml
# .github/workflows/lint.yml — add step:
- name: ShellCheck
  uses: ludeeus/action-shellcheck@2.0.0
  with:
    scandir: './scripts'
    severity: warning
```

### 2. Add ruff Linting for Python (1-2 hours)
```yaml
# .github/workflows/lint.yml — add step:
- name: Ruff lint
  uses: astral-sh/ruff-action@v3
  with:
    src: './scripts'
```

### 3. Add gitleaks Secret Scanning (1-2 hours)
```yaml
# .github/workflows/lint.yml — add step:
- name: Gitleaks
  uses: gitleaks/gitleaks-action@v2
  env:
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

### 4. Add pytest for validate_yaml_schema.py (2-3 hours)
Create `tests/test_validate_yaml_schema.py` with:
- Valid YAML passes validation
- Missing required fields fail with clear errors
- Invalid field values (bad patterns, wrong types) caught
- Conditional validation (ODH vs RHOAI) works correctly

## Detailed Findings

### CI/CD Pipeline

**Workflows found**: 2 (minimal)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `lint.yml` | push/PR to main | Runs skillsaw lint (skill metadata validation) |
| `lint-review.yml` | workflow_run on lint | Posts skillsaw review comments on PRs |

**What's missing**:
- No test execution jobs
- No Python linting (ruff, mypy)
- No shell linting (ShellCheck)
- No security scanning
- No dependency auditing
- No caching strategy needed (no builds)
- No concurrency control configured

**Makefile targets**: `skillsaw`, `skillsaw-fix`, `lint` — all point to skillsaw only.

### Test Coverage

**Status**: No tests exist.

- `*_test.py`: 0 files
- `*_test.sh`: 0 files
- `test_*.py`: 0 files
- `tests/` directory: does not exist
- `pytest.ini`, `setup.cfg [tool:pytest]`, `pyproject.toml [tool.pytest]`: none
- No testing framework referenced anywhere

**Test-to-code ratio**: 0:7654 (0%)

### Code Quality

**Positive findings**:
- All 33 shell scripts use `set -euo pipefail` (100% strict mode adoption)
- 16 of 21 Python scripts use `uv run --script` with PEP 723 inline metadata
- JSON Schema validation with Draft 2020-12 for input data
- Well-structured argument parsing in both Python and shell scripts
- Consistent error handling patterns (stderr messages, meaningful exit codes)

**Missing tools**:
- No `.pre-commit-config.yaml`
- No `ruff.toml`, `.flake8`, `mypy.ini`, or `pyproject.toml`
- No `.golangci.yaml` (not applicable — no Go code)
- No `.eslintrc` (not applicable — no JS/TS code)
- No ShellCheck configuration

**Linting in CI**: Only `skillsaw` — validates skill metadata structure (SKILL.md format, context budgets, content positions). Does not lint code.

### Container Images

**N/A** — This repository does not build container images. It is a pure script/skill collection. The `check_dockerfile_digests.py` script validates Dockerfiles in *other* repositories but does not build anything locally.

### Security

**Current state**: No security tooling.

- No gitleaks/trufflehog for secret detection
- No CodeQL/Semgrep SAST analysis
- No dependency scanning (Python deps are inline, but no audit)
- No `.trivyignore` or Trivy configuration

**Risk**: Scripts handle sensitive credentials:
- `GITHUB_TOKEN`, `GITHUB_USER`
- `GITLAB_TOKEN`, `GITLAB_USER`
- `JIRA_API_TOKEN`, `JIRA_USER_EMAIL`
- `EXT_OC_TOKEN`, `INT_OC_TOKEN` (OpenShift tokens)

Scripts read these from environment variables (good practice), but no automated scanning prevents accidental hardcoding or leakage.

### Agent Rules (Agentic Flow Quality)

**Status**: Partial — Rich skills, no test rules

**What exists**:
- `.claude/skills/` directory with 17 skills, each having a SKILL.md
- `.skillsaw.yaml` configuring skill metadata validation
- `docs/skills/index.md` with comprehensive pipeline documentation
- `ADLC/` directory with Agentic SDLC documentation (3 versions)
- `.claude/skills/install.sh` for skill distribution

**What's missing**:
- No `CLAUDE.md` in repo root (project-level agent instructions)
- No `AGENTS.md` or `GEMINI.md`
- No `.claude/rules/` directory
- No test automation guidance for agents
- No coding standards documentation for agents

**Skill quality**: The 17 skills are well-documented with:
- Clear prerequisites and error tables
- Idempotent execution patterns
- State machine tracking via pipeline_state.json
- Bash code blocks with step-by-step instructions

**Gap**: Skills define *what to do* but not *how to test*. An agent contributing to this repo has no guidance on writing tests for new scripts or validating changes.

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests for Python scripts** — Start with:
   - `validate_yaml_schema.py` (critical entry point for all onboarding)
   - `build_progress_summary.py` (renders Jira comments)
   - `sync_state_from_jira.py` (state reconstruction logic)
   - `check_pr_mr_status.sh` via BATS (pipeline state machine)

2. **Add ShellCheck + ruff to CI** — Immediate, zero-effort quality gate:
   ```yaml
   jobs:
     lint:
       steps:
         - uses: actions/checkout@v4
         - uses: ludeeus/action-shellcheck@2.0.0
           with: { scandir: './scripts', severity: warning }
         - uses: astral-sh/ruff-action@v3
           with: { src: './scripts' }
         - uses: stbenjam/skillsaw@v0
           with: { strict: 'true' }
   ```

3. **Add secret detection** — gitleaks action to prevent credential leaks.

### Priority 1 (High Value)

4. **Add integration tests for orchestrator flow** — Mock API responses for GitHub, GitLab, Jira, and OpenShift; verify that `pipeline_state.json` transitions correctly through the full step graph.

5. **Create CLAUDE.md** — Include:
   - Project overview and architecture
   - Testing requirements for new scripts
   - Shell scripting conventions (strict mode, argument parsing pattern)
   - Python scripting conventions (uv inline deps, docstring format)
   - PR/commit message conventions

6. **Add `.claude/rules/` with test rules** — Create rules for:
   - `unit-tests.md` — pytest for Python, BATS for shell
   - `integration-tests.md` — API mocking patterns
   - `script-conventions.md` — set -euo pipefail, uv run --script

7. **Add mypy type checking** — Most Python scripts are well-documented; adding type annotations and mypy would catch type errors.

### Priority 2 (Nice-to-Have)

8. **Add pre-commit hooks** — `.pre-commit-config.yaml` with shellcheck, ruff, gitleaks, trailing-whitespace.

9. **Add CodeQL or Semgrep** — SAST scanning for Python and shell code.

10. **Add BATS framework** — [Bash Automated Testing System](https://github.com/bats-core/bats-core) for shell script unit testing.

11. **Add `uv audit`** — Check inline Python dependencies for known vulnerabilities.

## Comparison to Gold Standards

| Dimension | aiops-infra | odh-dashboard | notebooks | kserve |
|-----------|:-----------:|:-------------:|:---------:|:------:|
| Unit Tests | 0/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 0/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 1/10 | 8/10 | 7/10 | 8/10 |
| Image Testing | N/A | 7/10 | 10/10 | 7/10 |
| Coverage Tracking | 0/10 | 8/10 | 5/10 | 9/10 |
| CI/CD Automation | 3/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 6/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **2.7** | **8.5** | **7.5** | **8.0** |

**Note**: Image Testing is scored N/A for aiops-infra (no images built) and excluded from the weighted average.

## File Paths Reference

### CI/CD
- `.github/workflows/lint.yml` — Skillsaw lint on PR/push
- `.github/workflows/lint-review.yml` — Skillsaw review comments
- `Makefile` — `skillsaw`, `skillsaw-fix`, `lint` targets
- `.skillsaw.yaml` — Skillsaw configuration

### Scripts (Source Code)
- `scripts/*.sh` — 33 shell scripts (pipeline automation)
- `scripts/*.py` — 21 Python scripts (API interactions, YAML processing)

### Schemas
- `schemas/component_onboarding_details.schema.json` — JSON Schema for onboarding input

### Agent Skills
- `.claude/skills/*/SKILL.md` — 17 Claude Code skill definitions
- `.claude/skills/install.sh` — Skill installation script
- `.claude/skills/install-dependencies.sh` — Dependency installer
- `docs/skills/index.md` — Skill pipeline documentation

### Documentation
- `README.md` — Minimal (1 line)
- `ADLC/` — Agentic SDLC documentation (3 versions)
