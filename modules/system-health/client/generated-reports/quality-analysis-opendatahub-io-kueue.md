---
repository: "opendatahub-io/kueue"
overall_score: 6.9
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Strong coverage (100 pkg tests, 17 cmd tests) with well-structured test utilities, but client-go has 0 tests and apis has only 2"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Excellent multi-layer testing: 79 integration + 29 E2E files, envtest framework, multi-K8s-version E2E (1.30-1.32), multikueue and TAS suites"
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time build validation — all workflows are manual dispatch only; no CI on pull_request trigger"
  - dimension: "Image Testing"
    score: 3.5
    status: "Dockerfile and Dockerfile.rhoai present but no runtime validation, no image startup testing, no PR-triggered image builds"
  - dimension: "Coverage Tracking"
    score: 4.0
    status: "Coverage profile generated locally (cover.out) but no codecov/coveralls integration, no PR enforcement, no thresholds"
  - dimension: "CI/CD Automation"
    score: 3.5
    status: "Only 5 workflows, all manual dispatch or tag-triggered; no PR-triggered CI; relies entirely on upstream Prow for PR validation"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory — zero AI agent guidance for test creation"
critical_gaps:
  - title: "No PR-triggered CI workflows"
    impact: "Fork-specific changes (Dockerfile.rhoai, config/rhoai/) are never validated by CI before merge. Relies entirely on upstream Prow which doesn't test ODH-specific code."
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No container image testing"
    impact: "Dockerfile.rhoai builds are never validated — image startup failures, missing dependencies, or runtime errors discovered only in Konflux/production"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No coverage tracking or enforcement"
    impact: "Coverage can silently regress with no visibility; cover.out generated locally but not reported or enforced on PRs"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No security scanning in fork CI"
    impact: "Snyk policy file exists but no Trivy/CodeQL/gosec workflows run on fork PRs; vulnerabilities discovered only by upstream or post-release"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "client-go package has zero test coverage"
    impact: "143 Go files in client-go/ with no tests — generated code but still a significant gap for any custom modifications"
    severity: "MEDIUM"
    effort: "8-16 hours"
quick_wins:
  - title: "Add PR-triggered lint and unit test workflow"
    effort: "2-4 hours"
    impact: "Catches code quality and test failures before merge for fork-specific changes"
  - title: "Add codecov integration"
    effort: "2-3 hours"
    impact: "Coverage visibility on every PR, prevent silent regression"
  - title: "Add Trivy container scanning workflow"
    effort: "1-2 hours"
    impact: "Catch known CVEs in base images and dependencies before release"
  - title: "Create basic CLAUDE.md with test patterns"
    effort: "2-3 hours"
    impact: "Enable consistent AI-generated test quality aligned with upstream patterns (Ginkgo/Gomega, envtest)"
  - title: "Add Dockerfile.rhoai build validation"
    effort: "3-4 hours"
    impact: "Catch RHOAI-specific image build failures before merge"
recommendations:
  priority_0:
    - "Add PR-triggered CI workflow that runs linting, unit tests, and builds Dockerfile.rhoai"
    - "Add container image build validation for Dockerfile.rhoai on PRs to catch build failures before merge"
    - "Integrate codecov with coverage thresholds to prevent silent regression"
  priority_1:
    - "Add Trivy/CodeQL security scanning on PRs for the fork"
    - "Create CLAUDE.md and .claude/rules/ for AI agent test guidance"
    - "Add RHOAI-specific integration tests for the kustomize overlay"
    - "Add image runtime validation — build and startup-test Dockerfile.rhoai in Kind"
  priority_2:
    - "Add pre-commit hooks for the fork to catch issues locally"
    - "Add SBOM generation to PR workflow"
    - "Add Helm chart validation tests for RHOAI config"
---

# Quality Analysis: opendatahub-io/kueue

## Executive Summary

