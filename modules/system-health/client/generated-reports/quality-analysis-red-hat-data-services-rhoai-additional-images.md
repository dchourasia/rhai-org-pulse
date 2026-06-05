---
repository: "red-hat-data-services/rhoai-additional-images"
overall_score: 1.2
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No code exists — repository is a YAML-only image reference list"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests; no executable code to test"
  - dimension: "Build Integration"
    score: 0.0
    status: "No build process — no Dockerfiles, Makefiles, or build scripts"
  - dimension: "Image Testing"
    score: 1.0
    status: "Images are referenced by digest (pinned), but no validation of digest integrity or image pull testing"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tools — no code to cover"
  - dimension: "CI/CD Automation"
    score: 2.0
    status: "No CI/CD workflows; PR reviews are the only gate; branch-per-release strategy provides some structure"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "No YAML schema validation on PRs"
    impact: "Malformed YAML or invalid image references can be merged without detection, potentially breaking disconnected installations"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No image digest verification"
    impact: "Referenced image digests could point to non-existent or deleted images; broken references not caught until customer installation"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No CI/CD pipeline at all"
    impact: "Zero automated checks on PRs — entirely dependent on human review for correctness"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No branch protection or required reviews"
    impact: "PRs can be merged without review, risking accidental data corruption across release branches"
    severity: "MEDIUM"
    effort: "1 hour"
quick_wins:
  - title: "Add YAML lint workflow"
    effort: "1-2 hours"
    impact: "Catches syntax errors and formatting inconsistencies before merge"
  - title: "Add image digest existence check"
    effort: "2-3 hours"
    impact: "Validates that every referenced image digest is pullable from its registry"
  - title: "Add CODEOWNERS file"
    effort: "30 minutes"
    impact: "Ensures correct reviewers are automatically assigned for PR reviews"
  - title: "Add a LICENSE file"
    effort: "15 minutes"
    impact: "Clarifies usage rights for this public repository"
recommendations:
  priority_0:
    - "Create a GitHub Actions workflow that validates YAML syntax and schema on every PR"
    - "Add an image digest verification step that confirms all referenced digests exist and are pullable"
    - "Enforce branch protection rules requiring at least 1 review approval before merge"
  priority_1:
    - "Define a YAML schema (JSON Schema) for rhoai-disconnected-images.yaml to enforce structure"
    - "Add automated cross-branch consistency checks to detect drift between release branches"
    - "Create agent rules (.claude/rules/) with guidelines for updating image references"
  priority_2:
    - "Add a changelog or release-notes automation to track image reference changes per release"
    - "Implement image vulnerability pre-screening by checking Quay/Red Hat security grades for referenced images"
    - "Add documentation on the disconnected installation workflow this repository supports"
---

# Quality Analysis: rhoai-additional-images

## Executive Summary

- **Overall Score: 1.2/10**
- **Repository Type**: Data-only (YAML image reference list)
- **Primary Language**: None (YAML configuration only)
- **Purpose**: Stores additional RHOAI container image references not tracked in manifests, primarily for disconnected/air-gapped installations

This is an extremely minimal repository containing only a single YAML file (`rhoai-disconnected-images.yaml`) and a README across all 30+ branches. It has **zero code**, **zero tests**, **zero CI/CD**, and **zero automation**. While its simplicity is understandable given its narrow purpose (image reference storage), the complete absence of validation creates real risk — a typo in a SHA256 digest or malformed YAML could break disconnected installations with no automated detection.

- **Key Strengths**: Images pinned by digest (not tag), clear branch-per-release strategy
- **Critical Gaps**: No CI/CD, no YAML validation, no image verification, no agent rules
- **Agent Rules Status**: Missing

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No code exists — YAML-only repository |
| Integration/E2E | 0/10 | No integration or E2E tests |
| **Build Integration** | **0/10** | **No build process of any kind** |
| Image Testing | 1/10 | Digests pinned but never validated |
| Coverage Tracking | 0/10 | No code to cover |
| CI/CD Automation | 2/10 | Branch structure only; no automated checks |
| Agent Rules | 0/10 | No .claude/ directory or agent guidance |

## Critical Gaps

### 1. No YAML Schema Validation on PRs
- **Impact**: Malformed YAML or invalid image references can be merged without detection, potentially breaking disconnected installations
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Evidence**: All 87+ PRs merged with zero automated checks; PR #79 removed images that had to be reverted in PR #80, suggesting manual review alone is insufficient

