---
repository: "red-hat-data-services/spark-operator"
overall_score: 7.9
scorecard:
  - dimension: "Unit Tests"
    score: 8.0
    status: "Strong unit test coverage with Ginkgo/Gomega + testify; 42 test files covering controllers, webhooks, schedulers, and utilities (9,280+ lines of test code)"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Exceptional E2E: dual install paths (Helm + Kustomize), 9 Kubernetes versions matrix, OpenShift E2E with SparkConnect, ScheduledSpark, Prometheus metrics, and Spark UI tests"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR-time Docker build + Helm chart testing + Minikube install; Konflux build via Tekton but not simulated at PR time"
  - dimension: "Image Testing"
    score: 6.5
    status: "Multi-arch Konflux builds (x86_64, arm64, ppc64le, s390x); KIND image loading validates startup; no explicit image runtime tests"
  - dimension: "Coverage Tracking"
    score: 8.0
    status: "Codecov integration with separate unit/e2e flags, auto-threshold with 1% tolerance, PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "17 workflows with concurrency control, path-based triggers, reusable workflows, custom composite actions, comprehensive PR checks"
  - dimension: "Agent Rules"
    score: 7.5
    status: "Detailed CLAUDE.md with project structure, build/test/lint commands, key files, and debugging guidance; no .claude/rules/ directory for test-specific patterns"
critical_gaps:
  - title: "No PR-time Konflux build simulation"
    impact: "Konflux build failures (RPM deps, FIPS compliance, multi-arch) discovered only post-merge in Tekton pipelines"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No container image runtime validation"
    impact: "Image startup or entrypoint issues not caught until deployment; operator may build but fail to run"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Trivy scanning is scheduled-only, not PR-triggered"
    impact: "Vulnerability-introducing PRs merge without security feedback; weekly scan means up to 7-day exposure window"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "No SAST in PR workflow"
    impact: "Semgrep rules exist but no CI workflow runs them; security issues may be committed"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "2-3 hours"
    impact: "Catch CVEs before merge instead of weekly; immediate security posture improvement"
  - title: "Add Semgrep to PR workflow"
    effort: "2-3 hours"
    impact: "Leverage existing 60+ rule semgrep.yaml for automated SAST on every PR"
  - title: "Add .claude/rules/ with test creation patterns"
    effort: "3-4 hours"
    impact: "Standardize AI-generated tests to match existing Ginkgo/envtest patterns"
  - title: "Add e2e-test target to PR workflow with coverage upload"
    effort: "3-4 hours"
    impact: "PR-time E2E coverage reporting matches existing Kustomize E2E coverage"
recommendations:
  priority_0:
    - "Add Konflux build simulation to PR workflow (Dockerfile.konflux build with hermetic mode)"
    - "Move Trivy image scanning from weekly schedule to PR trigger"
    - "Add Semgrep CI workflow using existing semgrep.yaml rules"
  priority_1:
    - "Add container runtime validation (image startup + entrypoint test in KIND)"
    - "Create .claude/rules/ directory with test patterns for unit, e2e, webhook, and scheduler tests"
    - "Add CRD validation testing (apply generated CRDs to cluster, verify schema)"
    - "Add pre-commit hooks for Go linting and code generation (currently only has helm-docs)"
  priority_2:
    - "Add SBOM generation and attestation to release workflow"
    - "Add Gitleaks to PR workflow (config exists but no CI integration)"
    - "Add performance regression testing for SparkApplication reconciliation"
    - "Add OSSF Scorecard to PR workflow (currently only runs on push to master)"
---

# Quality Analysis: spark-operator

## Executive Summary