- **Overall Score: 6.9/10**
- **Repository Type**: Kubernetes Operator (job queueing system) — fork of `kubernetes-sigs/kueue`
- **Primary Language**: Go 1.24
- **Default Branch**: `stable-2.x`
- **Key Strength**: Excellent upstream test infrastructure with comprehensive integration and E2E suites, multi-K8s version testing, envtest framework, and performance benchmarks
- **Critical Gap**: The ODH fork has **zero PR-triggered CI workflows** — all 5 workflows are manual dispatch or tag-triggered, meaning fork-specific changes (Dockerfile.rhoai, config/rhoai/) are never validated by CI before merge
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Strong pkg/cmd coverage, rich test utilities, but gaps in client-go and apis |
| Integration/E2E | 9.0/10 | Exceptional: 79 integration + 29 E2E files, envtest, multi-K8s versions, multikueue |
| **Build Integration** | **3.0/10** | **No PR-time build validation — all workflows are manual dispatch only** |
| Image Testing | 3.5/10 | Dockerfiles present but no runtime validation or PR-triggered builds |
| Coverage Tracking | 4.0/10 | Local cover.out generation but no CI integration or enforcement |
| CI/CD Automation | 3.5/10 | 5 workflows, all manual/tag-triggered; relies on upstream Prow for PR testing |
| Agent Rules | 0.0/10 | No AI agent guidance exists |

## Critical Gaps

### 1. No PR-Triggered CI Workflows
- **Impact**: Fork-specific changes are never validated before merge. The 5 existing workflows are:
  - `odh-build-and-publish-kueue-image.yaml` — manual dispatch only
  - `odh-release.yml` — manual dispatch + tag push
  - `sbom.yaml` — manual dispatch only
  - `openvex.yaml` — manual dispatch only
  - `krew-release.yml` — release event only
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Note**: Upstream uses Prow CI (via `kubernetes-sigs/kueue`), but Prow doesn't test ODH-specific code like `Dockerfile.rhoai` or `config/rhoai/`

### 2. No Container Image Testing
- **Impact**: `Dockerfile.rhoai` (RHOAI-specific image) is never build-tested. Uses custom UBI9 base image with manual Go installation — fragile and untested.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The RHOAI Dockerfile has unique concerns (custom Go install, UBI9 base, different build flags) that differ from the upstream `Dockerfile`

### 3. No Coverage Tracking or Enforcement
- **Impact**: Coverage can silently regress without visibility
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: The Makefile generates `cover.out` with `-coverpkg=./... -coverprofile`, but there's no codecov integration, no PR reporting, no minimum threshold enforcement

### 4. No Security Scanning in Fork CI
- **Impact**: `.snyk` policy file exists (excluding `cmd/kueuectl/**` and `test/**`) but no scanning workflows run in the fork
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: No Trivy, CodeQL, gosec, or Semgrep workflows. Dependabot is active for dependency updates but that's a supply chain control, not a vulnerability scanner

### 5. client-go Has Zero Tests
- **Impact**: 143 Go files in `client-go/` with no test files
- **Severity**: MEDIUM
- **Effort**: 8-16 hours (mostly generated code, but any ODH-specific changes would be unprotected)

## Quick Wins

### 1. Add PR-Triggered Lint + Unit Test Workflow (2-4 hours)
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on:
  pull_request:
    branches: [stable-2.x]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - name: Lint
        run: make ci-lint
      - name: Unit Tests
        run: make test
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./bin/cover.out
```

### 2. Add Codecov Integration (2-3 hours)
Create `.codecov.yml` with minimum coverage thresholds and integrate with the PR workflow above.

### 3. Add Trivy Container Scanning (1-2 hours)
```yaml
# Add to PR workflow
- name: Build RHOAI Image
  run: docker build -f Dockerfile.rhoai -t kueue-rhoai:test .
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'kueue-rhoai:test'
    severity: 'CRITICAL,HIGH'
