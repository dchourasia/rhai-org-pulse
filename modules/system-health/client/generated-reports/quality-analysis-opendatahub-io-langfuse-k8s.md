---
repository: "opendatahub-io/langfuse-k8s"
overall_score: 3.8
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Strong helm-unittest suite with 52 test cases and 89% test-to-template ratio"
  - dimension: "Integration/E2E"
    score: 1.0
    status: "No integration or E2E tests; no Kind/Minikube deployment validation"
  - dimension: "Build Integration"
    score: 5.0
    status: "Helm lint and helm-docs validation on PRs; no deployment-level validation"
  - dimension: "Image Testing"
    score: 2.0
    status: "No chart artifact runtime validation; no referenced image verification"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tracking, enforcement, or reporting"
  - dimension: "CI/CD Automation"
    score: 6.5
    status: "4 workflows with lint/test/release/auto-bump; missing concurrency control and security scanning"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, .claude/ directory, or agent rules"
critical_gaps:
  - title: "No integration or E2E testing"
    impact: "Chart may fail to deploy on real clusters despite passing unit tests; template rendering correctness ≠ deployment success"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No security scanning"
    impact: "Vulnerabilities in chart dependencies (PostgreSQL, ClickHouse, Redis, MinIO sub-charts) go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No visibility into which templates and value combinations lack test coverage; untested templates include HPA, VPA, ScaledObject, secrets"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "Missing test coverage for several templates"
    impact: "HPA, VPA, ScaledObject, postgresql-secret, nextauth-secret, and extra-manifests templates have no dedicated tests"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI agents lack guidance on chart conventions, test patterns, and values.yaml schema when contributing"
    severity: "LOW"
    effort: "3-4 hours"
quick_wins:
  - title: "Add concurrency control to CI workflows"
    effort: "30 minutes"
    impact: "Prevent redundant workflow runs on rapid PR updates"
  - title: "Add Kubeconform/Kubeval validation to PR workflow"
    effort: "1-2 hours"
    impact: "Validate rendered manifests against Kubernetes API schemas before merge"
  - title: "Add Trivy scanning for sub-chart dependencies"
    effort: "1-2 hours"
    impact: "Detect known CVEs in PostgreSQL, ClickHouse, Redis, and MinIO images referenced by the chart"
  - title: "Add helm-unittest tests for untested templates (HPA, VPA, ScaledObject, secrets)"
    effort: "4-6 hours"
    impact: "Close the template coverage gap from ~60% to ~95%"
  - title: "Create basic CLAUDE.md with chart development conventions"
    effort: "1-2 hours"
    impact: "Enable AI agents to contribute correctly following existing patterns"
recommendations:
  priority_0:
    - "Add integration testing with ct (chart-testing) and Kind to validate chart installation on real clusters"
    - "Add Kubeconform validation to PR workflow to catch schema violations before merge"
    - "Add security scanning (Trivy) for sub-chart container images"
  priority_1:
    - "Add helm-unittest coverage for HPA, VPA, ScaledObject, postgresql-secret, nextauth-secret, and extra-manifests templates"
    - "Add concurrency control and caching to GitHub Actions workflows"
    - "Create CLAUDE.md and agent rules for consistent AI-assisted contributions"
  priority_2:
    - "Add Dependabot or Renovate for automated dependency management of sub-charts"
    - "Add pre-commit hooks for local validation (helm lint, yaml lint)"
    - "Add Pluto or kubepug to detect deprecated Kubernetes API usage"
---

# Quality Analysis: langfuse-k8s

## Executive Summary

