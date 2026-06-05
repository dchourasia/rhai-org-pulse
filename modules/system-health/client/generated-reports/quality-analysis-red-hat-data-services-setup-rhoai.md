---
repository: "red-hat-data-services/setup-rhoai"
overall_score: 1.0
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist anywhere in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or end-to-end test suites"
  - dimension: "Build Integration"
    score: 1.0
    status: "Has Dockerfile but no CI build validation or PR checks"
  - dimension: "Image Testing"
    score: 1.0
    status: "Dockerfile exists with security context but no scanning or runtime validation"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tracking of any kind"
  - dimension: "CI/CD Automation"
    score: 0.0
    status: "No CI/CD workflows, no GitHub Actions, no Makefile test targets"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "No CI/CD pipeline whatsoever"
    impact: "Changes merge without any automated validation — broken scripts, YAML syntax errors, and regressions go undetected until manual execution on a live cluster"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Zero test coverage"
    impact: "The uninstall-rhoai.sh script is ~890 lines of complex cluster teardown logic with no test coverage. Regressions in this script can leave clusters in broken states with stuck namespaces, orphaned CRDs, and dangling webhooks"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No shell script linting (shellcheck)"
    impact: "Bash/shell antipatterns, quoting issues, and potential injection vulnerabilities go undetected. Several scripts already have unquoted variable expansions"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Dockerfile uses outdated base image (Fedora 38 EOL)"
    impact: "Fedora 38 reached EOL in May 2024. The upgrader container uses unpatched OS packages with known vulnerabilities, and pins to OCP 4.6 client which is also EOL"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No container image scanning"
    impact: "Vulnerabilities in base images and dependencies are not detected before deployment"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Hardcoded secrets path (~/.ssh/.brew_token)"
    impact: "Brew token is read from a fixed filesystem path with no validation. No secret management integration"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add ShellCheck linting via GitHub Actions"
    effort: "1-2 hours"
    impact: "Catch shell scripting bugs, quoting issues, and portability problems automatically on every PR"
  - title: "Add YAML validation workflow"
    effort: "1-2 hours"
    impact: "Validate Kubernetes YAML manifests are syntactically correct and follow best practices"
  - title: "Update Dockerfile base image to current Fedora and OCP client"
    effort: "30 minutes"
    impact: "Eliminate known vulnerabilities from EOL base image and tooling"
  - title: "Add basic PR workflow with shellcheck + yamllint"
    effort: "2-3 hours"
    impact: "Establish minimum quality gate preventing broken changes from merging"
recommendations:
  priority_0:
    - "Create GitHub Actions CI pipeline with shellcheck linting and YAML validation"
    - "Update Dockerfile from Fedora 38 (EOL) to current Fedora and from OCP 4.6 client to stable"
    - "Add Trivy container scanning for the upgrader image"
  priority_1:
    - "Add BATS (Bash Automated Testing System) unit tests for shell functions in uninstall-rhoai.sh"
    - "Add integration test framework using kind/minikube for YAML manifest validation"
    - "Create CLAUDE.md and agent rules for test creation guidance"
  priority_2:
    - "Add pre-commit hooks for shellcheck and yamllint"
    - "Implement secret management instead of hardcoded ~/.ssh/.brew_token path"
    - "Add documentation for contribution guidelines and testing requirements"
---

# Quality Analysis: setup-rhoai

## Executive Summary

- **Overall Score: 1.0/10**
- **Repository Type**: Shell script utility / Kubernetes automation tooling
- **Primary Language**: Bash (~1,500 lines across 13 non-config files)
- **Purpose**: Install, upgrade, and uninstall Red Hat OpenShift AI (RHOAI) on OpenShift clusters
- **Activity Level**: Very low — 1 commit since January 2024 (last commit updates uninstall script)
- **Key Strengths**: The `uninstall-rhoai.sh` script is well-structured with proper function decomposition, error handling, and comprehensive CRD/resource cleanup logic. The upgrader pod spec includes appropriate security context (non-root, drop all caps, seccomp).
- **Critical Gaps**: No CI/CD, no tests, no linting, no security scanning, no coverage tracking, no agent rules. This repository has essentially zero quality automation infrastructure.
- **Agent Rules Status**: Missing

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist |
| Integration/E2E | 0/10 | No integration or E2E tests |
| **Build Integration** | **1/10** | **Dockerfile present but no CI validation** |
| Image Testing | 1/10 | Dockerfile with security context, no scanning |
| Coverage Tracking | 0/10 | No coverage tracking |
| CI/CD Automation | 0/10 | No workflows, no GitHub Actions |
| Agent Rules | 0/10 | No CLAUDE.md, no .claude/ directory |

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: Changes merge without any automated validation. Broken scripts, YAML syntax errors, and regressions go undetected until someone manually runs the scripts on a live cluster.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: No `.github/workflows/` directory exists. No Makefile with test targets. No `.gitlab-ci.yml` or Jenkinsfile. There is zero automated quality enforcement.

