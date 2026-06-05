---
repository: "red-hat-data-services/distributed-workloads"
overall_score: 6.4
scorecard:
  - dimension: "Unit Tests"
    score: 4.0
    status: "Limited unit tests — only support package tested; E2E-first test repo"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Exceptional E2E suite: 175+ tests across 4 suites, tiered, GPU/multi-node coverage"
  - dimension: "Build Integration"
    score: 7.0
    status: "Konflux PR builds on image changes; no PR-time Go test image build validation"
  - dimension: "Image Testing"
    score: 6.0
    status: "39 Dockerfiles with Konflux variants; build-only validation, no runtime smoke tests"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tracking, no codecov, no thresholds"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Good PR checks (vet, lint, imports); E2E tests are external/manual; strong lake-gate sync"
  - dimension: "Agent Rules"
    score: 7.0
    status: "Comprehensive AGENTS.md with test patterns, namespace isolation, tags; no .claude/ rules directory"
critical_gaps:
  - title: "No code coverage tracking"
    impact: "Cannot measure or enforce test coverage; regressions go undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Unit tests cover only support package"
    impact: "33 unit tests for 5000+ lines of support code; E2E test helpers have low unit coverage"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No container runtime validation"
    impact: "39 Dockerfiles are built but never smoke-tested; startup failures caught only in deployment"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "E2E tests run externally (Jenkins/manual), not in GitHub CI"
    impact: "No automated E2E gate on PRs; test image built and pushed post-merge only"
    severity: "MEDIUM"
    effort: "16-24 hours"
quick_wins:
  - title: "Add Go coverage to unit test workflow"
    effort: "2-3 hours"
    impact: "Visibility into support package coverage; foundation for enforcement"
  - title: "Run golangci-lint in CI on PRs"
    effort: "1-2 hours"
    impact: "Makefile target exists but no GitHub workflow; catches lint issues earlier"
  - title: "Add Trivy container scanning to PR workflow"
    effort: "2-3 hours"
    impact: "Early CVE detection for runtime images beyond Snyk Dockerfile-only scan"
  - title: "Create .claude/rules/ for test patterns"
    effort: "2-3 hours"
    impact: "AI-assisted test creation follows the Tags/namespace/GenerateName conventions"
recommendations:
  priority_0:
    - "Add codecov integration with coverage thresholds for the support package"
    - "Expand unit tests for support package (currently 33 tests for 5000+ LOC)"
    - "Add container startup smoke tests for built images (at minimum a health check)"
  priority_1:
    - "Run golangci-lint as a PR workflow (target exists in Makefile but missing from CI)"
    - "Add Trivy container image scanning beyond Snyk Dockerfile-only scanning"
    - "Create .claude/rules/ directory with test-type-specific rules mirroring AGENTS.md"
  priority_2:
    - "Add semgrep as a CI workflow (config exists in repo but no automation)"
    - "Upgrade pre-commit-config hooks to latest versions (currently pinned to v2.3.0 from 2020)"
    - "Add renovate/dependabot for Go dependency updates (renovate.json currently disabled)"
---

# Quality Analysis: distributed-workloads

## Executive Summary

