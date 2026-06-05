---
repository: "langfuse/langfuse-k8s"
overall_score: 5.4
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Good helm-unittest coverage across 11 test suites with 1674 lines of tests"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "No integration or E2E tests - no Kind/Minikube deployment validation"
  - dimension: "Build Integration"
    score: 3.0
    status: "Helm lint and docs validation on PR, but no template rendering or install simulation"
  - dimension: "Image Testing"
    score: 1.0
    status: "No container image testing - chart deploys upstream images without validation"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tracking, thresholds, or codecov integration"
  - dimension: "CI/CD Automation"
    score: 7.5
    status: "Well-organized workflows with concurrency control, pinned actions, and automated version bumps"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, .claude/ directory, or agent rules present"
critical_gaps:
  - title: "No integration/E2E testing"
    impact: "Chart regressions (broken env vars, missing resources, invalid manifests) only caught by unit tests asserting individual values, not by actual cluster deployment"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No coverage tracking or enforcement"
    impact: "No visibility into which templates or value combinations are tested; untested paths silently regress"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container image validation"
    impact: "Upstream image startup failures, missing env vars, or broken health endpoints not caught until user deploys"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "No security scanning in CI"
    impact: "Vulnerable base images or Helm template security misconfigurations not detected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Missing sentinel mode test coverage"
    impact: "Sentinel configuration templates have validations but no unit tests verifying rendered output"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add helm template --validate to PR workflow"
    effort: "1-2 hours"
    impact: "Catch Kubernetes API validation errors before merge without a live cluster"
  - title: "Add Trivy scanning for Helm chart"
    effort: "1-2 hours"
    impact: "Detect misconfigurations (no resource limits, no securityContext enforcement) in rendered manifests"
  - title: "Add kubeconform/kubeval validation"
    effort: "2-3 hours"
    impact: "Validate rendered manifests against Kubernetes OpenAPI schemas for multiple K8s versions"
  - title: "Create CLAUDE.md with testing patterns"
    effort: "2-3 hours"
    impact: "Ensure AI-assisted contributions follow existing helm-unittest patterns"
  - title: "Add chart-testing (ct) lint and install"
    effort: "4-6 hours"
    impact: "Industry-standard Helm chart CI that includes lint, install, and upgrade testing with Kind"
recommendations:
  priority_0:
    - "Add chart-testing (ct) with Kind cluster for install and upgrade testing"
    - "Add kubeconform validation against multiple Kubernetes versions (1.27-1.31)"
    - "Add Trivy chart scanning for security misconfigurations"
  priority_1:
    - "Add sentinel mode unit tests to match cluster and standalone coverage"
    - "Add VPA and KEDA ScaledObject unit tests (templates exist, no tests)"
    - "Create CLAUDE.md or agent rules for test automation guidance"
    - "Add upgrade path testing (previous chart version -> current)"
  priority_2:
    - "Add schema validation for values.yaml (values.schema.json)"
    - "Add Polaris or Datree for best-practice enforcement"
    - "Consider Helm-specific code coverage tooling"
---

# Quality Analysis: langfuse-k8s

## Executive Summary

- **Overall Score: 5.4/10**
- **Repository Type**: Helm chart for deploying Langfuse (LLM observability platform) on Kubernetes
- **Primary Language**: YAML (Helm templates + helm-unittest)
- **Key Strengths**: Well-structured unit test suite covering complex configuration scenarios (Redis cluster/sentinel, auth providers, ClickHouse cluster, S3 validation), strong CI/CD workflow organization with pinned actions and concurrency control, extensive input validation templates
- **Critical Gaps**: No integration/E2E testing with a live cluster, no coverage tracking, no security scanning, no container image validation, no agent rules
- **Agent Rules Status**: Missing - no CLAUDE.md, .claude/ directory, or testing guidance

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Good helm-unittest coverage: 11 test suites, 1674 lines, covering Redis, ClickHouse, auth, ingress, S3, PDB, HPA, downward API |
| Integration/E2E | 2.0/10 | No integration tests - no Kind/Minikube install, no upgrade testing, no runtime validation |
| **Build Integration** | **3.0/10** | **Helm lint + docs validation on PR, but no template rendering validation or install simulation** |
| Image Testing | 1.0/10 | No image testing - chart deploys upstream images without any startup or health validation |
| Coverage Tracking | 1.0/10 | No coverage tracking, no codecov, no thresholds, no visibility into untested template paths |
| CI/CD Automation | 7.5/10 | 5 well-organized workflows, concurrency control, pinned action SHAs, dependabot, automated version bumps, JUnit test reporting |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude/ directory, no testing guidance for AI agents |

