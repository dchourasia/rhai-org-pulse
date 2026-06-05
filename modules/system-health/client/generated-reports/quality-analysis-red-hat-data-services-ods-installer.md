---
repository: "red-hat-data-services/ods-installer"
overall_score: 0.8
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No tests of any kind exist in this repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E test infrastructure"
  - dimension: "Build Integration"
    score: 0.0
    status: "No CI/CD pipelines, no build validation"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images built or tested"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tools or tracking configured"
  - dimension: "CI/CD Automation"
    score: 2.0
    status: "No CI/CD; setup.sh provides basic scripted install"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No agent rules, CLAUDE.md, or .claude/ directory"
critical_gaps:
  - title: "No CI/CD pipeline whatsoever"
    impact: "Script changes are never validated before merge; broken installs shipped silently"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No tests of any kind"
    impact: "Regressions in install workflow go undetected; manual QA is the only safety net"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "Hardcoded dummy credentials in version control"
    impact: "Secrets (SNITCH_URL, SMTP password, LDAP passwords) checked into Git; potential security incident if repo cloned/forked carelessly"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No linting or static analysis on shell script"
    impact: "Bash bugs (quoting, error handling) not caught; setup.sh lacks set -euo pipefail"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "Single commit, appears unmaintained"
    impact: "No evidence of ongoing development, code review, or maintenance practices"
    severity: "MEDIUM"
    effort: "N/A"
quick_wins:
  - title: "Add ShellCheck linting via GitHub Actions"
    effort: "1-2 hours"
    impact: "Catches bash scripting errors (unquoted vars, missing error handling) on every PR"
  - title: "Add set -euo pipefail to setup.sh"
    effort: "15 minutes"
    impact: "Fail fast on errors instead of silently continuing with broken state"
  - title: "Move secrets to templates or external secret references"
    effort: "2-3 hours"
    impact: "Remove hardcoded credentials from version control; use envsubst or sealed secrets"
  - title: "Add a basic BATS test for setup.sh"
    effort: "4-6 hours"
    impact: "Validate install script logic without requiring a live cluster (mock oc commands)"
recommendations:
  priority_0:
    - "Remove hardcoded credentials from YAML files; use placeholder references or external secret management"
    - "Add a GitHub Actions CI workflow with ShellCheck linting for setup.sh"
    - "Add set -euo pipefail and proper error handling to setup.sh"
  priority_1:
    - "Add BATS or shUnit2 tests to validate script logic (argument parsing, wait loops, error paths)"
    - "Add YAML validation (yamllint) for all manifest files"
    - "Add a CODEOWNERS file and branch protection rules"
  priority_2:
    - "Consider whether this repo is still actively needed or should be archived"
    - "Add agent rules (.claude/rules/) for script and manifest quality standards"
    - "Add documentation for supported RHODS versions and catalog images"
---

# Quality Analysis: ods-installer

## Executive Summary

- **Overall Score: 0.8/10**
- **Repository Type**: Shell-based installer script with Kubernetes YAML manifests
- **Primary Language**: Bash (1 script, 51 lines) + YAML manifests (6 files, ~170 lines)
- **Total Codebase**: ~246 lines across 9 files
- **Commits**: 1 (single initial commit — appears unmaintained)
- **Purpose**: Facilitates RHODS (Red Hat OpenShift Data Science) OLM installation on non-OSD OpenShift clusters

**Key Strengths**: The repository provides a functional, straightforward installer script with clear README instructions.

**Critical Gaps**: This repository has essentially **zero quality infrastructure** — no CI/CD, no tests, no linting, no security scanning, and hardcoded credentials checked into version control. With only a single commit ever made, it appears to be unmaintained.

**Agent Rules Status**: Missing — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No tests of any kind exist |
| Integration/E2E | 0/10 | No integration or E2E testing |
| **Build Integration** | **0/10** | **No CI/CD pipelines or build validation** |
| Image Testing | 0/10 | No container images built or tested |
| Coverage Tracking | 0/10 | No coverage tools configured |
| CI/CD Automation | 2/10 | Shell script provides basic automation |
| Agent Rules | 0/10 | No agent rules or AI guidance |

