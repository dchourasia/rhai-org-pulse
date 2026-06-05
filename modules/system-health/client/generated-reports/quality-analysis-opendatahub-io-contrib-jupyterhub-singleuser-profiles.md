---
repository: "opendatahub-io-contrib/jupyterhub-singleuser-profiles"
overall_score: 1.8
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "2 trivial snapshot tests for UI, zero Python unit tests for 1500+ LOC backend"
  - dimension: "Integration/E2E"
    score: 0.5
    status: "No automated integration or E2E tests; manual cluster-based testing only"
  - dimension: "Build Integration"
    score: 1.0
    status: "No CI workflows at all; legacy OpenShift S2I build with Python 3.6"
  - dimension: "Image Testing"
    score: 0.5
    status: "No container image build pipeline, no runtime validation, no scanning"
  - dimension: "Coverage Tracking"
    score: 0.5
    status: "Jest config has coverage thresholds set to 0%; no codecov; no Python coverage"
  - dimension: "CI/CD Automation"
    score: 0.5
    status: "No GitHub Actions workflows; only AICoE-CI release config and Thoth version manager"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "No CI/CD pipeline exists"
    impact: "No automated quality gate on any PR — code merges unchecked"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "Zero Python unit tests for the entire backend"
    impact: "1500+ lines of OpenShift/K8s interaction code completely untested"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "Only 2 trivial snapshot tests for 34-file React/TypeScript UI"
    impact: "UI regressions not caught; snapshot tests only verify render-without-crash"
    severity: "HIGH"
    effort: "12-20 hours"
  - title: "No container image build or scanning"
    impact: "No Dockerfile, no vulnerability scanning, no SBOM generation"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Repository is archived/inactive (last commit August 2022)"
    impact: "Outdated dependencies (React 16, Python 3.6 build target, Enzyme), potential CVEs"
    severity: "HIGH"
    effort: "N/A"
  - title: "No security scanning of any kind"
    impact: "No SAST, no dependency scanning, no secret detection"
    severity: "HIGH"
    effort: "4-6 hours"
quick_wins:
  - title: "Add basic GitHub Actions lint workflow"
    effort: "2-3 hours"
    impact: "Catch syntax errors and style issues on every PR"
  - title: "Add Python pytest with a few smoke tests"
    effort: "3-4 hours"
    impact: "Establish testing baseline for the most critical backend modules"
  - title: "Add Trivy container scanning"
    effort: "1-2 hours"
    impact: "Surface known CVEs in dependencies"
  - title: "Add dependabot or renovate for dependency updates"
    effort: "1 hour"
    impact: "Keep critically outdated dependencies visible"
recommendations:
  priority_0:
    - "Evaluate whether this repository should be archived — last commit was August 2022 and it lives in opendatahub-io-contrib (not core)"
    - "If still active: add a minimal GitHub Actions CI pipeline with lint + test steps"
    - "Add Python unit tests for core modules (profiles.py, openshift.py, user.py)"
  priority_1:
    - "Upgrade from Enzyme to React Testing Library (Enzyme is unmaintained)"
    - "Add meaningful component tests beyond snapshot rendering"
    - "Create a Dockerfile/Containerfile and add vulnerability scanning"
    - "Add pre-commit hooks for Python (ruff/black) and TypeScript (eslint/prettier)"
  priority_2:
    - "Add integration tests using mocked OpenShift client"
    - "Add API contract tests for the Swagger/connexion endpoints"
    - "Create agent rules (.claude/rules/) for test automation guidance"
    - "Migrate from setup.py to pyproject.toml"
---

# Quality Analysis: jupyterhub-singleuser-profiles

## Executive Summary