```

### 4. Create CLAUDE.md (2-3 hours)
Document test patterns: unit tests use `testing` package with `go-cmp`, integration uses Ginkgo/Gomega with envtest, E2E uses Kind clusters.

### 5. Add Dockerfile.rhoai Build Validation (3-4 hours)
Add a PR-triggered job that builds `Dockerfile.rhoai` to catch build failures before merge.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (5 workflows, ALL manual/tag-triggered):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `odh-build-and-publish-kueue-image.yaml` | `workflow_dispatch` | Build and push to Quay |
| `odh-release.yml` | `workflow_dispatch` + `push:tags` | Compile E2E tests, create GitHub release |
| `sbom.yaml` | `workflow_dispatch` | Generate SBOM with `bom` tool |
| `openvex.yaml` | `workflow_dispatch` | Generate OpenVEX vulnerability data |
| `krew-release.yml` | `release:released` | Update krew-index |

**Key Observations**:
- **No `pull_request` trigger exists** in any workflow — this is the single biggest gap
- Upstream CI (Prow) handles PR validation for the `kubernetes-sigs/kueue` repository, but does NOT run on the ODH fork
- Cloud Build (`cloudbuild.yaml`) is configured for upstream staging image pushes only
- Release workflow uses Go 1.21 (outdated) while `go.mod` specifies Go 1.24.13

**Build Process**:
- Makefile is well-organized with clear targets: `build`, `test`, `verify`, `image-build`
- Two Dockerfiles: `Dockerfile` (upstream, distroless base) and `Dockerfile.rhoai` (UBI9 base, custom Go install)
- Multi-architecture support: `PLATFORMS` variable support, `multiplatform-build.sh` script
- Dependabot configured for: gomod, npm (site), github-actions, docker (shellcheck)

### Test Coverage

**Test File Distribution** (excluding vendor):

| Category | Test Files | Source Files | Ratio |
|----------|-----------|-------------|-------|
| `pkg/` (unit) | 100 | 202 | 0.50 |
| `cmd/` (unit) | 17 | 55 | 0.31 |
| `apis/` (unit) | 2 | 34 | 0.06 |
| `client-go/` | 0 | 143 | 0.00 |
| `test/integration/` | 79 | — | — |
| `test/e2e/` | 29 | — | — |
| `test/performance/` | 9 | — | — |
| **Total** | **226** | **450** | **0.50** |

**Strengths**:
- 50% test-to-code ratio (excellent for an operator)
- Well-structured test utilities in `pkg/util/testing/` (wrappers, matchers, metrics matchers)
- 15 job-type-specific test builders in `pkg/util/testingjobs/`
- Comprehensive test infrastructure with dedicated framework

**Coverage Generation**:
- `make test` generates `cover.out` with `-coverpkg=./...`
- JUnit XML output via `gotestsum`
- But NO codecov/coveralls integration, NO PR reporting, NO thresholds

### Testing Frameworks

**Unit Tests**: Standard Go `testing` package with:
- `google/go-cmp` for comparison assertions
- Table-driven tests (map-based test cases)
- Rich test builder pattern (`MakeWorkload`, `MakeJob`, etc.)

**Integration Tests**: Ginkgo v2 + Gomega with:
- `envtest` (kubebuilder) for API server simulation
- 110 files using Ginkgo/Gomega
- Parallel execution (4 procs for singlecluster, 3 for multikueue)
- CRD loading from `config/components/crd/bases`
- Webhook testing support
- Suites: controller, scheduler, webhook, TAS, kueuectl, importer
- Baseline vs. extended split (`--label-filter="!slow && !redundant"`)

**E2E Tests**: Ginkgo v2 with Kind clusters:
- Multi-K8s version testing: 1.30.10, 1.31.6, 1.32.3
- 5 E2E suites: singlecluster, multikueue, TAS, customconfigs, certmanager
- Comprehensive infrastructure: cluster create/cleanup, image loading, external controller installation
- Tests against: AppWrapper, JobSet, Kubeflow, MPI, KubeRay, LeaderWorkerSet, cert-manager

**Performance Tests**:
- Custom scheduler performance runner
- `minimalkueue` binary for isolated perf testing
- CPU profiling support
- Metrics scraping integration
- Retry mechanism for flaky perf tests

### Code Quality

**Linting** (`.golangci.yaml`):
- 18 linters enabled (strong configuration)
- Notable linters: `ginkgolinter`, `gocritic`, `goheader`, `govet` (nilness), `gci`, `nolintlint` (requires explanation), `perfsprint`, `revive`
- Shell linting via ShellCheck
- License header enforcement via `goheader`
- Import ordering via `gci`

**Pre-commit Hooks**: None — no `.pre-commit-config.yaml`

**Static Analysis**: Limited in fork:
- No CodeQL workflows
- No gosec integration
- No Semgrep
- `.snyk` policy exists (excludes kueuectl and tests) but no active scanning workflow

**Makefile Verification Target**:
```
verify: gomod-verify ci-lint fmt-verify shell-lint toc-verify manifests generate update-helm helm-verify prepare-release-branch
```
This is comprehensive but only runs locally — not enforced by CI on the fork.

### Container Images

**Dockerfiles**:

| File | Base Image | Builder | Purpose |
|------|-----------|---------|---------|
| `Dockerfile` | `gcr.io/distroless/static:nonroot` | `golang:1.24.13` | Upstream, minimal |
| `Dockerfile.rhoai` | `registry.access.redhat.com/ubi9/ubi:latest` | Custom Go install on UBI9 | RHOAI build |

**Dockerfile.rhoai Concerns**:
- Manually installs Go (copies from registry-proxy golang image) — fragile
- Uses `CGO_ENABLED=1` with gcc
- No multi-stage caching optimization
- No `.dockerignore` specific to RHOAI (symlinks to `.gitignore`)
- Uses `:latest` tag for UBI9 base — not pinned

**Container Security**:
- `.snyk` policy file present
- OpenVEX generation workflow (manual dispatch)
- SBOM generation with `bom` tool (manual dispatch)
- No Trivy, Grype, or other container scanning
- No image signing or attestation

### Security

| Practice | Status |
|----------|--------|
| Dependabot | Active (gomod, npm, github-actions, docker) |
| Snyk | Policy file only, no active scanning |
| CodeQL | Not configured |
| Trivy | Not configured |
| gosec | Not configured |
| SBOM | Manual dispatch workflow |
| OpenVEX | Manual dispatch workflow |
| Secret Detection | Not configured |
| Image Signing | Not configured |
| SECURITY-INSIGHTS.yaml | Present (from upstream) |
| SECURITY.md | Present (from upstream) |

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/`, `CLAUDE.md`, or `AGENTS.md`
- **Quality**: N/A
- **Gaps**: Complete absence of AI agent guidance
- **Recommendation**: Create rules covering:
  - Unit test patterns (Go `testing`, table-driven, `go-cmp`)
  - Integration test patterns (Ginkgo/Gomega, envtest, CRD setup)
  - E2E test patterns (Kind cluster, workload test builders)
  - Linting requirements (18 golangci-lint rules)

