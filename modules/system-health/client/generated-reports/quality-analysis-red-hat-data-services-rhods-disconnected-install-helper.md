---
repository: "red-hat-data-services/rhods-disconnected-install-helper"
overall_score: 1.4
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No tests of any kind exist in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests; script runs only via manual GH Actions dispatch"
  - dimension: "Build Integration"
    score: 1.0
    status: "Containerfile present but never built or validated in CI"
  - dimension: "Image Testing"
    score: 0.5
    status: "Containerfile exists but no image build, scan, or runtime validation in CI"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling of any kind"
  - dimension: "CI/CD Automation"
    score: 4.0
    status: "Two GitHub Actions workflows with schedule and dispatch triggers, but no PR checks or quality gates"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, .claude/ directory, or AI agent guidance"
critical_gaps:
  - title: "Zero test coverage across the entire repository"
    impact: "Script failures (wrong image lists, broken regex, version parsing errors) are only discovered in production disconnected installs"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No PR-triggered CI workflow — no quality gates"
    impact: "Any code change is merged without automated validation; broken scripts ship directly"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Massive code duplication between rhoai-dih.sh and rhoai-z-dih.sh (~85% identical)"
    impact: "Bug fixes applied to one script may not be applied to the other; divergence causes silent failures for z-stream releases"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No container image build or scan in CI"
    impact: "Containerfile may be broken or contain vulnerable base images; users building the image discover issues at runtime"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "Command injection risk in GitHub Actions workflows"
    impact: "User-supplied inputs are interpolated directly into shell commands without sanitization"
    severity: "HIGH"
    effort: "2-3 hours"
quick_wins:
  - title: "Add ShellCheck linting to a PR workflow"
    effort: "1-2 hours"
    impact: "Catches common bash pitfalls (unquoted variables, deprecated syntax, unused variables) automatically on every PR"
  - title: "Add a basic PR-triggered CI workflow with syntax validation"
    effort: "2-3 hours"
    impact: "Prevents broken scripts from being merged; establishes a quality gate"
  - title: "Pin GitHub Actions to SHA digests instead of tags"
    effort: "30 minutes"
    impact: "Prevents supply-chain attacks via compromised action tags (actions/checkout@v3 → actions/checkout@SHA)"
  - title: "Fix command injection in workflow inputs"
    effort: "1 hour"
    impact: "Prevents malicious input from executing arbitrary commands in CI"
recommendations:
  priority_0:
    - "Add unit tests for core bash functions (version parsing, image filtering, regex matching) using bats-core"
    - "Create a PR-triggered CI workflow that runs ShellCheck, bats tests, and validates script syntax"
    - "Fix command injection vulnerabilities in GitHub Actions workflows (use env vars instead of direct interpolation)"
  priority_1:
    - "Refactor rhoai-dih.sh and rhoai-z-dih.sh to eliminate ~85% code duplication into a shared library"
    - "Add container image build validation to CI (build Containerfile, verify image starts)"
    - "Add Trivy/Grype scanning for the Containerfile and base images"
    - "Create integration tests that validate generated markdown output against expected format"
  priority_2:
    - "Add CLAUDE.md and agent rules for test creation and contribution guidelines"
    - "Add pre-commit hooks (ShellCheck, trailing whitespace, YAML validation)"
    - "Implement version pinning for external tools (yq, oc, skopeo) in scripts"
    - "Add CODEOWNERS file for review requirements"
---

# Quality Analysis: rhods-disconnected-install-helper

## Executive Summary

- **Overall Score: 1.4/10**
- **Repository Type**: Bash automation tool (shell scripts generating disconnected install image lists for RHOAI)
- **Primary Language**: Bash (~1,272 lines across 4 scripts)
- **Key Strengths**: Scheduled CI automation exists, input validation for version formats, cleanup routines
- **Critical Gaps**: Zero tests, no PR-triggered CI, massive code duplication, security vulnerabilities in CI, no quality tooling
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