- **Overall Score: 7.9/10**
- **Repository Type**: Kubernetes Operator (Go, controller-runtime)
- **Primary Language**: Go 1.24 with Ginkgo/Gomega test framework
- **Key Strengths**: Exceptional E2E test infrastructure with dual install paths (Helm + Kustomize), 9-version Kubernetes matrix, comprehensive unit tests across controllers/webhooks/schedulers, Codecov integration with separate unit/e2e flags, well-organized CI with 17 workflows
- **Critical Gaps**: No PR-time Konflux build simulation, Trivy/Semgrep not running on PRs, no container image runtime validation
- **Agent Rules Status**: CLAUDE.md present with detailed project documentation; no `.claude/rules/` directory for test-specific patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.0/10 | Strong coverage with Ginkgo/envtest across controllers, webhooks, schedulers |
| Integration/E2E | 9.0/10 | Dual install paths, 9 K8s versions, OpenShift E2E with SparkConnect |
| **Build Integration** | **7.0/10** | **PR-time Docker build + Helm install; no Konflux simulation** |
| Image Testing | 6.5/10 | Multi-arch Konflux builds; no explicit image runtime validation |
| Coverage Tracking | 8.0/10 | Codecov with unit/e2e flags, auto threshold, PR reporting |
| CI/CD Automation | 8.5/10 | 17 workflows, concurrency control, reusable workflows |
| Agent Rules | 7.5/10 | Detailed CLAUDE.md; missing .claude/rules/ test patterns |

## Critical Gaps

### 1. No PR-time Konflux Build Simulation
- **Impact**: Konflux builds use `Dockerfile.konflux` with UBI9 base, FIPS-compliant Go flags (`CGO_ENABLED=1`, `GOEXPERIMENT=strictfipsruntime`), RPM dependencies, and PySpark installation. None of this is validated at PR time. Breakages in the Konflux build path are discovered only after merge in Tekton pipelines.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Evidence**: `.tekton/spark-operator-ci-pull-request.yaml` runs Konflux pipeline post-PR, but the GitHub PR workflow (`integration.yaml`) only builds with the standard `Dockerfile`

### 2. No Container Image Runtime Validation
- **Impact**: Images are built and loaded into KIND clusters, but there's no explicit test that validates the image starts correctly, the entrypoint works, and the operator process initializes. Issues with image layering, missing dependencies, or entrypoint scripts are caught late.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Evidence**: `kind-load-image` target loads the image but E2E suite assumes it works

### 3. Trivy Scanning is Scheduled-Only
- **Impact**: The `trivy-image-scanning.yaml` workflow only runs weekly (Monday at 00:00) and on manual dispatch. PRs that introduce vulnerable dependencies merge without security feedback. Up to 7-day exposure window.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Evidence**: `.github/workflows/trivy-image-scanning.yaml` trigger: `schedule: - cron: '0 0 * * 1'`

### 4. Semgrep Rules Exist But No CI Integration
- **Impact**: A comprehensive `semgrep.yaml` with 60+ rules covering Go, Python, TypeScript, YAML, and generic secrets detection exists in the repository root. However, no GitHub Actions workflow runs these rules, making them documentation-only.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Evidence**: `semgrep.yaml` (62KB, 60+ rules) exists but no `.github/workflows/semgrep.yaml`

## Quick Wins

### 1. Add Trivy Scanning to PR Workflow (2-3 hours)
- **Impact**: Catch CVEs before merge instead of weekly
- **Implementation**: Add Trivy step to `integration.yaml` or create dedicated PR-triggered workflow:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@0.33.1
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

### 2. Add Semgrep to PR Workflow (2-3 hours)
- **Impact**: Leverage existing 60+ rules for automated SAST
- **Implementation**: Create `.github/workflows/semgrep.yaml`:
```yaml
- name: Run Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: semgrep.yaml
```

### 3. Add `.claude/rules/` Test Patterns (3-4 hours)
- **Impact**: Standardize AI-generated tests to follow existing patterns
- **Details**: Create rules for unit tests (envtest + Ginkgo), E2E tests (Helm/Kustomize install), webhook tests, and scheduler tests