- **Overall Score: 3.8/10**
- **Repository Type**: Helm chart for deploying [Langfuse](https://langfuse.com/) (LLM observability platform) on Kubernetes
- **Primary Language**: YAML (Helm templates + Helm unit tests)
- **Chart Version**: 1.5.22 | **App Version**: 3.155.1
- **Contributors**: 21 contributors across 100+ commits
- **Key Strengths**: Strong unit test suite (52 test cases, 89% test-to-template ratio), excellent input validation templates, automated version bumping workflow, comprehensive Redis/ClickHouse/S3 configuration testing
- **Critical Gaps**: No integration/E2E testing, no security scanning, no coverage tracking, no agent rules
- **Agent Rules Status**: Missing

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Strong helm-unittest suite with 52 test cases covering major config permutations |
| Integration/E2E | 1.0/10 | No integration or E2E tests; no Kind/Minikube deployment validation |
| **Build Integration** | **5.0/10** | **Helm lint + helm-docs on PRs; no deployment-level validation** |
| Image Testing | 2.0/10 | No chart artifact runtime validation; no referenced image verification |
| Coverage Tracking | 1.0/10 | No coverage tracking, enforcement, or reporting |
| CI/CD Automation | 6.5/10 | 4 workflows with lint/test/release/auto-bump; gaps in concurrency + security |
| Agent Rules | 0.0/10 | No CLAUDE.md, .claude/ directory, or agent rules |

## Critical Gaps

### 1. No Integration or E2E Testing
- **Impact**: Chart unit tests validate template rendering correctness, but a chart can render valid YAML and still fail to deploy (wrong RBAC, misconfigured probes, dependency ordering issues). Without Kind/Minikube testing, deployment failures are only discovered by end users.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Recommendation**: Add [chart-testing (ct)](https://github.com/helm/chart-testing) with Kind to validate chart installation and basic smoke tests in CI.

### 2. No Security Scanning
- **Impact**: The chart bundles 5 sub-charts (PostgreSQL 16.4.9, ClickHouse 8.0.5, Valkey 2.2.4, MinIO 14.10.5, Common 2.30.0) from Bitnami. Vulnerabilities in these container images or their configurations go completely undetected.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Recommendation**: Add Trivy scanning to the PR workflow to scan rendered manifests and referenced container images for known CVEs.

### 3. No Coverage Tracking
- **Impact**: Several templates have no dedicated test coverage: `web/hpa.yaml`, `web/vpa.yaml`, `web/scaled-object.yaml`, `worker/hpa.yaml`, `worker/vpa.yaml`, `worker/scaled-object.yaml`, `postgresql-secret.yaml`, `nextauth-secret.yaml`, `extra-manifests.yaml`. Changes to these templates have no safety net.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours (for tracking), 8-12 hours (for closing coverage gaps)

### 4. Missing Template Test Coverage
- **Impact**: 9 of 15 template files (60%) have dedicated test coverage. The remaining 6 templates (40%) rely only on `helm lint` for validation.
- **Severity**: MEDIUM
- **Effort**: 8-12 hours
- **Templates needing tests**:
  - `web/hpa.yaml` - HPA configuration and thresholds
  - `web/vpa.yaml` - VPA resource controls
  - `web/scaled-object.yaml` - KEDA ScaledObject configuration
  - `worker/hpa.yaml`, `worker/vpa.yaml`, `worker/scaled-object.yaml` - Mirror of web scaling
  - `postgresql-secret.yaml` - Secret generation
  - `nextauth-secret.yaml` - NextAuth secret generation
  - `extra-manifests.yaml` - Custom manifests rendering

### 5. No Agent Rules
- **Impact**: AI agents contributing to this chart have no guidance on Helm template patterns, values.yaml schema, test conventions, or naming standards.
- **Severity**: LOW
- **Effort**: 3-4 hours

## Quick Wins

### 1. Add Concurrency Control to Workflows (30 minutes)
Add concurrency groups to prevent redundant runs on rapid PR updates:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 2. Add Kubeconform Validation (1-2 hours)
Validate rendered manifests against Kubernetes API schemas:
```yaml
- name: Install Kubeconform
  run: |
    wget -O /tmp/kubeconform.tar.gz https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz
    tar xf /tmp/kubeconform.tar.gz -C /usr/local/bin

- name: Validate manifests
  run: |
    helm template langfuse charts/langfuse/ -f charts/langfuse/values.lint.yaml | \
      kubeconform -strict -summary
```

### 3. Add Trivy Scanning (1-2 hours)
Scan for vulnerabilities in referenced container images:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'config'
    scan-ref: 'charts/langfuse/templates/'
    severity: 'CRITICAL,HIGH'
```

### 4. Add Missing Template Tests (4-6 hours)
Create `hpa_test.yaml`, `vpa_test.yaml`, `scaled-object_test.yaml`, and `secrets_test.yaml` to cover the remaining ~40% of untested templates.

### 5. Create CLAUDE.md (1-2 hours)
Add basic agent rules covering chart conventions, test patterns, and contribution guidelines.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (4 workflows)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate.yaml` | PR (charts/** paths) | Helm lint + helm-docs validation |
| `test.yaml` | PR + push to main | Helm unit tests with JUnit output |
| `release.yaml` | Push to main (Chart.yaml changes) | Package + push to GHCR + GitHub Release |
| `update-langfuse-version.yml` | Weekly schedule (Mon 9am UTC) + manual | Auto-bump Langfuse appVersion |

**Strengths**:
- Automated version bumping with PR creation (smart use of `peter-evans/create-pull-request`)
- JUnit test result publishing via `EnricoMi/publish-unit-test-result-action` for PR visibility
- helm-docs validation prevents documentation drift
- OCI registry publishing (GHCR) for modern Helm distribution
- Dual release (GHCR OCI + GitHub chart-releaser) for maximum compatibility

**Gaps**:
- No concurrency control on any workflow
- No caching (Helm plugins, dependencies downloaded fresh every run)
- No security scanning workflow
- No branch protection validation
- No Kubernetes schema validation (Kubeconform/Kubeval)
- Helm version pinned to v3.13.2 (may be outdated)
- No matrix testing across multiple Kubernetes versions

### Test Coverage

**Test Suite Summary**:
- **Framework**: helm-unittest v1.0.0
- **Test Files**: 9
- **Test Cases**: 52
- **Test Lines**: 1,387
- **Template Lines**: 1,560 (including `_helpers.tpl`)
- **Test-to-Template Ratio**: 89% (excellent)

**Test Coverage by Feature**:

| Test File | Test Cases | Lines | Coverage Area |
|-----------|-----------|-------|---------------|
| `redis-cluster_test.yaml` | 17 | 550 | Redis standalone/cluster/TLS/auth/passwordless/overrides/validation |
| `ingress_test.yaml` | 4 | 188 | Ingress rendering, custom backends, mixed backends, disabled |
| `downward-api_test.yaml` | 6 | 166 | Kubernetes Downward API env vars (fieldRef, resourceFieldRef) |
| `clickhouse-cluster_test.yaml` | 6 | 138 | ClickHouse cluster/standalone modes, replica counts |
| `s3-media-upload-validation_test.yaml` | 6 | 94 | S3 media upload validation, MinIO forcePathStyle, bucket config |
| `minimal-installation_test.yaml` | 3 | 83 | Minimal install rendering, secret references, DB connections |
| `basic_test.yaml` | 3 | 70 | Basic rendering, labels, image tags |
| `extra-containers_test.yaml` | 3 | 64 | Sidecar containers for web/worker |
| `extra-env_test.yaml` | 1 | 34 | Additional environment variables |

**Templates WITH Test Coverage** (9/15 = 60%):
- `web/deployment.yaml` - Extensively tested
- `worker/deployment.yaml` - Extensively tested
- `web/service.yaml` - Basic test
- `serviceaccount.yaml` - Basic test
- `ingress.yaml` - Thorough testing
- `validations.yaml` - Validation failure tests

**Templates WITHOUT Test Coverage** (6/15 = 40%):
- `web/hpa.yaml` - No tests
- `web/vpa.yaml` - No tests
- `web/scaled-object.yaml` - No tests
- `worker/hpa.yaml` - No tests
- `worker/vpa.yaml` - No tests
- `worker/scaled-object.yaml` - No tests
- `postgresql-secret.yaml` - No tests
- `nextauth-secret.yaml` - No tests
- `extra-manifests.yaml` - No tests

**Testing Strengths**:
- Excellent edge case coverage (passwordless Redis, null passwords, TLS combinations)
- Validation failure testing (tests that chart correctly rejects invalid configs)
- Multiple value file combinations (lint values, minimal install values, custom test values)
- Both positive (should render) and negative (should fail) assertions

### Code Quality

**Linting**: Helm lint runs on PRs with dedicated lint values (`values.lint.yaml`).

**Documentation**: helm-docs enforced via CI - documentation stays in sync with `values.yaml` comments.

**Input Validation**: Exceptionally strong - 250 lines of validation templates (`validations.yaml`) covering:
- Logging level/format validation
- Auth provider validation
- ClickHouse configuration (shard count, host requirements)
- Redis configuration (standalone vs cluster vs sentinel mutual exclusivity)
- S3 configuration (bucket, forcePathStyle, provider type)
- PostgreSQL, Redis, ClickHouse, S3 `additionalEnv` conflict detection
- Scaling configuration conflicts (KEDA + HPA/VPA mutual exclusivity)

**Template Quality**: Well-structured helper templates (`_helpers.tpl`, 726 lines) with:
- Consistent naming patterns
- Value-or-secret resolution pattern (supports direct values, secretKeyRef, fieldRef, resourceFieldRef)
- Comprehensive environment variable generation for all dependencies

**Missing**:
- No pre-commit hooks
- No YAML linting beyond `helm lint`
- No static analysis

### Container Images

This is a Helm chart repository - it does not build container images. It references:
- `langfuse/langfuse` (web)
- `langfuse/langfuse-worker` (worker)
- Bitnami sub-chart images (PostgreSQL, ClickHouse, Valkey, MinIO)

No verification of referenced images is performed. No scanning for vulnerabilities in referenced images.

### Security

**Current State**: No security practices in place.

**Missing**:
- No Trivy/Snyk scanning for container image vulnerabilities
- No SAST/CodeQL analysis
- No secret detection (Gitleaks/TruffleHog)
- No Kubeconform/Kubeval for Kubernetes schema validation
- No network policy templates
- No Pod Security Standards enforcement
- No RBAC least-privilege verification

**Positive Notes**:
- Chart uses `secretKeyRef` patterns for sensitive values (passwords, keys, tokens)
- Input validation prevents common misconfiguration errors
- Uses separate deployment for web and worker components (good separation of concerns)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**:
  - No guidance for AI agents on Helm template patterns
  - No test creation rules for helm-unittest
  - No values.yaml schema documentation for agents
  - No contribution guidelines for chart development
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering helm-unittest patterns, values.yaml conventions, and template naming standards

## Recommendations

### Priority 0 (Critical)

1. **Add chart-testing (ct) with Kind for integration testing**
   - Install chart on real Kind cluster in CI
   - Validate all sub-chart dependencies deploy correctly
   - Test upgrade paths between chart versions
   - Effort: 16-24 hours

2. **Add Kubeconform validation to PR workflow**
   - Validate rendered manifests against Kubernetes API schemas
   - Test across multiple K8s versions (1.28, 1.29, 1.30, 1.31)
   - Effort: 1-2 hours

3. **Add security scanning for sub-chart dependencies**
   - Trivy for container image CVE scanning
   - Config scanning for Kubernetes security best practices
   - Effort: 2-4 hours

### Priority 1 (High Value)

4. **Close template test coverage gap**
   - Add tests for HPA, VPA, ScaledObject templates (web + worker)
   - Add tests for postgresql-secret and nextauth-secret generation
   - Add tests for extra-manifests rendering
   - Effort: 8-12 hours

5. **Add CI workflow improvements**
   - Concurrency control on all workflows
   - Helm dependency caching
   - Matrix testing across Kubernetes versions
   - Effort: 2-4 hours

6. **Create CLAUDE.md and agent rules**
   - Chart development conventions
   - Test creation patterns for helm-unittest
   - Values.yaml schema documentation
   - Effort: 3-4 hours

### Priority 2 (Nice-to-Have)

7. **Add Dependabot/Renovate for sub-chart dependency updates**
   - Currently only Langfuse app version is auto-bumped
   - Sub-chart versions (PostgreSQL, ClickHouse, Valkey, MinIO) require manual updates
   - Effort: 1-2 hours

8. **Add pre-commit hooks**
   - YAML linting, helm lint, helm-docs validation
   - Catch issues before CI
   - Effort: 1-2 hours

9. **Add Pluto for Kubernetes API deprecation detection**
   - Detect deprecated API usage before Kubernetes upgrades break deployments
   - Effort: 1 hour

## Comparison to Gold Standards

| Dimension | langfuse-k8s | odh-dashboard | notebooks | kserve |
|-----------|:---:|:---:|:---:|:---:|
| Unit Tests | 7.5 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 1.0 | 9.0 | 8.0 | 9.0 |
| Build Integration | 5.0 | 8.0 | 7.0 | 8.0 |
| Image Testing | 2.0 | 7.0 | 9.0 | 7.0 |
| Coverage Tracking | 1.0 | 8.0 | 5.0 | 8.0 |
| CI/CD Automation | 6.5 | 9.0 | 8.0 | 9.0 |
| Agent Rules | 0.0 | 8.0 | 3.0 | 2.0 |
| **Overall** | **3.8** | **8.5** | **7.0** | **8.0** |

**Key Observations**:
- langfuse-k8s has surprisingly strong unit testing for a community Helm chart (7.5/10)
- The massive gap is in integration/E2E testing - this is where gold standards like kserve and odh-dashboard invest heavily
- Security and coverage tracking are the easiest areas to improve with the least effort

## File Paths Reference

### CI/CD
- `.github/workflows/validate.yaml` - Helm lint + helm-docs validation
- `.github/workflows/test.yaml` - Helm unit tests
- `.github/workflows/release.yaml` - Chart packaging and release
- `.github/workflows/update-langfuse-version.yml` - Automated version bumping

### Chart
- `charts/langfuse/Chart.yaml` - Chart metadata and dependencies
- `charts/langfuse/values.yaml` - Default values (732 lines)
- `charts/langfuse/values.lint.yaml` - CI lint values
- `charts/langfuse/templates/_helpers.tpl` - Helper templates (726 lines)
- `charts/langfuse/templates/validations.yaml` - Input validation (250 lines)

### Templates (15 files, 1560 lines)
- `charts/langfuse/templates/web/deployment.yaml` - Web deployment
- `charts/langfuse/templates/worker/deployment.yaml` - Worker deployment
- `charts/langfuse/templates/web/service.yaml` - Web service
- `charts/langfuse/templates/ingress.yaml` - Ingress resource
- `charts/langfuse/templates/serviceaccount.yaml` - ServiceAccount
- `charts/langfuse/templates/web/hpa.yaml` - Web HPA (UNTESTED)
- `charts/langfuse/templates/web/vpa.yaml` - Web VPA (UNTESTED)
- `charts/langfuse/templates/web/scaled-object.yaml` - Web KEDA ScaledObject (UNTESTED)
- `charts/langfuse/templates/worker/hpa.yaml` - Worker HPA (UNTESTED)
- `charts/langfuse/templates/worker/vpa.yaml` - Worker VPA (UNTESTED)
- `charts/langfuse/templates/worker/scaled-object.yaml` - Worker KEDA ScaledObject (UNTESTED)
- `charts/langfuse/templates/postgresql-secret.yaml` - PostgreSQL secret (UNTESTED)
- `charts/langfuse/templates/nextauth-secret.yaml` - NextAuth secret (UNTESTED)
- `charts/langfuse/templates/extra-manifests.yaml` - Custom manifests (UNTESTED)

### Tests (9 files, 1387 lines, 52 test cases)
- `charts/langfuse/tests/basic_test.yaml` - Basic rendering (3 tests)
- `charts/langfuse/tests/clickhouse-cluster_test.yaml` - ClickHouse config (6 tests)
- `charts/langfuse/tests/downward-api_test.yaml` - Downward API (6 tests)
- `charts/langfuse/tests/extra-containers_test.yaml` - Sidecar containers (3 tests)
- `charts/langfuse/tests/extra-env_test.yaml` - Additional env vars (1 test)
- `charts/langfuse/tests/ingress_test.yaml` - Ingress (4 tests)
- `charts/langfuse/tests/minimal-installation_test.yaml` - Minimal install (3 tests)
- `charts/langfuse/tests/redis-cluster_test.yaml` - Redis cluster/sentinel (17 tests)
- `charts/langfuse/tests/s3-media-upload-validation_test.yaml` - S3 validation (6 tests)
- `charts/langfuse/tests/values/` - Test value files (6 files)

### Documentation
- `README.md` - Main documentation (auto-generated by helm-docs)
- `UPGRADE.md` - Upgrade guide
- `TROUBLESHOOTING.md` - Troubleshooting guide
- `examples/` - Example configurations

### Governance
- `.github/CODEOWNERS` - @Steffen911 owns all files
- `.github/ISSUE_TEMPLATE/bug_report.yml` - Bug report template
- `.github/ISSUE_TEMPLATE/feature_request.yml` - Feature request template