This repository is a utility that generates lists of container images needed for disconnected (air-gapped) RHOAI installations. It clones multiple repos from the `red-hat-data-services` GitHub org, extracts image references, and produces markdown files with `ImageSetConfiguration` examples. Despite being a critical tool for disconnected customers, it has **no automated quality controls whatsoever**.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No tests of any kind exist |
| Integration/E2E | 0/10 | No integration or E2E tests |
| **Build Integration** | **1/10** | **Containerfile present but never built in CI** |
| Image Testing | 0.5/10 | Containerfile exists but no validation |
| Coverage Tracking | 0/10 | No coverage tooling |
| CI/CD Automation | 4/10 | Two workflows exist but no PR checks |
| Agent Rules | 0/10 | No AI agent guidance |

## Critical Gaps

### 1. Zero Test Coverage
- **Impact**: Script failures (wrong image lists, broken regex patterns, version parsing errors) are only discovered when customers attempt disconnected installs in production
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The repository contains 1,272 lines of bash code across 4 scripts with complex version branching logic, regex-based image extraction, and GitHub API pagination — all completely untested. Functions like `is_rhods_version_greater_or_equal_to`, `find_images`, `filter_legacy_workbench_images_33/34`, and `validate_rhoai_branch` are prime candidates for unit testing.

### 2. No PR-Triggered CI Workflow
- **Impact**: Any code change is merged without automated validation; broken scripts ship directly to production
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The two existing workflows (`rhods-disconnected-install-helper.yml` and `rhods-disconnected-install-helper-z-stream.yml`) only trigger on `schedule`, `workflow_dispatch`, and `repository_dispatch`. There is **no `pull_request` trigger** — changes to the bash scripts are never validated before merge.

### 3. Massive Code Duplication (~85%)
- **Impact**: Bug fixes applied to one script are frequently missed in the other; the two versions diverge silently
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Details**: `rhoai-dih.sh` (624 lines) and `rhoai-z-dih.sh` (546 lines) share approximately 85% identical code. Key differences:
  - `rhoai-dih.sh` has `excluded_repos_from_rhoai_2_24`, `is_rhoai_34_or_greater()`, `get_base_branch()`, `filter_legacy_workbench_images_34()` — none present in `rhoai-z-dih.sh`
  - `rhoai-z-dih.sh` still references `must_gather_image` in `image_set_configuration()` while `rhoai-dih.sh` has it commented out
  - `rhoai-z-dih.sh` has a typo: `"Error: rhods-2.22 ditected"` (should be "detected")
  - Different `find_images()` logic paths for the same version ranges
  - `rhoai-z-dih.sh` lacks the `excluded_repos_from_rhoai_2_24` list, meaning z-stream runs clone repos that y-stream excludes

### 4. Security Vulnerabilities in CI Workflows
- **Impact**: Command injection via user-controlled workflow dispatch inputs
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: Both workflows directly interpolate `github.event.inputs.*` values into shell commands:
  ```yaml
  # Vulnerable pattern in rhods-disconnected-install-helper.yml
  rhoai_branch="${{ github.event.inputs.branch_name }}"
  ```
  While the y-stream workflow has basic regex validation, the z-stream workflow passes `${{ github.event.inputs.repositories }}` directly to a shell script without sanitization.

### 5. Container Image Never Built in CI
- **Impact**: Containerfile may be broken; users discover issues only when trying to build it themselves
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: A `Containerfile` exists using `ubi8/ubi-minimal` base, installing bash, jq, skopeo, oc, yq — but it is never built, tested, or scanned in any CI workflow. It also copies `rhods-disconnected-helper.sh` (which no longer exists under that exact name), suggesting the Containerfile is outdated/broken.

## Quick Wins

### 1. Add ShellCheck Linting to PR Workflow (1-2 hours)
```yaml
name: PR Checks
on: [pull_request]
jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run ShellCheck
      uses: ludeeus/action-shellcheck@2.0.0
      with:
        scandir: '.'
        format: gcc
```

### 2. Pin GitHub Actions to SHA Digests (30 minutes)
Replace tag-based action references to prevent supply-chain attacks:
```yaml
# Before (vulnerable)
- uses: actions/checkout@v3
- uses: actions-js/push@master

# After (pinned)
- uses: actions/checkout@<full-sha>  # v4
- uses: actions-js/push@<full-sha>   # specific version
```

