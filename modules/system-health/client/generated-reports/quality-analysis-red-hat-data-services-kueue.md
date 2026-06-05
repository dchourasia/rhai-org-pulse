---
repository: "red-hat-data-services/kueue"
overall_score: 7.4
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test-to-code ratio (0.50) with 226 test files, 119K LOC of tests vs 73K source. Go testing + Ginkgo/Gomega framework. Coverage profiling enabled via -coverprofile."
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Comprehensive envtest-based integration suites (25+ suites), multi-version E2E across K8s 1.30-1.32, multi-cluster (MultiKueue), TAS, cert-manager, and custom configs E2E variants."
  - dimension: "Build Integration"
    score: 4.0
    status: "No PR-triggered CI workflows in the fork. Konflux pipeline builds on PR but only validates container image build, not functional tests. No PR-time integration or E2E test execution."
  - dimension: "Image Testing"
    score: 5.0
    status: "Three Dockerfiles (upstream, Konflux, RHOAI) with multi-arch support (x86_64, arm64, ppc64le, s390x). No runtime validation, startup testing, or container security scanning in CI."
  - dimension: "Coverage Tracking"
    score: 4.0
    status: "Unit tests generate cover.out via -coverprofile but no Codecov/Coveralls integration, no coverage thresholds, and no PR coverage reporting in the downstream fork."
  - dimension: "CI/CD Automation"
    score: 5.0
    status: "Fork has only 5 dispatch-only workflows (build/publish, release, SBOM, OpenVEX, Krew). No PR-triggered test workflows. Relies on upstream Prow CI. Konflux pipeline for PR image builds."
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory. No AI agent test automation guidance."
critical_gaps:
  - title: "No PR-triggered test CI in the downstream fork"
    impact: "Code changes merged without running unit, integration, or E2E tests in CI. Quality regressions can reach production undetected."
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No coverage tracking or enforcement"
    impact: "Coverage can silently regress. No visibility into test coverage trends or PR-level coverage deltas."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container security scanning (Trivy/Snyk/CodeQL)"
    impact: "Vulnerable dependencies or images could ship undetected. Only Snyk policy file exists but no CI integration."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI-generated code and tests lack project-specific guidance, reducing quality and consistency."
    severity: "MEDIUM"
    effort: "4-8 hours"
quick_wins:
  - title: "Add Codecov integration with coverage thresholds"
    effort: "2-4 hours"
    impact: "Immediate visibility into coverage trends and PR-level delta reporting. Prevent coverage regression."
  - title: "Add Trivy container scanning to Konflux pipeline"
    effort: "1-2 hours"
    impact: "Catch known CVEs in container images before merge. Trivial to add as a Tekton task."
  - title: "Create basic agent rules for test patterns"
    effort: "2-3 hours"
    impact: "Standardize AI-generated test quality with project-specific Ginkgo/Gomega patterns."
  - title: "Add PR-triggered unit test workflow"
    effort: "2-4 hours"
    impact: "Catch unit test failures before merge. Reuse existing Makefile test target."
recommendations:
  priority_0:
    - "Add PR-triggered GitHub Actions workflows for unit tests, linting, and integration tests in the downstream fork"
    - "Integrate Codecov with coverage thresholds and PR reporting"
    - "Add container vulnerability scanning (Trivy) to the Konflux pipeline and/or GitHub Actions"
  priority_1:
    - "Add PR-time integration test execution using envtest"
    - "Create comprehensive agent rules for unit, integration, and E2E test patterns"
    - "Add image startup validation testing for built container images"
  priority_2:
    - "Add CodeQL/SAST scanning workflow"
    - "Implement pre-commit hooks for local development quality gates"
    - "Add performance regression testing to CI"
---

# Quality Analysis: red-hat-data-services/kueue

## Executive Summary

