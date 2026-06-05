---
repository: "red-hat-data-services/jupyterhub-singleuser-profiles"
overall_score: 0.6
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "Only 2 trivial UI snapshot tests using deprecated Enzyme; zero Python tests for 1,363-line core library"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests exist anywhere in the repository"
  - dimension: "Build Integration"
    score: 1.0
    status: "No PR-time build validation; only .aicoe-ci.yaml for PyPI release with empty check list"
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfile/Containerfile in repository; no image build or runtime validation"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "Jest config has --collectCoverage flag but no enforcement, no codecov, no thresholds"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "No GitHub Actions workflows, no Makefile, no CI pipeline; only AICoE CI for PyPI publish"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules or test automation guidance"
critical_gaps:
  - title: "No CI/CD pipeline — zero automated checks on PRs"
    impact: "Code merges without any automated validation; bugs, regressions, and security issues ship unchecked"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No Python unit tests for core library (1,363 LOC)"
    impact: "Core JupyterHub profile logic, OpenShift API interactions, and user management are entirely untested"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No integration or E2E tests"
    impact: "OpenShift deployment flow, API endpoints, and UI-to-backend integration are never validated"
    severity: "HIGH"
    effort: "24-40 hours"
  - title: "No security scanning of any kind"
    impact: "Dependency vulnerabilities (openshift, PyYAML, tornado, etc.) go undetected; no SAST, no secret detection"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Repository appears abandoned (last commit Aug 2022)"
    impact: "Dependencies are severely outdated; no active maintenance means known vulnerabilities remain unpatched"
    severity: "HIGH"
    effort: "Ongoing"
quick_wins:
  - title: "Add GitHub Actions CI workflow with linting"
    effort: "2-4 hours"
    impact: "Establish baseline automated checks on PRs (Python linting with ruff, TypeScript lint, type-check)"
  - title: "Add Dependabot or Renovate for dependency updates"
    effort: "1 hour"
    impact: "Surface outdated and vulnerable dependencies automatically"
  - title: "Add Trivy or Snyk dependency scanning"
    effort: "1-2 hours"
    impact: "Detect known CVEs in Python and Node.js dependencies"
  - title: "Migrate UI tests from deprecated Enzyme to React Testing Library"
    effort: "2-4 hours"
    impact: "Fix broken test infrastructure; Enzyme has been unmaintained since 2018 and doesn't support modern React"
recommendations:
  priority_0:
    - "Evaluate whether this repository should be archived — last commit was August 2022 and it has no active CI"
    - "If still active: add GitHub Actions CI with Python linting (ruff), TypeScript lint/type-check, and basic test execution"
    - "Add Python unit tests for core modules (profiles.py, openshift.py, images.py, user.py) — these contain critical JupyterHub extension logic"
  priority_1:
    - "Add integration tests for the Connexion-based REST API (api.py)"
    - "Add dependency vulnerability scanning (Trivy/Snyk) to catch CVEs in unmaintained dependencies"
    - "Replace deprecated Enzyme tests with React Testing Library and add meaningful UI component tests"
    - "Add pre-commit hooks for consistent code formatting and lint enforcement"
  priority_2:
    - "Add Dockerfile and container image build/test pipeline"
    - "Create agent rules (.claude/rules/) for test patterns specific to this codebase"
    - "Add OpenShift integration tests to validate deployment manifests"
    - "Add API contract tests for the connexion/swagger-based API"
---

# Quality Analysis: jupyterhub-singleuser-profiles

## Executive Summary

- **Overall Score: 0.6/10** — Critical quality deficits across every dimension
- **Repository Status: Likely Abandoned** — Last commit August 8, 2022 (nearly 4 years ago)
- **Key Strengths**: PR template with review checklist; UI has ESLint + Prettier + TypeScript type-checking configured
- **Critical Gaps**: No CI/CD pipeline, no Python tests, no integration/E2E tests, no security scanning, no coverage enforcement
- **Agent Rules Status**: Missing — No CLAUDE.md, no .claude/ directory

