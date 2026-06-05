---
repository: "red-hat-data-services/odh-images"
overall_score: 1.2
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist anywhere in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests of any kind"
  - dimension: "Build Integration"
    score: 0.5
    status: "No CI/CD workflows; Makefiles are image-build only with no validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "Dockerfiles exist but use severely outdated base images; no runtime validation"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tools, no codecov, no thresholds"
  - dimension: "CI/CD Automation"
    score: 0.5
    status: "No GitHub Actions workflows; only a PR template exists under .github/"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "Zero test coverage — no tests of any kind"
    impact: "All Go code (configmap-puller, leader-election) ships without any automated verification; bugs reach production unchecked"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No CI/CD pipeline"
    impact: "No automated builds, no PR checks, no linting — all quality assurance is entirely manual"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "Severely outdated and insecure base images"
    impact: "Dockerfiles reference EOL images (CentOS 7/8, UBI8 Go 1.14/1.15, Python 3.6) with known CVEs; Go 1.14/1.15 are 4+ years past EOL"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No dependency scanning or security tooling"
    impact: "Vendored Go dependencies and pip packages are never scanned for vulnerabilities"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Repository appears abandoned (last commit July 2022)"
    impact: "No active maintenance means accumulating security debt and drift from upstream projects"
    severity: "HIGH"
    effort: "N/A — requires organizational decision"
quick_wins:
  - title: "Add a basic GitHub Actions workflow for Go build verification"
    effort: "2-3 hours"
    impact: "Catch compile errors on PRs before merge; establish CI foundation"
  - title: "Add unit tests for configmap-puller utility functions"
    effort: "2-4 hours"
    impact: "Cover writeFile() and getDataFromCM() — pure functions easy to test"
  - title: "Add Trivy container scanning as a GitHub Action"
    effort: "1-2 hours"
    impact: "Immediately surface the critical CVEs in outdated base images"
  - title: "Update Dockerfiles to current UBI9/Go 1.22+ base images"
    effort: "4-6 hours"
    impact: "Eliminate hundreds of known CVEs from base image layer"
recommendations:
  priority_0:
    - "Determine if this repository is still actively used — if not, archive it to prevent confusion"
    - "If still in use: update all base images from EOL CentOS 7/8 and UBI8 Go 1.14/1.15 to current UBI9 equivalents"
    - "Add a minimal CI/CD pipeline with build verification and container scanning"
  priority_1:
    - "Add unit tests for Go components (configmap-puller, leader-election)"
    - "Add linting with golangci-lint for Go code"
    - "Pin and audit all vendored dependencies"
    - "Add CODEOWNERS and branch protection rules"
  priority_2:
    - "Add agent rules (.claude/rules/) for test automation guidance"
    - "Add integration tests that validate container startup and health endpoints"
    - "Add multi-architecture build support"
    - "Generate SBOMs for all container images"
---

# Quality Analysis: odh-images

## Executive Summary

- **Overall Score: 1.2/10**
- **Repository Status: Likely Abandoned** — Last commit was July 2022 (nearly 4 years ago), with only 7 total PRs merged in the repository's lifetime.
- **Key Strengths**: Multi-stage Dockerfiles for Go components; PR template includes a QE sign-off checklist.
- **Critical Gaps**: Zero tests, zero CI/CD, severely outdated base images (Go 1.14/1.15, CentOS 7/8, Python 3.6 — all EOL), no security scanning, no linting, no coverage tracking.
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory.

**Bottom line**: This repository has virtually no quality infrastructure. Before investing in quality improvements, the first question to answer is whether this repository is still actively used. If it is, it needs foundational work across every dimension.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist anywhere in the repository |
| Integration/E2E | 0/10 | No integration or end-to-end tests |
| **Build Integration** | **0.5/10** | **No CI/CD workflows; Makefile is image-build only** |
| Image Testing | 1/10 | Dockerfiles exist but use EOL base images; no runtime validation |
| Coverage Tracking | 0/10 | No coverage tools or thresholds |
| CI/CD Automation | 0.5/10 | No GitHub Actions; only a PR template under .github/ |
| Agent Rules | 0/10 | No agent rules or test automation guidance |

## Critical Gaps

### 1. Zero Test Coverage
- **Impact**: Both Go components (configmap-puller: 154 LOC, leader-election: 111 LOC) ship without any automated tests. Bugs, regressions, and broken Kubernetes API interactions are only caught in production.
- **Severity**: HIGH
- **Effort**: 16-24 hours to add meaningful unit and integration tests
- **Details**: No `*_test.go` files, no `test/` directories, no test frameworks configured, no test targets in the Makefile.

### 2. No CI/CD Pipeline
- **Impact**: No automated builds, no PR checks, no lint, no vulnerability scanning. All quality assurance relies entirely on manual review per the PR template checklist.
- **Severity**: HIGH
- **Effort**: 8-12 hours to establish a basic pipeline
- **Details**: The `.github/` directory contains only `PULL_REQUEST_TEMPLATE.md`. No workflows directory exists.

