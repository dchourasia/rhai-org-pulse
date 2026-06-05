---
repository: "red-hat-data-services/misc_tools"
overall_score: 1.2
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist anywhere in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or end-to-end tests of any kind"
  - dimension: "Build Integration"
    score: 0.0
    status: "No CI/CD pipelines, no build validation, no PR checks"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images, no Dockerfiles, no image testing"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tracking, no codecov, no thresholds"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "No workflows at all — no .github/workflows, no Makefile, no CI config"
  - dimension: "Code Quality"
    score: 1.5
    status: "No linting, no pre-commit hooks, no static analysis. Has LICENSE file."
  - dimension: "Security"
    score: 0.5
    status: "No security scanning, no dependency management, hardcoded fake secret in YAML"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "Complete absence of CI/CD pipeline"
    impact: "No automated checks on PRs — bugs, regressions, and security issues can merge unchecked"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Zero test coverage"
    impact: "No tests for either Python script — any change risks silent breakage"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No dependency management"
    impact: "Python scripts import koji and requests with no requirements.txt or pyproject.toml — users cannot install dependencies reliably"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No linting or code quality tools"
    impact: "Code style inconsistencies, bare except clauses, and potential bugs go undetected"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "No security scanning"
    impact: "Vulnerable dependencies and hardcoded secrets not detected"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Stale/unmaintained code"
    impact: "Last commit was for operator version 1.0.13 — catalog source still references quay.io/modh/modh:v1013 with no recent activity"
    severity: "MEDIUM"
    effort: "N/A"
quick_wins:
  - title: "Add requirements.txt for Python dependencies"
    effort: "30 minutes"
    impact: "Users can actually install and run the koji tools without guessing dependencies"
  - title: "Add a basic GitHub Actions linting workflow"
    effort: "1-2 hours"
    impact: "Catch syntax errors and style issues on every PR with ruff/flake8"
  - title: "Fix bare except clause in copy_image_build.py"
    effort: "15 minutes"
    impact: "Prevents swallowing unexpected exceptions silently"
  - title: "Add basic unit tests for pure functions"
    effort: "2-3 hours"
    impact: "Validates URL construction, NVR parsing, tag list extraction"
recommendations:
  priority_0:
    - "Create requirements.txt or pyproject.toml listing koji, requests, and argparse dependencies"
    - "Add a minimal GitHub Actions CI workflow with Python linting (ruff) and syntax checks"
    - "Add basic unit tests for find_commit.py and copy_image_build.py utility functions"
  priority_1:
    - "Add pre-commit hooks for Python linting and YAML validation"
    - "Implement secret scanning (gitleaks) to prevent real credentials from entering the repo"
    - "Add shellcheck linting for the bash scripts in quick-install/"
  priority_2:
    - "Create CLAUDE.md or AGENTS.md with contribution guidelines"
    - "Consider whether this repo is still actively used — last substantive change was a version bump"
    - "Add integration tests that validate koji API interactions with mocked responses"
---

# Quality Analysis: misc_tools

## Executive Summary

- **Overall Score: 1.2/10**
- **Repository Type**: Collection of utility scripts (Python CLI tools + Bash install scripts)
- **Primary Language**: Python (2 scripts, 186 LOC) + Bash (2 scripts, 56 LOC)
- **Total Code**: 242 lines across 4 files
- **Contributors**: 4
- **Total Commits**: 52
- **Key Strengths**: Has an Apache 2.0 license; scripts have decent inline documentation and argparse usage
- **Critical Gaps**: No CI/CD, no tests, no linting, no dependency management, no security scanning — essentially zero quality infrastructure
- **Agent Rules Status**: Missing

This is a very small, low-activity utility repository with two Python CLI tools for Koji build system interactions and a set of Bash scripts for quick-installing RHODS (Red Hat OpenShift Data Science). The repository has **no quality infrastructure whatsoever** — no CI/CD pipeline, no tests, no linting, no dependency management, and no security scanning. Given the repo's small size and apparent low activity (last commit was a version bump), the cost of adding full quality infrastructure may not be justified unless the tools are still actively used.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist anywhere |
| Integration/E2E | 0/10 | No integration or E2E tests |
| Build Integration | 0/10 | No CI/CD, no build validation |
| Image Testing | 0/10 | N/A — no container images built |
| Coverage Tracking | 0/10 | No coverage tools configured |
| CI/CD Automation | 1/10 | No workflows, no Makefile, no CI config |
| Code Quality | 1.5/10 | No linting; has LICENSE; some docstrings |
| Security | 0.5/10 | No scanning; hardcoded fake secret in YAML |
| Agent Rules | 0/10 | No CLAUDE.md, no .claude/ directory |