## Repository Overview

| Attribute | Value |
|-----------|-------|
| **Type** | Python library + React UI (JupyterHub extension) |
| **Purpose** | Customize JupyterHub workspace deployments on OpenShift |
| **Primary Languages** | Python (1,529 LOC), TypeScript/JavaScript (3,718 LOC) |
| **Source Files** | 13 Python, 37 TS/JS/TSX |
| **Last Commit** | August 8, 2022 |
| **Default Branch** | master |
| **Package** | PyPI (`jupyterhub-singleuser-profiles`) |

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1/10 | 2 trivial snapshot tests; zero Python tests |
| Integration/E2E | 0/10 | None exist |
| **Build Integration** | **1/10** | **No PR-time validation; empty AICoE CI checks** |
| Image Testing | 0/10 | No Dockerfile; no image pipeline |
| Coverage Tracking | 1/10 | Jest flag exists but unused/unenforced |
| CI/CD Automation | 1/10 | No workflows, no PR checks |
| Agent Rules | 0/10 | Nothing exists |

**Overall: 0.6/10** (weighted average of Unit Tests 20%, Integration/E2E 25%, Image Testing 20%, Coverage Tracking 15%, CI/CD 20%)

## Critical Gaps

### 1. No CI/CD Pipeline — Zero Automated Checks on PRs
- **Severity**: HIGH
- **Impact**: Code merges without any automated validation. No linting, no tests, no type-checking, no security scanning runs on pull requests.
- **Evidence**: No `.github/workflows/` directory. `.aicoe-ci.yaml` has `check: []` (empty list) — only PyPI release is automated.
- **Effort**: 4-8 hours to establish baseline

### 2. No Python Unit Tests for Core Library (1,363 LOC)
- **Severity**: HIGH
- **Impact**: The core library — `profiles.py` (374 LOC), `openshift.py` (278 LOC), `sizes.py` (86 LOC), `images.py` (156 LOC), `user.py` (115 LOC) — is entirely untested. This is the code that interacts with OpenShift APIs to configure JupyterHub workspaces.
- **Evidence**: `find . -name "test_*.py" -o -name "*_test.py"` returns zero results
- **Effort**: 16-24 hours

### 3. No Integration or E2E Tests
- **Severity**: HIGH
- **Impact**: The Connexion-based REST API (`api.py`), OpenShift deployment flow, and UI-to-backend integration are never validated.
- **Evidence**: No `test/`, `tests/`, `e2e/`, or `integration/` directories
- **Effort**: 24-40 hours

### 4. No Security Scanning
- **Severity**: HIGH
- **Impact**: Dependencies include `openshift`, `PyYAML`, `tornado`, `jinja2`, `connexion` — all with known CVE histories. No scanning means vulnerabilities ship silently.
- **Evidence**: No Trivy, Snyk, CodeQL, Gitleaks, or any security tooling configured
- **Effort**: 2-4 hours to add basic scanning

### 5. Repository Appears Abandoned
- **Severity**: HIGH
- **Impact**: No commits for ~4 years. Dependencies are severely outdated (Node.js 14 EOL, PatternFly v4, deprecated Enzyme). Active CVEs likely exist.
- **Evidence**: Last commit `2022-08-08`; no recent branches or tags

## Quick Wins

### 1. Add GitHub Actions CI Workflow (2-4 hours)
Establish baseline automated PR checks:

```yaml
name: CI
on: [pull_request]
jobs:
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install ruff
      - run: ruff check jupyterhub_singleuser_profiles/
  ui-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '18' }
      - run: cd jupyterhub_singleuser_profiles/ui && npm ci && npm run test:lint && npm run test:type-check
```

### 2. Add Dependabot (1 hour)
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: npm
    directory: /jupyterhub_singleuser_profiles/ui
    schedule: { interval: weekly }
