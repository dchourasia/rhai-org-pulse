---
repository: "red-hat-data-services/rhoai-disconnected-install-helper"
overall_score: 1.2
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist — zero unit tests for any shell functions"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or end-to-end tests of any kind"
  - dimension: "Build Integration"
    score: 1.0
    status: "Containerfile exists but is never built or validated in CI"
  - dimension: "Image Testing"
    score: 1.0
    status: "No image build, scanning, or runtime validation in CI"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling, thresholds, or reporting"
  - dimension: "CI/CD Automation"
    score: 3.0
    status: "Two workflows run scripts on schedule/dispatch but include zero test steps"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "Zero test coverage for all shell scripts"
    impact: "Any logic change (version parsing, image filtering, clone behavior) can silently break disconnected installs for customers"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "Massive code duplication between y-stream and z-stream scripts"
    impact: "rhoai-dih.sh (624 lines) and rhoai-z-dih.sh (546 lines) are ~85% identical — bugs fixed in one are routinely missed in the other"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Containerfile never built or validated in CI"
    impact: "Container may be broken at any point without detection — uses outdated yq v4.9.6 and unpinned 'latest' tags"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No shellcheck or linting in CI"
    impact: "Shell scripting bugs (unquoted variables, incorrect conditionals) go undetected until runtime failure"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "Outdated GitHub Actions versions"
    impact: "actions/checkout@v3 is deprecated; actions-js/push@master is a community action pinned to a branch, not a SHA"
    severity: "MEDIUM"
    effort: "1 hour"
  - title: "No security scanning or secret detection"
    impact: "Vulnerabilities in the container image or accidental credential leaks would go undetected"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add shellcheck to CI workflow"
    effort: "1-2 hours"
    impact: "Catches common bash bugs (unquoted vars, incorrect test operators) before they reach production"
  - title: "Upgrade actions/checkout to v4 and pin push action to a SHA"
    effort: "30 minutes"
    impact: "Security best practice — prevents supply chain attacks via mutable action references"
  - title: "Add a Containerfile build step to CI"
    effort: "1-2 hours"
    impact: "Ensures the container image actually builds — catches broken Dockerfile changes immediately"
  - title: "Pin tool versions in Containerfile"
    effort: "1 hour"
    impact: "Reproducible builds — prevents surprise breakage from upstream 'latest' changes"
recommendations:
  priority_0:
    - "Add unit tests for critical functions (version parsing, image filtering, branch validation) using bats-core or shunit2"
    - "Eliminate code duplication by extracting shared logic into a single sourced library"
    - "Add shellcheck linting to both CI workflows"
  priority_1:
    - "Build and validate the Containerfile in CI on every PR"
    - "Add integration tests that verify generated markdown output against known-good fixtures"
    - "Upgrade all GitHub Actions to current versions and pin to commit SHAs"
  priority_2:
    - "Add Trivy scanning for the container image"
    - "Create agent rules (.claude/rules/) for shell script quality patterns"
    - "Add pre-commit hooks with shellcheck and yamllint"
---

# Quality Analysis: rhoai-disconnected-install-helper

## Executive Summary

- **Overall Score: 1.2/10**
- **Repository Type**: Shell script CLI tool (Bash)
- **Primary Language**: Bash (4 scripts, ~1,272 lines of shell code)
- **Purpose**: Generates lists of additional container images needed to install RHOAI in disconnected (air-gapped) OpenShift environments using oc-mirror
- **Key Strengths**: Functional CI automation for generating image lists on a schedule; input validation for version formats
- **Critical Gaps**: Zero test coverage, massive code duplication, no linting, no container build validation, no security scanning
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

This repository has **critical quality gaps** across every dimension. Despite serving an important operational function (enabling disconnected RHOAI installations), it has no tests, no linting, no container build validation, and significant code duplication that creates a maintenance burden and bug propagation risk.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist |
| Integration/E2E | 0/10 | No integration or E2E tests |
| **Build Integration** | **1/10** | **Containerfile exists but never built in CI** |
| Image Testing | 1/10 | No image scanning or runtime validation |
| Coverage Tracking | 0/10 | No coverage tooling |
| CI/CD Automation | 3/10 | Workflows exist but contain zero test steps |
| Agent Rules | 0/10 | No agent rules or guidance |

