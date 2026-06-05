---
repository: "red-hat-data-services/self-managed-installer"
overall_score: 0.6
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No tests of any kind exist in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or end-to-end tests; no cluster validation"
  - dimension: "Build Integration"
    score: 0.0
    status: "No CI/CD pipeline; no PR-time validation of any kind"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images built; N/A but no manifest validation either"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling; no test coverage to track"
  - dimension: "CI/CD Automation"
    score: 0.0
    status: "No GitHub Actions, no Makefile, no GitLab CI, no Jenkinsfile"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent guidance"
critical_gaps:
  - title: "Zero test coverage across the entire repository"
    impact: "Shell script bugs (install, uninstall, cleanup) are only caught in production environments"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No CI/CD pipeline of any kind"
    impact: "No automated validation on PRs; broken scripts can be merged without any checks"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Hardcoded credentials in manifest files"
    impact: "Dummy secrets with real-looking patterns (SMTP host, PagerDuty keys) could be mistaken for real credentials or copied into production"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Shell scripts pipe commands through sh with no input validation"
    impact: "Potential command injection if variables contain unexpected values; fragile error handling"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "No linting or static analysis for shell scripts"
    impact: "Common shell scripting pitfalls (unquoted variables, missing error handling) go undetected"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add ShellCheck linting via GitHub Actions"
    effort: "1-2 hours"
    impact: "Catches common Bash pitfalls (unquoted variables, unused vars, POSIX compliance issues)"
  - title: "Add YAML linting for Kubernetes manifests"
    effort: "1-2 hours"
    impact: "Validates manifest syntax and structure before merge"
  - title: "Add secret scanning with Gitleaks"
    effort: "1-2 hours"
    impact: "Prevents accidental credential commits; flags existing dummy secrets for review"
  - title: "Add basic BATS unit tests for utility functions"
    effort: "4-6 hours"
    impact: "Validates core helper functions (contains, checkNodeResource, log utilities) without requiring a cluster"
recommendations:
  priority_0:
    - "Establish a GitHub Actions CI pipeline with ShellCheck and YAML validation"
    - "Add BATS unit tests for all utility functions in scripts/utils.sh"
    - "Review and remediate hardcoded credentials in manifests/ directory"
  priority_1:
    - "Add integration tests using Kind/Minikube to validate install/uninstall workflows"
    - "Implement proper error handling (set -euo pipefail) across all scripts"
    - "Add pre-commit hooks with ShellCheck and yamllint"
  priority_2:
    - "Create agent rules (.claude/rules/) for shell script and manifest quality standards"
    - "Add documentation for testing and contribution guidelines"
    - "Consider deprecation notice if this installer is superseded by operator-based installation"
---

# Quality Analysis: self-managed-installer

## Executive Summary

- **Overall Score: 0.6/10**
- **Repository Type**: Shell script-based installer for Red Hat OpenShift Data Science (RHODS)
- **Primary Language**: Bash (699 lines across 7 scripts + 1 entry point)
- **Key Strengths**: Simple, self-contained installer with clear README and usage instructions
- **Critical Gaps**: No tests, no CI/CD, no linting, no security scanning, hardcoded credentials in manifests
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

This repository has **no quality infrastructure whatsoever**. There are no tests, no CI/CD pipeline, no linting, no pre-commit hooks, and no security scanning. The repository appears to be a legacy installer tool with very low activity (1 contributor, limited commit history). It contains hardcoded dummy credentials in Kubernetes manifests which is a security concern.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No tests of any kind exist |
| Integration/E2E | 0/10 | No integration or cluster validation tests |
| **Build Integration** | **0/10** | **No CI/CD pipeline; no PR-time validation** |
| Image Testing | 0/10 | No container images; no manifest validation |
| Coverage Tracking | 0/10 | No coverage tooling |
| CI/CD Automation | 0/10 | No workflows, Makefile, or CI config |
| Agent Rules | 0/10 | No agent guidance files |

## Critical Gaps

### 1. Zero Test Coverage
- **Impact**: Shell script bugs in install, uninstall, and cleanup operations are only caught when run against real OpenShift clusters in production-like environments
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Details**: The repository contains 699 lines of shell code across 7 scripts with functions for OpenShift resource management, cluster validation, and operator lifecycle management — none of which have tests. Key untested functions include:
  - `checkNodeResource()` — CPU/memory validation logic
  - `contains()` — array membership check
  - `wait_for_kfdef_deletion()` — async deletion polling
  - `check_oc_status()` — cluster connectivity validation
  - `check_ocp_version()` — version compatibility check

### 2. No CI/CD Pipeline
- **Impact**: Any contributor can merge broken scripts without automated checks. There is no gate preventing syntax errors, linting failures, or manifest issues from reaching the main branch.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: No `.github/workflows/`, no `Makefile`, no `.gitlab-ci.yml`, no `Jenkinsfile`. The repository has zero automation.