```

### 3. Add Trivy Dependency Scanning (1-2 hours)
```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          severity: CRITICAL,HIGH
```

### 4. Migrate Tests from Enzyme to React Testing Library (2-4 hours)
Enzyme is unmaintained and incompatible with modern React. The 2 existing snapshot tests should be migrated to `@testing-library/react`.

## Detailed Findings

### CI/CD Pipeline

**Status: Virtually non-existent**

| File | Purpose | Findings |
|------|---------|----------|
| `.aicoe-ci.yaml` | AICoE CI config | `check: []` — no checks. Only `release: upload-pypi-sesheta` |
| `.thoth.yaml` | Thoth version management | Only version bumping by bot, no quality checks |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist | Manual checklist (squash, JIRA link, testing instructions) — no automated enforcement |

The repository relies entirely on manual review with zero automated validation. The PR template asks for testing instructions but there is no CI to run them.

### Test Coverage

**Python Tests: None (0/1,363 LOC)**

| Module | LOC | Test Coverage |
|--------|-----|---------------|
| `profiles.py` | 374 | None |
| `openshift.py` | 278 | None |
| `images.py` | 156 | None |
| `ui_config.py` | 146 | None |
| `service.py` | 169 | None |
| `user.py` | 115 | None |
| `api/api.py` | 135 | None |
| `sizes.py` | 86 | None |
| `utils.py` | 34 | None |

**UI Tests: Minimal (2 files)**

| Test File | What It Tests | Quality |
|-----------|--------------|---------|
| `Admin.test.js` | Shallow snapshot of Admin component | Trivial; uses deprecated Enzyme |
| `App.test.js` | Shallow snapshot of Spawner component | Trivial; uses deprecated Enzyme |

Both tests are simple `shallow()` renders that check snapshots — they verify HTML structure but not behavior, interactions, or data flow.

**Test-to-Code Ratio**: 2 test files / 40 source files = 5% (critical deficit)

### Code Quality

| Tool | Status | Notes |
|------|--------|-------|
| **ESLint (UI)** | Configured | Runs via `npm run test:lint`, covers `.json,.js,.ts,.jsx,.tsx` |
| **Prettier (UI)** | Configured | Format script in package.json |
| **TypeScript (UI)** | Configured | `tsc --noEmit` via `test:type-check` |
| **Python Linting** | Missing | No ruff, flake8, pylint, mypy, or any Python linting |
| **Pre-commit Hooks** | Missing | No `.pre-commit-config.yaml` |
| **Static Analysis** | Missing | No CodeQL, gosec, Semgrep, or SAST tools |

The UI has adequate code quality tooling configured in `package.json`, but none of it runs automatically since there is no CI pipeline.

### Container Images

**Status: Not applicable / Missing**

- No `Dockerfile` or `Containerfile` in the repository
- No `docker-compose.yml`
- No `.dockerignore`
- OpenShift build configs (`openshift/api-build.yaml`, `openshift/api-image.yaml`) suggest images were built via OpenShift's S2I (Source-to-Image) process
- No image scanning, SBOM generation, or runtime validation

### Security

**Status: No security practices in place**

| Practice | Status |
|----------|--------|
| Container scanning (Trivy/Snyk) | Missing |
| SAST/CodeQL | Missing |
| Dependency scanning | Missing |
| Secret detection (Gitleaks) | Missing |
| Dependabot/Renovate | Missing |
| Supply chain security (SBOM) | Missing |

Dependencies include several packages with known CVE histories:
- `PyYAML` — multiple deserialization vulnerabilities
- `tornado` — HTTP header injection CVEs
- `jinja2` — template injection vulnerabilities
- `openshift` / `kubernetes` Python clients — various CVEs
- Node.js 14 — end-of-life since April 2023

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test types have rules
- **Quality**: N/A
- **Gaps**: Everything — no CLAUDE.md, no .claude/ directory, no rules, no skills
- **Recommendation**: If the repository remains active, generate rules with `/test-rules-generator` covering Python unit tests (pytest patterns), API integration tests, and React component tests

## Recommendations

### Priority 0 (Critical)

1. **Determine repository status** — If this repo is deprecated/archived, formally archive it on GitHub to prevent accidental usage. If it's still consumed by downstream projects, it needs urgent attention.
2. **Add GitHub Actions CI workflow** — At minimum: Python linting, TypeScript lint/type-check, and test execution on PRs
3. **Add Python unit tests for core modules** — Start with `profiles.py` and `openshift.py` which contain the most critical business logic
4. **Add dependency vulnerability scanning** — Pin dependencies with versions and add Trivy/Snyk scanning

### Priority 1 (High Value)

5. **Add integration tests for the REST API** — The Connexion/Swagger-based API in `api.py` should have request/response tests
6. **Replace deprecated Enzyme with React Testing Library** — Enzyme is unmaintained; existing tests are likely broken with any React upgrade
7. **Add pre-commit hooks** — Enforce linting and formatting before commits reach PR
8. **Update dependencies** — Node.js 14 → 18+, PatternFly v4 → v5, update all Python packages

### Priority 2 (Nice-to-Have)

9. **Add Dockerfile for containerized deployment** — Enable consistent builds and testing
10. **Create agent rules** — `.claude/rules/` with patterns for pytest, React Testing Library, and API tests
11. **Add OpenShift integration tests** — Validate deployment manifests against a test cluster
12. **Add API contract tests** — Validate the Connexion/Swagger spec matches actual behavior

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| **Unit Tests** | 2 trivial snapshots | Comprehensive Jest suite | Python + shell tests | Go test with coverage |
| **Integration/E2E** | None | Cypress E2E, contract tests | Multi-layer validation | envtest + E2E |
| **Build Integration** | None | PR-time builds | Image builds on PR | Konflux simulation |
| **Image Testing** | No Dockerfile | Multi-stage builds | 5-layer image validation | Image startup tests |
| **Coverage Tracking** | None (flag only) | Codecov with thresholds | Coverage reporting | Enforced minimums |
| **CI/CD** | None | 20+ workflows | Extensive matrix | Prow + GitHub Actions |
| **Security** | None | Trivy, CodeQL | Vulnerability scanning | Multiple scanners |
| **Agent Rules** | None | Comprehensive rules | Basic rules | N/A |
| **Overall** | **0.6/10** | **~8.5/10** | **~8.0/10** | **~8.5/10** |

## Key Risk Assessment

This repository represents a **high-risk component** if it is still used in production:

1. **No automated quality gates** means any PR could introduce regressions
2. **No security scanning** on a codebase that interacts with OpenShift APIs and handles user data
3. **4 years without updates** means known CVEs in dependencies are unpatched
4. **No tests** means no safety net for any changes

**Recommended immediate action**: Determine if this repository is still actively consumed. If yes, prioritize CI/CD and basic test coverage. If no, archive it.

## File Paths Reference

| Category | Files |
|----------|-------|
| **Python Source** | `jupyterhub_singleuser_profiles/*.py` (9 modules, 1,363 LOC) |
| **API** | `jupyterhub_singleuser_profiles/api/api.py` (135 LOC) |
| **UI Source** | `jupyterhub_singleuser_profiles/ui/src/` (27 files, 3,718 LOC) |
| **UI Tests** | `jupyterhub_singleuser_profiles/ui/src/App/__tests__/` (2 files) |
| **OpenShift Manifests** | `openshift/*.yaml` (9 files) |
| **CI Config** | `.aicoe-ci.yaml`, `.thoth.yaml` |
| **Package Config** | `setup.py`, `requirements.txt`, `jupyterhub_singleuser_profiles/ui/package.json` |
| **PR Template** | `.github/PULL_REQUEST_TEMPLATE.md` |