### 4. Add Gitleaks to PR Workflow (1-2 hours)
- **Impact**: Automated secret detection using existing `.gitleaks.toml` configuration
- **Implementation**: Add Gitleaks action to `integration.yaml`

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (17 workflows)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `integration.yaml` | PR + Push | Code checks, unit tests, Helm tests, E2E (9 K8s versions) |
| `kustomize-e2e.yaml` | PR + Push | Kustomize-based E2E tests (9 K8s versions) |
| `integration-odh.yaml` | Push + Dispatch | OpenShift/KIND Spark Pi E2E |
| `openshift-docling-e2e.yaml` | Push + Dispatch | Heavy docling-spark E2E tests |
| `scheduledspark-smoke.yaml` | PR + Push | ScheduledSparkApplication smoke tests |
| `codecov.yaml` | PR + Push | Coverage upload to Codecov |
| `build-quay.yaml` | Dispatch | Build and push to Quay.io |
| `trivy-image-scanning.yaml` | Schedule (weekly) | Vulnerability scanning |
| `scorecard.yaml` | Schedule + Push | OSSF Scorecard supply-chain security |
| `check-release.yaml` | PR (release branches) | Version validation |
| `release.yaml` | Push (release branches) | Release builds |
| `helm-release.yaml` | Push (chart changes) | Helm chart release |
| `release-latest-images.yaml` | Push | Latest image releases |
| `release-helm-charts.yaml` | Push | Chart repository updates |
| `pushImageToDPQuay.yaml` | Push | DP Quay image push |
| `stale.yaml` | Schedule | Stale issue/PR management |
| `_run-kustomize-e2e.yaml` | Reusable | Reusable Kustomize E2E workflow |

**Strengths**:
- Excellent concurrency control (`cancel-in-progress: true` on most workflows)
- Path-based triggers avoid unnecessary CI runs
- Reusable workflow pattern (`_run-kustomize-e2e.yaml`) for DRY CI
- Custom composite action (`.github/actions/kind-cluster-setup/`) for cluster setup
- Multi-version K8s testing (v1.24 through v1.32, 9 versions)

**Gaps**:
- No PR-triggered security scanning (Trivy, Semgrep, Gitleaks)
- Codecov runs as separate workflow rather than integrated into test workflows

### Test Coverage

**Unit Tests (8.0/10)**:
- **42 test files** covering:
  - Controller tests: 4,799 lines (sparkapplication: 4,142, scheduledsparkapplication: 183, sparkconnect: 274)
  - Webhook tests: 3,014 lines (sparkpod_defaulter: 2,351 lines - very thorough)
  - Package tests: 1,467 lines (util, certificate, features)
  - API tests: defaults_test.go
  - Scheduler tests: kubescheduler, volcano, yunikorn
- **Test-to-source ratio**: 42 test files / 114 source files = 37%
- **Framework**: Ginkgo/Gomega BDD + stretchr/testify + envtest
- **Coverage generation**: `cover.out` and `cover.html` via Makefile

**E2E Tests (9.0/10)**:
- **Dual install path E2E**:
  - `test/e2e/` - Helm-based install (upstream pattern)
  - `examples/openshift/tests/e2e/` - Kustomize-based install (OpenShift pattern, supports `preinstalled` mode)
- **2,719 lines of E2E test code**
- **Test scenarios**: SparkApplication, SparkConnect, ScheduledSparkApplication, Prometheus metrics, Spark UI, SparkConnect Query
- **Infrastructure**: KIND clusters with envtest, multi-version K8s matrix
- **Coverage**: E2E coverage uploaded to Codecov with separate `e2e-kustomize` flag

**Helm Chart Tests**:
- **20 Helm unittest files** covering controller, webhook, spark, certmanager, hook, and prometheus components
- Helm lint and chart-testing integration
- CRD drift detection between `config/` and `charts/`

### Code Quality