### 2. No Image Digest Verification
- **Impact**: Referenced image digests could point to non-existent, deleted, or compromised images; failures only surface during customer installation in air-gapped environments
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Evidence**: The YAML file on `rhoai-3.4` references 60+ image digests across `quay.io/modh` and `registry.redhat.io/rhoai` — none are verified to be pullable

### 3. No CI/CD Pipeline
- **Impact**: Zero automated checks on PRs — entirely dependent on human review for correctness
- **Severity**: HIGH
- **Effort**: 2-4 hours to set up basic GitHub Actions
- **Evidence**: No `.github/workflows/` directory exists on any branch

### 4. No Branch Protection or Required Reviews
- **Impact**: PRs can be merged without review, risking accidental data corruption
- **Severity**: MEDIUM
- **Effort**: 1 hour (GitHub settings)

## Quick Wins

### 1. Add YAML Lint Workflow (1-2 hours)
Catches syntax errors and formatting inconsistencies before merge.

```yaml
# .github/workflows/yaml-lint.yml
name: YAML Lint
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: YAML Lint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: '*.yaml'
          config_data: |
            extends: default
            rules:
              line-length:
                max: 256
              document-start: disable
```

### 2. Add Image Digest Existence Check (2-3 hours)
Validates that every referenced image digest is pullable from its registry.

```yaml
# .github/workflows/verify-images.yml
name: Verify Image Digests
on: [pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install skopeo
        run: sudo apt-get install -y skopeo
      - name: Verify digests exist
        run: |
          grep -oP '^\s*-\s+\K\S+@sha256:\S+' rhoai-disconnected-images.yaml | while read img; do
            echo "Checking: $img"
            skopeo inspect --no-tags "docker://$img" > /dev/null 2>&1 || {
              echo "::error::Image not found: $img"
              exit 1
            }
          done
```

### 3. Add CODEOWNERS File (30 minutes)
Ensures correct reviewers are automatically assigned.

```
# CODEOWNERS
* @red-hat-data-services/rhoai-release-team
```

### 4. Add a LICENSE File (15 minutes)
This is a public repository with no license, which creates legal ambiguity.

## Detailed Findings

### CI/CD Pipeline

**Status**: Non-existent

- No `.github/workflows/` directory on any branch (all 30+ branches checked)
- No `Makefile`, `Jenkinsfile`, `.gitlab-ci.yml`, or any CI configuration
- PRs are merged through GitHub UI with manual review only
- 87+ PRs merged to date with zero automation gates
- **Notable incident**: PR #79 (remove 2024.1 images) was immediately reverted by PR #80 (restore required notebook images), suggesting that better validation could have prevented the incorrect removal

### Test Coverage

**Status**: Not applicable (no executable code)

- The repository contains zero executable code — only YAML data files
- No test files of any kind exist (`*_test.go`, `*.spec.ts`, `*.test.py`, etc.)
- No test directories (`test/`, `tests/`, `e2e/`, `integration/`)
- **However**, the YAML data itself is testable:
  - YAML syntax validation
  - Schema conformance checks
  - Image digest format validation (sha256 hex, correct length)
  - Registry reachability checks
  - Cross-branch consistency verification

### Code Quality

**Status**: Minimal

- No linting tools configured (no `.yamllint`, `.pre-commit-config.yaml`, etc.)
- No pre-commit hooks
- No static analysis
- YAML file uses comments to annotate image sources (e.g., `# Corresponds to quay.io/modh/ray:2.52.1-py311-cu121`), which is good practice
- Image references are consistently pinned by `@sha256:` digest rather than mutable tags — this is the single strongest quality practice in the repository

### Container Images

**Status**: Reference-only (no builds)

- This repository does not build images — it references them
- Images are sourced from two registries:
  - `quay.io/modh/` — upstream/community images
  - `registry.redhat.io/rhoai/` — official Red Hat images
- All references use immutable `@sha256:` digests (good practice)
- Categories of referenced images:
  - Ray runtime images (CUDA, ROCm variants)
  - Notebook images (minimal, data science, PyTorch, TensorFlow, TrustyAI)
  - Code Server images
  - FMS HF Tuning images
  - LLM Compressor images
- **Gap**: No verification that these digests are valid, pullable, or free of known CVEs

### Security

**Status**: Non-existent