## Critical Gaps

### 1. No Integration/E2E Testing
- **Impact**: Chart installation failures, upgrade breakages, and resource rendering issues only detectable through unit tests that check individual YAML paths - not through actual Kubernetes API validation
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Detail**: The chart has complex dependencies (PostgreSQL, ClickHouse, Valkey, MinIO) and sophisticated template logic. Unit tests verify individual env vars and paths but cannot detect issues like:
  - Incompatible resource versions across K8s versions
  - Dependency chart interaction failures
  - Upgrade path regressions (CRD changes, migration issues)
  - Service connectivity between web and worker deployments

### 2. No Coverage Tracking or Enforcement
- **Impact**: No visibility into which templates, helper functions, or value combinations are actually tested. Contributors can add new template logic without tests.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Detail**: While 11 test suites exist, several templates have no dedicated tests:
  - `worker/scaled-object.yaml` - no tests
  - `web/scaled-object.yaml` - no tests
  - `worker/vpa.yaml` - no tests
  - `web/vpa.yaml` - no tests
  - `nextauth-secret.yaml` - no dedicated tests
  - `postgresql-secret.yaml` - no dedicated tests
  - `extra-manifests.yaml` - no dedicated tests
  - Sentinel mode validation has template logic but no unit tests

### 3. No Security Scanning in CI
- **Impact**: Rendered manifests may contain security misconfigurations (containers running as root, missing securityContext, no resource limits by default) and upstream images may have vulnerabilities
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Detail**: The repository has zizmor for GitHub Actions security scanning but no Helm-specific security tools:
  - No Trivy chart scanning for misconfiguration detection
  - No Polaris or Datree for best-practice enforcement
  - No container image vulnerability scanning
  - Default values set empty `securityContext: {}` and `podSecurityContext: {}`

### 4. No Container Image Validation
- **Impact**: The chart deploys `langfuse/langfuse` and `langfuse/langfuse-worker` images but never validates that they start, respond to health checks, or have the expected env var interface
- **Severity**: MEDIUM
- **Effort**: 8-12 hours
- **Detail**: Health check paths are configured (`/api/public/health`, `/api/public/ready`) but never tested in CI. Version bumps are automated weekly but the new version's image is never validated before the chart release.

### 5. Missing Sentinel Mode Test Coverage
- **Impact**: Redis Sentinel configuration has extensive validation template logic (6 validation rules) but zero unit tests verifying rendered deployments
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Detail**: Cluster mode has comprehensive tests (550 lines) but sentinel mode - which has similar complexity in template rendering - has only validation failure tests implicitly (through the validations.yaml template), not positive rendering tests.

## Quick Wins

### 1. Add `helm template --validate` to PR workflow
- **Effort**: 1-2 hours
- **Impact**: Catches Kubernetes API schema validation errors without a live cluster
- **Implementation**:
```yaml
- name: Validate rendered templates
  run: |
    helm template test charts/langfuse/ \
      -f charts/langfuse/values.lint.yaml \
      --validate
```

### 2. Add kubeconform validation
- **Effort**: 2-3 hours
- **Impact**: Validates rendered manifests against Kubernetes OpenAPI schemas for multiple versions
- **Implementation**:
```yaml
- name: Install kubeconform
  run: |
    curl -sSL https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz | tar xz
    sudo mv kubeconform /usr/local/bin/

- name: Validate manifests
  run: |
    helm template test charts/langfuse/ -f charts/langfuse/values.lint.yaml | \
      kubeconform -strict -kubernetes-version 1.29.0 -summary
```

### 3. Add Trivy chart scanning
- **Effort**: 1-2 hours
- **Impact**: Detect Helm misconfiguration issues (no resource limits, missing securityContext)
- **Implementation**:
```yaml
- name: Run Trivy misconfiguration scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'config'
    scan-ref: 'charts/langfuse/'
    exit-code: '1'
    severity: 'HIGH,CRITICAL'
```

