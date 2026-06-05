---
repository: "opendatahub-io/ODH-Build-Config"
overall_score: 2.8
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No source code or unit tests — this is a pure configuration/manifest repository"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "Enterprise Contract integration test exists but is narrowly scoped to FBC fragment only"
  - dimension: "Build Integration"
    score: 5.0
    status: "Konflux Tekton pipelines for bundle and catalog builds on PR and push, but no manifest validation"
  - dimension: "Image Testing"
    score: 2.0
    status: "Dockerfiles build FROM scratch and ose-operator-registry; no runtime validation or scanning"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tracking — no source code to cover"
  - dimension: "CI/CD Automation"
    score: 6.0
    status: "Robust GitHub Actions + Tekton/Konflux pipeline integration with auto-merge and schedulers"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "No manifest validation on PRs"
    impact: "Malformed CRDs, CSV errors, or invalid catalog YAML can merge without detection, breaking operator installation"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No OLM bundle validation in CI"
    impact: "Bundle scorecard tests exist in config but are never executed in any workflow or Tekton pipeline"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning for container images"
    impact: "Vulnerability-laden base images or dependencies can ship without detection"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Skip-checks enabled on FBC catalog builds"
    impact: "FBC fragment Tekton pipelines explicitly set skip-checks: true and skip-fips: true, bypassing Konflux security and FIPS compliance checks"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No YAML schema validation for patch files"
    impact: "Malformed bundle-patch.yaml or catalog-patch.yaml can cause silent failures in downstream processing"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Insta-merge bypasses all quality gates"
    impact: "Bot PRs from Konflux are auto-merged with minimal feasibility check (title regex only), no content validation"
    severity: "MEDIUM"
    effort: "6-8 hours"
quick_wins:
  - title: "Add YAML lint validation to PR workflow"
    effort: "1-2 hours"
    impact: "Catch malformed YAML in bundle manifests, patches, and catalog configurations before merge"
  - title: "Run operator-sdk bundle validate on PRs"
    effort: "2-3 hours"
    impact: "Validate OLM bundle structure, CRD schemas, and CSV completeness using the existing scorecard config"
  - title: "Remove skip-checks: true from FBC Tekton pipelines"
    effort: "1 hour"
    impact: "Re-enable Konflux security and FIPS compliance checks for catalog builds"
  - title: "Add Trivy scan for Dockerfile base images"
    effort: "2-3 hours"
    impact: "Detect vulnerabilities in ose-operator-registry and scratch-based bundle images"
recommendations:
  priority_0:
    - "Add OLM bundle validation (operator-sdk bundle validate) to PR workflows to catch CSV, CRD, and metadata errors"
    - "Remove skip-checks and skip-fips flags from FBC Tekton pipeline configurations to restore security compliance gates"
    - "Add YAML schema validation for bundle-patch.yaml, catalog-patch.yaml, and build-config.yaml"
  priority_1:
    - "Add Trivy or similar vulnerability scanning for built container images (bundle and FBC fragment)"
    - "Validate catalog.yaml with opm validate before committing auto-generated catalog changes"
    - "Add content validation to insta-merge workflows beyond title regex matching"
    - "Create Enterprise Contract integration test for the bundle component, not just the FBC fragment"
  priority_2:
    - "Add agent rules (.claude/rules/) for manifest editing patterns and YAML configuration standards"
    - "Add SBOM generation for bundle and catalog images"
    - "Add Kustomize build validation for bundle manifests"
    - "Implement image signing and attestation for built artifacts"
---

# Quality Analysis: ODH-Build-Config

## Executive Summary