## Recommendations

### Priority 0 (Critical)

1. **Add PR-triggered CI workflow for the ODH fork**
   - Run linting (`make ci-lint`), unit tests (`make test`), and `make verify` on every PR to `stable-2.x`
   - This is the single highest-impact improvement — currently ALL fork-specific changes merge without CI validation

2. **Add Dockerfile.rhoai build validation on PRs**
   - Build `Dockerfile.rhoai` on every PR to catch build failures before merge
   - Test image startup: `docker run --rm kueue-rhoai:test /manager --help`

3. **Integrate codecov with coverage thresholds**
   - Add `.codecov.yml` with patch coverage requirement (e.g., 60%)
   - Upload coverage from `make test` to codecov on PRs

### Priority 1 (High Value)

4. **Add security scanning to PR workflow**
   - Trivy for container scanning of Dockerfile.rhoai
   - CodeQL for Go SAST analysis
   - Consider activating the existing Snyk policy

5. **Create CLAUDE.md and .claude/rules/ for AI agent guidance**
   - Document test frameworks: `testing` (unit), Ginkgo/Gomega (integration/E2E)
   - Document test builder patterns in `pkg/util/testingjobs/`
   - Document envtest setup and CRD loading
   - Use `/test-rules-generator` to auto-generate rules

6. **Add RHOAI-specific integration tests**
   - Validate `config/rhoai/` kustomize overlay builds correctly
   - Test RHOAI-specific patches (webhook, metrics, role)
   - Add `make verify-rhoai` target

