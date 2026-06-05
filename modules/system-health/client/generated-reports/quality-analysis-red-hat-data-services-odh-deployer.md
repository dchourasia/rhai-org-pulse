---
repository: "red-hat-data-services/odh-deployer"
overall_score: 1.4
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist anywhere in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E test infrastructure"
  - dimension: "Build Integration"
    score: 1.0
    status: "Basic Dockerfile exists but no PR-time build validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "Dockerfile present but no runtime validation, scanning, or multi-arch support"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling — no code to cover"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "Only aicoe-ci build check; no GitHub Actions workflows"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "Zero automated tests"
    impact: "deploy.sh (415 lines of complex bash with OCP API calls) has no validation whatsoever — regressions ship silently"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No CI/CD pipeline (GitHub Actions)"
    impact: "No PR checks, no automated linting, no build verification on pull requests"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No YAML/Kustomize validation"
    impact: "Malformed Kubernetes manifests (80 YAML files, kustomization overlays) are not validated before merge"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image scanning"
    impact: "Base image vulnerabilities (ubi8/ubi-minimal) and downloaded binaries (oc CLI) are not scanned"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "deploy.sh has no shellcheck or linting"
    impact: "Shell scripting bugs (quoting, variable expansion, error handling) go undetected"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No secret detection"
    impact: "Repository handles secrets (PagerDuty, SMTP, segment keys) — accidental commits possible"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add ShellCheck linting for deploy.sh"
    effort: "1-2 hours"
    impact: "Catches quoting bugs, unused variables, and shell anti-patterns in the critical deployment script"
  - title: "Add YAML validation with kube-linter or kubeval"
    effort: "2-3 hours"
    impact: "Validates all 80 Kubernetes manifests against schemas, catches typos and misconfigurations"
  - title: "Add Trivy container scanning"
    effort: "1-2 hours"
    impact: "Scans the built image for known CVEs in base image and installed packages"
  - title: "Add Gitleaks secret detection"
    effort: "1 hour"
    impact: "Prevents accidental commit of secrets, tokens, or credentials"
  - title: "Add basic GitHub Actions workflow"
    effort: "2-3 hours"
    impact: "Establishes PR gating with build verification, linting, and YAML validation"
recommendations:
  priority_0:
    - "Create a GitHub Actions CI workflow that gates PRs with: ShellCheck, YAML validation, Dockerfile build, and Trivy scan"
    - "Add kustomize build validation for all overlays (apps, apps-managed-service, apps-on-prem, crds, modelserving)"
  priority_1:
    - "Write BATS or shUnit2 tests for deploy.sh functions (oc::wait::object::availability, oc::object::safe::to::apply, oc::dashboard::apply::isvs)"
    - "Add Hadolint for Dockerfile linting (catches security issues like ADD from URL without checksum)"
    - "Add Gitleaks or TruffleHog for secret detection in CI"
  priority_2:
    - "Add agent rules (.claude/rules/) for manifest authoring standards and deployment script patterns"
    - "Create integration tests that validate deploy.sh against a mock cluster (Kind or envtest)"
    - "Add multi-architecture image builds (currently only linux/amd64 implicit)"
---

# Quality Analysis: odh-deployer

## Executive Summary

- **Overall Score: 1.4/10**
- **Repository Type**: Kubernetes deployment container (shell script + manifests)
- **Primary Language**: Bash (deploy.sh) + YAML (80 Kubernetes manifests)
- **Framework**: OpenShift/Kubernetes deployment via KfDef CRDs
- **Agent Rules Status**: Missing

**odh-deployer** is a deployment container that bundles `deploy.sh` with Kubernetes manifests to orchestrate RHODS (Red Hat OpenShift Data Science) component installation. The repository has **zero automated tests**, **no CI/CD workflows**, **no linting**, **no security scanning**, and **no coverage tracking**. It is among the lowest-scoring repositories in the RHODS ecosystem.

The deployment script (`deploy.sh`, 415 lines) performs complex operations — creating namespaces, applying CRDs, configuring Prometheus monitoring, managing secrets, and handling OSD vs. self-managed environment branching — all without any automated validation.

