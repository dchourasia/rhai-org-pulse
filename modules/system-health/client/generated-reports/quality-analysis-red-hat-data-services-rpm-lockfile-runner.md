---
repository: "red-hat-data-services/rpm-lockfile-runner"
overall_score: 1.0
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No tests exist - zero test files in repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests of any kind"
  - dimension: "Build Integration"
    score: 2.0
    status: "Workflow runs script but no PR-time validation or build checks"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container files in repo, no image testing"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tools, frameworks, or tracking"
  - dimension: "CI/CD Automation"
    score: 3.0
    status: "Single workflow with auto-commit but no PR checks, caching, or concurrency"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "Zero test coverage across entire repository"
    impact: "Script failures and regressions are only discovered in production CI runs"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No PR-time validation or checks"
    impact: "Broken changes merge without any automated quality gates"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No linting or static analysis"
    impact: "Shell script bugs and Python errors go undetected until runtime"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "No security scanning"
    impact: "Vulnerabilities in dependencies or scripts are never detected"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add ShellCheck linting for runner.sh"
    effort: "1 hour"
    impact: "Catch common bash pitfalls (unquoted variables, missing error handling)"
  - title: "Add Python linting with ruff for sanitize-ubi-repo.py"
    effort: "1 hour"
    impact: "Catch Python errors before runtime"
  - title: "Add unit tests for sanitize-ubi-repo.py"
    effort: "2-3 hours"
    impact: "Validate repo file sanitization logic with known inputs/outputs"
  - title: "Add PR workflow with dry-run validation"
    effort: "2-3 hours"
    impact: "Catch config.yaml errors before merge"
recommendations:
  priority_0:
    - "Add unit tests for sanitize-ubi-repo.py with pytest (test section dedup, suffix addition, edge cases)"
    - "Add ShellCheck and a linting CI step for runner.sh"
    - "Create a PR-triggered workflow that validates config.yaml syntax and runs a dry-run"
  priority_1:
    - "Add integration tests that verify lockfile generation with sample configs"
    - "Add Python type hints and mypy checking to sanitize-ubi-repo.py"
    - "Create agent rules (.claude/rules/) for test automation guidance"
  priority_2:
    - "Add SBOM generation for the lockfile output"
    - "Add caching for podman image pulls in CI"
    - "Add concurrency control to prevent parallel workflow runs on same branch"
---

# Quality Analysis: rpm-lockfile-runner

## Executive Summary

- **Overall Score: 1.0/10**
- **Repository Type**: Automation/CLI tool (Bash + Python)
- **Primary Languages**: Bash, Python
- **Key Strengths**: Working CI workflow with multi-arch lockfile generation and repoid validation
- **Critical Gaps**: Zero test coverage, no PR checks, no linting, no security scanning
- **Agent Rules Status**: Missing - no CLAUDE.md, no .claude/ directory

This is a small utility repository (~170 lines of code across 2 source files) that automates RPM lockfile generation for Konflux/Hermeto builds. Despite its small size, it has **zero quality infrastructure** beyond a single CI workflow that auto-commits results. The complete absence of tests is especially concerning given that the tool manipulates security-critical package lockfiles.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No tests exist - zero test files in repository |
| Integration/E2E | 0/10 | No integration or E2E tests of any kind |
| **Build Integration** | **2/10** | **Workflow runs script but no PR-time validation** |
| Image Testing | 0/10 | No container files in repo, no image testing |
| Coverage Tracking | 0/10 | No coverage tools, frameworks, or tracking |
| CI/CD Automation | 3/10 | Single workflow with auto-commit, no PR checks |
| Agent Rules | 0/10 | No CLAUDE.md, no .claude/ directory |

## Critical Gaps

### 1. Zero Test Coverage
- **Impact**: Script failures and regressions are only discovered during live CI runs; broken lockfiles could propagate to downstream builds
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Details**: Neither `runner.sh` (126 lines) nor `sanitize-ubi-repo.py` (68 lines) has any associated tests. The Python script has testable pure functions (section deduplication, suffix addition) that could easily be unit-tested. The bash script has validation logic (repoid checking) that should be tested with known inputs.

### 2. No PR-Time Validation
- **Impact**: Broken `config.yaml` changes or script modifications merge without any quality gates
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The only workflow triggers on `push` (when `config.yaml` changes) and `workflow_dispatch`. There is no PR-triggered workflow to validate changes before merge. A developer could push a broken `config.yaml` and the workflow would fail silently after merge.

