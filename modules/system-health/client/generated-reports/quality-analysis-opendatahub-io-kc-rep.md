---
repository: "opendatahub-io/kc-rep"
overall_score: 1.5
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No tests of any kind exist in this repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests; no Tekton YAML validation"
  - dimension: "Build Integration"
    score: 2.0
    status: "Replicator workflow exists but only covers 2/26 components"
  - dimension: "Image Testing"
    score: 1.0
    status: "No image testing; repo stores configs for other repos' builds"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling of any kind"
  - dimension: "CI/CD Automation"
    score: 2.0
    status: "Manual-dispatch replicator workflow, severely incomplete component coverage"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "No YAML schema validation for Tekton PipelineRun configs"
    impact: "Invalid or broken pipeline configs can be merged without any validation, causing Konflux build failures across 22+ ODH repositories"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Replicator workflow covers only 2 of 26 components"
    impact: "24 components cannot use automated Tekton file replication; manual updates are error-prone and inconsistent"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "Task bundle version drift across pipelines"
    impact: "Pipelines use different SHA digests for the same task versions (e.g., buildah-oci-ta:0.4 has 2 different digests), causing inconsistent build behavior"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No PR-triggered pipelines or checks"
    impact: "All changes are merged without any CI validation; broken configs are only discovered when Konflux runs the pipeline in a target repo"
    severity: "HIGH"
    effort: "6-8 hours"
  - title: "Zero tests in the repository"
    impact: "No confidence that pipeline configs are correct, consistent, or will work when replicated"
    severity: "HIGH"
    effort: "8-12 hours"
quick_wins:
  - title: "Add all 26 component folders to the replicator workflow choices"
    effort: "30 minutes"
    impact: "Enable automated Tekton file replication for all components instead of just 2"
  - title: "Add YAML lint CI check on PRs"
    effort: "1-2 hours"
    impact: "Catch syntax errors in Tekton pipeline YAML before merge"
  - title: "Add a version-consistency check script"
    effort: "2-3 hours"
    impact: "Detect and alert on task bundle version drift across pipelines"
  - title: "Add a CODEOWNERS file"
    effort: "30 minutes"
    impact: "Ensure pipeline config changes are reviewed by the right teams"
recommendations:
  priority_0:
    - "Add PR-triggered CI with YAML schema validation against the Tekton PipelineRun CRD schema"
    - "Complete the replicator workflow to cover all 26 components"
    - "Standardize task bundle versions across all pipelines to eliminate version drift"
  priority_1:
    - "Add automated version-drift detection that flags inconsistent task bundle SHA digests"
    - "Create a dry-run validation pipeline that tests Tekton configs before merge"
    - "Add comprehensive documentation covering component inventory, update procedures, and troubleshooting"
  priority_2:
    - "Add agent rules (.claude/rules/) for maintaining Tekton pipeline consistency"
    - "Implement automated nudge workflow that creates PRs when new task bundle versions are released"
    - "Add PR-triggered pipeline that validates replication would succeed for each component"
---

# Quality Analysis: kc-rep (odh-konflux-central)

## Executive Summary

- **Overall Score: 1.5/10**
- **Repository Type**: Infrastructure-as-Code (IaC) — centralized Konflux/Tekton build configuration
- **Languages**: YAML (Tekton PipelineRun definitions), Shell (GitHub Actions workflow)
- **Key Strengths**: Comprehensive security scanning tasks within pipeline definitions (11 security/quality tasks per pipeline), centralized management of 26 ODH components, SBOM generation
- **Critical Gaps**: Zero tests, zero validation, incomplete automation (2/26 components), task bundle version drift, no PR checks
- **Agent Rules Status**: Missing — no CLAUDE.md, .claude/, or AGENTS.md

## Repository Overview

`kc-rep` (odh-konflux-central) is a central repository storing Konflux/Tekton PipelineRun configurations for 26 OpenDataHub components. It is **not a source code repository** — it contains only YAML pipeline definitions that are replicated to target component repositories for Konflux CI/CD builds.

### Component Inventory