- **Overall Score: 7.4/10**
- **Repository Type**: Kubernetes Operator (Go) - downstream fork of `kubernetes-sigs/kueue`
- **Primary Language**: Go 1.24.13
- **Framework**: Kubernetes controller-runtime with Kueue job queueing
- **Key Strengths**: Exceptional upstream test infrastructure with 226 test files (0.50 test-to-code ratio), comprehensive integration suites using envtest, multi-version E2E testing across K8s 1.30-1.32, performance benchmarking, and multi-cluster (MultiKueue) testing
- **Critical Gaps**: No PR-triggered CI in the fork, no coverage tracking, no container scanning, no agent rules
- **Agent Rules Status**: Missing

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent coverage with Go testing + Ginkgo/Gomega, 119K LOC tests |
| Integration/E2E | 9.0/10 | 25+ envtest integration suites, multi-version E2E, MultiKueue, TAS |
| **Build Integration** | **4.0/10** | **No PR-time functional testing. Konflux builds images only.** |
| Image Testing | 5.0/10 | Multi-arch Dockerfiles but no runtime validation or scanning |
| Coverage Tracking | 4.0/10 | Cover.out generated but no CI integration or enforcement |
| CI/CD Automation | 5.0/10 | Fork relies on upstream Prow. Only dispatch workflows locally. |
| Agent Rules | 0.0/10 | No AI agent guidance present |

**Weighted Overall: 7.4/10**

## Critical Gaps

### 1. No PR-Triggered Test CI in the Downstream Fork
- **Impact**: Code changes can be merged without any automated test execution in the fork's CI. Quality regressions can reach RHOAI releases undetected.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The fork has only 5 GitHub Actions workflows, all triggered by `workflow_dispatch` or `release` events. None run on `pull_request`. The Konflux Tekton pipeline builds the container image on PR but runs no tests. The upstream `kubernetes-sigs/kueue` uses Prow for CI which doesn't apply to this fork.

### 2. No Coverage Tracking or Enforcement
- **Impact**: Coverage can silently regress across releases. No visibility into which code paths are tested.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The Makefile generates `cover.out` via `-coverprofile` flag in the `test` target, but there's no Codecov/Coveralls configuration in the fork. No coverage thresholds are enforced.

### 3. No Container Security Scanning
- **Impact**: Vulnerable base images or dependencies could ship in RHOAI releases undetected.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: A `.snyk` policy file exists (excluding `cmd/kueuectl` and `test/`) but there's no Snyk CI integration. No Trivy, CodeQL, or Grype scanning in workflows. The Konflux pipeline may include some scanning via centralized tasks, but it's not visible in the repo.

### 4. No Agent Rules for AI-Assisted Development
- **Impact**: AI-generated code and tests lack project-specific patterns, frameworks, and quality standards.
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: No `CLAUDE.md`, `AGENTS.md`, or `.claude/` directory exists. AI agents don't know to use Ginkgo/Gomega, envtest patterns, or Kueue-specific testing conventions.

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- Create `.codecov.yml` with coverage thresholds
- Add `codecov/codecov-action` step to a PR workflow
- Configure `patch` and `project` coverage targets
```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: 60%
    patch:
      default:
        target: 70%
```

### 2. Add Trivy Container Scanning (1-2 hours)
- Add Trivy scan step to the Konflux pipeline or a GitHub Actions workflow
- Scan built images for HIGH/CRITICAL vulnerabilities
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE_TAG }}
    format: 'sarif'
    severity: 'CRITICAL,HIGH'
```

### 3. Add PR-Triggered Unit Test Workflow (2-4 hours)
```yaml
name: Unit Tests
on:
  pull_request:
    branches: [main, release-*]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: make test