- **Overall Score: 6.4/10**
- **Repository Type**: E2E test suite + container runtime images for distributed ML workloads on RHOAI
- **Primary Languages**: Go (test framework), Python (training scripts), Dockerfiles
- **Key Strengths**: Extensive E2E test suite (208 test functions across 4 suites), comprehensive Konflux pipeline coverage (47 Tekton pipelines), strong agent rules in AGENTS.md, excellent security tooling configuration (Semgrep, Gitleaks, Snyk)
- **Critical Gaps**: No code coverage tracking, limited unit testing, no container runtime validation, E2E tests not integrated into PR CI
- **Agent Rules Status**: Present (AGENTS.md) — comprehensive but no `.claude/rules/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 4.0/10 | Limited unit tests — only support package tested |
| Integration/E2E | 9.0/10 | Exceptional: 175+ E2E tests, 4 suites, tiered, GPU/multi-node |
| Build Integration | 7.0/10 | Konflux PR builds on image changes; no Go test image validation |
| Image Testing | 6.0/10 | 39 Dockerfiles with Konflux variants; build-only, no runtime tests |
| Coverage Tracking | 1.0/10 | No coverage tracking at all |
| CI/CD Automation | 7.0/10 | Good PR checks; E2E external; strong lake-gate sync automation |
| Agent Rules | 7.0/10 | Comprehensive AGENTS.md; no `.claude/rules/` directory |

## Critical Gaps

### 1. No Code Coverage Tracking
- **Impact**: Cannot measure how much of the support library or test helpers are covered; regressions in test infrastructure go undetected
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No `.codecov.yml`, no coverage flags in `go test`, no PR coverage reporting. The `go-unit-test.yml` workflow runs `go test ./tests/common/support/...` without `-cover` or `-coverprofile`.

### 2. Unit Tests Cover Only Support Package
- **Impact**: The support package has ~5000 LOC but only 33 unit test functions. Test helpers for Ray, PyTorchJob, Kueue, TrainJob, etc. lack unit-level validation.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Details**: Unit tests exist in `tests/common/support/*_test.go` (13 test files), but they only cover a fraction of the support code. Files like `ray.go`, `pytorchjob.go`, `kueue.go`, `trainjob.go` have test files but likely low coverage.

### 3. No Container Runtime Validation
- **Impact**: 39 Dockerfiles across training, Ray, and utility images are built by Konflux but never runtime-tested. Startup failures or missing dependencies are caught only when deployed to real clusters.
- **Severity**: MEDIUM
- **Effort**: 8-12 hours
- **Details**: Konflux pipelines build images on PR and push events, but there's no container startup test, health check, or even `docker run --entrypoint` validation.

### 4. E2E Tests Run Externally
- **Impact**: The 175+ E2E tests require real OpenShift clusters with GPUs — they cannot run in GitHub Actions. Tests run via Jenkins or manual execution, meaning PR authors don't get automated E2E feedback.
- **Severity**: MEDIUM
- **Effort**: 16-24 hours (for subset automation)
- **Details**: This is an inherent constraint of GPU-dependent distributed training tests. The test image is built and pushed to Quay post-merge. The lake-gate workflow provides a gating mechanism for image changes via the `stable` branch.

## Quick Wins

### 1. Add Go Coverage to Unit Test Workflow (2-3 hours)
```yaml
# In .github/workflows/go-unit-test.yml
- name: Unit tests
  run: |
    go test -cover -coverprofile=coverage.out ./tests/common/support/...
    go tool cover -func=coverage.out
```
Add codecov upload step for PR coverage reporting.

### 2. Run golangci-lint in CI on PRs (1-2 hours)
The `Makefile` has a `golangci-lint` target with v2.12.1, but there's no GitHub workflow that runs it on PRs. Create `.github/workflows/golangci-lint.yml`:
```yaml
name: golangci-lint
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-go@v5
      with:
        go-version-file: './go.mod'
    - name: Run golangci-lint
      run: make golangci-lint
```

### 3. Add Trivy Container Scanning (2-3 hours)
The repo has Snyk scanning for Dockerfiles (IaC scan only), but no actual container image scanning. Add Trivy to the PR workflow for built images.

### 4. Create .claude/rules/ for Test Patterns (2-3 hours)
The AGENTS.md is excellent but lives at the root level. Creating structured `.claude/rules/` files for e2e-tests, unit-tests, and notebook-editing would improve AI-assisted development.

## Detailed Findings

### CI/CD Pipeline

**Workflows (10 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `go-unit-test.yml` | PR + push (Go files) | Unit tests for support package |
| `go-vet.yml` | PR + push (Go files) | Go vet static analysis |
| `verify_generated_files.yml` | PR + push (Go files) | Import organization verification |
| `build-and-push-test-images.yml` | Push to main | Build & push E2E test image |
| `build-and-push-test-images-release-branch.yml` | Push to rhoai-* | Build test image for RHOAI releases |
| `build-and-push-osu-benchmark.yml` | PR + push (benchmark changes) | Build OSU MPI benchmark images |
| `snyk-dockerfile-scan.yml` | Push + scheduled + labeled PRs | Snyk IaC scan on training Dockerfiles |
| `odh-release.yml` | Manual dispatch | Compile & release test binaries |
| `sync-main-to-stable.yml` | Every 4 hours + manual | Sync main→stable with lake-gate gating |
| `notify-autofix-prs.yml` | PR opened + daily schedule | Slack notifications for jira-autofix PRs |

**Strengths:**
- Path-based triggers on Go/image files avoid unnecessary runs
- Sophisticated lake-gate sync process with Mergify auto-merge
- Release workflow compiles test binaries for distribution
- Good use of workflow_dispatch for manual controls

**Gaps:**
- No golangci-lint CI workflow (only available via Makefile)
- No semgrep CI workflow (config exists but not automated)
- No coverage reporting
- E2E tests are external to GitHub CI

**Tekton/Konflux Pipelines (47 pipelines):**
- Extensive Konflux coverage for training runtime images
- Both pull-request and push pipelines for each image variant
- Path-based CEL expressions trigger only on relevant image changes
- Centrally managed via `konflux-central` repository
- Covers CUDA (121, 124, 128, 130), ROCm (62, 64), and CPU variants
- Multiple Python versions (3.11, 3.12) and PyTorch versions (2.4-2.10)

### Test Coverage

**Test Organization:**
- **Total test functions**: 208
- **Unit tests** (support package): 33 functions in 13 files
- **E2E tests**: 175 functions across 4 suites:
  - `tests/trainer/`: 68 tests (Kubeflow Trainer v2, MPI, SDK)
  - `tests/kfto/`: 52 tests (KFTO v1, PyTorchJob)
  - `tests/odh/`: 13 tests (ODH integration, Ray)
  - `tests/fms/`: 42 tests (fms-hf-tuning, GPU fine-tuning)

**Test Infrastructure:**
- Shared support library: ~5000 LOC in `tests/common/support/`
- Covers: Kubernetes clients, Ray clusters, PyTorchJob, Kueue, TrainJob, RBAC, S3, namespaces
- Fake client support for unit testing (`fakeclient.go`)
- Test tier system: Smoke, Tier1-3, GPU, MultiGpu, MultiNode
- Namespace isolation with automatic cleanup
- GenerateName for resource uniqueness

**Test Frameworks:**
- Go standard `testing` package
- Gomega matchers for assertions
- Custom `test.Eventually()` for async Kubernetes operations
- `gotestsum` for test output formatting

**Test-to-Code Ratio**: 41 test files / 102 total Go files = 40% (good for an E2E-focused repo)

**Coverage Tracking**: None. No `-cover` flag, no codecov, no thresholds.

### Code Quality

**Linting:**
- `.golangci.yml` (v2 format): 3 linters enabled (govet, unused, ineffassign) — minimal configuration
- `go vet` runs on PRs via dedicated workflow
- Import verification via `openshift-goimports`

**Pre-commit Hooks:**
- `.pre-commit-config.yaml` present with:
  - check-yaml, check-json, end-of-file-fixer, trailing-whitespace, pretty-format-json
  - Python: isort (5.11.5), black (24.2.0), flake8 (7.1.1)
- Hook versions are moderately dated (pre-commit-hooks v2.3.0 from ~2020)
- No Go-specific pre-commit hooks (no gofmt, golangci-lint)

**Static Analysis:**
- `semgrep.yaml`: Comprehensive 1800+ line config covering Go, Python, TypeScript, YAML, Dockerfiles, shell scripts
  - Generic secrets detection (AWS keys, GitHub tokens, etc.)
  - Kubernetes RBAC security rules
  - Container security patterns
  - GitHub Actions security (script injection, pull_request_target)
  - Go security (SQL injection, TLS, command injection)
  - Python security (pickle, eval, subprocess)
  - **BUT**: No CI workflow runs it automatically

### Container Images

**Image Matrix:**
- **Training runtime images**: 11 variants (CUDA 121/124/128/130, ROCm 62/64, CPU, OpenMPI)
- **Ray images**: 5 variants (CPU, CUDA 121/128, ROCm 61/64)
- **Universal training images (TrainingHub 0.6)**: 3 variants (CPU, CUDA 130, ROCm 64)
- **Utility images**: test runner, mc-cli, dataset, model
- **Benchmark images**: OSU MPI (CPU + CUDA)

**Dockerfile Practices:**
- UBI9 base images (Red Hat certified)
- Proper LABEL metadata
- Both upstream Dockerfiles and Konflux variants (`.konflux` suffix with pinned SHA digests)
- USER 0 for package installation, though no switch back to non-root in all cases
- No multi-stage builds (images are primarily package installation)
- No HEALTHCHECK instructions

**Build Validation:**
- Konflux pipelines build images on PR for path-gated changes
- GitHub workflow builds OSU benchmark images on PR
- No runtime validation (no `docker run` or startup test)
- No image startup smoke test

### Security

**Strengths:**
- **Snyk**: Dockerfile IaC scanning for training images (daily + push + labeled PRs), HIGH/Critical threshold
- **Gitleaks**: Comprehensive config with test file exclusions, default rules extended
- **Semgrep**: 1800-line config covering multiple languages and security patterns (but not automated in CI)
- **.snyk**: Policy file excluding examples and tests from scans

**Gaps:**
- No Trivy or container image scanning (Snyk only does Dockerfile IaC scan)
- Semgrep config exists but no CI workflow to run it
- No CodeQL/SAST integration
- No SBOM generation
- No image signing/attestation (may be handled by Konflux)
- Renovate dependency bot is **disabled** (`"enabled": false`)

### Agent Rules (Agentic Flow Quality)

**Status**: Present (AGENTS.md at root) — no `.claude/` directory

**AGENTS.md Quality**: Excellent — one of the more comprehensive agent rules files analyzed:
- Repository structure overview
- Test suite organization
- Running instructions with examples
- Lint/format commands (both project-wide and targeted)
- **Writing Tests** section with:
  - Namespace isolation patterns
  - Resource naming with GenerateName
  - Cleanup guidance
  - Test structure template
  - Notebook editing conventions
  - Environment variable patterns
  - Tag system documentation
  - CVE fix instructions

**Gaps:**
- No `.claude/` directory with structured rules files
- No `.claude/rules/` for test-type-specific guidance
- AGENTS.md format is good but not machine-parseable for different test types
- Missing rules for: unit test patterns, container image testing, CI workflow changes

## Recommendations

### Priority 0 (Critical)

1. **Add codecov integration with coverage thresholds**
   - Add `-cover -coverprofile=coverage.out` to go-unit-test workflow
   - Create `.codecov.yml` with minimum thresholds
   - Add codecov upload step
   - Effort: 4-6 hours

2. **Expand unit tests for support package**
   - Current: 33 unit tests for ~5000 LOC
   - Target: Cover key helper functions in ray.go, pytorchjob.go, kueue.go, trainjob.go
   - Use existing fakeclient.go infrastructure
   - Effort: 16-24 hours

3. **Add container startup smoke tests**
   - At minimum, run `docker run --entrypoint <image> --version` or a health check
   - Can be added to Konflux pipelines or as a GitHub workflow
   - Effort: 8-12 hours

### Priority 1 (High Value)

4. **Run golangci-lint in CI on PRs**
   - Makefile target exists; just needs a GitHub workflow
   - Currently only runs manually; PRs can merge with lint issues
   - Effort: 1-2 hours

5. **Add Trivy container image scanning**
   - Snyk only does Dockerfile IaC analysis, not full image scanning
   - Add Trivy scan as part of image build workflows
   - Effort: 2-3 hours

6. **Automate semgrep scanning in CI**
   - The 1800-line semgrep.yaml config is excellent but not run automatically
   - Add a PR workflow or pre-commit hook
   - Effort: 2-3 hours

7. **Create .claude/rules/ directory**
   - Port AGENTS.md test patterns into structured per-type rule files
   - Add rules for e2e-tests, unit-tests, notebook-editing, dockerfile-changes
   - Effort: 2-3 hours

### Priority 2 (Nice-to-Have)

8. **Enable Renovate for Go dependency updates**
   - `renovate.json` exists but has `"enabled": false`
   - Enable with appropriate grouping and auto-merge rules
   - Effort: 1-2 hours

9. **Upgrade pre-commit hook versions**
   - pre-commit-hooks at v2.3.0 (~2020), should be v5.x
   - isort, black, flake8 could be updated
   - Effort: 1-2 hours

10. **Add SBOM generation to image builds**
    - Konflux may handle this, but explicit SBOM generation ensures compliance
    - Effort: 4-6 hours

## Comparison to Gold Standards

| Dimension | distributed-workloads | odh-dashboard (Gold) | notebooks (Gold) | Gap |
|-----------|----------------------|---------------------|-------------------|-----|
| Unit Tests | 4/10 (support only) | 9/10 (high coverage) | 7/10 | Large |
| E2E Tests | 9/10 (exceptional) | 9/10 | 8/10 | None |
| Coverage Tracking | 1/10 (none) | 8/10 (codecov) | 6/10 | Critical |
| Image Testing | 6/10 (build only) | 7/10 | 9/10 (5-layer) | Moderate |
| CI/CD | 7/10 | 9/10 | 8/10 | Small |
| Security Scanning | 6/10 (Snyk only) | 8/10 | 7/10 | Moderate |
| Agent Rules | 7/10 (AGENTS.md) | 9/10 (.claude/rules/) | 5/10 | Small |
| Linting | 5/10 (3 linters, no CI) | 9/10 | 7/10 | Moderate |

## File Paths Reference

### CI/CD
- `.github/workflows/go-unit-test.yml` — Unit tests
- `.github/workflows/go-vet.yml` — Go vet
- `.github/workflows/verify_generated_files.yml` — Import verification
- `.github/workflows/build-and-push-test-images.yml` — Test image build
- `.github/workflows/snyk-dockerfile-scan.yml` — Snyk scanning
- `.github/workflows/sync-main-to-stable.yml` — Lake-gate sync
- `.tekton/` — 47 Konflux pipelines (managed via konflux-central)

### Testing
- `tests/common/support/` — Shared test infrastructure (~5000 LOC)
- `tests/trainer/` — Kubeflow Trainer v2 tests (68 tests)
- `tests/kfto/` — KFTO v1 tests (52 tests)
- `tests/odh/` — ODH integration tests (13 tests)
- `tests/fms/` — fms-hf-tuning tests (42 tests)

### Code Quality
- `.golangci.yml` — golangci-lint v2 config (3 linters)
- `.pre-commit-config.yaml` — Pre-commit hooks
- `semgrep.yaml` — Comprehensive security rules (not automated)
- `hack/verify-imports.sh` — Import verification script

### Container Images
- `images/runtime/training/` — 11 training runtime image variants
- `images/runtime/ray/` — 5 Ray image variants
- `images/universal/training/` — 3 TrainingHub 0.6 variants
- `images/tests/Dockerfile` — E2E test runner image

### Security
- `.gitleaks.toml` — Gitleaks secret detection config
- `.snyk` — Snyk policy (excludes examples/tests)
- `semgrep.yaml` — 1800+ line security rules

### Agent Rules
- `AGENTS.md` — Comprehensive agent guidance
- `Makefile` — Build/test/lint targets