### Key Strengths
- PR template includes manual testing checklist and QE sign-off requirement
- OWNERS file establishes code review requirements
- `.gitignore` excludes secret files (`*secret.yaml`)
- `set -e -o pipefail` in deploy.sh provides basic error handling

### Critical Gaps
- Zero test files in the entire repository
- No GitHub Actions workflows (only legacy `.aicoe-ci.yaml` build config)
- No YAML/manifest validation
- No container security scanning
- No shell script linting
- No agent rules for AI-assisted contributions

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist anywhere in the repository |
| Integration/E2E | 0/10 | No integration or E2E test infrastructure |
| **Build Integration** | **1/10** | **Basic Dockerfile but no PR-time build validation** |
| Image Testing | 1/10 | Dockerfile present but no runtime validation or scanning |
| Coverage Tracking | 0/10 | No coverage tooling (no code to instrument) |
| CI/CD Automation | 1/10 | Only legacy aicoe-ci build check; no GitHub Actions |
| Agent Rules | 0/10 | No CLAUDE.md, AGENTS.md, or .claude/ directory |

## Critical Gaps

### 1. Zero Automated Tests
- **Impact**: The critical `deploy.sh` (415 lines) has 3 bash functions and 50+ `oc` commands with zero test coverage. Regressions in namespace creation, CRD application, secret handling, or monitoring configuration ship silently.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Detail**: Functions like `oc::wait::object::availability()`, `oc::dashboard::apply::isvs()`, and `oc::object::safe::to::apply()` contain complex logic (retry loops, conditional branching for OSD vs self-managed) that is entirely untested.

### 2. No CI/CD Pipeline
- **Impact**: No PR checks of any kind. The only CI config is `.aicoe-ci.yaml` which only defines a container build (no tests, no linting).
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Detail**: No GitHub Actions workflows exist. PRs merge based solely on manual review and the PR template checklist.

### 3. No YAML/Kustomize Validation
- **Impact**: 80 YAML files including CRDs, ConfigMaps, Kustomization overlays, RBAC policies, and monitoring configs are never validated against Kubernetes schemas.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Detail**: Kustomize overlays exist in `odh-dashboard/apps/`, `odh-dashboard/crds/`, `odh-dashboard/modelserving/` but `kustomize build` is never run in CI.

### 4. No Container Image Scanning
- **Impact**: The Dockerfile uses `ubi8/ubi-minimal` base image and downloads `oc` CLI binary from the internet (`ADD https://mirror.openshift.com/...`) without checksum verification.
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Detail**: No Trivy, Snyk, or any vulnerability scanning. Downloaded binary is not verified.

### 5. No Shell Script Linting
- **Impact**: `deploy.sh` has potential issues including unquoted variables, `sed -i` with in-place modifications, and complex string interpolation that ShellCheck would flag.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours

### 6. No Secret Detection
- **Impact**: Repository handles PagerDuty tokens, SMTP credentials, Dead Man's Snitch URLs, and segment keys. While `.gitignore` excludes `*secret.yaml`, no automated detection prevents accidental secret commits.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours

## Quick Wins

### 1. Add ShellCheck Linting (1-2 hours)
```yaml
# .github/workflows/lint.yml
name: Lint
on: [pull_request]
jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: ShellCheck
        uses: ludeeus/action-shellcheck@2.0.0
        with:
          scandir: '.'
```

### 2. Add YAML Validation (2-3 hours)
```yaml
  yaml-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: YAML Lint
        uses: ibiqlik/action-yamllint@v3
      - name: Kustomize Build Validation
        run: |
          for dir in odh-dashboard/apps odh-dashboard/apps-managed-service odh-dashboard/apps-on-prem odh-dashboard/crds odh-dashboard/modelserving; do
            echo "Validating $dir..."
            kustomize build $dir > /dev/null
          done
```

### 3. Add Trivy Scanning (1-2 hours)
```yaml
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t odh-deployer:test .
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'odh-deployer:test'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
```