### 3. No Linting or Static Analysis
- **Impact**: Common bash pitfalls (unquoted variables, word splitting) and Python errors go undetected
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: No ShellCheck for `runner.sh`, no ruff/flake8/mypy for `sanitize-ubi-repo.py`, no pre-commit hooks. The bash script already has potential issues:
  - `podman run -it` on line 46 uses interactive TTY flag in CI
  - `trap "rm *.tmp" EXIT` may fail if no `.tmp` files exist
  - Several unquoted variables susceptible to word splitting

### 4. No Security Scanning
- **Impact**: Vulnerabilities in the tool's dependencies or output are never detected
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No Trivy, CodeQL, Gitleaks, or any other security scanning. This is a supply-chain-relevant tool (it generates package lockfiles), making security scanning especially important.

## Quick Wins

### 1. Add ShellCheck Linting (1 hour)
Immediately catches common bash issues in `runner.sh`.

```yaml
# Add to .github/workflows/lint.yml
name: Lint
on: [pull_request]
jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run ShellCheck
        uses: ludeeus/action-shellcheck@master
        with:
          scandir: './src'
```

### 2. Add Python Linting with Ruff (1 hour)
```yaml
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
```

### 3. Add Unit Tests for sanitize-ubi-repo.py (2-3 hours)
```python
# tests/test_sanitize.py
import pytest
from src.sanitize_ubi_repo import sanitize_file
import tempfile

def test_adds_rpms_suffix():
    content = "[ubi-8-baseos]\nenabled = 1\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.repo', delete=False) as f:
        f.write(content)
        f.flush()
        sanitize_file(f.name)
        with open(f.name) as result:
            assert '[ubi-8-baseos-rpms]' in result.read()

def test_skips_existing_rpms_suffix():
    content = "[ubi-8-baseos-rpms]\nenabled = 1\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.repo', delete=False) as f:
        f.write(content)
        f.flush()
        sanitize_file(f.name)
        with open(f.name) as result:
            assert result.read().count('[ubi-8-baseos-rpms]') == 1

def test_removes_duplicates():
    content = "[ubi-8-baseos]\nenabled = 1\n[ubi-8-baseos]\nenabled = 1\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.repo', delete=False) as f:
        f.write(content)
        f.flush()
        sanitize_file(f.name)
        with open(f.name) as result:
            assert result.read().count('[ubi-8-baseos-rpms]') == 1
```

### 4. Add PR Dry-Run Workflow (2-3 hours)
```yaml
name: Validate Config
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate config.yaml syntax
        run: |
          sudo snap install yq --channel=v4/stable
          yq e '.' config.yaml > /dev/null
          # Verify required fields
          yq e '.arches | length > 0' config.yaml
          yq e '.stages | length > 0' config.yaml
```

## Detailed Findings

### CI/CD Pipeline

**Workflow**: `.github/workflows/rpm-lockfile-runner.yml`

| Aspect | Status | Notes |
|--------|--------|-------|
| Triggers | Push (config.yaml changes) + manual | No PR trigger |
| Concurrency | None | Parallel runs on same branch possible |
| Caching | None | Podman images pulled fresh every run |
| Dependency pinning | Partial | `actions/checkout@v4` pinned, but `yq` from snap unpinned |
| Auto-commit | Yes | Uses `actions-js/push@master` (unpinned action) |
| Matrix builds | None | Single runner only |

**Issues Found**:
1. `actions-js/push@master` is not version-pinned, creating supply chain risk
2. No concurrency control - parallel runs on same branch could create race conditions
3. Python version pinned to `3.10.13` with `actions/setup-python@v4` (should be v5)
4. `podman run -it` flag on line 46 of `runner.sh` may cause issues in non-TTY CI environments

### Test Coverage

| Category | Files | Coverage |
|----------|-------|----------|
| Unit Tests | 0 | 0% |
| Integration Tests | 0 | 0% |
| E2E Tests | 0 | 0% |
| Test Framework | None | N/A |

**Source Files Without Tests**:
- `src/runner.sh` (126 lines) - Main lockfile generation script
- `src/sanitize-ubi-repo.py` (68 lines) - Repo file sanitization

### Code Quality

| Tool | Status |
|------|--------|
| ShellCheck | Not configured |
| Ruff/Flake8 | Not configured |
| Mypy | Not configured |
| Pre-commit hooks | Not configured |
| EditorConfig | Not configured |
| .gitignore | Not present |

**Positive**: `runner.sh` uses `set -euo pipefail` for bash strict mode.

**Issues in runner.sh**:
- Line 46: `podman run -it` uses interactive TTY flag in CI (should be just `-i` or no flag)
- Line 13: `trap "rm *.tmp" EXIT` - glob may fail if no tmp files exist
- Line 112: `if [ -z $match ]` - unquoted variable, should be `"$match"`
- Inconsistent quoting throughout