7. **Add image runtime validation**
   - Build Dockerfile.rhoai, load into Kind, verify startup
   - Test RHOAI kustomize overlay deployment in Kind

### Priority 2 (Nice-to-Have)

8. **Add pre-commit hooks**
   - Hook into `make fmt`, `make ci-lint`, `make vet`
   - Catch issues before commit

9. **Pin UBI9 base image in Dockerfile.rhoai**
   - Replace `ubi9/ubi:latest` with a specific digest
   - Reproducible builds

10. **Fix Go version mismatch in release workflow**
    - `odh-release.yml` uses `go-version: v1.21` while `go.mod` specifies Go 1.24.13
    - Use `go-version-file: go.mod` like other workflows

11. **Add Helm chart tests for RHOAI configuration**
    - `make helm-verify` exists but runs locally only

## Comparison to Gold Standards

| Practice | kueue (ODH) | odh-dashboard | notebooks | kserve |
|----------|-------------|---------------|-----------|--------|
| PR CI | None | Comprehensive | Multi-layer | Full |
| Unit Tests | 7.5/10 | 8/10 | 6/10 | 8/10 |
| Integration | 9/10 | 9/10 | 7/10 | 9/10 |
| E2E | 9/10 (upstream) | 8/10 | 8/10 | 9/10 |
| Coverage Tracking | None | Codecov | None | Codecov |
| Image Testing | None | Basic | 5-layer | Basic |
| Security Scan | Snyk policy only | Trivy + Snyk | Trivy | Trivy |
| Agent Rules | None | Comprehensive | None | Basic |
| Pre-commit | None | Yes | No | No |
| Multi-K8s Version | 3 versions | 1 version | N/A | 2 versions |
| Performance Tests | Yes | No | No | No |
| Helm Charts | Yes + lint | N/A | N/A | Yes |

**Key Insight**: The upstream kueue project (kubernetes-sigs/kueue) has excellent test infrastructure and code quality practices. The ODH fork inherits all of this code but **none of the CI** — the fork's workflows are exclusively for release/build automation, not quality gates.

## File Paths Reference

| Category | Path |
|----------|------|
| CI Workflows | `.github/workflows/` (5 files) |
| Makefile | `Makefile`, `Makefile-test.mk`, `Makefile-deps.mk` |
| Linting | `.golangci.yaml` |
| Upstream Dockerfile | `Dockerfile` |
| RHOAI Dockerfile | `Dockerfile.rhoai` |
| RHOAI Config | `config/rhoai/` |
| Unit Tests | `pkg/**/`, `cmd/**/`, `apis/**/` |
| Integration Tests | `test/integration/` (singlecluster, multikueue) |
| E2E Tests | `test/e2e/` (singlecluster, multikueue, TAS, customconfigs, certmanager) |
| Performance Tests | `test/performance/` |
| Test Framework | `test/integration/framework/framework.go` |
| Test Utilities | `pkg/util/testing/`, `pkg/util/testingjobs/`, `test/util/` |
| E2E Scripts | `hack/e2e-test.sh`, `hack/e2e-common.sh`, `hack/multikueue-e2e-test.sh` |
| Security | `.snyk`, `SECURITY-INSIGHTS.yaml`, `SECURITY.md` |
| Dependabot | `.github/dependabot.yml` |
| Helm Chart | `charts/kueue/` |
| KEPs | `keps/` (20+ enhancement proposals) |