**Linting (Good)**:
- `.golangci.yaml` with 7 enabled linters: copyloopvar, dupword, importas, predeclared, tagalign, unconvert, unused
- Import alias enforcement for Kubernetes packages
- goimports formatter enabled
- Integrated into PR workflow via `make go-lint`

**Pre-commit Hooks (Minimal)**:
- `.pre-commit-config.yaml` exists but only has helm-docs hook
- No Go-specific pre-commit hooks (gofmt, golangci-lint, etc.)

**Static Analysis**:
- Semgrep: Comprehensive `semgrep.yaml` (60+ rules) but **not integrated into CI**
- Gitleaks: `.gitleaks.toml` with thorough path allowlists but **not in PR workflow**
- OSSF Scorecard: Scheduled on push to master only

### Container Images

**Build Process (Good)**:
- **Standard Dockerfile**: Multi-stage (golang:1.24 builder → spark:4.0.1 runtime), build caching, tini process manager
- **Konflux Dockerfile**: UBI9 base, FIPS-compliant build (`CGO_ENABLED=1`, `GOEXPERIMENT=strictfipsruntime`), PySpark installation, Java 17, OpenShift UID compatibility
- **Multi-arch**: Tekton pipeline builds for x86_64, arm64, ppc64le, s390x

**Security (Moderate)**:
- Non-root user (spark UID 185)
- Proper permissions for webhook certs
- OpenShift arbitrary UID compatibility in Konflux image
- Red Hat labels and licensing metadata

**Gaps**:
- No image startup validation test
- No SBOM generation in release workflow
- No image signing/attestation

### Security

**Present**:
- Gitleaks configuration (`.gitleaks.toml`) with comprehensive path allowlists
- Semgrep rules (60+ rules covering Go, Python, TS, YAML, secrets)
- Trivy image scanning (weekly schedule)
- OSSF Scorecard (scheduled)
- Permissions: `contents: read` default on most workflows
- Pin-hash actions in Tekton pipelines (Konflux)

**Missing**:
- No PR-triggered security scanning
- No CodeQL/SAST in CI
- No dependency scanning (Dependabot/Renovate)
- No image signing or attestation

### Agent Rules (Agentic Flow Quality)

**Status**: Present (CLAUDE.md) but Incomplete (no `.claude/rules/`)

**CLAUDE.md Quality (7.5/10)**:
- Comprehensive project structure documentation
- Build, test, lint, and debugging commands
- Key file paths for all CRDs and controllers
- Two test location documentation with install method differences
- CI workflow summary

**Gaps**:
- No `.claude/` directory or `.claude/rules/` for test creation patterns
- No test-specific guidance (how to write unit tests with envtest, E2E patterns, webhook test patterns)
- No `AGENTS.md` for broader agent guidance
- **Recommendation**: Generate missing rules with `/test-rules-generator` skill

## Recommendations

### Priority 0 (Critical)

1. **Add Konflux build simulation to PR workflow**
   - Build `Dockerfile.konflux` in PR workflow to catch FIPS, RPM, and base image issues early
   - Example: `docker build -f Dockerfile.konflux --target builder .` (at minimum validate the builder stage)

2. **Move Trivy scanning to PR trigger**
   - Add `pull_request` trigger to `trivy-image-scanning.yaml` or add Trivy step to `integration.yaml`
   - Use `scan-type: 'fs'` for filesystem scanning (faster than image scanning)

3. **Add Semgrep CI workflow**
   - Create workflow using existing `semgrep.yaml` rules
   - Block PRs on CRITICAL/HIGH findings

### Priority 1 (High Value)

4. **Add container runtime validation**
   - After KIND image load, run explicit image startup test
   - Validate entrypoint.sh works, operator binary responds to `--version`

5. **Create `.claude/rules/` directory**
   - Unit test rules (envtest setup, Ginkgo patterns, controller test structure)
   - E2E test rules (Helm vs Kustomize install, KIND cluster setup)
   - Webhook test rules (sparkpod_defaulter patterns)
   - Scheduler test rules