```

### 4. Create Basic Agent Rules (2-3 hours)
- Use `/test-rules-generator` to bootstrap `.claude/rules/` with Ginkgo/Gomega patterns
- Cover unit test, integration test (envtest), and E2E test patterns

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (5 workflows, all non-PR)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `odh-build-and-publish-kueue-image.yaml` | `workflow_dispatch` | Build & publish container image to Quay |
| `odh-release.yml` | `workflow_dispatch`, `push` (tags) | Compile E2E tests and create release assets |
| `openvex.yaml` | `workflow_dispatch` | Generate OpenVEX vulnerability data |
| `sbom.yaml` | `workflow_dispatch` | Generate SBOM using bom tool |
| `krew-release.yml` | `release` | Publish krew plugin on release |

**Tekton/Konflux Pipeline**:
- Single PipelineRun (`odh-kueue-controller-pull-request.yaml`) triggered on PR via labels (`kfbuild-all`, `kfbuild-kueue`) or comment (`/build-konflux`)
- Builds multi-arch image (x86_64, arm64, ppc64le, s390x) using `Dockerfile.konflux`
- Hermetic build with Go module prefetch
- Pipeline definition is centralized in `konflux-central` repo
- **No test execution in the pipeline** - only image build validation

**Gaps**:
- No PR-triggered workflows for tests, linting, or verification
- No concurrency control needed since no PR workflows exist
- No test result caching or parallelization in CI
- Fork entirely depends on upstream Prow CI for test execution

### Test Coverage

**Unit Tests (Score: 8.5/10)**:
- 226 test files across `pkg/`, `cmd/`, and `apis/` directories
- 119,520 lines of test code vs 73,225 lines of source code
- Test-to-code ratio: 0.50 (files), 1.63 (LOC) - excellent
- Framework: Go standard `testing` + Ginkgo v2/Gomega
- Coverage generation: `-coverprofile` with `-coverpkg=./...` for full package coverage
- JUnit XML output: `--junitfile $(ARTIFACTS)/junit.xml`
- Race detection: `-race` flag enabled by default

**Integration Tests (Score: 9.0/10)**:
- 25+ integration test suites using controller-runtime envtest
- Test categories:
  - **Webhook tests**: 14 suites covering all job types (Job, JobSet, Pod, StatefulSet, Deployment, RayJob, RayCluster, PyTorchJob, MPIJob, XGBoostJob, TFJob, PaddleJob, AppWrapper)
  - **Core webhook tests**: 7 suites (Workload, ResourceFlavor, LocalQueue, Cohort, ClusterQueue, AdmissionCheck)
  - **Controller tests**: Per-job-type controller validation
  - **Scheduler tests**: Preemption, fair sharing, pods-ready
  - **TAS tests**: Topology-aware scheduling
  - **Kueuectl tests**: CLI integration
  - **Importer tests**: Migration tooling
  - **MultiKueue tests**: Multi-cluster scenarios
- Parallelization: 4 processes (singlecluster), 3 processes (multikueue)
- Baseline/Extended split: `--label-filter="!slow && !redundant"` for fast CI

**E2E Tests (Score: 9.0/10)**:
- 5 E2E test variants:
  1. **Singlecluster**: Core scheduling, admission, preemption, visibility, metrics
  2. **MultiKueue**: Multi-cluster federation scenarios
  3. **TAS**: Topology-aware scheduling with multiple job types
  4. **Custom Configs**: `ManageJobsWithoutQueueName` scenarios
  5. **Cert-Manager**: TLS certificate management
- Multi-version testing: K8s 1.30.10, 1.31.6, 1.32.3
- Kind cluster infrastructure with custom cluster configs
- External controller integration: AppWrapper, JobSet, LeaderWorkerSet, KubeFlow Training, KubeRay

**Performance Tests**:
- Scheduler performance benchmarking with `minimalkueue` runner
- Configurable generator for workload simulation
- Stats collection with CPU profiling support
- Retry mechanism for flaky performance results
- Range-spec based pass/fail assertions

### Code Quality

**Linting (Strong)**:
- `.golangci.yaml` with 18 linters enabled:
  - `copyloopvar`, `dupword`, `durationcheck`, `fatcontext`, `gci`, `ginkgolinter`, `gocritic`, `goheader`, `govet`, `loggercheck`, `misspell`, `nilerr`, `nilnesserr`, `nolintlint`, `perfsprint`, `revive`, `unconvert`, `makezero`
- `ginkgolinter` ensures Ginkgo/Gomega best practices
- `nolintlint` requires explanations for `nolint` directives
- Shell linting via `.shellcheckrc` with external source following
- Makefile `verify` target: `gomod-verify ci-lint fmt-verify shell-lint toc-verify manifests generate update-helm helm-verify prepare-release-branch`

**Dependency Management (Good)**:
- Dependabot configured for weekly updates across 7 directories
  - Go modules (root, hack/internal/tools, site, kueue-viz backend)
  - npm (site, kueue-viz frontend)
  - Docker (hack/shellcheck, kueue-viz frontend)
  - GitHub Actions (daily, grouped)
- Renovate configured via `konflux-central` shared config
- K8s dependency updates limited to patch-only (major/minor ignored)

**Pre-commit Hooks**: Not configured (no `.pre-commit-config.yaml`)

**Static Analysis**: No CodeQL, gosec, or Semgrep configured

### Container Images

**Dockerfiles (3 variants)**:
1. **Dockerfile** (upstream): Multi-stage with distroless base, CGO_ENABLED=1, multi-platform support
2. **Dockerfile.konflux**: Red Hat build system (`brew.registry.redhat.io/rh-osbs/openshift-golang-builder`), FIPS-compliant (`GOEXPERIMENT=strictfipsruntime`), UBI9-minimal base with Red Hat labels
3. **Dockerfile.rhoai**: UBI9 full base, Go 1.24.13, system dependency installation (gcc, make, openssl-devel)

**Multi-Architecture Support**: linux/amd64, linux/arm64, linux/s390x, linux/ppc64le (Konflux pipeline)

**Gaps**:
- No image startup validation (e.g., `/manager --help` smoke test)
- No runtime container tests
- No Trivy/Grype scanning in CI
- Dockerfile.rhoai uses full UBI9 base (larger attack surface vs UBI9-minimal)

### Security

**Strengths**:
- SECURITY-INSIGHTS.yaml with formal vulnerability reporting process
- OpenVEX generation workflow for vulnerability attestation
- SBOM generation workflow using bom tool
- Snyk policy file (`.snyk`) excluding test directories
- FIPS compliance in Konflux builds (`strictfipsruntime`)
- Dependabot for automated dependency updates
- Bug bounty program via HackerOne

**Gaps**:
- No SAST/CodeQL workflow
- No Trivy/Snyk CI integration (only policy file)
- No secret detection (Gitleaks, TruffleHog)
- SECURITY-INSIGHTS expiration date passed (2024-09-28)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**:
  - No unit test creation rules (Ginkgo/Gomega patterns)
  - No integration test rules (envtest setup, webhook testing)
  - No E2E test rules (Kind cluster, job type testing)
  - No code quality rules (linter compliance, import ordering)
- **Recommendation**: Generate missing rules with `/test-rules-generator` targeting:
  - Unit tests with Go testing + Ginkgo v2 patterns
  - Integration tests with envtest and controller-runtime
  - E2E tests with Kind cluster and multi-version K8s
  - Webhook validation test patterns

## Recommendations

### Priority 0 (Critical)

1. **Add PR-triggered CI workflows** - Create GitHub Actions that run `make test`, `make ci-lint`, and `make test-integration-baseline` on every PR. This is the single highest-impact improvement for the fork.

2. **Integrate Codecov with coverage enforcement** - Add `.codecov.yml` with project target (60%) and patch target (70%). Upload `cover.out` from unit test workflow.

3. **Add container vulnerability scanning** - Add Trivy scanning to the Konflux pipeline as a Tekton task, or add a GitHub Actions workflow scanning built images for HIGH/CRITICAL CVEs.

### Priority 1 (High Value)

4. **Add PR-time integration tests** - Run `make test-integration-baseline` (the fast, non-slow/redundant subset) on PRs to catch controller and webhook regressions.

5. **Create comprehensive agent rules** - Bootstrap `.claude/rules/` with patterns for:
   - Unit tests: Go testing + Ginkgo v2 + Gomega matchers
   - Integration tests: envtest framework, CRD loading, webhook testing
   - E2E tests: Kind cluster setup, Ginkgo suites, multi-job-type testing
   - Code quality: golangci-lint compliance, import ordering via gci

6. **Add image startup validation** - Test that built images can start the manager binary (`/manager --help` or health check) before merging.

### Priority 2 (Nice-to-Have)

7. **Add CodeQL/SAST workflow** - Enable GitHub's CodeQL for Go static analysis to catch security issues.

8. **Add pre-commit hooks** - Configure `.pre-commit-config.yaml` with golangci-lint, gofmt, shellcheck, and boilerplate checks for local development.

9. **Add performance regression testing to CI** - Run `make test-performance-scheduler` on a periodic schedule to catch scheduler performance regressions.

10. **Update SECURITY-INSIGHTS.yaml** - Expiration date (2024-09-28) has passed. Update to reflect current release version and reset expiration.

## Comparison to Gold Standards

| Dimension | kueue (this fork) | odh-dashboard | notebooks | kserve |
|-----------|-------------------|---------------|-----------|--------|
| Unit Tests | 8.5 (226 files, Ginkgo) | 9.0 (Jest, comprehensive) | 7.0 (basic) | 9.0 (Go, high coverage) |
| Integration/E2E | 9.0 (25+ envtest suites) | 9.0 (Cypress, contract) | 8.0 (5-layer) | 9.0 (multi-version) |
| Build Integration | 4.0 (Konflux image only) | 8.0 (PR builds validated) | 7.0 (PR image tests) | 6.0 (basic) |
| Image Testing | 5.0 (multi-arch, no scanning) | 7.0 (startup tests) | 9.0 (5-layer validation) | 6.0 (basic) |
| Coverage Tracking | 4.0 (local only) | 9.0 (Codecov enforced) | 5.0 (basic) | 8.0 (Codecov) |
| CI/CD Automation | 5.0 (dispatch only) | 9.0 (PR + periodic) | 8.0 (automated) | 8.0 (Prow + GH Actions) |
| Agent Rules | 0.0 (none) | 8.0 (comprehensive) | 2.0 (minimal) | 3.0 (basic) |

## File Paths Reference

### CI/CD
- `.github/workflows/odh-build-and-publish-kueue-image.yaml` - Image build & publish
- `.github/workflows/odh-release.yml` - Release workflow
- `.github/workflows/sbom.yaml` - SBOM generation
- `.github/workflows/openvex.yaml` - OpenVEX attestation
- `.tekton/odh-kueue-controller-pull-request.yaml` - Konflux PR pipeline

### Testing
- `Makefile-test.mk` - All test targets (unit, integration, E2E, performance)
- `test/integration/` - 25+ envtest-based integration suites
- `test/e2e/` - E2E tests (singlecluster, multikueue, TAS, customconfigs, certmanager)
- `test/performance/` - Scheduler performance benchmarks
- `test/util/` - Shared test utilities
- `hack/e2e-test.sh` - E2E test runner script
- `hack/e2e-common.sh` - Shared E2E infrastructure

### Code Quality
- `.golangci.yaml` - 18 linters enabled
- `.shellcheckrc` - Shell linting config
- `.github/dependabot.yml` - Dependency update automation
- `.github/renovate.json` - Renovate bot config

### Container Images
- `Dockerfile` - Upstream multi-stage build
- `Dockerfile.konflux` - FIPS-compliant Konflux build
- `Dockerfile.rhoai` - RHOAI-specific build
- `.dockerignore` -> `.gitignore` (symlink)

### Security
- `.snyk` - Snyk policy file
- `SECURITY-INSIGHTS.yaml` - Security posture documentation
- `.openvex/` - OpenVEX templates
- `SECURITY.md` - Security reporting instructions