### 3. Hardcoded Credentials in Manifests
- **Impact**: Files like `manifests/smtp-dummy-secret.yaml` contain values such as `host: "smtp.corp.redhat.com"`, `username: "alertmanager"`, `password: "password"`. While labeled as "dummy," these patterns are problematic:
  - Real internal hostnames are exposed (`smtp.corp.redhat.com`)
  - Default passwords could be copied to production
  - No secret scanning prevents real credentials from being committed
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 4. Shell Script Security Patterns
- **Impact**: Multiple scripts use patterns like `echo "oc delete ..." | sh` which pipes constructed commands through a shell. This is fragile and potentially vulnerable to command injection if variables contain unexpected values.
- **Severity**: MEDIUM
- **Effort**: 8-12 hours
- **Details**: Found in `scripts/beta_features.sh` — commands are constructed as strings and piped to `sh` rather than executed directly.

### 5. No Linting or Static Analysis
- **Impact**: Common shell scripting pitfalls go undetected: unquoted variables, missing error handling, POSIX compliance issues
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

## Quick Wins

### 1. Add ShellCheck Linting via GitHub Actions (1-2 hours)
**Impact**: Catches common Bash pitfalls automatically on every PR

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
        uses: ludeeus/action-shellcheck@master
        with:
          scandir: './scripts'
          additional_files: 'rhods'
```

### 2. Add YAML Linting for Kubernetes Manifests (1-2 hours)
**Impact**: Validates manifest syntax and structure before merge

```yaml
# Add to .github/workflows/lint.yml
  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: YAML Lint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: manifests/
```

### 3. Add Secret Scanning with Gitleaks (1-2 hours)
**Impact**: Prevents accidental credential commits; flags existing dummy secrets

```yaml
# Add to .github/workflows/lint.yml
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4. Add BATS Unit Tests for Utility Functions (4-6 hours)
**Impact**: Validates core helper functions without requiring a cluster

```bash
# test/utils.bats
#!/usr/bin/env bats

setup() {
  source scripts/utils.sh
}

@test "contains returns 1 for matching element" {
  run contains "yes" "Y" "y" "YES" "yes"
  [ "$status" -eq 0 ]
  [ "$output" = "" ]
}

@test "contains returns 0 for non-matching element" {
  run contains "maybe" "Y" "y" "YES" "yes"
  [ "$status" -eq 0 ]
}

@test "checkNodeResource validates CPU and memory thresholds" {
  # Mock oc command for testing
  function oc() { echo "8"; }
  export -f oc
  # Would need more sophisticated mocking for real tests
}
```

## Detailed Findings

### CI/CD Pipeline

**Status**: Non-existent

The repository has zero CI/CD configuration:
- No `.github/workflows/` directory
- No `Makefile` with test/lint targets
- No `.gitlab-ci.yml`
- No `Jenkinsfile`
- No build automation of any kind

**Impact**: Contributors can merge any change without automated validation. There is no protection against broken scripts, invalid YAML manifests, or security issues.

### Test Coverage

**Status**: Zero tests

- **Test files found**: 0
- **Test directories**: None (`test/`, `tests/`, `e2e/`, `integration/` — all absent)
- **Test frameworks**: None configured
- **Test-to-code ratio**: 0:699 (0%)

The repository contains 699 lines of shell code with complex logic for:
- OpenShift cluster validation (node resources, storage classes, version checks)
- Operator lifecycle management (install, uninstall, cleanup)
- Async resource polling with timeouts
- Beta feature deployment (Data Science Pipelines)

None of this logic has any test coverage.

### Code Quality

**Status**: No quality tooling

- **ShellCheck**: Not configured
- **Pre-commit hooks**: None (no `.pre-commit-config.yaml`)
- **Static analysis**: None
- **Code formatting**: No `shfmt` or equivalent

**Notable Code Quality Issues**:
1. Scripts use `echo "command" | sh` pattern instead of direct execution
2. Missing `set -euo pipefail` in most scripts (only some use `set -e`)
3. Unquoted variables in multiple locations
4. Color codes defined as global variables without `readonly`
5. Mixed indentation styles

### Container Images

**Status**: N/A (no container builds)

The repository does not build container images. It references external images:
- `quay.io/modh/self-managed-rhods-index:beta` (operator catalog)
- `quay.io/modh/must-gather:v1.0.0` (must-gather image)
- `registry.access.redhat.com/ubi8/ubi-minimal` (cache image)

No Dockerfile or Containerfile exists in the repository.

### Security

**Status**: Multiple concerns

1. **Hardcoded Credentials**: Manifests contain dummy secrets with real-looking values:
   - `manifests/smtp-dummy-secret.yaml`: `smtp.corp.redhat.com`, password: `password`
   - `manifests/deadmansnitch-secret.yaml`: Contains a Snitch URL
   - `manifests/parameters-dummy-secret.yaml`: Contains email address
   - `manifests/pagerduty-empty-secret.yaml`: Contains `dummyToken`

2. **No Secret Scanning**: No Gitleaks, TruffleHog, or equivalent
3. **No SAST**: No CodeQL, Semgrep, or shell-specific static analysis
4. **No Dependency Scanning**: Though the project has no formal dependencies
5. **Command Injection Risk**: `echo "oc ..." | sh` pattern in beta_features.sh