- No security scanning of any kind
- No dependency scanning (though there are no dependencies)
- No secret detection
- No Trivy/Snyk/CodeQL integration
- No image vulnerability checking for referenced images
- **Risk**: Referenced images could contain known CVEs without detection at the reference-list level
- **Positive**: No secrets to leak — the YAML contains only public image references

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: 
  - No guidelines for how to add or update image references
  - No conventions documented for comment formatting
  - No branch naming or PR title conventions documented
  - No guidance on which images belong in this repo vs. manifests
- **Recommendation**: Create a `CLAUDE.md` with guidelines for updating the YAML file, including:
  - Always use `@sha256:` digests, never tags
  - Add a comment with the human-readable tag for each digest
  - Group images by category (notebooks, runtimes, etc.)
  - Reference the JIRA ticket in PR title

## Recommendations

### Priority 0 (Critical)

1. **Create a GitHub Actions YAML validation workflow** — Validates syntax and schema on every PR. Prevents malformed data from reaching release branches.
2. **Add image digest verification** — Uses `skopeo inspect` to confirm every referenced digest exists and is pullable. Prevents broken references from reaching disconnected installations.
3. **Enable branch protection** — Require at least 1 approved review before merge on all `rhoai-*` branches. Prevents accidental merges of bad data.

### Priority 1 (High Value)

4. **Define a formal YAML schema** — Create a JSON Schema for `rhoai-disconnected-images.yaml` to enforce structure (list of strings, each matching `registry/repo@sha256:hex` format).
5. **Add cross-branch consistency checks** — Automated comparison to detect unintended drift between release branches (e.g., image removed from one branch but not others).
6. **Create agent rules** — `.claude/rules/` with guidelines for modifying the image reference list, including format conventions and validation requirements.
7. **Add CODEOWNERS** — Automatic reviewer assignment for PRs.

### Priority 2 (Nice-to-Have)

8. **Automated changelog generation** — Track which images were added, removed, or updated per release branch.
9. **Image vulnerability pre-screening** — Check Quay/RH security grades for referenced images before accepting a PR.
10. **Documentation** — Add a CONTRIBUTING.md explaining the workflow for updating image references, the relationship to disconnected installations, and the branch strategy.
11. **Add a LICENSE file** — Clarify usage rights for this public repository.

## Comparison to Gold Standards

| Practice | Gold Standard (odh-dashboard) | Gold Standard (notebooks) | rhoai-additional-images |
|----------|-------------------------------|---------------------------|------------------------|
| CI/CD Workflows | 15+ workflows covering lint, test, build, deploy | Multi-stage image testing pipeline | None |
| Unit Tests | Comprehensive Jest/Cypress suite | Python/notebook tests | N/A (no code) |
| Integration Tests | Contract tests, API tests | Multi-framework notebook validation | None |
| E2E Tests | Cypress E2E with multi-browser | Image boot tests across platforms | None |
| Coverage Tracking | Codecov with thresholds | Coverage reports | None |
| Image Testing | N/A | 5-layer image validation | None (images referenced but not validated) |
| Security Scanning | CodeQL, Trivy, Snyk | Trivy scanning | None |
| Agent Rules | Comprehensive .claude/rules/ | Testing guidance docs | None |
| YAML Validation | Schema-validated configs | N/A | None |
| Branch Protection | Required reviews, status checks | Required reviews | Not configured |

## Repository Characteristics

This repository is unusual in that it contains **zero executable code**. It serves as a versioned registry of container image references for RHOAI disconnected/air-gapped installations. Key characteristics:

- **30+ branches** spanning RHOAI versions 2.11 through 3.5-ea.1
- **Single YAML file** per branch listing image digests
- **87+ merged PRs** to date, all manually reviewed
- **Active maintenance** — most recent PR merged May 14, 2026
- **Contributors** primarily update image SHA digests as new versions are released
- **No build artifacts** — this repo is consumed by other tools/processes that mirror images for disconnected environments

## File Paths Reference

| File | Location | Purpose |
|------|----------|---------|
| `README.md` | Root | Repository description (1 line) |
| `rhoai-disconnected-images.yaml` | Root | Image reference list |
| `.github/workflows/` | Missing | No CI/CD configuration |
| `CLAUDE.md` | Missing | No agent rules |
| `CODEOWNERS` | Missing | No automatic reviewer assignment |
| `LICENSE` | Missing | No license file |
| `CONTRIBUTING.md` | Missing | No contribution guidelines |
