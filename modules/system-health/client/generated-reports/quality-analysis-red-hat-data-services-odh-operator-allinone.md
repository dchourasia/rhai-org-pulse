---
repository: "red-hat-data-services/odh-operator-allinone"
overall_score: 0.6
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files of any kind exist in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests present"
  - dimension: "Build Integration"
    score: 0.5
    status: "Legacy AICoE CI config only, no PR-time validation"
  - dimension: "Image Testing"
    score: 0.5
    status: "Dockerfile exists but no image testing, scanning, or validation"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tracking or enforcement of any kind"
  - dimension: "CI/CD Automation"
    score: 0.5
    status: "Only legacy AICoE CI build config, no GitHub Actions workflows"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "Repository is deprecated and unmaintained"
    impact: "No active development since November 2020; README states build moved to opendatahub-operator"
    severity: "HIGH"
    effort: "N/A - consider archiving"
  - title: "Zero test coverage across all dimensions"
    impact: "No unit, integration, or E2E tests exist; any image built from this repo is completely unvalidated"
    severity: "HIGH"
    effort: "N/A for deprecated repo"
  - title: "No CI/CD pipeline (GitHub Actions)"
    impact: "No automated quality gates on PRs; only legacy AICoE CI build trigger exists"
    severity: "HIGH"
    effort: "N/A for deprecated repo"
  - title: "No container image scanning or validation"
    impact: "Multi-stage image combining operator and manifests has no security scanning, SBOM, or runtime validation"
    severity: "HIGH"
    effort: "2-4 hours if repo were active"
  - title: "No code quality tooling"
    impact: "No linting, static analysis, pre-commit hooks, or secret detection configured"
    severity: "MEDIUM"
    effort: "N/A for deprecated repo"
quick_wins:
  - title: "Archive the repository on GitHub"
    effort: "< 1 hour"
    impact: "Clearly signals deprecation status to any visitors; prevents accidental use"
  - title: "Add deprecation badge to README"
    effort: "< 30 minutes"
    impact: "More visible deprecation notice for anyone landing on the repo"
  - title: "If reactivated: Add Trivy scanning to Dockerfile"
    effort: "1-2 hours"
    impact: "Baseline security scanning for the multi-stage image"
recommendations:
  priority_0:
    - "Archive this repository on GitHub to formalize its deprecated status"
    - "Verify that the successor repo (opendatahub-operator) has adequate quality practices for the allinone image build"
  priority_1:
    - "If the repo must remain active: add GitHub Actions workflows with basic image build and Trivy scan"
    - "If the repo must remain active: add image startup validation testing"
  priority_2:
    - "Add a CODEOWNERS file pointing to the team responsible for the successor repo"
    - "Update the AICoE CI config or remove it since the registry-project is already marked deprecated"
---

# Quality Analysis: odh-operator-allinone

## Executive Summary

