---
repository: "opendatahub-io/spark-operator"
overall_score: 7.7
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Good Ginkgo/Gomega suite with envtest; 42 test files, 0.76 test-to-code LOC ratio"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Excellent dual-method (Helm + Kustomize) E2E across 9 Kubernetes versions (v1.24-v1.32)"
  - dimension: "Build Integration"
    score: 7.0
    status: "Konflux pipelines for PR/push/release; multi-arch builds; centralized pipeline from odh-konflux-central"
  - dimension: "Image Testing"
    score: 5.5
    status: "Images loaded to KIND for E2E but Trivy runs weekly only; no PR-time scanning or SBOM"
  - dimension: "Coverage Tracking"
    score: 7.5
    status: "Codecov with separate unit/e2e flags and auto threshold with 1% regression tolerance"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "17 workflows with concurrency control, multi-version matrix, reusable workflows, composite actions"
  - dimension: "Agent Rules"
    score: 3.0
    status: "CLAUDE.md with project context present but no .claude/rules/ for test automation guidance"
critical_gaps:
  - title: "No PR-time container vulnerability scanning"
    impact: "Security vulnerabilities in dependencies only detected weekly; can ship to production undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No SBOM generation or image signing"
    impact: "Supply chain compliance gaps; no verifiable software bill of materials for production images"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Weak pre-commit hooks (only helm-docs)"
    impact: "Code quality checks only enforced in CI, not at developer commit time"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No CodeQL or SAST in PR workflow"
    impact: "Static analysis security findings not surfaced until weekly Semgrep runs"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catch security vulnerabilities before merge; already have Trivy workflow as template"
  - title: "Expand pre-commit hooks with golangci-lint and go-vet"
    effort: "1-2 hours"
    impact: "Shift-left code quality checks to developer workstation"
  - title: "Add CodeQL workflow for Go"
    effort: "1-2 hours"
    impact: "Automated SAST on every PR; GitHub provides free CodeQL for open source"
  - title: "Create basic .claude/rules/ for test patterns"
    effort: "2-3 hours"
    impact: "Guide AI-assisted test generation with project-specific Ginkgo/envtest patterns"
recommendations:
  priority_0:
    - "Add Trivy container scanning to PR workflow to catch vulnerabilities before merge"
    - "Add SBOM generation to Konflux pipelines for supply chain compliance"
  priority_1:
    - "Add CodeQL SAST workflow for Go security analysis on PRs"
    - "Expand pre-commit hooks to include golangci-lint, go-vet, go-fmt"
    - "Create .claude/rules/ with Ginkgo/envtest test patterns for AI-assisted development"
    - "Add strict coverage threshold enforcement (e.g., minimum 60% for new code)"
  priority_2:
    - "Add image signing/attestation with cosign for supply chain security"
    - "Add performance regression testing for operator reconciliation loops"
    - "Consolidate E2E test suites (test/e2e/ and examples/openshift/tests/e2e/) as noted in CLAUDE.md"
---

# Quality Analysis: opendatahub-io/spark-operator

## Executive Summary

- **Overall Score: 7.7/10**
- **Repository Type**: Kubernetes Operator (Go, controller-runtime)
- **Tech Stack**: Go 1.24 | Ginkgo/Gomega | envtest | Helm 3 | Kustomize | Tekton/Konflux
- **Key Strengths**: Exceptional E2E test coverage across 9 Kubernetes versions with dual installation methods (Helm + Kustomize), well-organized CI/CD with 17 workflows, comprehensive Semgrep security rules, and Konflux build integration
- **Critical Gaps**: No PR-time container vulnerability scanning, no SBOM generation, weak pre-commit hooks
- **Agent Rules Status**: Partial - CLAUDE.md present with project documentation, but no `.claude/rules/` for test automation guidance

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Good Ginkgo/Gomega suite with envtest; 42 test files, 0.76 test-to-code LOC ratio |
| Integration/E2E | 9.0/10 | Excellent dual-method E2E across 9 K8s versions (v1.24-v1.32) |
| **Build Integration** | **7.0/10** | **Konflux pipelines configured; multi-arch builds; centralized pipeline** |
| Image Testing | 5.5/10 | Images loaded to KIND for E2E but Trivy weekly only; no PR-time scanning or SBOM |
| Coverage Tracking | 7.5/10 | Codecov with separate unit/e2e flags, auto threshold with 1% tolerance |
| CI/CD Automation | 8.5/10 | 17 workflows, concurrency control, multi-version matrix, reusable workflows |
| Agent Rules | 3.0/10 | CLAUDE.md with project context but no .claude/rules/ for test patterns |