### 4. Add Gitleaks (1 hour)
```yaml
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

### 5. Add Hadolint for Dockerfile (30 minutes)
```yaml
  hadolint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
```

## Detailed Findings

### CI/CD Pipeline

**Current State**: Minimal. Only `.aicoe-ci.yaml` exists, which configures a Thoth/AICoE CI build pipeline with `build-stratergy: "Dockerfile"`. This is a legacy CI system that only builds the container image.

- **No GitHub Actions workflows** — the `.github/` directory only contains `PULL_REQUEST_TEMPLATE.md`
- **No PR checks** — no automated tests, linting, or validation runs on PRs
- **No periodic jobs** — no scheduled scanning or validation
- **No concurrency control** — no workflow concurrency settings
- **No caching** — no build caching strategy

**PR Process**: Entirely manual, governed by the PR template checklist:
- Developer manually tests changes
- QE contact acknowledges testing
- JIRA story is acked
- Live build image is provided

### Test Coverage

**Current State**: Zero. No test files of any kind exist in the repository.

- **Unit Tests**: 0 files (no `*_test.*`, `test_*.*`, `*.spec.*`, or `*.test.*` files)
- **Integration Tests**: None
- **E2E Tests**: None
- **Test directories**: No `test/`, `tests/`, `e2e/`, or `integration/` directories
- **Test-to-code ratio**: 0:1

**What Should Be Tested**:
1. `oc::wait::object::availability()` — retry logic with configurable intervals and iterations
2. `oc::dashboard::apply::isvs()` — CRD application and ISV configuration
3. `oc::object::safe::to::apply()` — safe-apply logic checking modification labels
4. Environment branching — OSD vs. self-managed configuration paths
5. Kustomize overlays — all `kustomization.yaml` files build correctly
6. Secret templating — `sed` substitutions produce valid YAML

### Code Quality

**Current State**: No quality tooling configured.

- **Linting**: None (no ShellCheck, yamllint, or kube-linter)
- **Pre-commit hooks**: None (no `.pre-commit-config.yaml`)
- **Static analysis**: None (no CodeQL, Semgrep, or gosec)
- **Code formatters**: None
- **Dependency scanning**: None

**Observations on deploy.sh quality**:
- Uses `set -e -o pipefail` (good)
- Some functions have documentation comments (basic)
- Variable quoting is inconsistent (e.g., `echo $cmd` instead of `echo "$cmd"`)
- `sed -i` in-place modifications on config files during deployment
- Complex string interpolation with nested command substitutions
- Several `TODO` comments for cleanup items that persist across versions

### Container Images

**Current State**: Basic Dockerfile with significant security concerns.

**Dockerfile Analysis**:
- **Base image**: `registry.access.redhat.com/ubi8/ubi-minimal` (supported, good)
- **Security issues**:
  - `ADD https://mirror.openshift.com/.../oc.tar.gz` downloads binary without checksum verification
  - No multi-stage build (all build artifacts remain in final image)
  - User 1001 is set (good)
- **No multi-architecture support** — no `--platform` flags
- **No SBOM generation**
- **No image signing/attestation**
- **No vulnerability scanning**
- **Labels**: Uses `org.label-schema` (deprecated, should use OCI annotations)

### Security

**Current State**: Minimal security practices.

- **Container scanning**: None
- **SAST/CodeQL**: None
- **Dependency scanning**: None
- **Secret detection**: None (`.gitignore` excludes `*secret.yaml` but no automated scanning)
- **RBAC**: Pod security RoleBindings are defined but not validated
- **Secrets handling**: deploy.sh handles PagerDuty, SMTP, Dead Man's Snitch, and segment key secrets — all via `oc get secret` and `sed` substitution

### Agent Rules (Agentic Flow Quality)