| # | Component | Tekton Files | Target Repository |
|---|-----------|-------------|-------------------|
| 1 | caikit-nlp | 1 | opendatahub-io/caikit-nlp |
| 2 | codeflare-operator | 1 | opendatahub-io/codeflare-operator |
| 3 | data-science-pipelines | 5 | opendatahub-io/data-science-pipelines |
| 4 | data-science-pipelines-operator | 1 | opendatahub-io/data-science-pipelines-operator |
| 5 | fms-guardrails-hf-detector | 1 | opendatahub-io/guardrails-detectors |
| 6 | fms-guardrails-orchestrator | 1 | opendatahub-io/fms-guardrails-orchestrator |
| 7 | fms-guardrails-regex-detector | 1 | opendatahub-io/guardrails-regex-detector |
| 8 | kserve-agent | 1 | opendatahub-io/kserve |
| 9 | kserve-controller | 1 | opendatahub-io/kserve |
| 10 | kserve-router | 1 | opendatahub-io/kserve |
| 11 | kubeflow | 2 | opendatahub-io/kubeflow |
| 12 | kuberay | 1 | opendatahub-io/kuberay |
| 13 | kueue | 1 | opendatahub-io/kueue |
| 14 | ml-metadata | 1 | opendatahub-io/ml-metadata |
| 15 | modelmesh | 1 | opendatahub-io/modelmesh |
| 16 | modelmesh-runtime-adapter | 1 | opendatahub-io/modelmesh-runtime-adapter |
| 17 | modelmesh-serving | 1 | opendatahub-io/modelmesh-serving |
| 18 | odh-dashboard | 1 | opendatahub-io/odh-dashboard |
| 19 | odh-feast-operator | 1 | opendatahub-io/feast |
| 20 | odh-feature-server | 1 | opendatahub-io/feast |
| 21 | odh-model-controller | 1 | opendatahub-io/odh-model-controller |
| 22 | odh-model-registry-operator | 1 | opendatahub-io/model-registry-operator |
| 23 | rest-proxy | 1 | opendatahub-io/rest-proxy |
| 24 | ta-lmes-driver | 1 | opendatahub-io/trustyai-service-operator |
| 25 | training-operator | 1 | opendatahub-io/training-operator |
| 26 | trustyai-vllm-orchestrator-gateway | 1 | opendatahub-io/vllm-orchestrator-gateway |

**Total**: 26 components, 31 Tekton PipelineRun YAML files, 22 unique target repositories

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No tests of any kind exist |
| Integration/E2E | 0/10 | No integration or E2E tests; no Tekton YAML validation |
| **Build Integration** | **2/10** | **Replicator workflow exists but only covers 2/26 components** |
| Image Testing | 1/10 | No image testing; repo stores configs for other repos' builds |
| Coverage Tracking | 0/10 | No coverage tooling of any kind |
| CI/CD Automation | 2/10 | Manual-dispatch replicator, severely incomplete |
| Agent Rules | 0/10 | No CLAUDE.md, .claude/, or AGENTS.md |

### Pipeline Content Quality (Bonus Assessment)

While the repository itself scores poorly, the **content** of the Tekton pipeline definitions is well-structured. Each pipeline includes 11 security/quality tasks:

| Security Task | Purpose |
|--------------|---------|
| clair-scan | Container vulnerability scanning |
| sast-snyk-check | Static application security testing (Snyk) |
| sast-coverity-check | Static analysis (Coverity) |
| sast-shell-check | Shell script security analysis |
| sast-unicode-check | Unicode homoglyph attack detection |
| clamav-scan | Malware scanning |
| rpms-signature-scan | RPM package signature validation |
| deprecated-image-check | Base image deprecation detection |
| ecosystem-cert-preflight-checks | Red Hat certification preflight |
| show-sbom | Software Bill of Materials generation |
| coverity-availability-check | Coverity service availability gate |

## Critical Gaps

### 1. No YAML Schema Validation for Tekton Configs
- **Severity**: HIGH
- **Impact**: Invalid or broken pipeline configs can be merged without any validation, causing Konflux build failures across 22+ ODH repositories
- **Effort**: 4-6 hours
- **Details**: There are no PR checks of any kind. A typo in a task reference, a missing parameter, or an invalid CEL expression would only be caught when Konflux attempts to run the pipeline in the target repository.

### 2. Replicator Workflow Covers Only 2 of 26 Components
- **Severity**: HIGH
- **Impact**: 24 components cannot use automated Tekton file replication; updates to those components require manual file copying and PR creation
- **Effort**: 1-2 hours (add remaining folders to the choice list)
- **Details**: The `okc-replicator.yml` workflow has a `type: choice` dropdown with only 2 options: `data-science-pipelines` and `odh-model-controller`. A comment reads `# Add all valid folder names here`, indicating this was known but never completed.

### 3. Task Bundle Version Drift
- **Severity**: HIGH
- **Impact**: Different pipelines use different SHA digests for the same task version, causing inconsistent build and security scanning behavior across components
- **Effort**: 4-8 hours
- **Examples**:
  - `buildah-oci-ta:0.4` has 2 different SHA digests
  - `clair-scan:0.2` has 2 different SHA digests