## Critical Gaps

1. **No PR-time container vulnerability scanning**
   - Impact: Security vulnerabilities in dependencies only detected weekly via scheduled Trivy scan; can ship to production undetected
   - Severity: HIGH
   - Effort: 2-4 hours
   - Current state: `trivy-image-scanning.yaml` runs weekly on Monday at 00:00, not on PRs

2. **No SBOM generation or image signing**
   - Impact: Supply chain compliance gaps; Konflux pipelines build images but no verifiable SBOM or cosign attestation
   - Severity: HIGH
   - Effort: 4-6 hours

3. **Weak pre-commit hooks**
   - Impact: Pre-commit only runs helm-docs; no Go linting, formatting, or vet checks at commit time
   - Severity: MEDIUM
   - Effort: 1-2 hours

4. **No CodeQL or PR-time SAST**
   - Impact: Semgrep rules exist in `semgrep.yaml` but no workflow runs them on PRs; CodeQL absent
   - Severity: MEDIUM
   - Effort: 2-3 hours

## Quick Wins

1. **Add Trivy scanning to PR workflow** (1-2 hours)
   - Impact: Catch security vulnerabilities before merge
   - Already have `trivy-image-scanning.yaml` as a template; add trigger on `pull_request`
   - Implementation: Add Trivy step to `integration.yaml` after image build

2. **Expand pre-commit hooks** (1-2 hours)
   - Impact: Shift-left code quality checks to developer workstation
   - Implementation: Add golangci-lint, go-vet, go-fmt to `.pre-commit-config.yaml`

3. **Add CodeQL workflow** (1-2 hours)
   - Impact: Automated SAST on every PR; free for open source projects
   - Implementation: Standard GitHub CodeQL configuration for Go

4. **Create .claude/rules/ for test patterns** (2-3 hours)
   - Impact: Guide AI-assisted test generation with Ginkgo/envtest patterns
   - Implementation: Create rules for unit tests, E2E tests, webhook tests

## Detailed Findings

### CI/CD Pipeline