### Agent Rules (Agentic Flow Quality)

**Status**: Missing

- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **`.claude/` directory**: Does not exist
- **`.claude/rules/`**: No test creation rules
- **`.claude/skills/`**: No custom skills

**Gap**: No guidance exists for AI agents working on this repository. There are no rules for:
- Shell script testing patterns
- Manifest validation standards
- Code review checklists
- Contributing guidelines

**Recommendation**: Generate agent rules with `/test-rules-generator` covering shell script testing with BATS, YAML validation, and security review checklists.

## Recommendations

### Priority 0 (Critical)

1. **Establish a GitHub Actions CI pipeline** with ShellCheck linting and YAML validation to provide minimum viable quality gates on PRs
2. **Add BATS unit tests** for all utility functions in `scripts/utils.sh` — these are pure functions that can be tested without a cluster
3. **Review and remediate hardcoded credentials** in the `manifests/` directory — replace with placeholder patterns and add documentation
4. **Add `set -euo pipefail`** to all scripts to fail fast on errors

### Priority 1 (High Value)

1. **Add integration tests** using Kind or Minikube to validate install/uninstall workflows in CI
2. **Implement proper error handling** — replace `echo | sh` patterns with direct command execution
3. **Add pre-commit hooks** with ShellCheck and yamllint for local developer feedback
4. **Add a Makefile** with standard targets (`lint`, `test`, `validate-manifests`)
5. **Add Gitleaks** for secret scanning on every PR

### Priority 2 (Nice-to-Have)

1. **Create agent rules** (`.claude/rules/`) for shell script and manifest quality standards
2. **Add contribution guidelines** (`CONTRIBUTING.md`) with testing requirements
3. **Consider deprecation notice** if this installer is superseded by operator-based installation (the `beta` channel and single-contributor history suggest this may be a legacy tool)
4. **Add `kube-linter`** to validate Kubernetes manifest best practices
5. **Implement `kubeval`/`kubeconform`** to validate manifests against Kubernetes schemas

## Comparison to Gold Standards

| Dimension | self-managed-installer | odh-dashboard | notebooks | kserve |
|-----------|----------------------|---------------|-----------|--------|
| Unit Tests | 0/10 — None | 9/10 — Jest + Go | 7/10 — pytest | 9/10 — Go testing |
| Integration/E2E | 0/10 — None | 9/10 — Cypress + Go | 8/10 — Pytest + cluster | 9/10 — envtest |
| Build Integration | 0/10 — None | 7/10 — Multi-mode | 8/10 — Multi-arch | 8/10 — Konflux |
| Image Testing | 0/10 — N/A | 7/10 — Build checks | 9/10 — 5-layer validation | 7/10 — Runtime tests |
| Coverage Tracking | 0/10 — None | 8/10 — Codecov | 6/10 — Basic | 8/10 — Enforced |
| CI/CD Automation | 0/10 — None | 9/10 — Comprehensive | 8/10 — Workflows | 9/10 — Multi-job |
| Agent Rules | 0/10 — None | 8/10 — Comprehensive | 3/10 — Basic | 2/10 — Minimal |
| **Overall** | **0.6/10** | **8.2/10** | **7.3/10** | **7.8/10** |

## File Paths Reference

### Scripts (All Source Code)
- `rhods` — Main entry point (CLI dispatcher)
- `scripts/utils.sh` — Shared utilities (320 lines)
- `scripts/deploy-rhods.sh` — Install workflow (130 lines)
- `scripts/uninstall-rhods.sh` — Uninstall workflow (58 lines)
- `scripts/cleanup.sh` — Cleanup workflow (47 lines)
- `scripts/beta_features.sh` — Beta features management (108 lines)
- `scripts/deploy-beta-features.sh` — Beta deploy (21 lines)
- `scripts/uninstall-beta-features.sh` — Beta uninstall (8 lines)
- `scripts/must-gather.sh` — Debug data collection (7 lines)

### Manifests
- `manifests/catalogsource.yaml` — Operator catalog source + subscription
- `manifests/beta_features.kfdef.yaml` — KfDef for Data Science Pipelines
- `manifests/ds-pipelines-config-templates.yaml` — Pipeline configuration templates
- `manifests/smtp-dummy-secret.yaml` — SMTP dummy credentials (**security concern**)
- `manifests/deadmansnitch-secret.yaml` — Dead Man's Snitch URL (**security concern**)
- `manifests/pagerduty-empty-secret.yaml` — PagerDuty dummy token
- `manifests/parameters-dummy-secret.yaml` — Addon parameters dummy
- `manifests/delconfigmap.yaml` — Deletion trigger ConfigMap

### Missing (Expected but Absent)
- `.github/workflows/` — No CI/CD
- `Makefile` — No build targets
- `test/` or `tests/` — No test directory
- `.pre-commit-config.yaml` — No pre-commit hooks
- `.shellcheckrc` — No ShellCheck config
- `CLAUDE.md` or `.claude/` — No agent rules
- `CONTRIBUTING.md` — No contribution guidelines
