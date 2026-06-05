---
repository: "red-hat-data-services/odh-manifests"
overall_score: 2.4
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No unit tests exist — repo contains only Kustomize manifests with zero test code files"
  - dimension: "Integration/E2E"
    score: 4.0
    status: "15 bash-based smoke tests validate component deployments on live OpenShift clusters via OpenShift-CI"
  - dimension: "Build Integration"
    score: 1.5
    status: "No PR-time CI workflows — no kustomize build validation, no manifest linting, no schema checks"
  - dimension: "Image Testing"
    score: 1.0
    status: "Minimal Dockerfile packages manifests as tarball — no runtime validation or security scanning"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling — no codecov, no coverage thresholds, no PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "Zero GitHub Actions workflows — CI relies entirely on external OpenShift-CI (Prow) with no in-repo config"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules or AI-assisted testing guidance"
critical_gaps:
  - title: "No PR-time CI validation at all"
    impact: "Broken manifests, invalid YAML, and kustomize errors merge without detection — discovered only during downstream consumption"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "Zero unit-level manifest validation"
    impact: "No kustomize build verification, no YAML schema validation, no CRD conformance checks"
    severity: "HIGH"
    effort: "6-8 hours"
  - title: "No security scanning of manifests or container images"
    impact: "Vulnerable base images, leaked secrets in manifests, and insecure RBAC rules go undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No way to measure which components have smoke tests vs which are untested"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Repository appears stale — last commit Feb 2024"
    impact: "Manifests may be outdated vs. upstream components, creating drift and deployment failures"
    severity: "HIGH"
    effort: "N/A"
quick_wins:
  - title: "Add kustomize build validation workflow"
    effort: "2-3 hours"
    impact: "Catch broken overlays, missing resources, and invalid patches before merge"
  - title: "Add YAML linting with yamllint"
    effort: "1-2 hours"
    impact: "Catch syntax errors, formatting inconsistencies, and YAML anti-patterns"
  - title: "Add kubeconform or kubeval for schema validation"
    effort: "2-3 hours"
    impact: "Validate all manifests against Kubernetes and OpenShift API schemas"
  - title: "Add Trivy filesystem scanning for IaC misconfigurations"
    effort: "1-2 hours"
    impact: "Detect insecure RBAC, missing security contexts, and misconfigurations in manifests"
recommendations:
  priority_0:
    - "Add GitHub Actions CI workflow with kustomize build validation for all 144 kustomization.yaml files"
    - "Add kubeconform/kubeval schema validation against OpenShift API schemas"
    - "Add YAML linting (yamllint) to catch syntax and formatting issues"
  priority_1:
    - "Add Trivy IaC scanning for Kubernetes manifest misconfigurations"
    - "Add kustomize overlay diff testing to catch unintended changes between base/overlay"
    - "Add Polaris or OPA/Gatekeeper policy checks for best practices enforcement"
    - "Create CLAUDE.md with contribution guidelines and agent rules"
  priority_2:
    - "Add Pluto to detect deprecated API versions"
    - "Add kube-score for manifest quality scoring"
    - "Implement automated component version tracking"
    - "Add pre-commit hooks for local validation"
---

# Quality Analysis: odh-manifests