### 3. Fix Command Injection (1 hour)
Use environment variables instead of direct interpolation:
```yaml
# Before (vulnerable)
run: |
  rhoai_branch="${{ github.event.inputs.branch_name }}"

# After (safe)
env:
  RHOAI_BRANCH: ${{ github.event.inputs.branch_name }}
run: |
  rhoai_branch="$RHOAI_BRANCH"
```

### 4. Add YAML Validation (30 minutes)
```yaml
- name: Validate releases.yaml
  run: yq e '.' releases.yaml > /dev/null
```

## Detailed Findings

### CI/CD Pipeline

**Workflows Found: 2**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `rhods-disconnected-install-helper.yml` | `schedule` (daily noon), `workflow_dispatch`, `repository_dispatch` | Y-stream image list generation |
| `rhods-disconnected-install-helper-z-stream.yml` | `workflow_dispatch` only | Z-stream image list generation |

**Strengths:**
- Daily scheduled runs for y-stream to keep image lists current
- `workflow_dispatch` allows manual execution with parameterized inputs
- Input validation for branch name format in y-stream workflow
- `repository_dispatch` enables external triggering (e.g., from FBC publish events)

**Weaknesses:**
- No `pull_request` trigger — no quality gates on code changes
- No concurrency control — concurrent runs could produce conflicting commits
- Using outdated `actions/checkout@v3` (current is v4)
- Using `actions-js/push@master` (tag-based, supply-chain risk)
- No caching strategies
- Commits pushed directly to main without review
- Auto-commit with generic message lacks traceability

### Test Coverage

**Score: 0/10**

- **Unit tests**: None
- **Integration tests**: None
- **E2E tests**: None
- **Test files found**: 0
- **Test frameworks**: None configured
- **Coverage tracking**: None

**Testable Functions (prime candidates for bats-core):**
- `validate_rhoai_branch` — version string validation
- `is_rhods_version_greater_or_equal_to` — version comparison logic
- `is_rhoai_34_or_greater` — EA version detection
- `get_base_branch` — EA-to-base version mapping
- `is_repo_excluded` — repository exclusion logic
- `parse_args` — argument parsing
- `find_images` — image extraction (with mocked filesystem)
- `filter_legacy_workbench_images_33/34` — regex filtering
- `image_set_configuration` — output generation

### Code Quality

**No quality tooling configured:**
- No ShellCheck integration
- No `.pre-commit-config.yaml`
- No `.editorconfig`
- No linting of any kind
- No formatting standards
- Significant commented-out code throughout (dead code)
- Inconsistent error handling (some functions exit, others return, some silently continue)
- Global variables used extensively without `local` declarations
- `set -o errexit` is notably absent — errors in subcommands are silently swallowed

**Code Smells:**
- 85% duplication between `rhoai-dih.sh` and `rhoai-z-dih.sh`
- Commented-out `must_gather_image` logic partially removed in one file but active in the other
- Typo in error message: `"ditected"` instead of `"detected"`
- Version comparison uses string-split-and-compare instead of a proper semver library
- `set -o nounset` is set but `set -o errexit` is missing

### Container Images

**Containerfile Analysis:**
- Base image: `registry.access.redhat.com/ubi8/ubi-minimal:latest` (UBI 8 — consider upgrading to UBI 9)
- Installs: bash, jq, gzip, skopeo, wget, git, findutils, oc CLI, yq v4.9.6
- **Issue**: Copies `rhods-disconnected-helper.sh` but the actual script is `rhoai-disconnected-helper.sh` — name mismatch suggests the Containerfile is stale
- **Issue**: yq is pinned to v4.9.6 (released 2021) while latest is 4.x — very outdated
- **Issue**: Uses `wget` to download yq without checksum verification
- No multi-stage build
- No `.dockerignore` for the container build (all markdown files, git history included)
- No image scanning configured
- No multi-architecture support
- No SBOM generation

### Security