### 3. Severely Outdated Base Images
- **Impact**: Every Dockerfile references end-of-life images with hundreds of known CVEs:
  - `configmap-puller`: `ubi8/go-toolset:1.15.13-4` (Go 1.15, EOL since Aug 2021)
  - `leader-election`: `ubi8/go-toolset:1.15.14-3` (Go 1.15, EOL since Aug 2021)
  - `superset`: `centos/python-36-centos7` (CentOS 7 EOL June 2024, Python 3.6 EOL Dec 2021)
  - `hue`: `centos/centos:8` (CentOS 8 EOL Dec 2021)
- **Severity**: HIGH
- **Effort**: 4-8 hours to update all Dockerfiles

### 4. No Security Scanning
- **Impact**: No Trivy, Snyk, CodeQL, or any vulnerability scanning. Vendored Go dependencies (committed in `configmap-puller/vendor/`) and pinned pip packages in superset Dockerfile are never audited.
- **Severity**: HIGH
- **Effort**: 2-4 hours for basic Trivy integration

### 5. Repository Appears Abandoned
- **Impact**: Last meaningful commit was July 2022. Go module versions (1.14, 1.15) are 4+ years behind current (1.22+). The superset image pins `superset==0.30` (current Apache Superset is 4.x). This suggests the repository is no longer maintained.
- **Severity**: HIGH
- **Effort**: N/A — requires organizational decision on whether to archive or revive

## Quick Wins

### 1. Add GitHub Actions Build Workflow (2-3 hours)
Catch compile errors on PRs:
```yaml
name: Build
on: [pull_request]
jobs:
  build-go:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [configmap-puller, leader-election]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: cd ${{ matrix.component }} && go build ./...
```

### 2. Add Trivy Container Scanning (1-2 hours)
Surface CVEs immediately:
```yaml
name: Security Scan
on: [pull_request]
jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
```

### 3. Add Unit Tests for Pure Functions (2-4 hours)
`configmap-puller` has two easily testable pure functions:
- `getDataFromCM()` — extracts data from ConfigMap
- `writeFile()` — writes string to file

### 4. Update Base Images (4-6 hours)
Replace all EOL images with current equivalents:
- `ubi8/go-toolset:1.15` → `ubi9/go-toolset:1.22`
- `centos/python-36-centos7` → `ubi9/python-312`
- `centos/centos:8` → `ubi9/ubi-minimal`

## Detailed Findings

### CI/CD Pipeline

**Status: Non-existent**

- No `.github/workflows/` directory
- No Jenkinsfile, `.gitlab-ci.yml`, or other CI configuration
- Only artifact: `.github/PULL_REQUEST_TEMPLATE.md` with a manual checklist
- The PR template includes good manual gates (QE sign-off, live build image, JIRA link) but none are enforced automatically
- Makefile in `configmap-puller/` has only `build` and `push` targets — no test, lint, or scan targets

### Test Coverage

**Status: Zero**

- **Unit Tests**: 0 test files across the entire repository
- **Integration Tests**: None
- **E2E Tests**: None
- **Test-to-Code Ratio**: 0:299 (299 lines of source code, 0 lines of test code)
- **Coverage Tools**: None configured
- **Testing Frameworks**: None

The two Go components (`configmap-puller` at 154 LOC, `leader-election` at 111 LOC) are small enough that achieving high test coverage would be straightforward.

### Code Quality

**Status: No tooling**

- **Linting**: No `.golangci.yaml`, no linter configuration of any kind
- **Pre-commit Hooks**: No `.pre-commit-config.yaml`
- **Static Analysis**: No SAST tools (CodeQL, gosec, Semgrep)
- **Code Formatting**: No `gofmt` enforcement in CI
- **Dependency Management**: `configmap-puller` vendors dependencies (committed `vendor/` directory); `leader-election` uses `go.mod` without vendor

### Container Images

**Status: Functional but dangerously outdated**

| Component | Base Image | Issues |
|-----------|-----------|--------|
| configmap-puller | `ubi8/go-toolset:1.15.13-4` | Go 1.15 EOL Aug 2021; UBI8 receiving limited updates |
| leader-election | `ubi8/go-toolset:1.15.14-3` | Same Go 1.15 EOL issue |
| superset | `centos/python-36-centos7` | CentOS 7 EOL June 2024; Python 3.6 EOL Dec 2021 |
| hue | `centos/centos:8` | CentOS 8 EOL Dec 2021 |

**Positive notes**:
- Go components use multi-stage builds (builder → runtime)
- Superset Dockerfile includes a `HEALTHCHECK` directive
- Hue uses a 3-stage build (base → builder → runtime)

