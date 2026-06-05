---
repository: "red-hat-data-services/noobaa-operator"
overall_score: 2.4
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "Only 2 test files (102 LoC) covering 24,529 LoC of source — 0.4% test-to-code ratio"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Shell-based CLI flow tests exist but no Go integration/E2E framework"
  - dimension: "Build Integration"
    score: 2.0
    status: "PR workflow builds image but no Konflux simulation or manifest validation"
  - dimension: "Image Testing"
    score: 1.5
    status: "Minimal single-arch Dockerfile, no runtime validation or scanning"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage generation, no codecov/coveralls, no thresholds"
  - dimension: "CI/CD Automation"
    score: 4.0
    status: "Basic PR workflows with lint+test+build, but outdated tooling (Go 1.15/1.16)"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "Near-zero unit test coverage"
    impact: "Only 2 of 30+ packages have any tests; regressions go undetected across controller, system, util, CRD, OBC, and all other packages"
    severity: "HIGH"
    effort: "40-80 hours"
  - title: "No code coverage tracking"
    impact: "No visibility into what is tested; PRs can reduce coverage without any signal"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No security scanning in CI"
    impact: "Container vulnerabilities, dependency CVEs, and secrets in code are not detected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Severely outdated Go toolchain (1.15)"
    impact: "Go 1.15 is 4+ years past EOL; missing security patches, module improvements, and modern language features"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No container image runtime validation"
    impact: "Image startup failures and runtime issues not caught until deployment"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No envtest or controller-runtime test infrastructure"
    impact: "Operator controllers (backingstore, bucketclass, noobaa, OBC, namespacestore, cephcluster) are completely untested"
    severity: "HIGH"
    effort: "24-40 hours"
quick_wins:
  - title: "Add codecov integration with coverage generation"
    effort: "2-4 hours"
    impact: "Immediate visibility into test coverage baseline and PR-level coverage changes"
  - title: "Add Trivy container scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Early detection of CVEs in base image (ubi8/ubi-minimal) and dependencies"
  - title: "Upgrade golangci-lint version and add config file"
    effort: "2-3 hours"
    impact: "Current v1.29 is years outdated; modern version enables more linters and better analysis"
  - title: "Add basic agent rules (.claude/rules/)"
    effort: "2-3 hours"
    impact: "Improve AI-generated test quality and ensure consistent test patterns"
  - title: "Pin GitHub Actions to SHA hashes"
    effort: "1 hour"
    impact: "Prevent supply-chain attacks through compromised action versions"
recommendations:
  priority_0:
    - "Add unit tests for all 6 controller packages using envtest (controller-runtime/pkg/envtest)"
    - "Add code coverage generation (-coverprofile) and integrate with codecov"
    - "Add Trivy or Snyk container scanning to PR workflows"
    - "Upgrade Go version from 1.15 to current supported version (1.22+)"
  priority_1:
    - "Replace shell-based CLI tests with Go-based integration tests"
    - "Add CRD validation tests for all custom resources (NooBaa, BackingStore, BucketClass, NamespaceStore)"
    - "Add webhook validation tests if webhooks exist"
    - "Create comprehensive agent rules for test automation (.claude/rules/)"
    - "Add golangci-lint config file (.golangci.yml) with expanded linter set"
  priority_2:
    - "Add multi-architecture image builds (arm64, s390x, ppc64le)"
    - "Add SBOM generation and image signing"
    - "Add pre-commit hooks for local validation"
    - "Add performance/benchmark tests for critical paths"
    - "Implement Konflux build simulation in PR workflow"
---

# Quality Analysis: noobaa-operator

## Executive Summary

- **Overall Score: 2.4/10**
- **Repository Type**: Kubernetes Operator (Go)
- **Primary Language**: Go 1.15 (severely outdated)
- **Codebase Size**: 24,529 lines of Go source code across 71 files
- **Test Coverage**: 102 lines of test code in 2 files (0.4% test-to-code ratio)
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