**Repository**: [red-hat-data-services/odh-manifests](https://github.com/red-hat-data-services/odh-manifests)
**Analysis Date**: 2026-06-03
**Repository Type**: Kustomize manifests repository (Infrastructure-as-Code)
**Primary Content**: 641 YAML files across 30+ ODH/RHOAI components
**Last Activity**: February 15, 2024 (appears stale — 16+ months without commits)

---

## Executive Summary

**Overall Score: 2.4/10**

`odh-manifests` is a Kustomize manifests repository that packages Kubernetes resource definitions for Open Data Hub components (dashboard, notebook controller, model-mesh, kserve, data science pipelines, TrustyAI, etc.). It contains **144 kustomization.yaml files** across 30+ component directories, serving as the deployment source-of-truth for ODH/RHOAI.

**Key Strengths:**
- Well-organized component structure with base/overlay pattern for ODH vs. RHOAI variants
- 15 bash-based smoke tests that validate component deployment on live OpenShift clusters
- PR template with checklist including JIRA linking and testing instructions
- Good issue templates for bugs and features

**Critical Gaps:**
- **Zero in-repo CI/CD**: No GitHub Actions workflows exist — no PR-time validation of any kind
- **No manifest validation**: 641 YAML files with no kustomize build checks, no schema validation, no linting
- **No security scanning**: No Trivy, no OPA/Gatekeeper, no RBAC analysis
- **No coverage tracking**: No way to measure which components are tested vs. untested
- **Appears stale**: Last commit was February 2024 — 16+ months ago

**Agent Rules Status**: Missing — No CLAUDE.md, no .claude/ directory, no AI agent guidance

---

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No unit tests — repo has zero test code files (Go, Python, TS) |
| Integration/E2E | 4/10 | 15 bash smoke tests for component deployment validation |
| **Build Integration** | **1.5/10** | **No PR-time CI — no kustomize build, no manifest linting** |
| Image Testing | 1/10 | Minimal Dockerfile (tarball packaging only) — no runtime validation |
| Coverage Tracking | 0/10 | No coverage tooling of any kind |
| CI/CD Automation | 1/10 | Zero GitHub Actions workflows — relies on external Prow |
| Agent Rules | 0/10 | No CLAUDE.md, no .claude/ directory, no agent rules |

---

## Critical Gaps

### 1. No PR-Time CI Validation
- **Impact**: Broken manifests, invalid YAML, and kustomize errors can merge to main without any automated detection. Downstream consumers (ODH operator, RHOAI installer) discover breakage at deployment time.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Details**: The `.github/` directory contains only issue templates and a PR template — zero workflow files. All CI relies on external OpenShift-CI (Prow) configured in the `openshift/release` repository, which only runs E2E tests after merge, not on PRs.

### 2. Zero Manifest Validation
- **Impact**: With 144 kustomization.yaml files and 641 total YAML files, there is no automated check that kustomize builds succeed, that resource schemas are valid, or that API versions are current.
- **Severity**: HIGH
- **Effort**: 6-8 hours
- **Details**: No kubeconform, no kubeval, no kustomize build test. A typo in any kustomization.yaml could break a downstream operator build.

### 3. No Security Scanning
- **Impact**: Manifests may contain insecure RBAC rules (wildcard permissions), missing security contexts, or reference vulnerable container images — all undetected.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No Trivy IaC scanning, no OPA/Gatekeeper policies, no Polaris checks. The Dockerfile uses `registry.access.redhat.com/ubi8/ubi-minimal:latest` without version pinning.

### 4. Repository Staleness
- **Impact**: Last commit was February 15, 2024. Components like kserve, model-mesh, and TrustyAI have likely received upstream updates that are not reflected here.
- **Severity**: HIGH
- **Effort**: N/A (organizational decision)
- **Details**: The repo may be deprecated in favor of the ODH operator's built-in manifest management. If still active, 16+ months of drift is a major deployment risk.

### 5. No Coverage Tracking
- **Impact**: No way to measure which of the 30+ components have smoke tests and which don't. Components like ai-library, partners, ceph, and monitoring have no corresponding test scripts.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours

---

## Quick Wins

### 1. Add Kustomize Build Validation Workflow (2-3 hours)
**Impact**: Catch broken overlays, missing resources, and invalid patches before merge.

```yaml
# .github/workflows/validate-manifests.yml
name: Validate Manifests
on: [pull_request]
jobs:
  kustomize-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install kustomize
        run: |
          curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
          sudo mv kustomize /usr/local/bin/
      - name: Validate all kustomize builds
        run: |
          find . -name kustomization.yaml -exec dirname {} \; | while read dir; do
            echo "Building $dir..."
            kustomize build "$dir" > /dev/null || exit 1
          done
```

### 2. Add YAML Linting (1-2 hours)
**Impact**: Catch syntax errors, formatting inconsistencies, and YAML anti-patterns.

```yaml
      - name: Lint YAML files
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: .
          config_data: |
            extends: default
            rules:
              line-length:
                max: 200
              truthy:
                allowed-values: ['true', 'false']
```

### 3. Add Kubeconform Schema Validation (2-3 hours)
**Impact**: Validate manifests against Kubernetes and OpenShift API schemas.

```yaml
      - name: Schema validation
        run: |
          wget https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz
          tar xzf kubeconform-linux-amd64.tar.gz
          find . -name kustomization.yaml -exec dirname {} \; | while read dir; do
            kustomize build "$dir" | ./kubeconform -strict -ignore-missing-schemas || exit 1
          done
```

### 4. Add Trivy IaC Scanning (1-2 hours)
**Impact**: Detect insecure RBAC, missing security contexts, and Kubernetes misconfigurations.

```yaml
      - name: Trivy IaC scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
```

---

## Detailed Findings

### CI/CD Pipeline

**Workflows**: None. The `.github/` directory contains only:
- `ISSUE_TEMPLATE/bug_report.md`
- `ISSUE_TEMPLATE/feature_request.md`
- `ISSUE_TEMPLATE/major-release.md`
- `ISSUE_TEMPLATE/minor-release.md`
- `ISSUE_TEMPLATE/patch-release.md`
- `PULL_REQUEST_TEMPLATE.md`

**External CI**: Tests run via OpenShift-CI (Prow), configured in `openshift/release` repo. The Prow job:
1. Builds a test container from `tests/Dockerfile` (CentOS Stream 8 based)
2. Spins up a fresh OpenShift cluster on AWS (ipi-aws workflow)
3. Installs ODH via KfDef
4. Runs bash smoke tests against the live cluster

**Build Automation**: The `Makefile` only handles release branching/tagging — no test targets, no build targets, no validation targets.

**Assessment**: All CI is external and opaque. There is no way for a PR author to know if their changes will pass validation without manually running `kustomize build` locally. The external Prow CI appears to be a post-merge gate, not a PR gate.

### Test Coverage

**Test Files**: 15 bash shell scripts in `tests/basictests/`:
- `airflow.sh`, `dashboard.sh`, `grafana.sh`, `hue.sh`
- `jupyterhub.sh`, `jupyterhub_load.sh`, `kafka.sh`
- `odhargo.sh`, `openshift-pipelines.sh`, `prometheus.sh`
- `radanalytics.sh`, `seldon.sh`, `superset.sh`
- `thriftserver.sh`, `trino.sh`

**Test Pattern**: Each test:
1. Checks that expected resources exist (`oc get deployment`, `oc get pods`)
2. Waits for pods to reach Running state
3. Optionally validates routes and API endpoints (e.g., dashboard UI test, grafana API test)
4. Uses OpenShift origin test utilities (`os::cmd::expect_success`, `os::cmd::try_until_text`)

**JupyterHub Test**: Most comprehensive — includes ODS-CI Robot Framework integration for UI testing.

**Components WITHOUT Tests**:
- `ai-library`, `ceph`, `codeflare-stack`
- `data-science-pipelines-operator`
- `kserve`, `model-mesh`, `modelmesh-monitoring`
- `monitoring` (alertmanager, blackbox-exporter)
- `odh-common`, `odh-model-controller`, `odh-notebook-controller`
- `osd-configs`, `partners`, `ray`
- `trustyai-service-operator`

**Test-to-Component Ratio**: 15 tests / 30+ components ≈ 50% coverage by count, but critical newer components (kserve, model-mesh, data science pipelines, TrustyAI) are entirely untested.

### Code Quality

- **Linting**: None configured. No `.golangci.yaml`, `.eslintrc`, `ruff.toml`, or equivalent.
- **Pre-commit Hooks**: None. No `.pre-commit-config.yaml`.
- **Static Analysis**: None. No CodeQL, no Semgrep, no YAML linters.
- **Formatting**: No enforced formatting for YAML files.

This is particularly concerning for a manifests repo where YAML correctness is the entire product.

### Container Images

**Root Dockerfile**: Minimal packaging image that:
1. Uses `ubi8/ubi-minimal:latest` (no version pinning)
2. Copies all manifests to `/opt/manifests`
3. Creates a tarball (`odh-manifests.tar.gz`)
4. No runtime validation, no health checks

**Test Dockerfile**: More complex — builds a CentOS Stream 8 test environment with:
- Go toolset, Python 3, Chrome/ChromeDriver
- `oc` CLI, `jq`, `peak` test runner
- ODS-CI Robot Framework
- Used by OpenShift-CI to run E2E tests

**Security**: No container scanning. No Trivy, no Snyk, no SBOM generation. No image signing.

### Security

- **Container Scanning**: None
- **SAST**: None
- **Dependency Scanning**: None (no code dependencies to scan, but manifest security is unvalidated)
- **Secret Detection**: None. No gitleaks, no TruffleHog.
- **RBAC Analysis**: No automated analysis of the ClusterRole and Role definitions across components
- **Security Contexts**: No enforcement of Pod Security Standards in manifests

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Not present
- **Rules**: No test creation rules, no contribution guidelines for AI agents
- **Coverage**: No test types have agent rules
- **Quality**: N/A
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering kustomize validation, YAML testing, and manifest quality checks

---

## Recommendations

### Priority 0 (Critical)

1. **Add GitHub Actions CI workflow with kustomize build validation**
   - Validate all 144 kustomization.yaml files build successfully on every PR
   - Fail fast on broken resources, missing files, or invalid patches
   - Estimated effort: 4-6 hours

2. **Add kubeconform/kubeval schema validation**
   - Validate all generated manifests against Kubernetes and OpenShift API schemas
   - Detect deprecated API versions before they cause runtime failures
   - Estimated effort: 2-3 hours

3. **Add YAML linting (yamllint)**
   - Enforce consistent YAML formatting across all 641 files
   - Catch common YAML pitfalls (duplicate keys, invalid anchors, wrong types)
   - Estimated effort: 1-2 hours

4. **Assess repository status — active or deprecated?**
   - Last commit is 16+ months old. If deprecated, document successor.
   - If active, establish regular sync cadence with upstream components.
   - Estimated effort: 2-4 hours (organizational)

### Priority 1 (High Value)

5. **Add Trivy IaC scanning for Kubernetes misconfigurations**
   - Detect insecure RBAC, missing security contexts, privileged containers
   - Estimated effort: 2-3 hours

6. **Add test coverage for missing components**
   - kserve, model-mesh, data-science-pipelines-operator, TrustyAI, odh-notebook-controller
   - These are critical RHOAI components with zero smoke tests
   - Estimated effort: 8-16 hours

7. **Add Polaris or OPA/Gatekeeper policy checks**
   - Enforce Kubernetes best practices (resource limits, health checks, security contexts)
   - Estimated effort: 4-6 hours

8. **Create CLAUDE.md and .claude/rules/ for agent-assisted contributions**
   - Document manifest patterns, naming conventions, and kustomize overlay structure
   - Create rules for AI agents contributing to the repo
   - Estimated effort: 3-4 hours

### Priority 2 (Nice-to-Have)

9. **Add Pluto for deprecated API detection**
   - Automatically flag manifests using deprecated or removed Kubernetes API versions
   - Estimated effort: 1-2 hours

10. **Add kube-score for manifest quality scoring**
    - Score manifests on best practices (resource requests/limits, anti-affinity, PDB)
    - Estimated effort: 2-3 hours

11. **Add pre-commit hooks for local validation**
    - Run yamllint and kustomize build checks before commits
    - Estimated effort: 1-2 hours

12. **Implement automated component version tracking**
    - Track upstream image versions vs. manifest references
    - Alert when manifests reference outdated images
    - Estimated effort: 4-8 hours

---

## Comparison to Gold Standards

| Dimension | odh-manifests | odh-dashboard | notebooks | kserve |
|-----------|--------------|---------------|-----------|--------|
| Unit Tests | None (0/10) | Comprehensive Jest suite (8/10) | N/A — image tests (7/10) | Go unit tests with coverage (8/10) |
| Integration/E2E | 15 bash scripts, partial (4/10) | Cypress E2E + contract tests (9/10) | 5-layer image validation (9/10) | Multi-version E2E (9/10) |
| Build Integration | None (1.5/10) | PR-time Docker build (7/10) | Konflux integration (8/10) | PR-time builds (7/10) |
| Image Testing | Tarball packaging only (1/10) | Multi-stage + runtime tests (7/10) | Startup + functional tests (9/10) | Runtime validation (7/10) |
| Coverage Tracking | None (0/10) | Codecov with thresholds (8/10) | N/A (6/10) | Codecov enforcement (8/10) |
| CI/CD | No in-repo CI (1/10) | GitHub Actions + Prow (9/10) | GitHub Actions + Konflux (8/10) | GitHub Actions (8/10) |
| Agent Rules | None (0/10) | Comprehensive (8/10) | Partial (4/10) | None (0/10) |
| **Overall** | **2.4/10** | **8.0/10** | **7.3/10** | **7.0/10** |

### Key Takeaway

`odh-manifests` is the weakest-scoring repository analyzed to date. As a pure manifests repository, it lacks the traditional code quality gates (unit tests, coverage), but it also lacks the manifest-specific gates that should replace them (kustomize validation, YAML linting, schema validation, policy checks). The absence of any in-repo CI means there is literally no automated quality gate between a PR and main.

---

## File Paths Reference

### CI/CD Configuration
| File | Purpose |
|------|---------|
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist (only CI-adjacent artifact) |
| `.aicoe-ci.yaml` | AICoE CI config (thoth-build strategy) |
| `.thoth.yaml` | Thoth release bot config |
| `Makefile` | Release branching/tagging only |

### Kustomize Structure
| Path Pattern | Count | Purpose |
|-------------|-------|---------|
| `*/base/kustomization.yaml` | ~20 | Base component definitions |
| `*/overlays/*/kustomization.yaml` | ~15 | ODH/RHOAI-specific overlays |
| `*/crd/kustomization.yaml` | ~5 | Custom Resource Definitions |
| `*/rbac/kustomization.yaml` | ~8 | RBAC resources |
| `*/manager/kustomization.yaml` | ~6 | Operator manager deployments |

### Test Infrastructure
| File | Purpose |
|------|---------|
| `tests/basictests/*.sh` | 15 component smoke tests |
| `tests/scripts/installandtest.sh` | Main test orchestrator for OpenShift-CI |
| `tests/scripts/install.sh` | ODH installation script |
| `tests/Dockerfile` | Test container image (CentOS Stream 8) |
| `tests/resources/ods-ci/*.robot` | Robot Framework UI tests |

### Container Images
| File | Purpose |
|------|---------|
| `Dockerfile` | Manifest tarball packaging (ubi8-minimal) |
| `tests/Dockerfile` | E2E test runner container |

### Key Component Directories
| Component | Path | Has Tests? |
|-----------|------|-----------|
| ODH Dashboard | `odh-dashboard/` | Yes (dashboard.sh) |
| Notebook Controller | `odh-notebook-controller/` | No |
| KServe | `kserve/` | No |
| Model Mesh | `model-mesh/` | No |
| Data Science Pipelines | `data-science-pipelines-operator/` | No |
| TrustyAI | `trustyai-service-operator/` | No |
| JupyterHub | `jupyterhub/` | Yes (jupyterhub.sh) |
| Grafana | `grafana/` | Yes (grafana.sh) |
| Kafka | `kafka/` | Yes (kafka.sh) |
| Prometheus | `prometheus/` | Yes (prometheus.sh) |