**Issues**:
- No `.dockerignore` files
- No image scanning in any pipeline
- No SBOM generation
- No image signing/attestation
- No multi-architecture support
- Superset uses `yum` (CentOS 7) and pins extremely old package versions (e.g., `Werkzeug==0.14.1`, `gevent==1.2.2`)
- Hue clones from GitHub at build time without pinning to a specific commit hash (only branch tag)

### Security

**Status: No security practices**

- No vulnerability scanning (Trivy, Snyk, Grype)
- No SAST/CodeQL integration
- No dependency scanning
- No secret detection (Gitleaks, TruffleHog)
- No `.trivyignore` or vulnerability baseline
- Vendored Go dependencies in `configmap-puller/vendor/` are never audited
- Superset Dockerfile pins specific versions of Python packages but they are severely outdated
- `superset_config.py` uses template variables for secrets (`{{ SUPERSET_SECRET_KEY }}`) — not ideal but acceptable if injected at deploy time
- Go code has a potential resource leak: `context.WithTimeout` at `configmap-puller/cmd/configmap-puller/main.go:125` creates a cancel function that is never called

### Agent Rules (Agentic Flow Quality)

**Status: Missing**

- No `CLAUDE.md` or `AGENTS.md` in repository root
- No `.claude/` directory
- No `.claude/rules/` for test creation rules
- No `.claude/skills/` for custom skills
- No testing documentation of any kind
- **Recommendation**: If the repository is revived, generate test automation rules with `/test-rules-generator`

## Recommendations

### Priority 0 (Critical — Do First)

1. **Determine repository status**: The last commit was July 2022. Decide whether to archive this repository or actively maintain it. If archived, document where the functionality has moved.
2. **If active: Update all base images** to current UBI9 equivalents to eliminate hundreds of known CVEs.
3. **If active: Add a minimal CI/CD pipeline** with at least build verification and container scanning.

### Priority 1 (High Value)

4. **Add unit tests** for Go components — both are small and have testable pure functions.
5. **Add golangci-lint** configuration and enforcement in CI.
6. **Update Go module versions** from 1.14/1.15 to current (1.22+).
7. **Pin and audit vendored dependencies** — remove vendor directory in favor of Go modules.
8. **Add CODEOWNERS** and branch protection rules.

### Priority 2 (Nice-to-Have)

9. **Add agent rules** (`.claude/rules/`) for test automation guidance.
10. **Add integration tests** that validate container startup and health endpoints.
11. **Add multi-architecture build support** (amd64, arm64).
12. **Generate SBOMs** for all container images.
13. **Add `.dockerignore`** files to reduce build context size.

## Comparison to Gold Standards

| Dimension | odh-images | odh-dashboard (Gold) | notebooks (Gold) | Gap |
|-----------|-----------|---------------------|-------------------|-----|
| Unit Tests | None | Jest + comprehensive coverage | Pytest + notebook validation | Critical |
| Integration/E2E | None | Cypress E2E + contract tests | Multi-layer validation | Critical |
| CI/CD | None | Multi-workflow with matrix builds | Automated image pipelines | Critical |
| Image Testing | Dockerfiles only | Build + scan + deploy validation | 5-layer image validation | Critical |
| Coverage | None | Codecov with thresholds | Coverage reporting | Critical |
| Security | None | Trivy + CodeQL + Snyk | Trivy + SBOM generation | Critical |
| Agent Rules | None | Comprehensive .claude/rules/ | Test automation rules | Critical |
| Code Quality | None | ESLint + Prettier + strict TS | Pre-commit + linting | Critical |

**Summary**: `odh-images` scores in the bottom tier across every dimension. It is a legacy repository with no quality infrastructure whatsoever, making it an outlier even among smaller utility repositories.

## File Paths Reference

| File | Purpose |
|------|---------|
| `.github/PULL_REQUEST_TEMPLATE.md` | Manual PR checklist (only CI artifact) |
| `configmap-puller/Dockerfile` | Multi-stage Go build (UBI8, Go 1.15) |
| `configmap-puller/cmd/configmap-puller/main.go` | ConfigMap watcher utility (154 LOC) |
| `configmap-puller/Makefile` | Docker build/push targets only |
| `configmap-puller/go.mod` | Go 1.15, k8s client-go 0.21.2 |
| `leader-election/Dockerfile` | Multi-stage Go build (UBI8, Go 1.15) |
| `leader-election/main.go` | Leader election HTTP server (111 LOC) |
| `leader-election/go.mod` | Go 1.14, k8s client-go 0.17.2 |
| `hue/Dockerfile` | 3-stage build from CentOS 8 (EOL) |
| `superset/Dockerfile` | Python 3.6 on CentOS 7 (both EOL) |
| `superset/bin/superset_config.py` | Superset configuration with template vars |
| `spark/README.md` | Build instructions only (no Dockerfile) |