6. **Expand pre-commit hooks**
   - Add gofmt, golangci-lint, go-vet, codegen verification hooks
   - Currently only has helm-docs

7. **Add CRD validation testing**
   - Validate generated CRDs apply cleanly to cluster
   - Test CRD versioning and conversion webhooks

### Priority 2 (Nice-to-Have)

8. **Add SBOM generation to release workflow**
   - Use Syft or Trivy for SBOM generation
   - Attach to release artifacts

9. **Add Gitleaks to PR workflow**
   - Leverage existing `.gitleaks.toml` configuration

10. **Add dependency update automation**
    - Dependabot or Renovate for Go modules and GitHub Actions

11. **Add performance regression testing**
    - Measure reconciliation latency for SparkApplication/ScheduledSparkApplication
    - Track over time in CI

## Comparison to Gold Standards

| Feature | spark-operator | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|---------|---------------|---------------------|-------------------|---------------|
| Unit Tests | Ginkgo + envtest | Jest + React Testing Library | Python pytest | Go testing + envtest |
| E2E Tests | Dual path (Helm + Kustomize) | Cypress + contract tests | Image validation | KServe predictor tests |
| K8s Version Matrix | 9 versions (v1.24-v1.32) | N/A | N/A | Multi-version |
| Coverage Tracking | Codecov (unit + e2e flags) | Codecov with enforcement | Basic | Codecov with threshold |
| Security Scanning | Trivy (weekly only) | Trivy + Semgrep in PR | Trivy + SBOM | Trivy in PR |
| Pre-commit | helm-docs only | Full suite | Basic | golangci-lint |
| Agent Rules | CLAUDE.md (detailed) | CLAUDE.md + .claude/rules/ | Minimal | Minimal |
| Image Testing | KIND load only | N/A | 5-layer validation | Container tests |
| SAST | Semgrep (not in CI) | Semgrep in CI | N/A | CodeQL |
| Helm Tests | 20 unittest files | N/A | N/A | Helm tests |
| Konflux | Tekton pipelines | Konflux pipelines | Konflux | N/A |

## File Paths Reference

### CI/CD
- `.github/workflows/integration.yaml` - Main PR/push workflow
- `.github/workflows/kustomize-e2e.yaml` - Kustomize E2E tests
- `.github/workflows/_run-kustomize-e2e.yaml` - Reusable E2E workflow
- `.github/workflows/codecov.yaml` - Coverage upload
- `.github/workflows/trivy-image-scanning.yaml` - Weekly Trivy scan
- `.github/workflows/scheduledspark-smoke.yaml` - ScheduledSpark smoke
- `.github/actions/kind-cluster-setup/action.yaml` - Custom composite action
- `.tekton/` - Konflux/Tekton pipeline definitions

### Testing
- `test/e2e/` - Upstream E2E tests (Helm install path)
- `examples/openshift/tests/e2e/` - OpenShift E2E tests (Kustomize/preinstalled)
- `internal/controller/sparkapplication/controller_test.go` - Main controller unit tests (1,440 lines)
- `internal/webhook/sparkpod_defaulter_test.go` - Webhook defaulter tests (2,351 lines)
- `charts/spark-operator-chart/tests/` - 20 Helm unit test files

### Code Quality
- `.golangci.yaml` - 7 linters enabled
- `.pre-commit-config.yaml` - helm-docs only
- `semgrep.yaml` - 60+ rules (not in CI)
- `.gitleaks.toml` - Secret detection config (not in CI)
- `.codecov.yml` - Coverage thresholds and flags

### Container Images
- `Dockerfile` - Standard multi-stage build
- `Dockerfile.konflux` - UBI9/FIPS-compliant build
- `entrypoint.sh` - Container entrypoint script

### Agent Rules
- `CLAUDE.md` - Detailed project documentation (7,136 bytes)