- **Overall Score: 2.8/10**
- **Repository Type**: Configuration/Manifest repository (operator bundle + FBC catalog management)
- **Primary Purpose**: Manages the OpenDataHub/RHOAI operator bundle CSV, CRD manifests, FBC (File-Based Catalog) fragments, and automated build pipelines via Konflux/Tekton
- **Key Strengths**: Well-structured CI/CD automation with GitHub Actions + Tekton/Konflux integration, auto-sync from upstream operator, Mergify-powered merge queues
- **Critical Gaps**: No manifest validation on PRs, OLM scorecard tests configured but never executed, security checks explicitly skipped in Tekton pipelines, no content validation on auto-merged PRs
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No source code — pure config/manifest repo |
| Integration/E2E | 2/10 | Single Enterprise Contract test for FBC fragment only |
| **Build Integration** | **5/10** | **Konflux Tekton builds on PR/push but no manifest validation** |
| Image Testing | 2/10 | Dockerfiles exist but no runtime validation or scanning |
| Coverage Tracking | 0/10 | N/A — no source code to cover |
| CI/CD Automation | 6/10 | Robust automation pipeline but quality gates are weak |
| Agent Rules | 0/10 | No AI agent guidance |

## Critical Gaps

### 1. No Manifest Validation on PRs
- **Impact**: Malformed CRDs, CSV errors, or invalid catalog YAML can merge undetected, breaking operator installation on customer clusters
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The repository contains 24+ CRD manifests, a complex CSV (2816 lines), and catalog configurations — none are validated on PR. The `bundle/tests/scorecard/config.yaml` defines 6 OLM scorecard tests (basic-check-spec, olm-bundle-validation, olm-crds-have-validation, olm-crds-have-resources, olm-spec-descriptors, olm-status-descriptors) but these are **never executed** in any workflow or pipeline.

### 2. Security Checks Explicitly Skipped
- **Impact**: FBC fragment builds bypass Konflux security and FIPS compliance verification
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Both FBC Tekton pipelines (`odh-fbc-fragment-ci-pull-request.yaml` and `odh-fbc-fragment-ci-push.yaml`) set `skip-checks: true` and `skip-fips: true`. This effectively disables Konflux's built-in security scanning and FIPS compliance checks for the catalog images.

### 3. Insta-Merge with Minimal Validation
- **Impact**: Bot-generated PRs from Konflux are auto-merged based solely on PR title regex matching, with no content validation
- **Severity**: MEDIUM
- **Effort**: 6-8 hours
- **Details**: The `bundle-insta-merge.yaml` and `fbc-insta-merge.yaml` workflows auto-merge PRs from `red-hat-konflux[bot]` if the title matches `^Update.*-ci.* to [0-9a-z]{1,40}$`. The merge feasibility check only verifies the title format and that only expected files changed — there's no validation of the YAML content being merged.

### 4. No Image Vulnerability Scanning
- **Impact**: Vulnerabilities in base images or dependencies ship without detection
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The bundle Dockerfile uses `FROM scratch` (minimal surface area, good) but the FBC catalog Dockerfile uses `FROM registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20` — a substantial image with no vulnerability scanning configured.

### 5. No YAML Schema Validation
- **Impact**: Malformed patch files can cause silent failures in downstream bundle/catalog processing
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: `bundle-patch.yaml` (348 lines, 80+ related images), `catalog-patch.yaml`, `build-config.yaml`, and `additional-images-patch.yaml` are critical configuration files with no schema validation. Errors in these files propagate through the entire build pipeline.

## Quick Wins

### 1. Add YAML Lint Validation (1-2 hours)
Add `yamllint` to the PR workflow to catch syntax errors in all YAML files:
```yaml
- name: Lint YAML files
  uses: ibiqlik/action-yamllint@v3
  with:
    file_or_dir: bundle/ catalog/ config/
    config_data: |
      extends: default
      rules:
        line-length: {max: 500}
        document-start: disable
```

### 2. Run OLM Bundle Validation (2-3 hours)
Execute the existing scorecard tests that are configured but never run:
```yaml
- name: Validate OLM bundle
  run: |
    operator-sdk bundle validate ./bundle --select-optional suite=basic
    operator-sdk bundle validate ./bundle --select-optional suite=olm
```