- **Overall Score: 0.6/10**
- **Repository Status: DEPRECATED** (last commit: November 18, 2020)
- **Key Finding**: This repository is explicitly marked as deprecated in its README. The build for the "all-in-one" operator image has been moved to [opendatahub-operator](https://github.com/red-hat-data-services/opendatahub-operator). The repository contains only 5 files (excluding `.git/`) and has zero quality infrastructure of any kind.
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

## Repository Overview

| Attribute | Value |
|-----------|-------|
| **Repository** | red-hat-data-services/odh-operator-allinone |
| **Status** | Deprecated |
| **Last Commit** | 2020-11-18 (deprecation notice) |
| **Primary Language** | Dockerfile / Shell |
| **Purpose** | Simplified deployment image combining ODH operator + manifests |
| **Successor** | red-hat-data-services/opendatahub-operator |
| **Total Files** | 5 (Dockerfile, change-version.sh, .aicoe-ci.yaml, README.md, LICENSE) |

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files of any kind |
| Integration/E2E | 0/10 | No integration or E2E tests |
| **Build Integration** | **0.5/10** | **Legacy AICoE CI config only, no PR-time validation** |
| Image Testing | 0.5/10 | Dockerfile exists but no testing/scanning |
| Coverage Tracking | 0/10 | No coverage tracking |
| CI/CD Automation | 0.5/10 | Only legacy AICoE CI build config |
| Agent Rules | 0/10 | No agent rules or AI guidance |

## Critical Gaps

### 1. Repository is Deprecated and Unmaintained
- **Severity**: HIGH
- **Impact**: No active development since November 2020. The README explicitly states: *"Deprecated! The build for this image is included in https://github.com/red-hat-data-services/opendatahub-operator"*
- **Risk**: Anyone using this repo is consuming a 5+ year old image definition with known security vulnerabilities in base images
- **Recommendation**: Archive the repository on GitHub

### 2. Zero Test Coverage
- **Severity**: HIGH
- **Impact**: No unit, integration, or E2E tests exist. The `change-version.sh` script performs `sed` replacements on the Dockerfile with no validation that the resulting Dockerfile is valid
- **Files at risk**: `change-version.sh` (untested shell script that modifies Dockerfile)
- **Effort**: N/A for deprecated repo

### 3. No CI/CD Pipeline
- **Severity**: HIGH
- **Impact**: No GitHub Actions workflows. The only CI configuration is a legacy `.aicoe-ci.yaml` that triggers a Thoth build to `quay.io/modh/odh-operator-image-deprecated`
- **Note**: The registry project name itself includes "deprecated" — `odh-operator-image-deprecated`
- **Effort**: N/A for deprecated repo

### 4. No Container Image Security
- **Severity**: HIGH
- **Impact**: The Dockerfile pulls from `quay.io/modh/odh-manifests` and `quay.io/modh/opendatahub-operator` with pinned tags (`1.0.0-experiment`), but there is:
  - No Trivy/Snyk scanning
  - No SBOM generation
  - No image signing
  - No vulnerability threshold enforcement
  - No base image update automation

### 5. No Code Quality Tooling
- **Severity**: MEDIUM
- **Impact**: No linting, static analysis, pre-commit hooks, or secret detection
- **Note**: The shell script `change-version.sh` has a minor issue: the shebang line is `#/bin/bash` instead of `#!/bin/bash`

## Quick Wins

### 1. Archive the Repository (< 1 hour)
Archive the repository on GitHub to clearly signal its deprecated status:
- Go to Settings → Danger Zone → Archive this repository
- This makes the repo read-only and adds a prominent banner

### 2. Add Deprecation Badge (< 30 minutes)
If archiving is not possible, add a visible deprecation badge:
```markdown
> [!WARNING]
> **This repository is deprecated.** The build is now part of [opendatahub-operator](https://github.com/red-hat-data-services/opendatahub-operator).
```

### 3. If Reactivated: Add Trivy Scanning (1-2 hours)
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t test-image .
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'test-image'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
```

## Detailed Findings

### CI/CD Pipeline

**Configuration Found**: `.aicoe-ci.yaml`
```yaml
check:
  - thoth-build
build:
  build-stratergy: "Dockerfile"  # Note: typo "stratergy"
  registry: "quay.io"
  registry-org: "modh"
  registry-project: "odh-operator-image-deprecated"
  registry-secret: "modh-pusher-secret"
```

**Analysis**:
- Uses legacy AICoE CI (Thoth) build system
- Registry project name includes "deprecated" suffix
- Only performs a build check — no testing, scanning, or validation
- Has a typo: `build-stratergy` instead of `build-strategy`
- No GitHub Actions workflows exist
- No PR checks, no status gates, no branch protection indicators

### Test Coverage

**No tests exist.** Zero test files were found:
- No `*_test.go` files
- No `*.spec.ts` or `*.test.ts` files  
- No `*_test.py` or `test_*.py` files
- No `test/` or `tests/` directories
- No test framework configuration

The `change-version.sh` script performs critical operations (modifying Dockerfile via `sed`, running `git add`, optionally `git commit`) with no test coverage. The script could silently produce an invalid Dockerfile.

### Code Quality

- **Linting**: None configured (no `.golangci.yaml`, `.eslintrc`, `ruff.toml`)
- **Pre-commit hooks**: None (no `.pre-commit-config.yaml`)
- **Static analysis**: None (no CodeQL, gosec, or Semgrep)
- **Secret detection**: None (no `.gitleaks.toml`)
- **Shell script quality**: `change-version.sh` has a broken shebang (`#/bin/bash` vs `#!/bin/bash`)

### Container Images

**Dockerfile Analysis**:
```dockerfile
ARG manifest_base=quay.io/modh/odh-manifests
ARG manifest_ver=1.0.0-experiment
ARG operator_base=quay.io/modh/opendatahub-operator
ARG operator_ver=1.0.0-experiment

FROM ${manifest_base}:${manifest_ver} as manifests
FROM ${operator_base}:${operator_ver}
USER root
COPY --from=manifests /opt/odh-manifests.tar.gz /opt/manifests/
RUN chown -R 1001:0 /opt/manifests && chmod -R a+r /opt/manifests
USER 1001
```

**Findings**:
- Simple 2-stage build combining operator binary with manifests tarball
- Uses parameterized build args for version flexibility
- Properly drops to non-root user (1001)
- No HEALTHCHECK instruction
- No image labels (maintainer, version, description)
- No `.dockerignore` file
- Pinned to experimental versions (`1.0.0-experiment`)
- No multi-architecture support
- No security scanning integration
- No SBOM generation

### Security

- **Container scanning**: None
- **SAST**: None  
- **Dependency scanning**: N/A (no application dependencies)
- **Secret detection**: None
- **Image signing**: None
- **Vulnerability management**: None

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Not present
- **Coverage**: No test types have rules
- **Quality**: N/A
- **Gaps**: Everything — no AI agent guidance exists
- **Recommendation**: N/A for deprecated repo; ensure successor repo has agent rules

## Recommendations

### Priority 0 (Critical)

1. **Archive this repository on GitHub**
   - The repo has been deprecated since November 2020
   - The successor repo (opendatahub-operator) should be used instead
   - Archiving prevents accidental use and clearly signals status

2. **Verify successor repo quality**
   - Run `/quality-repo-analysis` on `https://github.com/red-hat-data-services/opendatahub-operator`
   - Ensure the allinone image build in the successor has proper testing and scanning
   - Confirm the quality practices cover what this repo never had

### Priority 1 (If Repo Must Remain Active)

1. **Add GitHub Actions CI workflow**
   - Replace legacy AICoE CI with GitHub Actions
   - Include image build validation on PRs
   - Add Trivy security scanning

2. **Add image startup validation**
   - Test that the combined image starts correctly
   - Validate that manifests are accessible at `/opt/manifests/`
   - Verify the operator binary functions

3. **Fix the shell script**
   - Correct shebang from `#/bin/bash` to `#!/bin/bash`
   - Add input validation for version format
   - Add basic tests for `change-version.sh`

### Priority 2 (Nice-to-Have)

1. **Add CODEOWNERS file**
   - Point to the team responsible for the successor repo
   - Ensure any future activity is reviewed by the right people

2. **Clean up AICoE CI config**
   - Remove `.aicoe-ci.yaml` since it builds to a deprecated registry project
   - Or update it to clearly indicate deprecated status

3. **Add image metadata**
   - Add OCI labels to Dockerfile (maintainer, version, description)
   - Add HEALTHCHECK instruction

## Comparison to Gold Standards

| Practice | odh-operator-allinone | odh-dashboard (Gold) | notebooks (Gold) | Gap |
|----------|----------------------|----------------------|-------------------|-----|
| Unit Tests | None | Jest + comprehensive | Python tests | Critical |
| Integration Tests | None | Cypress E2E | Multi-layer validation | Critical |
| CI/CD Workflows | Legacy AICoE only | 15+ GitHub Actions | Automated pipelines | Critical |
| Coverage Tracking | None | Codecov enforced | Coverage reports | Critical |
| Image Scanning | None | Trivy + Snyk | Multi-scanner | Critical |
| Image Testing | None | Container validation | 5-layer validation | Critical |
| Pre-commit Hooks | None | Comprehensive | Configured | Critical |
| SBOM Generation | None | Automated | Automated | Critical |
| Agent Rules | None | Comprehensive .claude/ | Rules present | Critical |
| Multi-arch Support | None | Yes | Yes | Critical |

**Note**: This comparison is provided for completeness, but given the repository's deprecated status, these gaps are expected and not actionable for this specific repo.

## File Paths Reference

| File | Purpose | Notes |
|------|---------|-------|
| `Dockerfile` | Multi-stage image build | Combines operator + manifests |
| `change-version.sh` | Version update script | Has broken shebang |
| `.aicoe-ci.yaml` | Legacy CI configuration | Builds to deprecated registry |
| `README.md` | Documentation | Contains deprecation notice |
| `LICENSE` | Apache 2.0 license | Standard |

## Conclusion

This repository scores **0.6/10** overall, but this score must be interpreted in context: the repository has been **explicitly deprecated since November 2020**. The build has been moved to `opendatahub-operator`. The primary recommendation is to **archive this repository on GitHub** to formally reflect its deprecated status and prevent any accidental use. If the allinone image concept is still needed, all quality investment should go into the successor repository.