- **Root Cause**: No automated version management or consistency checking

### 4. No PR-Triggered Pipelines or Checks
- **Severity**: HIGH
- **Impact**: All Tekton pipeline configs are push-triggered only (`event == "push" && target_branch == "konflux-poc"`). Changes to this repo have no PR checks, no linting, no validation before merge.
- **Effort**: 6-8 hours

### 5. Zero Tests
- **Severity**: HIGH
- **Impact**: No confidence that pipeline configs are correct, will parse properly, or will work when replicated to target repos
- **Effort**: 8-12 hours

### 6. Minimal Documentation
- **Severity**: MEDIUM
- **Impact**: The README is a single line: "odh-konflux-central - To centrally store the Konflux configuration for all the components". No documentation on how to add a new component, update versions, use the replicator, or troubleshoot issues.
- **Effort**: 4-6 hours

## Quick Wins

### 1. Complete the Replicator Workflow Choices (30 minutes)
Add all 26 component folders to the `okc-replicator.yml` choice list:

```yaml
options:
  - caikit-nlp
  - codeflare-operator
  - data-science-pipelines
  - data-science-pipelines-operator
  - fms-guardrails-hf-detector
  - fms-guardrails-orchestrator
  - fms-guardrails-regex-detector
  - kserve-agent
  - kserve-controller
  - kserve-router
  - kubeflow
  - kuberay
  - kueue
  - ml-metadata
  - modelmesh
  - modelmesh-runtime-adapter
  - modelmesh-serving
  - odh-dashboard
  - odh-feast-operator
  - odh-feature-server
  - odh-model-controller
  - odh-model-registry-operator
  - rest-proxy
  - ta-lmes-driver
  - training-operator
  - trustyai-vllm-orchestrator-gateway
```

### 2. Add YAML Lint CI Check (1-2 hours)
Create `.github/workflows/lint.yml`:

```yaml
name: Lint Tekton YAML
on:
  pull_request:
    paths: ['**/.tekton/*.yaml']

jobs:
  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install yamllint
        run: pip install yamllint
      - name: Lint Tekton YAML files
        run: |
          find . -path '*/.tekton/*.yaml' | xargs yamllint -c .yamllint.yml
```

### 3. Add Version Consistency Check Script (2-3 hours)
Create a script that extracts all task bundle references, groups by task name, and flags where different SHA digests are used for the same task version:

```bash
#!/bin/bash
# check-version-consistency.sh
echo "Checking task bundle version consistency..."
grep -rh 'value: quay.io/konflux-ci/tekton-catalog/' */.tekton/*.yaml \
  | sed 's/.*value: //' | sort | uniq -c | sort -rn \
  | awk '{if ($1 > 1) print "OK: "$2; else print "DRIFT: "$2}'
```