## Critical Gaps

### 1. Zero Test Coverage for All Shell Scripts
- **Impact**: Any logic change to version parsing (`is_rhods_version_greater_or_equal_to`), image filtering (`filter_legacy_workbench_images_33/34`), or clone behavior (`clone_all_repos`) can silently break disconnected installs for customers
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The repository contains 4 shell scripts with ~1,272 total lines of complex bash logic including version comparison, regex-based image extraction, multi-repo cloning, and YAML generation — all completely untested

### 2. Massive Code Duplication (~85% Overlap)
- **Impact**: `rhoai-dih.sh` (624 lines) and `rhoai-z-dih.sh` (546 lines) contain nearly identical functions. Bug fixes or improvements made to one file are routinely missed in the other, leading to inconsistent behavior between y-stream and z-stream operations
- **Severity**: HIGH
- **Effort**: 4-8 hours to refactor
- **Details**: Functions duplicated across both files include: `set_defaults`, `verify_image_exists`, `image_tag_to_digest`, `find_images`, `image_set_configuration`, `change_rhods_version`, `fetch_repository`, `clone_all_repos`, `clone_repo`, `check_github_rate_limit`, `parse_args`, and many more. The z-stream version is slightly behind in features (e.g., missing `excluded_repos_from_rhoai_2_24`, missing `get_base_branch`)

### 3. Containerfile Never Built or Validated in CI
- **Impact**: The container image may be broken at any given point without detection
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**:
  - Uses `ubi8/ubi-minimal:latest` (unpinned — could break anytime)
  - Pins yq to `v4.9.6` (released 2021, current is v4.44+)
  - Downloads `openshift-client-linux.tar.gz` with `latest` (non-reproducible)
  - References `rhods-disconnected-helper.sh` but repo has `rhoai-disconnected-helper.sh` — possible filename mismatch

### 4. No Shellcheck or Linting
- **Impact**: Common bash pitfalls go undetected
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Observed issues**:
  - Several unquoted variables: `echo $latest_rhods_version`, `git checkout $notebooks_branch`
  - Unused variables and dead code blocks (extensive commented-out sections)
  - `set -o errexit` is missing (only `nounset` and `pipefail` are set)
  - Typo in z-stream script: `"Error: rhods-2.22 ditected"` (should be "detected")

### 5. Outdated and Insecure GitHub Actions
- **Impact**: Supply chain risk and deprecated functionality
- **Severity**: MEDIUM
- **Effort**: 1 hour
- **Details**:
  - `actions/checkout@v3` — v3 is deprecated, v4 is current
  - `actions-js/push@master` — pinned to a mutable branch reference on a community-maintained action; should be pinned to a commit SHA
  - No concurrency controls — multiple scheduled/dispatched runs could conflict

### 6. No Security Scanning
- **Impact**: No visibility into container vulnerabilities or accidental credential exposure
- **Severity**: MEDIUM
- **Effort**: 2-3 hours

## Quick Wins

### 1. Add Shellcheck to CI (1-2 hours)
```yaml
- name: Run shellcheck
  uses: ludeeus/action-shellcheck@2.0.0
  with:
    scandir: '.'
    severity: warning
```

### 2. Upgrade GitHub Actions and Pin SHAs (30 minutes)
```yaml
# Before
- uses: actions/checkout@v3
- uses: actions-js/push@master

# After
- uses: actions/checkout@v4
- uses: stefanzweifel/git-auto-commit-action@v5  # Better maintained alternative
```

### 3. Add Containerfile Build Step (1-2 hours)
```yaml
- name: Build container image
  run: docker build -f Containerfile -t rhoai-dih:test .
```