The noobaa-operator has **critical quality gaps** across nearly every dimension. With only 2 test files covering 2 of 30+ packages, the vast majority of operator logic — including all 6 controllers, CRD handling, system management, and utilities — is completely untested. The CI pipeline runs on Go 1.15 (4+ years EOL), has no security scanning, no coverage tracking, and uses outdated linting tools. This represents one of the lowest quality scores in the assessment framework.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1.0/10 | Only 2 test files (102 LoC) for 24,529 LoC source |
| Integration/E2E | 3.0/10 | Shell-based CLI flow tests, no Go integration framework |
| **Build Integration** | **2.0/10** | **PR builds image but no Konflux simulation** |
| Image Testing | 1.5/10 | Minimal single-arch Dockerfile, no runtime validation |
| Coverage Tracking | 0.0/10 | No coverage generation, no reporting, no enforcement |
| CI/CD Automation | 4.0/10 | Basic PR workflows but severely outdated tooling |
| Agent Rules | 0.0/10 | No agent rules, no test automation guidance |

## Critical Gaps

### 1. Near-Zero Unit Test Coverage
- **Impact**: Only `pkg/nb/api_test.go` (48 lines, BigInt marshaling) and `pkg/cli/cli_test.go` (54 lines, basic CLI output) have any tests. All 6 controller packages, system management, CRD handling, OBC provisioning, utilities, and more are completely untested.
- **Severity**: HIGH
- **Effort**: 40-80 hours
- **Packages with zero tests**: backingstore, bucket, bucketclass, bundle, bundler, controller/*, crd, diagnose, install, namespacestore, obc, olm, operator, options, pvstore, system, util, version (20+ packages)

### 2. No Code Coverage Tracking
- **Impact**: No `go test -coverprofile` flags, no codecov/coveralls integration, no PR coverage gates. PRs can remove tests or reduce coverage with zero visibility.
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 3. No Security Scanning
- **Impact**: No Trivy, Snyk, CodeQL, gosec, Semgrep, or Gitleaks in any workflow. Container vulnerabilities in ubi8/ubi-minimal base image go undetected. No dependency vulnerability scanning.
- **Severity**: HIGH
- **Effort**: 4-6 hours

### 4. Severely Outdated Go Toolchain
- **Impact**: `go.mod` specifies Go 1.15, CI uses Go 1.16. Both are 4+ years past end-of-life, missing critical security patches and language improvements. golangci-lint v1.29 is also severely outdated.
- **Severity**: HIGH
- **Effort**: 8-16 hours

### 5. No Container Image Runtime Validation
- **Impact**: Dockerfile builds a single-arch image with no startup validation, no health check testing, no functional verification. The `.dockerignore` excludes `pkg` and `test` entirely.
- **Severity**: HIGH
- **Effort**: 4-6 hours

### 6. No Controller Testing Infrastructure
- **Impact**: As a Kubernetes operator with 6 controllers (backingstore, bucketclass, cephcluster, namespacestore, noobaa, OBC), the complete absence of envtest or controller-runtime testing means reconciliation logic is never verified in isolation.
- **Severity**: HIGH
- **Effort**: 24-40 hours

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- Add `-coverprofile=coverage.out` to `go test` command in Makefile
- Add codecov upload step to `run_ci.yml` workflow
- Create `.codecov.yml` with initial threshold (even 5% would be an improvement)

### 2. Add Trivy Container Scanning (1-2 hours)
- Add Trivy scan step to `run_ci.yml` after image build
- Set severity threshold (CRITICAL,HIGH)
- Block PRs on critical vulnerabilities

### 3. Upgrade golangci-lint (2-3 hours)
- Update from v1.29 to current version (v1.59+)
- Create `.golangci.yml` config file with expanded linter set
- Replace deprecated linters (varcheck, structcheck, deadcode) with modern equivalents
- Add revive, govet, gocritic, gosec, misspell linters

### 4. Pin GitHub Actions Versions (1 hour)
- Replace `actions/checkout@v2` with SHA-pinned latest version
- Replace `actions/setup-go@v2` with SHA-pinned latest version
- Replace `golangci/golangci-lint-action@v2` with SHA-pinned latest version

### 5. Add Basic Agent Rules (2-3 hours)
- Create `CLAUDE.md` with project context and testing standards
- Create `.claude/rules/unit-tests.md` with Go testing patterns for this operator
- Generate rules with `/test-rules-generator` for comprehensive coverage

## Detailed Findings

### CI/CD Pipeline

**Workflows (4 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `golangci-lint.yml` | push, PR | Runs golangci-lint v1.29 with limited linters |
| `run_ci.yml` | push, PR | Builds CLI, image, runs unit tests and OLM tests |
| `testing.yml` | push, PR | Docker image tagging (mostly commented out) |
| `manual-build.yml` | workflow_dispatch | Manual operator build and publish |

**Issues identified:**
- **Outdated Actions**: All use `@v2` versions (checkout, setup-go, golangci-lint-action)
- **No caching**: No Go module caching, no Docker layer caching
- **No concurrency control**: No `concurrency` group to cancel stale runs
- **Deprecated set-output syntax**: Uses `::set-output` which is deprecated
- **Legacy Travis references**: CI still depends on `.travis/` scripts for tool installation
- **Hardcoded versions**: Kubernetes v1.17.3, Go 1.16 are severely outdated
- **`testing.yml` is mostly dead code**: Most steps are commented out

### Test Coverage

**Unit Tests:**
- `pkg/nb/api_test.go` (48 lines): Tests BigInt JSON marshal/unmarshal — 6 test functions
- `pkg/cli/cli_test.go` (54 lines): Tests CLI output format — 3 test functions, requires pre-built binary

**Test-to-code ratio**: 102 / 24,529 = **0.42%** (catastrophically low)

**Untested packages (critical):**
- `pkg/controller/noobaa/` — Main operator controller
- `pkg/controller/backingstore/` — BackingStore reconciler
- `pkg/controller/bucketclass/` — BucketClass reconciler
- `pkg/controller/namespacestore/` — NamespaceStore reconciler
- `pkg/controller/obc/` — ObjectBucketClaim provisioner
- `pkg/controller/cephcluster/` — CephCluster integration
- `pkg/system/` — System management (9 source files, 0 tests)
- `pkg/util/` — Utility functions (4 source files, 0 tests)
- `pkg/apis/noobaa/v1alpha1/` — API types (9 source files, 0 tests)

**Shell-based tests:**
- `test/cli/test_cli_flow.sh` — CLI integration flow (installs NooBaa, tests backingstore/bucketclass/OBC operations)
- `test/test-olm.sh` — OLM installation test
- `test/test-scenario.sh` — Manual test scenario script
- These provide some E2E coverage but are fragile, not parallelizable, and hard to maintain

**No testing dependencies**: `go.mod` contains zero testing libraries (no gomega, ginkgo, testify, envtest, or mock frameworks)

### Code Quality

**Linting:**
- golangci-lint v1.29 with only 8 linters enabled: varcheck, structcheck, typecheck, errcheck, gosimple, unused, deadcode, ineffassign, staticcheck
- Several enabled linters (varcheck, structcheck, deadcode) are **deprecated and removed** in modern golangci-lint
- No `.golangci.yml` config file — all configuration is inline in Makefile/workflow
- Also runs legacy `golint` (deprecated since 2020)

**Missing quality tools:**
- No pre-commit hooks (`.pre-commit-config.yaml`)
- No static analysis (gosec, semgrep)
- No secret detection (gitleaks, trufflehog)
- No dependency scanning
- No code formatting enforcement (gofmt/goimports are not in CI)

### Container Images

**Dockerfile** (`build/Dockerfile`):
- Based on `registry.access.redhat.com/ubi8/ubi-minimal:latest`
- Single-stage build (binary compiled externally)
- Single architecture only (no multi-arch)
- Installs `tar` for kubectl cp support
- Proper USER directive (non-root, UID 1001)
- No HEALTHCHECK instruction
- No LABEL instructions for metadata
- No vulnerability scanning

**Missing:**
- Multi-architecture support (arm64, s390x, ppc64le)
- Image startup validation
- SBOM generation
- Image signing/attestation
- Trivy/Snyk scanning

### Security

**No security tooling detected:**
- No container image scanning (Trivy, Snyk, Grype)
- No SAST (CodeQL, gosec, Semgrep)
- No dependency scanning (Dependabot, Renovate, Snyk)
- No secret detection (Gitleaks, TruffleHog)
- No SBOM generation
- Credentials handling in scripts (AWS keys, Azure keys) without secret management

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No rules exist
- **Quality**: N/A
- **Gaps**: No CLAUDE.md, no .claude/ directory, no rules for any test type
- **Recommendation**: Generate comprehensive rules with `/test-rules-generator` covering unit tests (envtest for controllers), integration tests, E2E tests, and CLI tests

## Recommendations

### Priority 0 (Critical)

1. **Upgrade Go toolchain** — Move from Go 1.15 to Go 1.22+ to receive security patches and modern features
2. **Add envtest-based controller tests** — Each of the 6 controllers needs reconciliation loop tests using `sigs.k8s.io/controller-runtime/pkg/envtest`
3. **Add code coverage generation** — Add `-coverprofile` flag and integrate with codecov to establish baseline
4. **Add container security scanning** — Integrate Trivy into PR workflow to scan built images

### Priority 1 (High Value)

5. **Replace shell tests with Go integration tests** — Convert `test/cli/test_cli_flow.sh` to Go-based tests with proper assertions and parallelization
6. **Add CRD validation tests** — Test all custom resource definitions (NooBaa, BackingStore, BucketClass, NamespaceStore)
7. **Modernize CI workflows** — Update GitHub Actions versions, add caching, add concurrency control
8. **Create agent rules** — Add `.claude/rules/` with unit test, integration test, and E2E test patterns
9. **Add `.golangci.yml` config** — Expand linter set, replace deprecated linters, increase strictness

### Priority 2 (Nice-to-Have)

10. **Add multi-architecture builds** — Support arm64, s390x, ppc64le for broader platform coverage
11. **Add pre-commit hooks** — Enforce formatting, linting, and basic checks locally
12. **Add SBOM generation and image signing** — Improve supply chain security
13. **Add benchmark tests** — Performance regression testing for critical data paths
14. **Implement Konflux build simulation** — Catch build integration issues before merge

## Comparison to Gold Standards

| Dimension | noobaa-operator | odh-dashboard | notebooks | kserve |
|-----------|:-:|:-:|:-:|:-:|
| Unit Test Coverage | 0.4% | ~70% | ~60% | ~80% |
| Integration/E2E | Shell scripts | Cypress + Jest | Multi-layer | Ginkgo + envtest |
| Coverage Tracking | None | Codecov enforced | Codecov | Codecov enforced |
| Security Scanning | None | Trivy + Snyk | Trivy | Trivy + CodeQL |
| Linting Config | Inline, outdated | Comprehensive | Standard | Comprehensive |
| Pre-commit Hooks | None | Yes | Yes | Yes |
| Agent Rules | None | Comprehensive | Basic | None |
| Image Testing | None | Multi-layer | 5-layer validation | Basic |
| Multi-arch | No | Yes | Yes | Yes |
| Go/Node Version | 1.15 (EOL) | Current | Current | Current |

## File Paths Reference

| Category | Path | Notes |
|----------|------|-------|
| CI Workflows | `.github/workflows/golangci-lint.yml` | Linting |
| CI Workflows | `.github/workflows/run_ci.yml` | Main CI (unit tests + build) |
| CI Workflows | `.github/workflows/testing.yml` | Mostly dead code |
| CI Workflows | `.github/workflows/manual-build.yml` | Manual dispatch build |
| Test Files | `pkg/nb/api_test.go` | BigInt marshaling tests (48 lines) |
| Test Files | `pkg/cli/cli_test.go` | CLI output tests (54 lines) |
| Shell Tests | `test/cli/test_cli_flow.sh` | CLI integration flow |
| Shell Tests | `test/test-olm.sh` | OLM installation test |
| Shell Tests | `test/test-scenario.sh` | Manual scenarios |
| Dockerfile | `build/Dockerfile` | Operator image |
| Makefile | `Makefile` | Build/test/lint targets |
| Go Module | `go.mod` | Go 1.15 (severely outdated) |
| CRDs | `deploy/crds/` | Custom Resource Definitions |
| Deploy | `deploy/` | Kubernetes manifests |
| Travis Scripts | `.travis/` | Legacy CI helper scripts |