**Issues in sanitize-ubi-repo.py**:
- Excessive `print()` statements used as logging (should use `logging` module)
- No type hints
- No docstrings
- No input validation for malformed repo files

### Container Images

- No Dockerfile or Containerfile in the repository
- The workflow builds `localhost/rpm-lockfile-prototype` from upstream Containerfile
- No image scanning of the built container
- No SBOM generation for lockfile output

### Security

| Practice | Status |
|----------|--------|
| SAST/CodeQL | Not configured |
| Dependency scanning | Not configured |
| Secret detection | Not configured |
| Container scanning | Not configured |
| Action pinning | Partial (v4 tags, not SHA) |
| Token permissions | Default (should be restricted) |

**Supply Chain Concerns**: This tool generates RPM lockfiles that pin package versions for Konflux builds. A compromised or buggy lockfile could introduce vulnerable packages into production images. The lack of any validation or scanning is a significant risk.

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no agent rules exist
- **Quality**: N/A
- **Gaps**: No CLAUDE.md, no AGENTS.md, no `.claude/` directory, no test automation guidance
- **Recommendation**: Generate rules with `/test-rules-generator` to provide unit test patterns for both Python and Bash

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests for `sanitize-ubi-repo.py`** - The Python script has pure functions that are easily testable. Use pytest with sample repo files as fixtures. Test section deduplication, `-rpms` suffix addition, and edge cases (empty files, malformed sections).

2. **Add ShellCheck linting for `runner.sh`** - Will immediately flag several real bugs (unquoted variables, TTY flag in CI). Add as a PR-triggered workflow step.

3. **Create a PR-triggered validation workflow** - Validate `config.yaml` syntax, check required fields exist, and optionally do a dry-run of the lockfile generation.

4. **Pin GitHub Actions to SHA digests** - `actions-js/push@master` is especially concerning as it auto-commits to the repository. Pin all actions to specific SHA commits.

### Priority 1 (High Value)

5. **Add integration tests with sample configs** - Create a test config with known packages and verify the generated lockfile matches expected structure and content.

6. **Add Python type hints and mypy** - Small effort for `sanitize-ubi-repo.py` (68 lines) with significant quality improvement.

7. **Create agent rules** (`.claude/rules/`) - Provide AI assistants with guidance on testing patterns for this repo's Bash+Python codebase.

8. **Add `.gitignore`** - Prevent accidental commits of `.tmp` files or other artifacts.

### Priority 2 (Nice-to-Have)

9. **Add caching for podman image pulls** - The `rpm-lockfile-prototype` image is rebuilt from scratch on every run.

10. **Add concurrency control** - Prevent parallel workflow runs on the same branch that could create race conditions with auto-commits.

11. **Restrict workflow token permissions** - Add explicit `permissions:` block to limit `GITHUB_TOKEN` scope.

12. **Add SBOM generation** - Generate an SBOM for the lockfile output to improve supply chain transparency.

## Comparison to Gold Standards

| Practice | rpm-lockfile-runner | odh-dashboard | notebooks | kserve |
|----------|-------------------|---------------|-----------|--------|
| Unit Tests | None | Comprehensive Jest | Python unittest | Go testing + coverage |
| Integration Tests | None | Cypress E2E | Image validation | envtest + Kind |
| Coverage Tracking | None | Codecov | N/A | Codecov w/ thresholds |
| CI/CD Workflows | 1 basic | 15+ workflows | 10+ workflows | 20+ workflows |
| Linting | None | ESLint + Prettier | Ruff | golangci-lint (30+ linters) |
| Security Scanning | None | Snyk + CodeQL | Trivy | Trivy + CodeQL |
| Pre-commit Hooks | None | Husky | Pre-commit | Pre-commit |
| Agent Rules | None | Comprehensive | Basic | None |
| PR Validation | None | Multi-layer | Image builds | Full test suite |

## File Paths Reference

| File | Purpose | Lines |
|------|---------|-------|
| `src/runner.sh` | Main lockfile generation script | 126 |
| `src/sanitize-ubi-repo.py` | UBI repo file sanitizer | 68 |
| `config.yaml` | Tool configuration (arches, stages, packages) | 13 |
| `rpms.lock.yaml` | Generated lockfile output | 721 |
| `ubi.repo` | Generated UBI repository file | 141 |
| `.github/workflows/rpm-lockfile-runner.yml` | CI workflow | 57 |
| `readme.md` | Usage documentation | 38 |