### 3. Remove skip-checks from FBC Pipelines (1 hour)
In both `.tekton/odh-fbc-fragment-ci-*.yaml` files, change:
```yaml
- name: skip-checks
  value: false   # was: true
- name: skip-fips
  value: false   # was: true
```

### 4. Add Trivy Scan for Base Images (2-3 hours)
```yaml
- name: Scan FBC base image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20
    severity: CRITICAL,HIGH
    exit-code: 1
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (7 GitHub Actions + 4 Tekton Pipelines)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `bundle-sync.yml` | Schedule (every 2h) + dispatch | Sync bundle from opendatahub-operator stable branch |
| `process-operator-bundle.yaml` | Push to bundle paths on main | Process and patch the operator bundle CSV |
| `process-fbc-fragment.yaml` | Push to catalog-patch.yaml on main | Generate FBC catalog from templates |
| `bundle-insta-merge.yaml` | PR opened (Konflux bot) | Auto-merge bundle nudge PRs |
| `fbc-insta-merge.yaml` | PR opened (Konflux bot) | Auto-merge FBC nudge PRs |
| `trigger-nightly-bundle-build.yaml` | Dispatch only | Nightly bundle build for release branches |
| `trigger-nightly-fbc-build.yaml` | Dispatch only | Nightly FBC build with PCC cache management |

| Tekton Pipeline | Trigger | Purpose |
|----------------|---------|---------|
| `odh-operator-bundle-ci-pull-request.yaml` | PR (label/comment) | Build bundle image for PR validation |
| `odh-operator-bundle-ci-push.yaml` | Push to main (bundle changes) | Build and push bundle image |
| `odh-fbc-fragment-ci-pull-request.yaml` | PR (label/comment) | Build FBC catalog image for PR validation |
| `odh-fbc-fragment-ci-push.yaml` | Push to main (catalog changes) | Build and push FBC catalog image |

**Strengths**:
- Good separation of concerns between GitHub Actions (processing) and Tekton (building)
- Tekton PR pipelines are triggered on-demand via labels (`build-bundle`, `build-catalog`, `build-all`) and comments (`/build-konflux bundle`, `/build-konflux catalog`), reducing unnecessary builds
- Cancel-in-progress enabled for PR pipelines, preventing resource waste
- Push pipelines use CEL expressions for precise path-based triggering
- Slack failure notifications enabled on push pipelines
- Build nudge notification configured via `build.appstudio.openshift.io/build-nudge-files`

**Weaknesses**:
- No PR-triggered validation workflows for YAML content — PR checks rely solely on Tekton builds
- GitHub Actions workflows use mixed checkout action versions (pinned sha vs v4)
- Bundle sync uses `actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd` (pinned to specific SHA) while others use `@v4` — inconsistent versioning
- No caching strategies in any workflow

### Test Coverage

**Unit Tests**: N/A — This repository contains zero source code files (no `.py`, `.go`, `.sh`, `.ts`, or `.js` files). All logic lives in external repositories (`RHOAI-Konflux-Automation`, `opendatahub-operator`).

**Integration Tests**: 
- Single Enterprise Contract (EC) test defined in `integration-tests/integration-test.yaml`
- Scoped only to the FBC fragment component (`rhoai-fbc-fragment-v2-17`)
- Uses `appstudio.redhat.com/v1beta2` IntegrationTestScenario
- References `POLICY_CONFIGURATION: rhoai-tenant/registry-rhoai-prod` for policy enforcement
- **Gap**: No equivalent EC test for the operator bundle component

**OLM Scorecard Tests**:
- `bundle/tests/scorecard/config.yaml` defines 6 scorecard tests:
  1. `basic-check-spec` (v1.31.0)
  2. `olm-bundle-validation` (v1.24.1)
  3. `olm-crds-have-validation` (v1.24.1)
  4. `olm-crds-have-resources` (v1.24.1)
  5. `olm-spec-descriptors` (v1.24.1)
  6. `olm-status-descriptors` (v1.24.1)
- **These tests are never executed** — they exist only as configuration for potential manual runs

### Code Quality

- **No linting tools**: No YAML linters, no pre-commit hooks, no static analysis
- **No `.pre-commit-config.yaml`**: No automated formatting or validation on commit
- **No secret detection**: No gitleaks, trufflehog, or similar tools despite the repo containing image references with registry credentials patterns
- **Mergify configured**: Two mergify files (`.mergify.yml` and `mergify.yml`) provide merge queue management with approval requirements and stale PR cleanup
- **CODEOWNERS**: Well-defined with 6 trusted reviewers for all paths

### Container Images

**Bundle Image** (`bundle/Dockerfile`):
- `FROM scratch` — minimal attack surface (good)
- Copies manifests, metadata, and scorecard tests
- Proper OLM labels for bundle discovery
- Build-time ARGs for traceability (git URL, commit, image, build metadata URL)
- Multi-architecture labels: amd64, ppc64le, s390x, arm64

**FBC Catalog Image** (`catalog/v4.20/Dockerfile`):
- `FROM registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20` — substantial base image
- Properly configured entrypoint with `opm serve`
- Cache pre-population with `opm serve --cache-only` (good for startup time)
- No vulnerability scanning configured
- x86_64 platform only (single arch)

**Gaps**:
- No multi-stage builds (bundle is FROM scratch which is appropriate, catalog doesn't need multi-stage)
- No image signing or attestation
- No SBOM generation
- FBC pipeline explicitly skips security checks

### Security

- **No SAST/CodeQL**: N/A (no source code)
- **No container scanning**: No Trivy, Snyk, or Grype integration
- **No secret detection**: No gitleaks or similar
- **FIPS compliance skipped**: Both FBC Tekton pipelines set `skip-fips: true`
- **Security checks skipped**: Both FBC Tekton pipelines set `skip-checks: true`
- **Credential handling**: Workflows use GitHub Actions secrets appropriately but have inline credential construction (base64 auth tokens in workflow scripts)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No agent rules whatsoever
- **Quality**: N/A
- **Gaps**: 
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory
  - No `.claude/rules/` for manifest editing patterns
  - No documentation on YAML configuration standards for AI agents
- **Recommendation**: Generate rules for YAML manifest editing, patch file structure, bundle validation requirements, and catalog configuration patterns using `/test-rules-generator`

## Recommendations

### Priority 0 (Critical)

1. **Add OLM bundle validation to PR workflows**
   - Execute the existing scorecard tests that are already configured in `bundle/tests/scorecard/config.yaml`
   - Add `operator-sdk bundle validate ./bundle` as a required PR check
   - Validates CRD schemas, CSV completeness, and metadata correctness

2. **Re-enable security checks in FBC Tekton pipelines**
   - Remove `skip-checks: true` and `skip-fips: true` from both FBC pipeline definitions
   - These flags bypass Konflux's built-in security and FIPS compliance verification
   - Critical for a component that ships as part of the Red Hat product

3. **Add YAML schema validation for critical config files**
   - Create JSON schemas for `bundle-patch.yaml`, `catalog-patch.yaml`, and `build-config.yaml`
   - Validate on PR to catch malformed image references, version strings, and structural errors
   - Especially important given the ~80+ related image entries in `bundle-patch.yaml`

### Priority 1 (High Value)

4. **Add container image vulnerability scanning**
   - Integrate Trivy or Grype for the FBC catalog base image
   - Scan the built bundle image for any embedded vulnerabilities
   - Set severity thresholds to fail builds on CRITICAL/HIGH findings

5. **Add opm validate for catalog YAML**
   - Run `opm validate` on generated catalog.yaml files before committing
   - The nightly FBC build already runs `catalog_validator.py` — extend this to CI

6. **Content validation for auto-merged PRs**
   - Beyond the title regex in insta-merge workflows, validate:
     - YAML syntax of changed files
     - Image reference format (registry/org/repo@sha256:...)
     - No unexpected file changes beyond the allowed paths

7. **Create Enterprise Contract test for bundle component**
   - The existing EC test only covers the FBC fragment
   - Add equivalent test for `odh-operator-bundle-ci` component

### Priority 2 (Nice-to-Have)

8. **Add agent rules for manifest management**
   - Create `.claude/rules/` with patterns for:
     - Adding new related images to `bundle-patch.yaml`
     - Updating CRD manifests
     - Modifying catalog configurations
     - YAML formatting standards

9. **Add SBOM generation**
   - Generate SBOM for both bundle and catalog images
   - Required for supply chain security compliance

10. **Standardize GitHub Actions checkout versions**
    - Some workflows use pinned SHA, others use `@v4`
    - Standardize to pinned SHA for reproducibility

11. **Add image signing and attestation**
    - Implement cosign signing for built artifacts
    - Required for increasing supply chain security requirements

## Comparison to Gold Standards

| Dimension | ODH-Build-Config | odh-dashboard | notebooks | kserve |
|-----------|-----------------|---------------|-----------|--------|
| Unit Tests | N/A (config repo) | Comprehensive Jest suite | N/A (image repo) | Go test + envtest |
| Integration/E2E | 1 EC test (FBC only) | Multi-layer E2E | Image validation | Multi-version E2E |
| Build Integration | Konflux builds, no validation | PR-time build + test | 5-layer validation | PR-time integration |
| Image Testing | No runtime validation | N/A | Startup + functional | N/A |
| Coverage Tracking | None | Codecov enforcement | N/A | Codecov enforcement |
| CI/CD Automation | GHA + Tekton, weak gates | Comprehensive, multi-stage | Automated matrix | Prow + GHA |
| Security Scanning | **Explicitly skipped** | CodeQL + dependency scan | Trivy scanning | CodeQL + Trivy |
| Agent Rules | None | Comprehensive | Basic | None |
| YAML Validation | None | ESLint + prettier | N/A | golangci-lint |

## File Paths Reference

### CI/CD
- `.github/workflows/bundle-sync.yml` — Upstream bundle sync (every 2h)
- `.github/workflows/process-operator-bundle.yaml` — Bundle CSV patching
- `.github/workflows/process-fbc-fragment.yaml` — FBC catalog generation
- `.github/workflows/bundle-insta-merge.yaml` — Auto-merge bundle nudges
- `.github/workflows/fbc-insta-merge.yaml` — Auto-merge FBC nudges
- `.github/workflows/trigger-nightly-bundle-build.yaml` — Nightly bundle build
- `.github/workflows/trigger-nightly-fbc-build.yaml` — Nightly FBC build

### Tekton/Konflux
- `.tekton/odh-operator-bundle-ci-pull-request.yaml` — PR bundle build
- `.tekton/odh-operator-bundle-ci-push.yaml` — Push bundle build
- `.tekton/odh-fbc-fragment-ci-pull-request.yaml` — PR FBC build
- `.tekton/odh-fbc-fragment-ci-push.yaml` — Push FBC build

### Bundle
- `bundle/Dockerfile` — Bundle container build
- `bundle/bundle-patch.yaml` — Related image patches (80+ images)
- `bundle/csv-patch.yaml` — CSV metadata patches
- `bundle/additional-images-patch.yaml` — Non-ODH related images
- `bundle/manifests/rhods-operator.clusterserviceversion.yaml` — Main CSV (2816 lines)
- `bundle/tests/scorecard/config.yaml` — OLM scorecard tests (configured but never run)

### Catalog
- `catalog/v4.20/Dockerfile` — FBC catalog container build
- `catalog/v4.20/rhods-operator/catalog.yaml` — Generated catalog
- `catalog/catalog-patch.yaml` — Catalog patches
- `catalog/catalog_build_args.map` — Build arguments

### Configuration
- `config/build-config.yaml` — Build configuration (OCP versions, base images)
- `.mergify.yml` / `mergify.yml` — Merge queue rules
- `integration-tests/integration-test.yaml` — Enterprise Contract test (FBC only)
- `CODEOWNERS` — Review requirements
- `OWNERS` — Prow approval config