### 2. Zero Test Coverage
- **Impact**: The `uninstall-rhoai.sh` script alone is ~890 lines of complex cluster teardown logic including namespace cleanup, CRD deletion, webhook removal, and finalizer handling. A regression in any of these functions can leave clusters in broken states with stuck namespaces, orphaned CRDs, and dangling webhooks. None of this is tested.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Key risk areas**:
  - `delete_namespace_with_cleanup()` — handles stuck Terminating namespaces
  - `delete_finalizers_using_namespace()` — removes finalizers across all namespaces
  - `delete_webhooks()` — cleans up validating/mutating webhooks
  - `cleanup_servicemesh3()` — deletes Istio/Gateway API resources
  - Operator-specific cleanup functions (authorino, serverless, kueue, etc.)

### 3. No Shell Script Linting
- **Impact**: Bash/shell antipatterns, quoting issues, and potential injection vulnerabilities go undetected.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Examples of existing issues**:
  - `upgrade-rhods.sh` uses `wget` to download content from S3 and passes it directly into `sed` without validation
  - `scripts/remove_finalizer.sh` writes to `tmp.json` in current directory (race condition potential)
  - Several scripts use unquoted variable expansions in `oc` commands
  - `add_brew_pull_secret.sh` uses `cat ~/.ssh/.brew_token` inside a sed substitution without escaping

### 4. Dockerfile Uses EOL Base Image
- **Impact**: The upgrader Dockerfile (`upgrader/Dockerfile`) uses `fedora:38` which reached EOL in May 2024, and pins to `openshift-client-linux` from OCP 4.6 stable (also EOL). The container runs with unpatched OS packages.
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Current**: `FROM fedora:38` + OCP 4.6 client
- **Should be**: `FROM fedora:42` (or UBI) + current OCP stable client

### 5. No Container Image Scanning
- **Impact**: No Trivy, Snyk, or any vulnerability scanning for the upgrader container image.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours

### 6. Hardcoded Secrets Path
- **Impact**: `add_brew_pull_secret.sh` reads a brew token from `~/.ssh/.brew_token` with no validation, no secret rotation support, and no integration with secret management tools.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

## Quick Wins

### 1. Add ShellCheck Linting via GitHub Actions (1-2 hours)
**Impact**: Catches shell scripting bugs, quoting issues, and portability problems automatically.

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
          severity: warning
```

### 2. Add YAML Validation (1-2 hours)
**Impact**: Validates Kubernetes manifests are syntactically correct.

```yaml
  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: YAML Lint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: '.'
          config_data: |
            extends: default
            rules:
              line-length: disable
              truthy:
                check-keys: false
```

### 3. Update Dockerfile Base Image (30 minutes)
**Impact**: Eliminate known CVEs from EOL base image.

```dockerfile
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest
RUN microdnf install -y tar gzip && \
    curl -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz \
    | tar -xz -C /usr/bin oc kubectl && \
    microdnf clean all
COPY src /nightlies
WORKDIR /nightlies
RUN oc version --client
ENTRYPOINT ["/nightlies/upgrade.sh"]
```

### 4. Add Pre-commit Hooks (1-2 hours)
**Impact**: Catch issues before they're committed.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
```

## Detailed Findings

### CI/CD Pipeline

**Status**: Non-existent

No CI/CD configuration was found anywhere in the repository:
- No `.github/workflows/` directory
- No `Makefile` with test targets
- No `.gitlab-ci.yml`
- No `Jenkinsfile`
- No build automation beyond the manual `upgrader/build.sh` script