- **Container scanning**: None (no Trivy, Snyk, or Grype)
- **SAST/CodeQL**: Not configured
- **Dependency scanning**: Not applicable (bash scripts), but external tool versions are not pinned
- **Secret detection**: No Gitleaks or TruffleHog
- **GitHub Actions security**: Workflow inputs interpolated directly into shell (injection risk)
- **Pinning**: Actions use mutable tags instead of SHA digests
- **Permissions**: No explicit `permissions:` block in workflows (defaults to broad write access)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **`.claude/` directory**: Not present
- **`.claude/rules/`**: Not present
- **Testing documentation**: None
- **Contribution guidelines**: None
- **Recommendation**: Generate agent rules with `/test-rules-generator` for bash testing patterns

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests using bats-core** (8-16 hours)
   - Install bats-core and bats-assert/bats-support helpers
   - Test all version parsing/comparison functions
   - Test regex filtering functions with fixture data
   - Test argument parsing
   - Target: 80%+ function coverage

2. **Create PR-triggered CI workflow** (4-6 hours)
   - ShellCheck on all `.sh` files
   - bats test execution
   - YAML validation for `releases.yaml`
   - Containerfile build validation

3. **Fix security vulnerabilities in CI** (2-3 hours)
   - Use env vars instead of direct `${{ }}` interpolation in `run:` blocks
   - Pin all actions to SHA digests
   - Add explicit `permissions:` blocks (least-privilege)
   - Add concurrency control to prevent conflicting auto-commits

### Priority 1 (High Value)

4. **Refactor to eliminate code duplication** (8-12 hours)
   - Extract shared functions into a single `lib.sh`
   - Keep `rhoai-dih.sh` and `rhoai-z-dih.sh` as thin wrappers with version-specific overrides
   - Sync missing features (excluded repos list, EA version support) to z-stream

5. **Add container image CI** (2-4 hours)
   - Fix Containerfile script name reference
   - Build image in PR CI to validate it works
   - Add Trivy scanning for vulnerability detection
   - Upgrade base image from UBI 8 to UBI 9

6. **Add integration tests for output validation** (4-6 hours)
   - Validate generated markdown files against expected format
   - Verify ImageSetConfiguration YAML is valid
   - Test with mock repository structures

### Priority 2 (Nice-to-Have)

7. **Add agent rules and contribution guidelines** (2-3 hours)
   - Create CLAUDE.md with project context and testing guidance
   - Add `.claude/rules/` with bash testing patterns
   - Document contribution workflow

8. **Add pre-commit hooks** (1-2 hours)
   - ShellCheck for all `.sh` files
   - Trailing whitespace and mixed line endings
   - YAML validation
   - Merge conflict markers

9. **Improve error handling** (4-6 hours)
   - Add `set -o errexit` to all scripts
   - Use consistent error handling patterns
   - Add proper logging (stderr for errors, stdout for output)
   - Remove commented-out dead code

10. **Pin external tool versions** (2 hours)
    - Pin yq version in scripts (currently hardcoded to v4.9.6 in Containerfile but not in CI)
    - Document required tool versions in README
    - Consider using a lockfile or version manifest

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 0/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 0/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 1/10 | 8/10 | 9/10 | 7/10 |
| Image Testing | 0.5/10 | 7/10 | 9/10 | 6/10 |
| Coverage Tracking | 0/10 | 8/10 | 6/10 | 8/10 |
| CI/CD Automation | 4/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **1.4/10** | **8.5/10** | **7.5/10** | **7.5/10** |

## File Paths Reference

| File | Purpose |
|------|---------|
| `.github/workflows/rhods-disconnected-install-helper.yml` | Y-stream CI (schedule + dispatch) |
| `.github/workflows/rhods-disconnected-install-helper-z-stream.yml` | Z-stream CI (dispatch only) |
| `rhoai-disconnected-helper.sh` | Y-stream main entry point |
| `rhoai-dih.sh` | Y-stream shared library (624 lines) |
| `rhoai-disconnected-helper-z-stream.sh` | Z-stream main entry point |
| `rhoai-z-dih.sh` | Z-stream shared library (546 lines) |
| `Containerfile` | Container image definition (stale) |
| `releases.yaml` | Active release versions list |
| `rhoai-*.md` | Generated image list outputs (~68 files) |