### 4. Add chart-testing (ct) lint
- **Effort**: 2-3 hours
- **Impact**: Industry-standard Helm chart CI with enhanced linting and change detection
- **Implementation**:
```yaml
- name: Run chart-testing (lint)
  uses: helm/chart-testing-action@v2
  with:
    command: lint
    config: ct.yaml
```

### 5. Create CLAUDE.md with testing patterns
- **Effort**: 2-3 hours
- **Impact**: Ensure AI-generated contributions follow existing helm-unittest patterns
- **Implementation**: Document the test file structure, values.lint.yaml usage, assertion patterns, and test naming conventions

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- **5 workflows** covering unit tests, validation, release, security scanning, and automated version updates
- **Concurrency control** on all workflows with `cancel-in-progress: true`
- **Pinned action SHAs** for supply chain security (e.g., `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2`)
- **JUnit test reporting** with PR comments for unit test results
- **Automated version bumps** via weekly scheduled workflow that creates PRs
- **Dependabot** configured for GitHub Actions updates with grouping
- **zizmor** for GitHub Actions security analysis with SARIF upload

**Gaps:**
- No chart-testing (ct) integration - the industry standard for Helm chart CI
- No Kind/Minikube cluster creation for install testing
- No upgrade path testing (previous version -> current version)
- Validate workflow only triggers on `charts/**` path changes, so CI config changes aren't tested
- No caching of Helm plugin installation (helm-unittest plugin installed fresh every run)