- **Overall Score: 1.8/10**
- **Repository Status**: Effectively **archived** — last commit was August 29, 2022 (nearly 4 years ago). Lives in `opendatahub-io-contrib` (community/contrib org, not core `opendatahub-io`).
- **Key Strengths**: Has an OpenAPI/Swagger spec for its API; ESLint + Prettier configured for the UI; mock data infrastructure exists for local UI development; testing documentation exists.
- **Critical Gaps**: No CI/CD pipeline, no Python tests whatsoever, only 2 trivial UI snapshot tests, no container scanning, no security tooling, severely outdated dependencies.
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1.0/10 | 2 trivial snapshot tests for UI; zero Python tests for 1500+ LOC backend |
| Integration/E2E | 0.5/10 | No automated tests; manual cluster deploy only |
| **Build Integration** | **1.0/10** | **No CI workflows; legacy OpenShift S2I build targeting Python 3.6** |
| Image Testing | 0.5/10 | No Dockerfile, no image build pipeline, no runtime validation |
| Coverage Tracking | 0.5/10 | Jest thresholds set to 0%; no codecov integration; no Python coverage |
| CI/CD Automation | 0.5/10 | No GitHub Actions; only AICoE-CI release hook and Thoth version manager |
| Agent Rules | 0.0/10 | No AI agent guidance files exist |

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: No automated quality gate runs on PRs. Code can be merged with broken syntax, failing tests, or security vulnerabilities.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The `.github/` directory contains only issue templates — no workflows. The `.aicoe-ci.yaml` configures only PyPI release uploads with empty checks (`check: []`). There is no GitHub Actions, GitLab CI, Jenkinsfile, or Makefile with test targets.

### 2. Zero Python Unit Tests
- **Impact**: The entire backend — 1,508 lines of Python across 10 modules — has no test coverage. This includes critical OpenShift/Kubernetes interaction code (`openshift.py`: 279 lines, `profiles.py`: 376 lines), API endpoints (`api.py`: 139 lines), and user management (`user.py`: 115 lines).
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Details**: No `test_*.py` or `*_test.py` files exist anywhere in the repository. No pytest configuration (no `pytest.ini`, `conftest.py`, or pyproject.toml test section). The `requirements.txt` has no test dependencies.

### 3. Trivial UI Tests
- **Impact**: The React/TypeScript UI has 34 source files but only 2 test files — both are shallow Enzyme snapshot tests that only verify components render without crashing. No behavioral testing, no user interaction testing, no API call mocking tests.
- **Severity**: HIGH
- **Effort**: 12-20 hours
- **Details**: Tests use Enzyme (`enzyme-adapter-react-16`), which is unmaintained and incompatible with React 17+. The Jest coverage thresholds are all set to 0% (branches, functions, lines, statements), meaning they provide no enforcement.

### 4. No Container Image Infrastructure
- **Impact**: No Dockerfile or Containerfile exists. The build relies entirely on an OpenShift S2I BuildConfig targeting Python 3.6 (EOL since December 2021). No vulnerability scanning, no SBOM generation, no multi-architecture support.
- **Severity**: HIGH
- **Effort**: 4-8 hours

### 5. Repository Appears Abandoned
- **Impact**: Last commit was August 29, 2022. Zero commits in 2023, 2024, 2025, or 2026. Dependencies are severely outdated (React 16.13, TypeScript 4.0, node-sass 4.14, Python 3.6 target). Multiple known CVEs likely exist in pinned dependency versions.
- **Severity**: HIGH
- **Effort**: N/A — may warrant formal archival

### 6. No Security Scanning
- **Impact**: No SAST, no dependency scanning (Dependabot/Snyk/Trivy), no secret detection (Gitleaks), no CodeQL. With outdated dependencies, the risk of unpatched CVEs is very high.
- **Severity**: HIGH
- **Effort**: 4-6 hours

## Quick Wins

### 1. Add Basic GitHub Actions Lint Workflow (2-3 hours)
Catch syntax and style issues on every PR.
```yaml
name: Lint
on: [pull_request]
jobs:
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check jupyterhub_singleuser_profiles/
  ui-lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: jupyterhub_singleuser_profiles/ui
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: npm run test:lint
```

### 2. Add Python pytest Smoke Tests (3-4 hours)
Establish a testing baseline for the most critical modules.
```bash
pip install pytest pytest-cov
# Create tests/ directory with basic tests for sizes.py, utils.py, images.py
```