### 4. Add CODEOWNERS File (30 minutes)
```
# Pipeline configurations
*/.tekton/ @opendatahub-io/konflux-admins
.github/ @opendatahub-io/konflux-admins
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory**:
- 1 workflow: `okc-replicator.yml` (manual dispatch only)
- **No PR-triggered workflows**
- **No scheduled/periodic workflows**
- **No automated validation**

**Replicator Workflow Analysis**:
- **Trigger**: `workflow_dispatch` (manual only)
- **Function**: Copies `.tekton/` files from this repo to a target repo, updates `output-image` version tags, and creates a PR
- **Permissions**: Write access to contents, pull-requests, repository-projects
- **Authentication**: Uses `getsentry/action-github-app-token` with ODH DevOps app credentials
- **Critical Issue**: Only 2 of 26 components are available in the dropdown (`data-science-pipelines`, `odh-model-controller`)
- **Missing**: Error handling for version tag replacement, validation of target repo existence, notification on failure

### Test Coverage

**Status**: No tests exist.

For an IaC/configuration repository, expected tests would include:
- YAML syntax validation
- Tekton PipelineRun schema validation
- Task bundle reference resolution checks
- Version consistency checks
- CEL expression validation
- Parameter completeness validation
- Replicator workflow tests (dry-run)

### Code Quality

**Status**: No quality tools configured.

- No YAML linting (yamllint, prettier)
- No schema validation (kubeconform, kubeval for Tekton CRDs)
- No pre-commit hooks
- No Makefile with quality targets
- No editor configuration (.editorconfig)

### Container Images

**Status**: Not applicable — this repo does not build images.

The repo stores Tekton pipeline configs that define how OTHER repositories build images. The pipeline definitions themselves include:
- `buildah-oci-ta` for image building
- `build-image-index` for multi-arch image index
- `source-build-oci-ta` for source image generation
- `push-dockerfile-oci-ta` for Dockerfile archival

### Security

**In-pipeline security** (defined in Tekton configs): Excellent — 11 security tasks per pipeline.

**Repository-level security**: None.
- No Dependabot/Renovate for action version updates
- No secret scanning
- No branch protection validation
- No signed commits requirement
- The `getsentry/action-github-app-token` action is pinned to `v2` (tag only, no SHA pin)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: No guidance for AI agents on how to maintain pipeline consistency, add new components, or update versions
- **Recommendation**: Generate rules with `/test-rules-generator` covering:
  - Pipeline template structure
  - Required security tasks checklist
  - Version consistency requirements
  - Naming conventions for components and pipelines

## Recommendations

### Priority 0 (Critical)

1. **Add PR-triggered CI with YAML validation** — Create a workflow that runs on PRs to validate Tekton YAML syntax, schema compliance, and parameter completeness. This is the single highest-impact improvement.

2. **Complete the replicator workflow** — Add all 26 component folders to the choice list. This is a 30-minute fix that unlocks automation for 24 currently-manual components.

3. **Standardize task bundle versions** — Create a central version manifest and a script/workflow that ensures all pipelines use the same task bundle SHA digests. Currently `buildah-oci-ta:0.4` and `clair-scan:0.2` each have 2 different SHA digests.

### Priority 1 (High Value)

4. **Add automated version-drift detection** — A scheduled workflow that checks for inconsistent task bundle versions and opens issues or PRs to standardize them.

5. **Create comprehensive documentation** — Document the component inventory, how to add a new component, how to update versions, how to use the replicator, and troubleshooting common issues.

6. **Pin GitHub Actions to SHA digests** — The replicator workflow uses `actions/checkout@v4` and `getsentry/action-github-app-token@v2` (tag-only). Pin to full SHA for supply chain security.

### Priority 2 (Nice-to-Have)

7. **Add agent rules** — Create `.claude/rules/` with guidance for maintaining Tekton pipeline consistency, adding new components, and version management.

8. **Implement automated task bundle updates** — A Renovate/Dependabot-like workflow that creates PRs when new Konflux task bundle versions are released.

9. **Add a `Makefile` with common targets** — `make lint`, `make validate`, `make check-versions`, `make replicate COMPONENT=x VERSION=y`.

10. **Add templating** — Consider using Kustomize, Helm, or a simple script to generate pipeline YAMLs from a template, reducing duplication across 31 files and ensuring consistency.

## Comparison to Gold Standards

| Practice | kc-rep | odh-dashboard | notebooks | kserve |
|----------|--------|---------------|-----------|--------|
| PR CI checks | None | Comprehensive | Comprehensive | Comprehensive |
| Test coverage | 0% | High | High | High |
| YAML validation | None | N/A | N/A | N/A |
| Version management | Manual | Automated | Automated | Automated |
| Documentation | 1-line README | Extensive | Extensive | Extensive |
| Security scanning | None (repo-level) | Integrated | Integrated | Integrated |
| Pre-commit hooks | None | Configured | Configured | Configured |
| Agent rules | None | Present | None | None |
| Pipeline security tasks | 11 tasks/pipeline | N/A | 5-layer validation | N/A |
| Automation coverage | 2/26 components | Full | Full | Full |

**Note**: The gold standard comparison is less direct here since kc-rep is an IaC config repo, not a source code repo. The comparison highlights the gap in quality practices that should apply to ANY repository.

## File Paths Reference

| File | Purpose |
|------|---------|
| `.github/workflows/okc-replicator.yml` | Replicates Tekton files to target repos (manual dispatch) |
| `*/. tekton/*-push.yaml` | Tekton PipelineRun definitions (31 files across 26 components) |
| `README.md` | Single-line repository description |

## Key Risk: Version Drift Evidence

```
buildah-oci-ta:0.4 — 2 different SHA digests:
  sha256:6ac9d16f...  (some pipelines)
  sha256:b91b634c...  (other pipelines)

clair-scan:0.2 — 2 different SHA digests:
  sha256:7c73e2be...  (some pipelines)
  sha256:878ae247...  (other pipelines)
```

This means different ODH components will get different build and security scanning behavior depending on which SHA digest their pipeline uses, even though they all reference the same task version number.