### 4. Pin Versions in Containerfile (1 hour)
```dockerfile
FROM registry.access.redhat.com/ubi8/ubi-minimal:8.10-1052
# Pin yq to current version
RUN wget https://github.com/mikefarah/yq/releases/download/v4.44.1/yq_linux_amd64 ...
# Pin oc client version
RUN curl -Lo oc.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.16.0/openshift-client-linux.tar.gz
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (2 total)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `rhods-disconnected-install-helper.yml` | Daily cron (12:00 UTC), `workflow_dispatch`, `repository_dispatch` | Generates y-stream image lists |
| `rhods-disconnected-install-helper-z-stream.yml` | `workflow_dispatch` only | Generates z-stream image lists |

**Strengths**:
- Automated daily schedule for y-stream updates
- Input validation for branch name format (regex check)
- `repository_dispatch` enables external triggering (e.g., from FBC nightly builds)

**Weaknesses**:
- Zero test steps in either workflow
- No concurrency controls — parallel runs could corrupt output
- No caching of any kind
- Uses deprecated `actions/checkout@v3`
- Uses community `actions-js/push@master` (pinned to mutable branch)
- Workflow directly commits to `main` — no PR review process for generated files
- No artifact upload or build summary

### Test Coverage

**Status**: No tests exist.

| Metric | Value |
|--------|-------|
| Test files | 0 |
| Test framework | None |
| Test-to-code ratio | 0:1 |
| Coverage tool | None |
| Coverage threshold | None |

**Functions that critically need testing**:
- `is_rhods_version_greater_or_equal_to` — version comparison logic with edge cases
- `is_rhoai_34_or_greater` — special EA version handling
- `get_base_branch` — EA version to base version mapping
- `filter_legacy_workbench_images_33/34` — regex-based image filtering
- `find_images` — complex conditional image discovery with many version-gated branches
- `validate_rhoai_branch` — input validation
- `is_repo_excluded` — version-specific repo exclusion logic

### Code Quality

**No quality tooling detected**:
- No `.golangci.yaml` / `ruff.toml` / `.flake8`
- No `.pre-commit-config.yaml`
- No `.editorconfig`
- No shellcheck configuration
- No Makefile with lint targets

**Code Issues Observed**:
1. **Massive duplication**: `rhoai-dih.sh` and `rhoai-z-dih.sh` share ~85% of their code
2. **Commented-out code**: Extensive blocks of commented code throughout both library files (30+ lines in `find_images` alone)
3. **Inconsistent error handling**: Some functions `exit 1` on error, others return, others echo and continue
4. **Missing `set -o errexit`**: Scripts use `nounset` and `pipefail` but not `errexit`
5. **Unquoted variables**: Multiple instances of unquoted variable expansion
6. **Typo**: `"Error: rhods-2.22 ditected"` in `rhoai-z-dih.sh:199`
7. **Global state**: Functions rely heavily on global variables (`rhods_version`, `repository_folder`, etc.)

### Container Images

**Containerfile Analysis**:
- **Base image**: `registry.access.redhat.com/ubi8/ubi-minimal:latest` (unpinned)
- **Installed tools**: bash, jq, gzip, skopeo, wget, git, findutils, oc, yq
- **Issues**:
  - `latest` tag for base image — non-reproducible
  - yq pinned to `v4.9.6` (2021 release, current is v4.44+)
  - oc client uses `latest` — non-reproducible
  - References `rhods-disconnected-helper.sh` but script was renamed to `rhoai-disconnected-helper.sh`
  - No HEALTHCHECK instruction
  - No USER instruction (runs as root)
  - No multi-stage build
  - No `.dockerignore` for build context optimization (only `.gitignore` exists)

**Not tested in CI**: The Containerfile is never built by any workflow.

### Security

| Practice | Status |
|----------|--------|
| Container scanning (Trivy/Snyk) | Not configured |
| SAST/CodeQL | Not configured |
| Dependency scanning | Not configured |
| Secret detection (Gitleaks) | Not configured |
| Image signing | Not configured |
| SBOM generation | Not configured |

**Security Concerns**:
- GitHub Actions workflow uses `${{ github.event.inputs.* }}` in shell context — potential injection vector (mitigated by dispatch-only trigger)
- No branch protection evident for `main` — workflows commit directly
- `actions-js/push@master` uses a mutable ref — supply chain risk

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: No guidance for AI agents on test creation, code style, or contribution patterns
- **Recommendation**: Generate rules with `/test-rules-generator` covering shell script testing patterns (bats-core), image list validation, and version parsing test cases

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests with bats-core** (8-16 hours)
   - Install [bats-core](https://github.com/bats-core/bats-core) as the test framework
   - Write tests for version comparison, image filtering, branch validation, and repo exclusion logic
   - Example test structure:
   ```bash
   @test "is_rhods_version_greater_or_equal_to returns true for equal version" {
     rhods_version="rhoai-2.25"
     run is_rhods_version_greater_or_equal_to rhoai-2.25
     [ "$status" -eq 0 ]
   }
   
   @test "validate_rhoai_branch rejects invalid format" {
     run validate_rhoai_branch "invalid-branch"
     [ "$status" -eq 1 ]
   }
   ```

2. **Eliminate code duplication** (4-8 hours)
   - Extract shared functions from `rhoai-dih.sh` and `rhoai-z-dih.sh` into a single `lib/common.sh`
   - Both entry scripts source the common library
   - Ensures bug fixes apply everywhere

3. **Add shellcheck to CI** (1-2 hours)
   - Add shellcheck step to both workflows
   - Fix existing violations
   - Enforce on all PRs

### Priority 1 (High Value)

4. **Build and test the Containerfile in CI** (2-4 hours)
   - Add a PR workflow that builds the container
   - Verify the image starts and the script runs with `--help`
   - Pin all tool versions for reproducibility

5. **Add fixture-based integration tests** (4-8 hours)
   - Create known-good markdown output fixtures for specific RHOAI versions
   - Verify generated output matches expected format and content
   - Can run in CI without external dependencies using mocked repo data

6. **Upgrade GitHub Actions** (1 hour)
   - `actions/checkout@v3` → `actions/checkout@v4`
   - Replace `actions-js/push@master` with `stefanzweifel/git-auto-commit-action@v5` or pin to SHA
   - Add concurrency controls

### Priority 2 (Nice-to-Have)

7. **Add Trivy scanning for the container image** (2-3 hours)
8. **Create agent rules** for shell script quality patterns (2-3 hours)
9. **Add pre-commit hooks** with shellcheck and yamllint (1-2 hours)
10. **Add a Makefile** with standard targets (test, lint, build, clean) (1-2 hours)
11. **Clean up commented-out code** throughout the codebase (1 hour)

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|--------------|-----------|--------|
| Unit Tests | 0/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 0/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 1/10 | 8/10 | 9/10 | 8/10 |
| Image Testing | 1/10 | 7/10 | 9/10 | 7/10 |
| Coverage Tracking | 0/10 | 8/10 | 6/10 | 9/10 |
| CI/CD Automation | 3/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **1.2/10** | **8.5/10** | **7.5/10** | **8.0/10** |

## File Paths Reference

| File | Purpose |
|------|---------|
| `.github/workflows/rhods-disconnected-install-helper.yml` | Y-stream CI workflow (daily + dispatch) |
| `.github/workflows/rhods-disconnected-install-helper-z-stream.yml` | Z-stream CI workflow (dispatch only) |
| `rhoai-disconnected-helper.sh` | Y-stream entry point script |
| `rhoai-disconnected-helper-z-stream.sh` | Z-stream entry point script |
| `rhoai-dih.sh` | Y-stream shared library (624 lines) |
| `rhoai-z-dih.sh` | Z-stream shared library (546 lines) |
| `Containerfile` | Container image definition (UBI8-based) |
| `releases.yaml` | Active release versions for scheduled runs |
| `rhoai-*.md` | Generated output files (image lists per version) |