### 3. Add Trivy Container Scanning (1-2 hours)
Even without a Dockerfile, Trivy can scan the filesystem for known CVEs in Python and npm dependencies.

### 4. Add Dependabot (1 hour)
Create `.github/dependabot.yml` to track outdated Python and npm dependencies.

## Detailed Findings

### CI/CD Pipeline

| Aspect | Finding |
|--------|---------|
| GitHub Actions workflows | **None** — `.github/` only contains issue templates |
| PR-triggered tests | **None** |
| Periodic/scheduled jobs | **None** |
| Build automation | AICoE-CI release to PyPI only (`check: []` — empty checks) |
| Version management | Thoth `.thoth.yaml` for version bumps |
| Concurrency control | N/A — no workflows |
| Caching | N/A — no workflows |

**Key files analyzed:**
- `.aicoe-ci.yaml` — Release-only config, explicitly empty checks
- `.thoth.yaml` — Version management config
- `.github/ISSUE_TEMPLATE/` — Release issue templates only

### Test Coverage

#### Python Backend (1,508 LOC)
- **Test files**: 0
- **Test framework**: None configured
- **Test-to-code ratio**: 0:1
- **Coverage generation**: None
- **Key untested modules**:
  - `profiles.py` (376 lines) — Core profile management, OpenShift ConfigMap CRUD
  - `openshift.py` (279 lines) — Kubernetes/OpenShift client wrapper
  - `images.py` (162 lines) — Image stream management
  - `service.py` (169 lines) — JupyterHub service integration
  - `api.py` (139 lines) — Flask/Connexion API endpoints with auth

#### TypeScript/React UI (34 source files, ~3,600 LOC)
- **Test files**: 2 (`App.test.js`, `Admin.test.js`)
- **Test framework**: Jest 26.6 + Enzyme 3.7
- **Test type**: Shallow snapshot rendering only
- **Test-to-code ratio**: ~0.006:1 (2 tests / 34 source files)
- **Coverage thresholds**: All set to 0% (no enforcement)
- **Mock infrastructure**: Comprehensive `mockData.ts` exists but is unused by tests

#### Integration/E2E
- **Automated**: None
- **Manual process**: Documented in `docs/testing.md` — requires deploying to an OpenShift cluster via `jsp-wrapper`, manual browser verification
- **E2E framework**: None (no Cypress, Playwright, or Selenium)

### Code Quality

| Tool | Status |
|------|--------|
| ESLint | Configured for UI (`@typescript-eslint`, `react-hooks`, `prettier`) |
| Prettier | Configured for UI (singleQuote, trailingComma, printWidth: 100) |
| TypeScript | Configured with `strict: true`, but `noImplicitAny: false` |
| Python linting | **None** — no ruff, flake8, mypy, pylint, or black |
| Pre-commit hooks | **None** — no `.pre-commit-config.yaml` |
| Static analysis | **None** — no CodeQL, gosec, Semgrep |
| Dependency scanning | **None** — no Dependabot, Snyk, or Renovate |
| Secret detection | **None** — no Gitleaks or TruffleHog |

### Container Images

| Aspect | Finding |
|--------|---------|
| Dockerfile/Containerfile | **None** — relies entirely on OpenShift S2I |
| Build process | OpenShift S2I BuildConfig targeting `python:3.6` (EOL) |
| Multi-architecture | Not supported |
| Runtime validation | None |
| Security scanning | None (no Trivy, Snyk, or Grype) |
| SBOM generation | None |
| Image signing | None |

### Security

| Practice | Status |
|----------|--------|
| SAST (CodeQL) | Not configured |
| Dependency scanning | Not configured |
| Container scanning | Not configured |
| Secret detection | Not configured |
| Vulnerability thresholds | Not configured |
| Security policy | No SECURITY.md |

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Not present
- **Coverage**: No test types have agent rules
- **Quality**: N/A
- **Gaps**: Everything — no AI agent guidance exists for any aspect of development
- **Recommendation**: If repository is still active, generate rules with `/test-rules-generator`

## Recommendations

### Priority 0 (Critical)