The only automation is the Kubernetes CronJob (`upgrader/k8s/upgrader-cron.yaml`) which runs daily to auto-upgrade clusters to the latest nightly build.

### Test Coverage

**Status**: Zero

No test files of any kind exist:
- No `*_test.sh` or `*.bats` files (Bash testing)
- No `*_test.go`, `*.spec.ts`, or `*.test.py` files
- No `test/`, `tests/`, `e2e/`, or `integration/` directories
- No test framework dependencies (BATS, shunit2, etc.)
- No `pytest.ini`, `conftest.py`, or similar configuration

**Key untested areas**:

| Script | Lines | Risk | What Could Break |
|--------|-------|------|-----------------|
| `scripts/uninstall-rhoai.sh` | ~890 | Critical | Stuck namespaces, orphaned CRDs, webhook leftovers |
| `scripts/add_brew_pull_secret.sh` | 34 | High | Broken pull secrets, cluster unable to pull images |
| `setup_rhoai.sh` | 7 | Medium | Operator installation failures |
| `upgrade-rhods.sh` | 16 | Medium | Failed upgrades, wrong catalog source image |
| `upgrader/src/upgrade.sh` | 6 | Medium | In-cluster upgrade failures |

### Code Quality

**Status**: No quality tools configured

- **Linting**: No shellcheck, no yamllint, no hadolint
- **Pre-commit hooks**: None (`.pre-commit-config.yaml` does not exist)
- **Static analysis**: No SAST tools, no CodeQL
- **Dependency scanning**: Not applicable (shell scripts)
- **Secret detection**: No gitleaks, no trufflehog
- **Code formatting**: No shfmt or similar

**Notable code quality observations**:
- `uninstall-rhoai.sh` is well-structured with clear function decomposition (`delete_finalizers`, `delete_webhooks`, `delete_resources`, `cleanup_*`)
- Proper use of `set -euo pipefail` in `uninstall-rhoai.sh`
- Good security context in upgrader pod specs (non-root, drop ALL capabilities, seccomp)
- However, other scripts lack `set -euo pipefail`
- Inconsistent quoting practices across scripts

### Container Images

**Status**: Minimal — single Dockerfile with significant issues

**upgrader/Dockerfile**:
- Base image: `fedora:38` (EOL since May 2024)
- Downloads OCP 4.6 client (EOL) from public mirror
- No multi-stage build
- No `.dockerignore` file
- No vulnerability scanning
- No SBOM generation
- No image signing
- Security context properly configured in K8s manifests (non-root, seccomp)

**Build process**:
- Manual build via `upgrader/build.sh` using podman
- Pushes to `quay.io/modh/nightlies-upgrader`
- No automated builds, no Konflux integration
- Hardcoded version (`VERSION=1.2`) in build script

### Security

**Status**: Minimal security posture

**Positive**:
- Upgrader pod runs as non-root with restricted security context
- RBAC follows least-privilege (only catalogsource access)
- Capabilities dropped with `drop: ["ALL"]`
- SeccompProfile set to `RuntimeDefault`

**Gaps**:
- No container scanning (Trivy, Snyk, etc.)
- No SAST/CodeQL integration
- No secret detection tooling
- Brew token stored in plaintext at `~/.ssh/.brew_token`
- `upgrade-rhods.sh` downloads from S3 via HTTP without checksum validation
- `upgrader/src/upgrade.sh` uses `curl` to fetch latest image name without TLS pinning
- `scripts/remove_finalizer.sh` writes temporary JSON to current directory (race condition)

### Agent Rules (Agentic Flow Quality)

**Status**: Missing

- No `CLAUDE.md` in repository root
- No `AGENTS.md`
- No `.claude/` directory
- No `.claude/rules/` for test creation rules
- No `.claude/skills/` for custom skills
- No testing documentation or contribution guidelines

**Recommendation**: Generate test rules with `/test-rules-generator` to establish:
- Shell script testing patterns (BATS framework)
- YAML manifest validation rules
- Dockerfile best practices
- Integration test patterns for OpenShift utilities

## Recommendations

### Priority 0 (Critical)

1. **Create GitHub Actions CI pipeline with shellcheck and yamllint**
   - Add `.github/workflows/lint.yml` with shellcheck and yamllint jobs
   - Block PR merges without passing checks
   - Effort: 4-6 hours