**Weighted Overall: 0.8/10**

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: Script changes are never validated before merge. Broken installs can be shipped silently.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: No `.github/workflows/`, no `.gitlab-ci.yml`, no Jenkinsfile, no Makefile. There is zero automated validation of any change.

### 2. No Tests of Any Kind
- **Impact**: Regressions in install workflow go completely undetected. The only safety net is manual testing on a live cluster.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: Zero test files. No `*_test.sh`, no BATS tests, no shUnit2, no test directory. The `setup.sh` script has a wait-loop function that could be unit-tested but isn't.

### 3. Hardcoded Credentials in Version Control
- **Impact**: Secrets checked into Git create a security risk. The `deadmansnitch-secret.yaml` contains a real-looking Snitch URL. SMTP credentials (`password`), LDAP passwords (base64-encoded), and dummy PagerDuty tokens are all in plaintext YAML.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Files affected**:
  - `deadmansnitch-secret.yaml` — contains Snitch URL `https://nosnch.in/2c3c0b6662`
  - `smtp-dummy-secret.yaml` — contains SMTP password `password` and host
  - `ldap.yaml` — contains base64-encoded admin and user passwords
  - `pagerduty-empty-secret.yaml` — contains dummy PagerDuty key

### 4. No Linting or Static Analysis
- **Impact**: Bash scripting errors (unquoted variables, missing error handling, race conditions) are not caught.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No ShellCheck, no yamllint, no pre-commit hooks. The `setup.sh` script lacks `set -euo pipefail`, meaning errors in `oc` commands may be silently ignored.

### 5. Appears Unmaintained
- **Impact**: Single commit suggests this was a one-time setup utility that may no longer reflect current RHODS installation practices.
- **Severity**: MEDIUM
- **Effort**: N/A
- **Details**: Only 1 commit. No branches, no PRs, no issues. References `v1.1.1-58` catalog image which is likely very outdated.

## Quick Wins

### 1. Add `set -euo pipefail` to setup.sh (15 minutes)
Makes the script fail fast on any error instead of silently continuing with broken state.

```bash
#!/bin/bash
set -euo pipefail
```

### 2. Add ShellCheck Linting via GitHub Actions (1-2 hours)
Catches common bash scripting errors automatically on every PR.

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
      - name: yamllint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: "*.yaml *.tpl"
```

### 3. Move Secrets to Templates (2-3 hours)
Replace hardcoded credentials with environment variable substitution or placeholder values that are clearly marked as needing replacement.

```yaml
# Instead of hardcoded values:
stringData:
  SNITCH_URL: ${DEADMANSNITCH_URL}
  password: ${SMTP_PASSWORD}