1. **Determine repository status** — With no commits since August 2022 and its location in `opendatahub-io-contrib` (not core), evaluate whether this should be formally archived. If archived, add a clear notice to the README.

2. **If still active: Add a minimal CI pipeline** — Even a basic lint + existing test run on PRs would be a massive improvement over the current state of zero automation.

3. **Add Python unit tests for core modules** — Start with `sizes.py` (simplest, 83 lines), `utils.py` (34 lines), then `images.py` and `user.py`. The `openshift.py` and `profiles.py` modules will need mocked K8s clients.

### Priority 1 (High Value)

4. **Migrate from Enzyme to React Testing Library** — Enzyme is unmaintained. React Testing Library is the standard for React component testing and works with modern React.

5. **Add meaningful UI tests** — Use the existing `mockData.ts` infrastructure to write behavioral tests (form submissions, image selection, size selection, environment variable management).

6. **Create a Dockerfile** — Replace the S2I dependency with a standard multi-stage Dockerfile targeting a supported Python version (3.11+).

7. **Add pre-commit hooks** — Configure ruff (Python) and eslint/prettier (TypeScript) as pre-commit hooks.

### Priority 2 (Nice-to-Have)

8. **Add API contract tests** — The Swagger spec (`swagger.yaml`) defines the API contract. Use `schemathesis` or `dredd` to validate the API implementation matches the spec.

9. **Add integration tests with mocked OpenShift client** — Use `unittest.mock` to mock the OpenShift client and test `profiles.py` and `openshift.py` in isolation.

10. **Create agent rules** — Add `.claude/rules/` with test creation guidance for Python (pytest patterns) and TypeScript (React Testing Library patterns).

11. **Migrate from setup.py to pyproject.toml** — Modern Python packaging standard.

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 0.0 (Python), 1.0 (UI) | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 0.5 | 9.0 | 8.0 | 9.0 |
| Build Integration | 1.0 | 8.0 | 9.0 | 8.0 |
| Image Testing | 0.5 | 7.0 | 9.5 | 7.0 |
| Coverage Tracking | 0.5 | 8.0 | 6.0 | 9.0 |
| CI/CD Automation | 0.5 | 9.0 | 8.0 | 9.0 |
| Agent Rules | 0.0 | 8.0 | 3.0 | 2.0 |
| **Overall** | **1.8** | **8.5** | **7.5** | **8.0** |

This repository scores in the bottom tier across all dimensions. However, the most important finding is that it appears to be an abandoned repository — no development activity for nearly 4 years. The quality gap may be moot if the project has been superseded.

## File Paths Reference

| File | Purpose |
|------|---------|
| `.aicoe-ci.yaml` | AICoE CI config (release only, empty checks) |
| `.thoth.yaml` | Thoth version management |
| `.github/ISSUE_TEMPLATE/` | Release issue templates |
| `setup.py` | Python package configuration |
| `requirements.txt` | Python dependencies |
| `jupyterhub_singleuser_profiles/api/swagger.yaml` | OpenAPI 3.0 spec |
| `jupyterhub_singleuser_profiles/api/api.py` | Flask/Connexion API |
| `jupyterhub_singleuser_profiles/profiles.py` | Core profile management (376 LOC) |
| `jupyterhub_singleuser_profiles/openshift.py` | K8s/OpenShift client (279 LOC) |
| `jupyterhub_singleuser_profiles/ui/package.json` | UI dependencies and scripts |
| `jupyterhub_singleuser_profiles/ui/.eslintrc` | ESLint configuration |
| `jupyterhub_singleuser_profiles/ui/jest.config.js` | Jest configuration (0% thresholds) |
| `jupyterhub_singleuser_profiles/ui/tsconfig.json` | TypeScript configuration |
| `jupyterhub_singleuser_profiles/ui/src/App/__tests__/` | 2 snapshot test files |
| `jupyterhub_singleuser_profiles/ui/src/__mock__/mockData.ts` | Mock data (unused by tests) |
| `openshift/api-build.yaml` | S2I BuildConfig (Python 3.6) |
| `docs/testing.md` | Manual testing documentation |