**Workflow Summary:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yaml` | PR, push to main | Helm unit tests with JUnit reporting |
| `validate.yaml` | PR (charts/** changes) | Helm lint + helm-docs validation |
| `release.yaml` | Push to main (Chart.yaml changes) | Package and publish to GHCR + chart-releaser |
| `zizmor.yml` | PR, push to main, merge group | GitHub Actions security scanning |
| `update-langfuse-version.yml` | Weekly cron (Monday 9 AM UTC) | Automated upstream version bump PRs |

### Test Coverage

**Strengths:**
- **11 test suites** with **1674 lines** of test YAML
- **Comprehensive Redis testing** (550 lines): standalone, cluster, TLS, passwordless, existing secrets, additionalEnv overrides, validation failures, edge cases
- **Auth provider testing** (219 lines): Azure AD, GitHub, Okta, Google, mixed direct/secret values, multi-provider
- **Ingress testing** (188 lines): default backend, custom backend, mixed backends, disabled state
- **Downward API testing** (166 lines): fieldRef, resourceFieldRef, optional fields, mixed with core secrets
- **ClickHouse cluster testing** (138 lines): single/multi-replica, external, override scenarios
- **S3 validation testing** (94 lines): MinIO forcePathStyle, external bucket requirements
- **Minimal installation testing** (83 lines): validates example values work end-to-end
- **Extra containers/env testing** (98 lines): sidecar injection, global/component-specific env vars

**Test-to-Template Ratio:**
- Templates: 17 YAML files + 1 TPL helper
- Test files: 11 test suites
- Coverage: ~60% of templates have dedicated tests

**Untested Templates:**
- `worker/scaled-object.yaml` - KEDA ScaledObject
- `web/scaled-object.yaml` - KEDA ScaledObject
- `worker/vpa.yaml` - Vertical Pod Autoscaler
- `web/vpa.yaml` - Vertical Pod Autoscaler
- `nextauth-secret.yaml` - Secret generation
- `postgresql-secret.yaml` - Secret generation
- `extra-manifests.yaml` - Custom manifests injection
- `_helpers.tpl` - No dedicated tests (tested indirectly)

**Untested Configuration Paths:**
- Redis Sentinel mode (rendering, not just validation)
- Worker PDB configuration
- KEDA ScaledObject rendering
- VPA configuration rendering
- GCS storage provider
- Azure Blob storage provider
- ClickHouse migration SSL
- Custom image pull secrets
- Multiple ingress TLS hosts

### Code Quality

**Strengths:**
- Helm lint runs on every PR
- helm-docs validation ensures documentation stays in sync
- Extensive input validation in `validations.yaml` (269 lines covering every configuration dimension)
- CODEOWNERS file requiring maintainer review for `.github/` changes
- Clear separation between web and worker deployment templates

**Gaps:**
- No pre-commit hooks
- No `.helmignore` optimization (exists but not analyzed for completeness)
- No values.schema.json for JSON Schema validation of values.yaml
- No markdown linting for documentation files

### Container Images

**Assessment:** The chart deploys two upstream images:
- `langfuse/langfuse` (web component)
- `langfuse/langfuse-worker` (worker component)

The chart configures health probes (`/api/public/health`, `/api/public/ready`) but never validates these in CI. The automated version bump workflow updates `appVersion` weekly but the new image is never tested before release.

**No container-related testing exists:**
- No Trivy/Snyk scanning of upstream images
- No image startup validation
- No SBOM generation
- No multi-architecture validation
- No image pull validation

### Security

**Strengths:**
- zizmor for GitHub Actions security auditing with SARIF upload
- Dependabot for GitHub Actions dependency updates
- Pinned action SHAs throughout all workflows
- `persist-credentials: false` on checkout actions
- Minimal permissions scoping per workflow

**Gaps:**
- No Helm chart security scanning (Trivy config, Polaris, Datree)
- No container image vulnerability scanning
- Default values leave `securityContext: {}` empty - no enforcement of non-root, read-only filesystem, or dropped capabilities
- No network policy templates
- No secret detection (Gitleaks, TruffleHog) - though values.lint.yaml contains dummy secrets
- No SAST/CodeQL integration (not applicable for YAML-only repo, but static analysis for Helm templates would help)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: N/A
- **Quality**: N/A
- **Gaps**: No CLAUDE.md, no AGENTS.md, no `.claude/` directory, no `.claude/rules/` for test automation guidance
- **Recommendation**: Generate rules with /test-rules-generator covering:
  - helm-unittest patterns (suite structure, assertion types, values files)
  - Validation test patterns (failedTemplate assertions)
  - Test file naming conventions (`{feature}_test.yaml`)
  - Values file organization (values.lint.yaml for base, `tests/values/` for scenarios)

## Recommendations

### Priority 0 (Critical)

1. **Add chart-testing (ct) with Kind cluster** for install and upgrade testing
   - Use `helm/chart-testing-action` with `command: install`
   - Test install with default values and minimal-installation example
   - Test upgrade from previous chart version
   - Validates actual Kubernetes API compatibility

2. **Add kubeconform validation** against multiple Kubernetes versions (1.27-1.31)
   - Ensures rendered manifests are valid for all supported K8s versions
   - Catches deprecated API versions before users hit them

3. **Add Trivy chart misconfiguration scanning**
   - Detect security misconfigurations in rendered manifests
   - Flag missing resource limits, empty securityContext, etc.

### Priority 1 (High Value)

4. **Add sentinel mode unit tests** to match cluster and standalone coverage
   - Positive rendering tests for web/worker deployments
   - TLS with sentinel
   - Existing secrets with sentinel
   - additionalEnv overrides

5. **Add VPA, KEDA ScaledObject, and secret template unit tests**
   - These templates exist and are configurable but have no test coverage
   - ScaledObject tests should verify KEDA/HPA mutual exclusion

6. **Create CLAUDE.md or agent rules** for test automation guidance
   - Document existing patterns for AI-assisted contributions
   - Include test structure examples and assertion cheatsheet

7. **Add upgrade path testing** (previous chart version -> current)
   - Critical for a chart with complex stateful dependencies
   - UPGRADE.md exists documenting breaking changes - tests should validate these

### Priority 2 (Nice-to-Have)

8. **Add values.schema.json** for JSON Schema validation
   - Provides IDE autocompletion for users
   - Catches invalid values before `helm install`
   - Can be auto-generated from values.yaml comments

9. **Add Polaris or Datree** for Kubernetes best-practice enforcement
   - Complement Trivy with policy-based checks
   - Enforce organizational standards

10. **Add Helm plugin caching** in CI workflows
    - helm-unittest plugin is installed fresh every run
    - Cache to reduce CI time

## Comparison to Gold Standards

| Dimension | langfuse-k8s | odh-dashboard | notebooks | kserve |
|-----------|-------------|---------------|-----------|--------|
| Unit Tests | helm-unittest (11 suites) | Jest + Cypress (multi-layer) | Shell-based validation | Go testing + envtest |
| Integration/E2E | None | Cypress E2E + contract tests | Image boot testing | E2E with Kind |
| Build Integration | Helm lint only | Multi-mode build validation | 5-layer image validation | Multi-version testing |
| Image Testing | None | Container startup tests | Comprehensive image validation | Deployment testing |
| Coverage Tracking | None | Codecov with enforcement | Per-image test tracking | Codecov with thresholds |
| CI/CD Automation | Strong (5 workflows) | Comprehensive | Strong | Comprehensive |
| Security Scanning | zizmor only | SAST + container scanning | Trivy + SBOM | CodeQL + Trivy |
| Agent Rules | None | Comprehensive .claude/rules/ | None | None |
| Input Validation | Extensive (269 lines) | N/A (operator pattern) | N/A | CRD validation |

## File Paths Reference

### CI/CD
- `.github/workflows/test.yaml` - Helm unit tests
- `.github/workflows/validate.yaml` - Helm lint + docs validation
- `.github/workflows/release.yaml` - Chart packaging and release
- `.github/workflows/zizmor.yml` - GitHub Actions security
- `.github/workflows/update-langfuse-version.yml` - Automated version bumps
- `.github/dependabot.yml` - Dependency updates

### Testing
- `charts/langfuse/tests/basic_test.yaml` - Basic chart functionality (112 lines)
- `charts/langfuse/tests/redis-cluster_test.yaml` - Redis configuration (550 lines)
- `charts/langfuse/tests/auth-providers_test.yaml` - Auth provider rendering (219 lines)
- `charts/langfuse/tests/ingress_test.yaml` - Ingress configuration (188 lines)
- `charts/langfuse/tests/downward-api_test.yaml` - Downward API env vars (166 lines)
- `charts/langfuse/tests/clickhouse-cluster_test.yaml` - ClickHouse config (138 lines)
- `charts/langfuse/tests/s3-media-upload-validation_test.yaml` - S3 validation (94 lines)
- `charts/langfuse/tests/minimal-installation_test.yaml` - Example values (83 lines)
- `charts/langfuse/tests/extra-containers_test.yaml` - Sidecar injection (64 lines)
- `charts/langfuse/tests/extra-env_test.yaml` - Environment variables (34 lines)
- `charts/langfuse/tests/hpa_test.yaml` - HPA annotations (26 lines)
- `charts/langfuse/tests/values/` - Test scenario value files
- `charts/langfuse/values.lint.yaml` - Base values for linting/testing

### Templates
- `charts/langfuse/templates/web/deployment.yaml` - Web deployment
- `charts/langfuse/templates/worker/deployment.yaml` - Worker deployment
- `charts/langfuse/templates/web/service.yaml` - Web service
- `charts/langfuse/templates/ingress.yaml` - Ingress resource
- `charts/langfuse/templates/validations.yaml` - Input validation (269 lines)
- `charts/langfuse/templates/_helpers.tpl` - Template helpers
- `charts/langfuse/templates/serviceaccount.yaml` - ServiceAccount
- `charts/langfuse/templates/nextauth-secret.yaml` - NextAuth secret
- `charts/langfuse/templates/postgresql-secret.yaml` - PostgreSQL secret
- `charts/langfuse/templates/web/hpa.yaml` - Web HPA
- `charts/langfuse/templates/worker/hpa.yaml` - Worker HPA
- `charts/langfuse/templates/web/pdb.yaml` - Web PDB
- `charts/langfuse/templates/worker/pdb.yaml` - Worker PDB
- `charts/langfuse/templates/web/vpa.yaml` - Web VPA (untested)
- `charts/langfuse/templates/worker/vpa.yaml` - Worker VPA (untested)
- `charts/langfuse/templates/web/scaled-object.yaml` - Web KEDA (untested)
- `charts/langfuse/templates/worker/scaled-object.yaml` - Worker KEDA (untested)
- `charts/langfuse/templates/extra-manifests.yaml` - Custom manifests (untested)

### Chart Configuration
- `charts/langfuse/Chart.yaml` - Chart metadata (v1.5.33, appVersion 3.177.0)
- `charts/langfuse/values.yaml` - Default values (779 lines)
- `charts/langfuse/.helmignore` - Helm ignore patterns

### Documentation
- `README.md` - Repository overview
- `UPGRADE.md` - Upgrade guide with breaking changes
- `TROUBLESHOOTING.md` - Common issues and solutions
- `examples/minimal-installation/` - Example values files
- `examples/upgrade-v0.13-to-v1.0/` - Migration values

### Security
- `.github/CODEOWNERS` - Code ownership
- `.github/workflows/zizmor.yml` - Actions security scanning