```

### 4. Add Basic BATS Tests (4-6 hours)
Validate script logic without requiring a live cluster by mocking `oc` commands.

```bash
# test/setup.bats
@test "wait function exits after max iterations" {
  function oc() { return 1; }
  export -f oc
  run oc::wait::object::availability "oc get pods" 0.1 3
  [ "$status" -eq 1 ]
}
```

## Detailed Findings

### CI/CD Pipeline
**Status**: Non-existent

No CI/CD configuration of any kind was found:
- No `.github/workflows/` directory
- No `.gitlab-ci.yml`
- No `Jenkinsfile`
- No `Makefile`
- No `Taskfile`

The repository relies entirely on manual execution of `setup.sh` with no automated validation.

### Test Coverage
**Status**: Non-existent

- **Unit tests**: 0 files
- **Integration tests**: 0 files
- **E2E tests**: 0 files
- **Test-to-code ratio**: 0:1

The `setup.sh` script contains a `oc::wait::object::availability` function that implements a retry loop — this is testable logic that has zero coverage.

### Code Quality
**Status**: No quality tooling

- **ShellCheck**: Not configured
- **yamllint**: Not configured
- **Pre-commit hooks**: None (no `.pre-commit-config.yaml`)
- **Static analysis**: None
- **Code formatting**: None

Script quality concerns in `setup.sh`:
- Missing `set -euo pipefail` — errors not caught
- Variable `$cmd` in wait function is not quoted for command execution
- Hard-exit on iteration 100 but loop condition uses `$iterations` parameter — inconsistent
- No cleanup/rollback on failure
- No input validation for `$1` parameter

### Container Images
**Status**: Not applicable

This repository does not build container images. It references external images:
- `quay.io/modh/rhods-catalog:v1.1.1-58` (default catalog source)
- `quay.io/modh/qe-catalog-source:v160-8` (hardcoded default in script)
- `quay.io/croberts/openldapserver:latest` (LDAP server — uses `latest` tag, not pinned)

### Security
**Status**: Critical concerns

1. **Hardcoded secrets in YAML files**: Multiple files contain credentials (even if "dummy"), which is poor practice for a public repository
2. **No secret scanning**: No Gitleaks, TruffleHog, or similar tools
3. **No dependency scanning**: N/A (no dependencies beyond `oc` CLI)
4. **Unpinned image tag**: `quay.io/croberts/openldapserver:latest` uses `latest` tag — vulnerable to supply chain attacks
5. **Insecure LDAP**: `insecure: true` in OAuth configuration

### Agent Rules (Agentic Flow Quality)
**Status**: Missing

- **No `.claude/` directory**: No agent rules configured
- **No `CLAUDE.md`**: No project-level AI guidance
- **No `AGENTS.md`**: No agent configuration
- **No test creation rules**: No guidance for AI-assisted test generation
- **Recommendation**: Generate rules with `/test-rules-generator` if this repo becomes actively maintained

## Recommendations

### Priority 0 (Critical)
1. **Remove hardcoded credentials** from YAML files; use environment variable substitution (`envsubst`) or external secret management
2. **Add a GitHub Actions CI workflow** with ShellCheck for `setup.sh` and yamllint for YAML manifests
3. **Add `set -euo pipefail`** and proper error handling to `setup.sh`

### Priority 1 (High Value)
1. **Add BATS or shUnit2 tests** to validate script logic (argument parsing, wait loops, error paths)
2. **Add YAML schema validation** for all Kubernetes manifest files
3. **Add `CODEOWNERS` and branch protection** rules to require review before merge
4. **Pin all image references** — replace `latest` tags with specific digests or version tags

### Priority 2 (Nice-to-Have)
1. **Evaluate whether this repo should be archived** — single commit, appears unmaintained, may not reflect current RHODS install practices
2. **Add agent rules** (`.claude/rules/`) for script and manifest quality standards
3. **Add documentation** for supported RHODS versions and catalog images
4. **Add a cleanup.sh script** — referenced in README but missing from the repository
5. **Add pre-commit hooks** for ShellCheck and yamllint

## Comparison to Gold Standards

| Dimension | ods-installer | odh-dashboard | notebooks | kserve |
|-----------|--------------|---------------|-----------|--------|
| Unit Tests | None | Comprehensive Jest suite | Image validation tests | Go test with coverage |
| Integration/E2E | None | Cypress E2E + contract tests | Multi-layer validation | envtest + E2E |
| Build Integration | None | PR-time builds + Module Fed | Multi-arch builds | Multi-version builds |
| Image Testing | N/A | Container startup tests | 5-layer validation | Runtime validation |
| Coverage Tracking | None | Codecov with enforcement | Per-image coverage | Codecov integration |
| CI/CD | None | Multi-workflow with caching | Automated pipelines | Comprehensive CI/CD |
| Agent Rules | None | Comprehensive `.claude/rules/` | Partial | Partial |
| **Overall** | **0.8/10** | **9/10** | **8.5/10** | **8/10** |

## File Paths Reference

| File | Purpose | Lines |
|------|---------|-------|
| `setup.sh` | Main installer script | 51 |
| `catalogsource.yaml.tpl` | OLM CatalogSource + Subscription template | 32 |
| `ldap.yaml` | OpenLDAP server deployment | 79 |
| `oauthldaplocal.yaml` | OpenShift OAuth LDAP configuration | 23 |
| `deadmansnitch-secret.yaml` | Dead Man's Snitch monitoring secret | 8 |
| `pagerduty-empty-secret.yaml` | PagerDuty dummy secret | 10 |
| `smtp-dummy-secret.yaml` | SMTP notification secret | 10 |
| `parameters-dummy-secret.yaml` | Addon parameters secret | 7 |
| `README.md` | Installation instructions | 26 |

**Total**: 9 files, ~246 lines of code