**Workflows (17 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `integration.yaml` | PR + Push | Code checks, unit tests, helm tests, E2E on 9 K8s versions |
| `kustomize-e2e.yaml` | PR + Push (path-filtered) | Kustomize-based E2E on 9 K8s versions |
| `codecov.yaml` | PR + Push | Coverage upload to Codecov |
| `scheduledspark-smoke.yaml` | PR + Push (path-filtered) | ScheduledSparkApplication smoke test |
| `trivy-image-scanning.yaml` | Weekly (Monday) | Container vulnerability scanning |
| `scorecard.yaml` | Weekly + Push to master | OSSF Scorecard supply chain security |
| `stale.yaml` | Every 2 hours | Mark stale issues/PRs |
| `build-quay.yaml` | Manual dispatch | Build and push to Quay |
| `pushImageToDPQuay.yaml` | Manual dispatch | Push Spark image to data-processing Quay |
| `openshift-docling-e2e.yaml` | Manual + Push (path-filtered) | EC2 runner E2E with docling workload |
| `integration-odh.yaml` | Push + Manual | ODH Spark Pi E2E on KIND |
| `release.yaml` | Push to release-* | Build and publish release |
| `release-latest-images.yaml` | Push to master | Build latest images |
| `release-helm-charts.yaml` | Release published | Publish Helm charts |
| `helm-release.yaml` | Push to main (chart paths) | Release Helm charts |
| `check-release.yaml` | PR to release-* | Validate semver pattern |
| `_run-kustomize-e2e.yaml` | Reusable workflow | Shared Kustomize E2E logic |

**Strengths:**
- Concurrency control on all PR/push workflows with `cancel-in-progress: true`
- Multi-version K8s matrix testing (9 versions: v1.24 through v1.32)
- Reusable workflow pattern (`_run-kustomize-e2e.yaml`)
- Composite action for cluster setup (`.github/actions/kind-cluster-setup/`)
- Path-filtered triggers to avoid unnecessary CI runs
- Debug/failure diagnostics in E2E workflows (pod logs, events, SparkApp status)

**Gaps:**
- No caching of Go modules or build artifacts in PR workflows
- Trivy scanning is scheduled-only, not PR-triggered
- No Semgrep CI workflow despite having comprehensive `semgrep.yaml` rules

### Test Coverage

**Unit Tests (42 files, 13,314 LOC):**
- Framework: Go testing + Ginkgo/Gomega + envtest (controller-runtime test harness)
- Coverage areas: controllers, webhooks, schedulers, certificates, utilities, API defaults
- Test-to-code ratio: 0.76 (13,314 test LOC / 17,456 source LOC)
- Coverage output: `cover.out` (unit), `cover-e2e.out` (Helm E2E), `cover-e2e-kustomize.out` (Kustomize E2E)

**E2E Tests (Two parallel suites):**

| Suite | Location | Install Method | Framework |
|-------|----------|---------------|-----------|
| Upstream E2E | `test/e2e/` | Helm | Ginkgo/Gomega |
| OpenShift E2E | `examples/openshift/tests/e2e/` | Helm or Kustomize | Ginkgo/Gomega |

- Both suites test SparkApplication and SparkConnect CRDs
- OpenShift suite adds: SparkUI, ScheduledSparkApplication, Prometheus metrics, SparkConnect query tests
- OpenShift suite supports three install methods: Helm, Kustomize, Preinstalled
- Both validate webhook readiness before running tests

**Helm Chart Tests (20 test files):**
- Categories: controller, webhook, certmanager, hook, prometheus, spark
- Tests: deployments, services, RBAC, PDB, webhook configs, service accounts

**Shell-based Integration Tests:**
- `test-operator-install.sh`, `test-spark-pi.sh`, `test-docling-spark.sh`
- Used in OpenShift/Docling E2E workflows

### Code Quality

**Linting:**
- golangci-lint v2.1.6 with 7 linters enabled:
  - `copyloopvar`, `dupword`, `importas`, `predeclared`, `tagalign`, `unconvert`, `unused`
  - Plus `goimports` formatter
- Import alias enforcement for k8s packages
- Reasonable limits: 50 issues/linter, 3 same issues

**Pre-commit Hooks:**
- Only `helm-docs` configured (v1.13.1)
- Missing: golangci-lint, go-fmt, go-vet, gitleaks

**Static Analysis:**
- **Semgrep**: Comprehensive `semgrep.yaml` with 40+ rules covering Go, Python, TS, YAML, Dockerfile, Shell
  - Go: exec injection, TLS skip verify, SQL injection, hardcoded credentials, log sensitive data
  - K8s: RBAC privilege escalation, privileged containers, hostPath, secrets in configmaps
  - GitHub Actions: script injection, pull_request_target checkout
  - Generic: secret detection (AWS, GitHub, Slack, Google)
- **Gitleaks**: Configured with allowlists for test files, fixtures, mock data
- **OSSF Scorecard**: Runs weekly for supply chain security assessment
- **Missing**: CodeQL, no Semgrep CI workflow

### Container Images

**Dockerfiles:**
- `Dockerfile` (main): Multi-stage build (golang:1.24.10 builder → spark:4.0.1 base)
  - BuildKit cache mounts for Go modules and build cache
  - Non-root user (UID 185)
  - Multi-arch support via `TARGETARCH` build arg
- `examples/openshift/Dockerfile`: OpenShift-specific build
- `examples/openshift/tests/Dockerfile`: Test image
- `spark-docker/Dockerfile`: Spark base image

**Build Process:**
- Image built and loaded into KIND cluster for E2E testing
- Multi-platform builds via `docker buildx` (linux/amd64, linux/arm64)
- Konflux multi-arch build pipeline from `odh-konflux-central`

**Gaps:**
- Trivy scanning weekly only, not on PRs
- No SBOM generation
- No image signing/attestation (cosign)
- No container runtime validation tests (e.g., startup probe testing)

### Security

**Present:**
- Trivy image scanning (weekly)
- Gitleaks secret detection (configured, allowlisted)
- Semgrep security rules (comprehensive, 40+ rules)
- OSSF Scorecard (weekly)
- Non-root container user
- Concurrency control on workflows
- Permissions: `contents: read` on most workflows

**Missing:**
- CodeQL (no SAST in PR workflow)
- No Semgrep CI workflow (rules exist but aren't run automatically)
- No PR-time vulnerability scanning
- No dependency scanning (Dependabot/Renovate)
- No SBOM or image attestation

### Build Integration (Konflux/Tekton)

**Tekton Pipelines (5 files):**
- `spark-operator-pull-request.yaml`: Builds ODH image on PRs, outputs to `quay.io/opendatahub/spark-operator:odh-pr`
- `spark-operator-push.yaml`: Builds on push to main
- `spark-operator-ci-pull-request.yaml`: CI pipeline with full inline `pipelineSpec`, image expires after 5 days
- `spark-operator-ci-push.yaml`: CI push pipeline
- `spark-operator-release-push.yaml`: Release build pipeline

**Strengths:**
- Uses centralized pipeline from `odh-konflux-central` (multi-arch container build)
- PR images tagged with revision hash for traceability
- CI images set to expire after 5 days
- Separate component for CI builds (`spark-operator-ci`)

**Gaps:**
- No explicit test step in Tekton pipelines (relies on GitHub Actions for testing)
- No Konflux-specific integration testing in GH Actions

### Agent Rules (Agentic Flow Quality)

**Status**: Partial

**Present:**
- `CLAUDE.md` in repository root with comprehensive project documentation:
  - Tech stack, project structure, build commands, test commands
  - Kustomize install configuration details
  - Container image configuration explanation
  - Key files reference
  - CI overview

**Missing:**
- No `.claude/` directory
- No `.claude/rules/` with test creation rules
- No `AGENTS.md`
- No test automation guidance for AI agents
- No Ginkgo/envtest patterns documentation for AI-assisted development

**Recommendation**: Generate test rules with `/test-rules-generator` covering:
- Unit test patterns (envtest + Ginkgo/Gomega)
- E2E test patterns (KIND cluster + Helm/Kustomize install)
- Webhook validation test patterns
- Controller reconciliation test patterns

## Recommendations

### Priority 0 (Critical)

1. **Add Trivy container scanning to PR workflow**
   - Add Trivy step to `integration.yaml` after `docker-build` step
   - Block merge on CRITICAL/HIGH vulnerabilities
   - Template already exists in `trivy-image-scanning.yaml`

2. **Add SBOM generation to build pipeline**
   - Use `syft` or `trivy sbom` in Konflux pipeline
   - Attach SBOM to image as attestation
   - Required for supply chain compliance

### Priority 1 (High Value)

3. **Add CodeQL SAST workflow**
   - Standard Go analysis on PR and push
   - Free for open source; surfaces security findings before merge

4. **Create Semgrep CI workflow**
   - Comprehensive `semgrep.yaml` already exists but no workflow runs it
   - Add `semgrep-scan` workflow triggered on PRs

5. **Expand pre-commit hooks**
   - Add: golangci-lint, go-vet, go-fmt, gitleaks
   - Currently only helm-docs is configured

6. **Create `.claude/rules/` for test automation**
   - `unit-tests.md`: Ginkgo/Gomega + envtest patterns for controller/webhook tests
   - `e2e-tests.md`: KIND cluster setup, Helm/Kustomize install, SparkApplication lifecycle
   - `helm-tests.md`: Helm chart unittest patterns

7. **Add strict coverage threshold**
   - Current: auto threshold with 1% tolerance (allows gradual decline)
   - Recommended: Set minimum 60% for new code (`patch.target: 60%`)

### Priority 2 (Nice-to-Have)

8. **Add image signing with cosign**
   - Sign images built in Konflux pipeline
   - Verify signatures in deployment workflows

9. **Consolidate E2E test suites**
   - As noted in CLAUDE.md, `test/e2e/` and `examples/openshift/tests/e2e/` should be unified
   - OpenShift suite already supports both install methods

10. **Add dependency update automation**
    - Configure Dependabot or Renovate for Go module updates
    - Auto-create PRs for security patches

11. **Add Go module caching in CI**
    - `actions/setup-go` already caches but verify cache hits
    - Can reduce CI time significantly for large dependency trees

## Comparison to Gold Standards

| Dimension | spark-operator | odh-dashboard | notebooks | kserve |
|-----------|---------------|---------------|-----------|--------|
| Unit Test Coverage | 0.76 ratio, Ginkgo | Multi-layer, Jest | N/A | Coverage enforcement |
| E2E Testing | 9 K8s versions, 2 install methods | Cypress + API | Image validation | Multi-version |
| Coverage Tracking | Codecov, auto threshold | Codecov enforced | N/A | Strict enforcement |
| Container Scanning | Weekly Trivy only | PR-time scanning | 5-layer validation | PR-time scanning |
| Pre-commit | helm-docs only | Comprehensive | N/A | Comprehensive |
| SAST | Semgrep (rules only) | CodeQL + ESLint | N/A | CodeQL |
| Agent Rules | CLAUDE.md (docs) | Full .claude/rules/ | N/A | N/A |
| Konflux | Multi-arch pipeline | Full integration | Full integration | N/A |
| SBOM | None | Generated | Generated | N/A |

## File Paths Reference

### CI/CD
- `.github/workflows/integration.yaml` - Main PR/push workflow (code checks, tests, E2E)
- `.github/workflows/kustomize-e2e.yaml` - Kustomize-based E2E on 9 K8s versions
- `.github/workflows/codecov.yaml` - Coverage upload
- `.github/workflows/trivy-image-scanning.yaml` - Weekly Trivy scan
- `.github/workflows/scheduledspark-smoke.yaml` - ScheduledSpark smoke test
- `.github/workflows/_run-kustomize-e2e.yaml` - Reusable Kustomize E2E workflow
- `.github/actions/kind-cluster-setup/action.yaml` - Composite action for KIND setup

### Testing
- `test/e2e/` - Upstream Ginkgo E2E suite (Helm install)
- `examples/openshift/tests/e2e/` - OpenShift Ginkgo E2E suite (Helm/Kustomize/Preinstalled)
- `charts/spark-operator-chart/tests/` - 20 Helm chart unit test files

### Build
- `Dockerfile` - Main multi-stage build
- `.tekton/` - 5 Tekton/Konflux pipeline configurations
- `Makefile` - Build, test, deploy targets

### Quality
- `.golangci.yaml` - 7 linters + goimports
- `.pre-commit-config.yaml` - helm-docs only
- `.codecov.yml` - Coverage config with flags
- `.gitleaks.toml` - Secret detection with allowlists
- `semgrep.yaml` - 40+ security rules (Go, Python, TS, YAML, generic)
- `CLAUDE.md` - AI agent project context