## Critical Gaps

### 1. Complete Absence of CI/CD Pipeline
- **Impact**: No automated checks on PRs — bugs, regressions, and security issues can merge unchecked
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No `.github/workflows/` directory, no Makefile, no `.gitlab-ci.yml`, no Jenkinsfile. PRs are merged with zero automated validation.

### 2. Zero Test Coverage
- **Impact**: No tests for either Python script — any change risks silent breakage
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: Neither `find_commit.py` nor `copy_image_build.py` has any associated test files. Functions like `get_resources_url()`, `get_tag_list()`, `check_build()` are testable with mocked Koji responses.

### 3. No Dependency Management
- **Impact**: Users cannot install dependencies reliably — must guess that `koji` and `requests` are needed
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Details**: Python scripts import `koji`, `requests`, `json`, `argparse`, `subprocess` but there is no `requirements.txt`, `setup.py`, `pyproject.toml`, or any dependency specification.

### 4. No Linting or Code Quality Tools
- **Impact**: Code quality issues go undetected
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No ruff, flake8, mypy, pylint, or any linter configured. The code has issues like a bare `except:` clause in `copy_image_build.py:11` which catches all exceptions silently.

### 5. No Security Scanning
- **Impact**: Vulnerable dependencies not detected; fake but misleading secret in repo
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No Trivy, Snyk, CodeQL, gitleaks, or any security tool. `fakesecret.yaml` contains a hardcoded PagerDuty key value (`foo-bar`), which while fake, sets a bad pattern.

### 6. Stale/Unmaintained Repository
- **Impact**: Tools may reference outdated APIs or versions
- **Severity**: MEDIUM
- **Effort**: N/A
- **Details**: The most recent commits are all version bumps to operator versions (v1.0.8 through v1.0.13). The catalog source references `quay.io/modh/modh:v1013`. No recent feature development or maintenance activity.

## Quick Wins

### 1. Add requirements.txt (30 minutes)
Create a `requirements.txt` or `pyproject.toml` for the koji tools:
```
koji
requests
```

### 2. Fix bare except clause (15 minutes)
In `koji_tools/copy_image_build/copy_image_build.py:11`:
```python
# Current (bad):
except:
    return False

# Fixed:
except (KeyError, TypeError):
    return False
```

### 3. Add basic GitHub Actions linting (1-2 hours)
```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check .
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: shellcheck quick-install/*.sh
```

### 4. Add basic unit tests (2-3 hours)
```python
# koji_tools/find_commit/test_find_commit.py
import pytest
from unittest.mock import patch, MagicMock
from find_commit import get_resources_url, display_title

def test_display_title(capsys):
    nvr = {'name': 'foo', 'version': '1.0', 'release': '1.el8'}
    display_title(nvr)
    captured = capsys.readouterr()
    assert 'foo-1.0-1.el8' in captured.out
```

## Detailed Findings

### CI/CD Pipeline
**Score: 1/10**

There is no CI/CD pipeline of any kind:
- No `.github/workflows/` directory
- No `Makefile`
- No `.gitlab-ci.yml`
- No `Jenkinsfile`
- No pre-commit hooks

The only "automation" is the manual bash scripts in `quick-install/` which are run by humans.

### Test Coverage
**Score: 0/10**

- **Unit Tests**: None. Zero test files in the entire repository.
- **Integration Tests**: None.
- **E2E Tests**: None.
- **Test-to-Code Ratio**: 0:242 (0%)
- **Coverage Tracking**: None — no codecov, coveralls, or any coverage tool.

Testable functions that should have tests:
- `find_commit.py`: `get_koji_pathinfo()`, `get_resources_url()`, `display_title()`, `parse_args()`
- `copy_image_build.py`: `check_build()`, `get_source_image()`, `get_tag_list()`, `get_latest_build()`

### Code Quality
**Score: 1.5/10**

**Positives:**
- Apache 2.0 LICENSE file present
- Python scripts use argparse with help text
- Functions have docstrings in `find_commit.py`
- READMEs exist for each tool

**Negatives:**
- Bare `except:` clause in `copy_image_build.py:11` — catches SystemExit, KeyboardInterrupt, etc.
- Unused import: `rsession = Session()` in `find_commit.py:64` is created but never used
- Global `args` variable leak: `copy_image_build.py:83` references global `args` inside `main()` function
- No type hints anywhere
- No linting configuration
- No pre-commit hooks
- Inconsistent code style (mixed quote styles, inconsistent spacing)

### Container Images
**Score: 0/10 (N/A)**