2. **Update Dockerfile from Fedora 38 (EOL) to UBI 9 or current Fedora**
   - Update OCP client from 4.6 to stable
   - Add hadolint for Dockerfile linting
   - Effort: 1-2 hours

3. **Add Trivy container scanning for the upgrader image**
   - Scan on build, fail on HIGH/CRITICAL CVEs
   - Effort: 2-3 hours

### Priority 1 (High Value)

4. **Add BATS unit tests for critical shell functions**
   - Focus on `uninstall-rhoai.sh` functions: `delete_namespace_with_cleanup`, `delete_finalizers_using_namespace`, `delete_webhooks`
   - Mock `oc` commands for isolated testing
   - Effort: 16-24 hours

5. **Add YAML manifest validation**
   - Use `kubeconform` or `kubeval` to validate K8s manifests against schemas
   - Catch invalid apiVersions, missing required fields
   - Effort: 3-4 hours

6. **Create CLAUDE.md and agent rules**
   - Document testing patterns for shell scripts
   - Add rules for YAML manifest best practices
   - Use `/test-rules-generator` skill
   - Effort: 2-3 hours

### Priority 2 (Nice-to-Have)

7. **Add pre-commit hooks**
   - shellcheck, yamllint, hadolint
   - Effort: 1-2 hours

8. **Implement proper secret management**
   - Replace hardcoded `~/.ssh/.brew_token` with environment variable or OpenShift secret reference
   - Effort: 2-4 hours

9. **Add contribution guidelines**
   - CONTRIBUTING.md with testing requirements
   - PR template with checklist
   - Effort: 2-3 hours

10. **Set up Renovate/Dependabot for Dockerfile base image updates**
    - Auto-create PRs when base images are updated
    - Effort: 1-2 hours

## Comparison to Gold Standards

| Dimension | setup-rhoai | odh-dashboard | notebooks | kserve |
|-----------|-------------|---------------|-----------|--------|
| Unit Tests | 0/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 0/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 1/10 | 8/10 | 8/10 | 8/10 |
| Image Testing | 1/10 | 7/10 | 9/10 | 7/10 |
| Coverage Tracking | 0/10 | 8/10 | 6/10 | 9/10 |
| CI/CD Automation | 0/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **1.0** | **8.5** | **7.5** | **8.0** |

This repository represents the opposite end of the quality spectrum from gold standards. As a utility/automation repository, it may not need the same level of infrastructure as a production operator, but the complete absence of any quality gates is a significant risk given that the `uninstall-rhoai.sh` script operates directly on production OpenShift clusters with destructive operations.

## File Paths Reference

| Category | File | Purpose |
|----------|------|---------|
| Install | `setup_rhoai.sh` | Main RHOAI installation script |
| Upgrade | `upgrade-rhods.sh` | Fetch and apply latest nightly image |
| Uninstall | `scripts/uninstall-rhoai.sh` | Comprehensive RHOAI uninstall (~890 lines) |
| Uninstall (legacy) | `scripts/uninstall_RHODS.sh` | Legacy RHODS uninstall |
| Uninstall (legacy) | `scripts/uninstall_ODH.sh` | ODH uninstall |
| Uninstall (legacy) | `scripts/uninstall_v2.sh` | V2 uninstall script |
| Secrets | `scripts/add_brew_pull_secret.sh` | Add brew registry pull secret |
| Utility | `scripts/remove_finalizer.sh` | Force-remove namespace finalizers |
| K8s Config | `config/catalogsource.yaml` | OLM CatalogSource |
| K8s Config | `config/subscription.yaml` | OLM Subscription |
| K8s Config | `config/imagepolicy.yaml` | Image content source policy |
| K8s Config | `operator/operatorgroup.yaml` | OperatorGroup |
| K8s Config | `operator/subscription.yaml` | Operator Subscription (duplicate) |
| Upgrader | `upgrader/Dockerfile` | Upgrader container image |
| Upgrader | `upgrader/build.sh` | Manual image build script |
| Upgrader | `upgrader/setup.sh` | Deploy upgrader CronJob |
| Upgrader | `upgrader/destroy.sh` | Remove upgrader CronJob |
| Upgrader | `upgrader/src/upgrade.sh` | In-cluster upgrade logic |
| Upgrader | `upgrader/k8s/*.yaml` | RBAC and CronJob manifests |