**Current State**: No agent rules exist.

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Does not exist
- **.claude/rules/**: Does not exist
- **Coverage**: No test types have rules
- **Quality**: N/A
- **Gaps**: Everything — no guidance for AI agents on deployment script patterns, manifest authoring standards, or testing requirements
- **Recommendation**: Generate rules with `/test-rules-generator` covering:
  - Shell script testing patterns (BATS/shUnit2)
  - Kubernetes manifest validation standards
  - Kustomize overlay testing
  - Secret handling guidelines

## Recommendations

### Priority 0 (Critical)

1. **Create a comprehensive GitHub Actions CI workflow** that gates PRs with:
   - ShellCheck for `deploy.sh`
   - YAML linting for all 80 manifest files
   - `kustomize build` validation for all overlays
   - Dockerfile build verification
   - Trivy container image scanning
   - Gitleaks secret detection

2. **Add `kustomize build` validation** for all kustomization overlays:
   - `odh-dashboard/apps/` (plus sub-overlays: managed-service, on-prem)
   - `odh-dashboard/crds/`
   - `odh-dashboard/modelserving/`

### Priority 1 (High Value)

3. **Write tests for deploy.sh functions** using BATS (Bash Automated Testing System):
   - Mock `oc` commands to test `oc::wait::object::availability()` retry logic
   - Test `oc::object::safe::to::apply()` with various label scenarios
   - Test OSD vs. self-managed branching logic
   - Validate `sed` template substitutions produce valid YAML

4. **Add Hadolint for Dockerfile linting** — catches:
   - `ADD` from URL without checksum (DL3020)
   - Missing `--no-cache` on package install
   - Deprecated label schema format

5. **Add secret detection** (Gitleaks or TruffleHog) given the repository handles multiple secrets

### Priority 2 (Nice-to-Have)

6. **Add agent rules** (`.claude/rules/`) for:
   - Manifest authoring standards
   - deploy.sh modification guidelines
   - Testing requirements for changes
   
7. **Create integration tests** that validate deploy.sh against a mock OpenShift cluster using Kind + fake `oc` wrapper

8. **Add multi-architecture image builds** — currently only builds for the host architecture

9. **Modernize the Dockerfile**:
   - Replace `ADD https://` with `COPY --from=` multi-stage build
   - Add checksum verification for downloaded binaries
   - Switch to OCI image annotations
   - Add SBOM generation

## Comparison to Gold Standards

| Capability | odh-deployer | odh-dashboard | notebooks | kserve |
|-----------|-------------|---------------|-----------|--------|
| Unit Tests | None | Comprehensive (Jest) | Python tests | Go tests + coverage |
| Integration Tests | None | Contract tests | Image validation | envtest |
| E2E Tests | None | Cypress + Playwright | Multi-layer | Multi-version |
| CI/CD Workflows | Legacy aicoe-ci only | 15+ GitHub Actions | Multiple workflows | Extensive |
| Coverage Tracking | None | Codecov enforced | Per-image | Threshold gating |
| Container Scanning | None | Trivy | Multi-scanner | Trivy |
| Linting | None | ESLint + Prettier | Various | golangci-lint |
| Pre-commit Hooks | None | Configured | Configured | Configured |
| Secret Detection | .gitignore only | Gitleaks | Gitleaks | Gitleaks |
| Agent Rules | None | Comprehensive | Present | N/A |
| YAML Validation | None | Automated | Automated | Automated |
| Image Testing | None | Build + test | 5-layer validation | Runtime tests |

## File Paths Reference

| File | Purpose |
|------|---------|
| `deploy.sh` | Main deployment script (415 lines, 3 functions) |
| `Dockerfile` | Container image build (UBI8 minimal + oc CLI) |
| `Makefile` | Build and push targets (podman) |
| `.aicoe-ci.yaml` | Legacy AICoE CI build configuration |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist template |
| `OWNERS` / `OWNERS_ALIASES` | Code review ownership |
| `kfdefs/*.yaml` | KfDef custom resources (9 files) |
| `odh-dashboard/` | Dashboard CRDs, configs, apps, model serving |
| `monitoring/` | Prometheus, alerting, segment.io configs |
| `network/` | NetworkPolicy resources |
| `pod-security-rbac/` | Pod security RoleBindings |
| `consolelink/` | OpenShift ConsoleLink CR |
| `partners/anaconda/` | Anaconda CE integration |

---

*Analysis performed on 2026-06-03 against commit f315a7a (Prepare rhods 1.33 release)*