This repository does not build container images. It contains tools that *interact* with container builds in Koji but does not produce images itself. No Dockerfile or Containerfile exists.

### Security
**Score: 0.5/10**

- No security scanning tools (Trivy, Snyk, CodeQL, gitleaks)
- No dependency scanning
- `fakesecret.yaml` contains a hardcoded PagerDuty key (`foo-bar`) — while clearly fake, this pattern is concerning
- Python scripts make HTTP requests to Koji build systems without SSL verification concerns documented
- No `.gitignore` — risk of accidental credential commits

### Agent Rules (Agentic Flow Quality)
**Score: 0/10**

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Not present
- **Coverage**: No test type rules
- **Quality**: N/A
- **Gaps**: Everything — no agent guidance of any kind
- **Recommendation**: Given repo size, a minimal CLAUDE.md documenting project purpose and contribution guidelines would suffice

## Recommendations

### Priority 0 (Critical)
1. **Create `requirements.txt`** listing `koji` and `requests` — without this, the tools are not reliably installable
2. **Add minimal CI workflow** with Python linting (ruff) and shellcheck for bash scripts
3. **Fix the bare `except:` clause** in `copy_image_build.py` — this silently swallows all exceptions including `KeyboardInterrupt`

### Priority 1 (High Value)
1. **Add basic unit tests** for the pure utility functions (URL construction, tag list parsing, build validation)
2. **Add pre-commit hooks** for Python formatting and YAML validation
3. **Add `.gitignore`** to prevent accidental commits of sensitive files
4. **Add secret scanning** (gitleaks) to PR workflow

### Priority 2 (Nice-to-Have)
1. **Evaluate repository activity** — determine if these tools are still actively used and maintained
2. **Add type hints** to Python functions for better IDE support and static analysis
3. **Create CLAUDE.md** with project purpose and contribution guidelines
4. **Add integration tests** with mocked Koji API responses
5. **Consider consolidating** into a Python package with proper `pyproject.toml`

## Comparison to Gold Standards

| Practice | misc_tools | odh-dashboard | notebooks | kserve |
|----------|-----------|---------------|-----------|--------|
| CI/CD Pipeline | None | Comprehensive | Multi-workflow | Extensive |
| Unit Tests | None | Jest + >1000 tests | Python tests | Go tests + coverage |
| Integration Tests | None | Cypress E2E | Multi-layer | envtest |
| Coverage Tracking | None | Codecov enforced | Per-image | Codecov enforced |
| Linting | None | ESLint strict | Various | golangci-lint |
| Security Scanning | None | Trivy + CodeQL | Trivy | Trivy + Snyk |
| Pre-commit Hooks | None | Husky + lint-staged | Pre-commit | Pre-commit |
| Container Testing | N/A | Image validation | 5-layer testing | Runtime validation |
| Agent Rules | None | Comprehensive | Partial | None |
| Dependency Mgmt | None | package.json | requirements.txt | go.mod |

## File Paths Reference

| File | Purpose | Issues |
|------|---------|--------|
| `koji_tools/find_commit/find_commit.py` | Report upstream commit for container build by NVR | Unused `rsession` variable; no tests |
| `koji_tools/copy_image_build/copy_image_build.py` | Copy images from Koji build to registry | Bare `except:`; global `args` leak; no tests |
| `quick-install/setup.sh` | Install RHODS operator on OpenShift | No error handling beyond wait loop |
| `quick-install/cleanup.sh` | Remove RHODS installation | Hardcoded resource names; no confirmation prompt |
| `quick-install/catalogsource.yaml` | OLM CatalogSource for RHODS | Hardcoded version `v1013` |
| `quick-install/fakesecret.yaml` | Fake PagerDuty secret for testing | Hardcoded secret pattern |
| `LICENSE` | Apache 2.0 | OK |

## Summary

`misc_tools` is a small, low-activity utility repository that serves as a collection of helper scripts for Red Hat OpenShift Data Science operations. With only 242 lines of code across 4 source files, it has **virtually no quality infrastructure**. The repository scores **1.2/10** overall, reflecting the complete absence of CI/CD, testing, linting, dependency management, and security scanning.

Given the repository's small size and apparently low maintenance activity, the most impactful improvements would be:
1. Adding a `requirements.txt` (30 minutes, unblocks reliable installation)
2. Fixing the bare `except:` clause (15 minutes, prevents silent failures)
3. Adding a basic linting CI workflow (1-2 hours, catches future issues)

Before investing significant effort, it's worth evaluating whether this repository is still actively used and maintained, or if its functionality has been superseded by other tools.
