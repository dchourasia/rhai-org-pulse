---
repository: "opendatahub-io/distributed-workloads"
overall_score: 6.2
scorecard:
  - dimension: "Unit Tests"
    score: 5.0
    status: "Unit tests only for support library; E2E test helpers untested"
  - dimension: "Integration/E2E"
    score: 8.5
    status: "Comprehensive E2E suite across 4 test suites with tier tagging and upgrade testing"
  - dimension: "Build Integration"
    score: 8.0
    status: "Strong Konflux integration with 18 PR-time pipelines and multi-scanner security checks"
  - dimension: "Image Testing"
    score: 7.0
    status: "24 Dockerfiles with Konflux Clair/SAST/ClamAV scanning but no runtime validation"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tracking, no codecov, no coverage thresholds or reporting"
  - dimension: "CI/CD Automation"
    score: 7.5
    status: "9 GHA workflows + 40 Tekton pipelines with path-based triggers but no caching"
  - dimension: "Agent Rules"
    score: 7.0
    status: "Comprehensive AGENTS.md with test patterns, tags, and conventions; no .claude/rules/"
critical_gaps:
  - title: "Zero coverage tracking"
    impact: "No visibility into test coverage; regressions in support library go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No unit tests outside support/ package"
    impact: "Test helper utilities in trainer/utils, fms, kfto test suites lack unit validation"
    severity: "MEDIUM"
    effort: "8-16 hours"
  - title: "Minimal golangci-lint configuration"
    impact: "Only 3 linters enabled (govet, unused, ineffassign); missing security and quality linters"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No container runtime validation"
    impact: "Image startup and basic functionality not validated pre-deployment"
    severity: "MEDIUM"
    effort: "4-8 hours"
quick_wins:
  - title: "Add coverage generation to unit test workflow"
    effort: "1-2 hours"
    impact: "Immediate visibility into support library test coverage with coverprofile flag"
  - title: "Enable more golangci-lint linters"
    effort: "2-3 hours"
    impact: "Catch bugs, security issues, and code quality problems early in PR review"
  - title: "Add Go test caching to GHA workflows"
    effort: "1 hour"
    impact: "Faster CI runs by leveraging Go module and build cache"
  - title: "Add concurrency control to GHA workflows"
    effort: "30 minutes"
    impact: "Prevent redundant CI runs on rapid-fire pushes to same PR"
recommendations:
  priority_0:
    - "Add coverage tracking with codecov integration and minimum threshold enforcement"
    - "Enable comprehensive golangci-lint configuration with security-focused linters (gosec, errcheck, staticcheck)"
  priority_1:
    - "Add container image startup validation in Konflux PR pipelines"
    - "Create .claude/rules/ directory with per-test-type rules for E2E, unit, and upgrade tests"
    - "Add unit tests for trainer/utils package and shared test infrastructure"
  priority_2:
    - "Add performance regression benchmarks for training job submission latency"
    - "Enable Renovate for automated dependency updates (currently disabled)"
    - "Add CodeQL or Semgrep scanning to GHA PR workflows (supplement Konflux SAST)"
---

# Quality Analysis: distributed-workloads

## Executive Summary

- **Overall Score: 6.2/10**
- **Repository Type**: E2E test suite for distributed workloads on RHOAI (Go + Python)
- **Primary Language**: Go (test framework), Python (training scripts, notebooks)
- **Key Strengths**: Comprehensive E2E test coverage across 4 suites (KFTO, Trainer, ODH, FMS) with well-structured tier tagging, strong Konflux build integration with multi-scanner security checks (Clair, SAST-Snyk, ClamAV, RPM signature), and excellent AGENTS.md documentation
- **Critical Gaps**: Zero coverage tracking, minimal linting configuration (only 3 linters), no container runtime validation
- **Agent Rules Status**: Present (AGENTS.md with CLAUDE.md symlink) - comprehensive test writing guidelines but no .claude/rules/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 5.0/10 | Unit tests only for `tests/common/support/` package |
| Integration/E2E | 8.5/10 | Comprehensive E2E suite with tier tagging and upgrade testing |
| **Build Integration** | **8.0/10** | **Strong Konflux with 18 PR pipelines, Clair/SAST/ClamAV** |
| Image Testing | 7.0/10 | 24 Dockerfiles, Konflux scanning, but no runtime validation |
| Coverage Tracking | 1.0/10 | No coverage at all - no codecov, no thresholds, no reporting |
| CI/CD Automation | 7.5/10 | 9 GHA + 40 Tekton pipelines, path-triggers, but no caching |
| Agent Rules | 7.0/10 | Strong AGENTS.md, no `.claude/rules/` per-test-type rules |

## Critical Gaps

### 1. Zero Coverage Tracking
- **Impact**: No visibility into what the unit tests actually cover in the support library; regressions can slip through undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The `go-unit-test.yml` workflow runs `go test ./tests/common/support/...` without `-coverprofile`. No codecov integration, no `.codecov.yml`, no coverage thresholds, no PR coverage comments
- **Fix**: Add `-coverprofile=coverage.out` and codecov upload step

### 2. Minimal Linting Configuration
- **Impact**: Only 3 linters enabled (`govet`, `unused`, `ineffassign`) out of 100+ available in golangci-lint v2
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: Missing critical linters: `gosec` (security), `errcheck` (unchecked errors), `staticcheck` (bugs), `revive` (style), `gocyclo` (complexity), `bodyclose` (HTTP resource leaks)
- **Fix**: Expand `.golangci.yml` with recommended linter set

### 3. No Container Runtime Validation
- **Impact**: Images may build successfully but fail to start or function correctly
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: Konflux pipelines build images and run security scans (Clair, SAST, ClamAV) but don't validate that the image can actually start and respond. For training runtime images, no basic `python -c "import torch"` validation

### 4. No Unit Tests Outside support/ Package
- **Impact**: Test helper utilities in `tests/trainer/utils/` and shared infrastructure in individual test suites lack unit-level validation
- **Severity**: MEDIUM
- **Effort**: 8-16 hours

## Quick Wins

### 1. Add Coverage to Unit Test Workflow (1-2 hours)
```yaml
# In .github/workflows/go-unit-test.yml
- name: Unit tests
  run: go test -coverprofile=coverage.out -covermode=atomic ./tests/common/support/...

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    files: coverage.out
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 2. Add Concurrency Control to GHA Workflows (30 minutes)
```yaml
# Add to each workflow
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 3. Add Go Module Caching (1 hour)
The `setup-go` action already has built-in caching, but verify it's configured properly. The Go module cache can significantly speed up CI runs.

### 4. Enable More Linters (2-3 hours)
```yaml
# .golangci.yml
version: "2"
run:
  allow-parallel-runners: true
linters:
  default: none
  enable:
    - govet
    - unused
    - ineffassign
    - errcheck
    - staticcheck
    - gosec
    - bodyclose
    - revive
    - gocyclo
    - misspell
```

## Detailed Findings

### CI/CD Pipeline

#### GitHub Actions Workflows (9 total)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `go-unit-test.yml` | PR + push (Go files) | Unit tests for `tests/common/support/` |
| `go-vet.yml` | PR + push (Go files) | `go vet ./...` static analysis |
| `verify_generated_files.yml` | PR + push (Go files) | Import organization verification |
| `build-and-push-test-images.yml` | push main + dispatch | Build E2E test container image |
| `build-and-push-osu-benchmark.yml` | PR + push (benchmarks/) | Build OSU MPI benchmark images |
| `snyk-dockerfile-scan.yml` | push main + nightly + labeled PRs | Snyk IaC scan on training Dockerfiles |
| `odh-release.yml` | dispatch only | Compile and release test binaries |
| `notify-autofix-prs.yml` | PR opened + daily schedule | Slack notifications for jira-autofix PRs |
| `sync-main-to-stable.yml` | every 4h + dispatch | Sync main to stable branch with lake-gate PRs |

**Strengths**:
- Path-based triggers prevent unnecessary builds
- Snyk scanning on Dockerfiles with HIGH/CRITICAL threshold
- Automated main-to-stable sync with Mergify fast-forward
- jira-autofix bot integration with Slack notifications

**Gaps**:
- No concurrency control on any workflow
- No Go module caching explicitly configured
- Unit tests only run on support/ package
- No coverage generation or reporting
- No E2E tests in CI (requires OpenShift cluster)

#### Tekton/Konflux Pipelines (40 total)

- **18 PR pipelines**: Build images on PRs with path-change triggers
- **22 push pipelines**: Build and push images on merge to main

Each Konflux pipeline includes:
- `build-container` (buildah)
- `clair-scan` (vulnerability scanning)
- `sast-snyk-check` (SAST analysis)
- `clamav-scan` (malware detection)
- `deprecated-base-image-check`
- `ecosystem-cert-preflight-checks`
- `rpms-signature-scan`
- `show-sbom` (SBOM generation)
- `push-dockerfile` (Dockerfile attestation)

**Image variants covered**:
- Training: CUDA 12.1-13.0, ROCm 6.2-6.4, PyTorch 2.4-2.10, Python 3.11-3.12
- Training Hub (th06): CPU, CUDA, ROCm
- Ray: CUDA and ROCm variants
- OpenMPI: CUDA 13.0 + PyTorch 2.10

### Test Coverage

#### Unit Tests (support/ package only)
- **13 test files**, **937 lines** of test code
- **37 source files**, **5,014 lines** of source code in `tests/common/support/`
- **Test-to-code ratio**: ~19% (lines), ~35% (file count)
- **Framework**: Go standard `testing` + Gomega matchers
- **Scope**: Tests cover core helpers (batch, core, environment, events, image, ingress, kueue, machine, pytorchjob, ray, rbac, route, test)
- **Gaps**: No tests for `accelerator.go`, `authentication.go`, `client.go`, `conditions.go`, `config.go`, `dataScienceCluster.go`, `defaults.go`, `dscInitialization.go`, `jobset.go`, `jobs.go`, `kueue_operator.go`, `namespace.go`, `olm.go`, `openshift.go`, `prometheus_api_client.go`, `ray_api.go`, `ray_cluster_client.go`, `ray_cluster_client_helper.go`, `rhoai.go`, `service.go`, `storage.go`, `support.go`, `trainjob.go`, `utils.go`

#### E2E Tests (primary purpose of repo)
- **28 E2E test files** across 4 suites, **8,816 lines**
- **Test Suites**:
  - `tests/trainer/` (12 files) - Kubeflow Trainer v2: smoke, SFT, MPI, Kueue integration, upgrade, fashion MNIST, JobSet workflow, ClusterTrainingRuntimes, SDK
  - `tests/kfto/` (8 files) - KFTO v1 (PyTorchJob): smoke, MNIST, SFT, upgrade, Kueue integration
  - `tests/odh/` (4 files) - ODH integration: Ray MNIST, RayTune HPO, DeepSpeed fine-tuning, gRPC
  - `tests/fms/` (4 files) - FMS-HF-Tuning: KFTO SFT + Trainer SFT (CPU and GPU variants)

- **Tier System**: Well-structured with `Smoke`, `Tier1`, `Tier2`, `Tier3`, `Gpu`, `MultiGpu`, `MultiNode`
- **Upgrade Testing**: Pre-upgrade sleep tests + post-upgrade validation (kfto_upgrade_sleep, trainer_upgrade_sleep, kueue_upgrade)
- **Test Resources**: 14 Jupyter notebooks + 10 Python training scripts as test inputs
- **Test Infrastructure**: Namespace isolation, GenerateName for resources, automated cleanup

#### Test Resources
- **14 Jupyter notebooks** (training scenarios: SFT, LoRA, OSFT, FSDP, DeepSpeed, MPI, MNIST, failure scenarios)
- **10 Python scripts** (training entrypoints, data downloaders, environment setup)
- **Kubernetes manifests** (TrainJobs, ClusterTrainingRuntimes, MPI runtimes)

### Code Quality

#### Linting
- **golangci-lint v2.12.1** configured but minimal:
  - Only 3 linters: `govet`, `unused`, `ineffassign`
  - `allow-parallel-runners: true`
  - `max-same-issues: 0`
  - Missing critical linters: `gosec`, `errcheck`, `staticcheck`, `revive`, `bodyclose`, `gocyclo`

#### Pre-commit Hooks
- **6 hooks** across 4 repos:
  - `check-yaml`, `check-json`, `end-of-file-fixer`, `trailing-whitespace`, `pretty-format-json` (generic)
  - `isort` with black profile (Python)
  - `black` (Python formatting)
  - `flake8` with `--max-line-length=88` (Python linting)
- Uses older versions (pre-commit-hooks v2.3.0 from 2019)

#### Import Organization
- Custom `openshift-goimports` tool with CI verification
- `verify-imports.sh` hack script enforced in GHA workflow

### Container Images

#### Image Matrix (24 Dockerfiles)
| Category | Variants | Base Image |
|----------|----------|------------|
| Training Runtime | 9 images (CUDA 12.1-13.0, ROCm 6.2-6.4) | UBI9 Python |
| Training Hub (th06) | 3 images (CPU, CUDA, ROCm) | UBI9 Python |
| Ray Runtime | 4 images (CUDA + ROCm, 2 versions) | Custom |
| Ray Examples | 4 images (data, RAG, torch-cuda, torch-rocm) | Ray base |
| Test Runner | 1 image | golang:1.25 |
| Utilities | 3 images (dataset, model, mc-cli) | Various |

**Strengths**:
- UBI9 base images for production
- Multi-variant builds (CUDA, ROCm, CPU)
- Comprehensive Konflux scanning pipeline
- SBOM generation
- Proper labeling (name, summary, description, k8s display)
- InfiniBand/RDMA support for HPC workloads

**Gaps**:
- No runtime validation (no `python -c "import torch"` health check)
- No multi-architecture builds (amd64 only)
- No image size optimization tracking
- No startup time benchmarking

### Security

| Tool | Scope | Integration |
|------|-------|------------|
| **Snyk** | Dockerfile IaC + dependency scanning | GHA workflow (nightly + push) |
| **Semgrep** | Multi-language SAST (Go, Python, TS, YAML, generic) | Config file present, ~64K lines of rules |
| **Gitleaks** | Secret detection | Config file present, test fixtures excluded |
| **Clair** | Container vulnerability scanning | Konflux pipeline (every PR + push) |
| **SAST-Snyk** | Static application security testing | Konflux pipeline |
| **ClamAV** | Malware detection | Konflux pipeline |
| **RPM signature** | RPM package authenticity | Konflux pipeline |
| **Ecosystem cert** | Container certification | Konflux pipeline |

**Strengths**:
- Multi-layer security scanning (7 different tools/checks)
- Konflux pipelines enforce scanning on every PR and push
- Semgrep rules cover generic secrets, Go, Python, TS, YAML, and K8s patterns
- Gitleaks configured with sensible exclusions for test data

**Gaps**:
- Semgrep not integrated into GHA PR workflow (config present but no workflow runs it)
- Gitleaks not integrated into GHA workflow (config only)
- No CodeQL/GitHub Advanced Security integration
- Snyk `.snyk` policy excludes `examples/**` and `tests/**`

### Agent Rules (Agentic Flow Quality)

- **Status**: Present - `AGENTS.md` (5,989 bytes) with `CLAUDE.md` symlink
- **Coverage**: Comprehensive test writing guidelines covering:
  - Repository structure and test suite organization
  - Namespace isolation patterns (`test.NewTestNamespace()`)
  - Resource naming (GenerateName)
  - Cleanup (namespace-scoped vs cluster-scoped)
  - Test structure template (tags, context, namespace, resources, assertions)
  - Notebook editing conventions (1-space indent, array-of-lines source format)
  - Environment variable management (getters, no direct `os.Getenv`)
  - Tier tagging system (Smoke, Tier1-3, GPU, MultiGpu, MultiNode)
  - Lint/format commands (golangci-lint, go vet, pre-commit, targeted per-file)
  - CVE fix workflows for Python dependencies
- **Quality**: High - actionable with code examples, clear conventions
- **Gaps**:
  - No `.claude/rules/` directory with per-test-type rules
  - No explicit rules for writing Konflux/Tekton pipeline YAML
  - No rules for Dockerfile conventions
  - Missing security testing guidelines

## Recommendations

### Priority 0 (Critical)

1. **Add coverage tracking with codecov integration**
   - Add `-coverprofile=coverage.out -covermode=atomic` to unit test command
   - Integrate codecov/codecov-action for PR coverage reporting
   - Set minimum coverage threshold (start at current level, enforce non-regression)
   - Effort: 2-4 hours

2. **Expand golangci-lint configuration**
   - Enable at minimum: `errcheck`, `staticcheck`, `gosec`, `bodyclose`, `revive`, `misspell`
   - Consider `gocyclo` for complexity limits
   - Run initial pass to baseline existing issues with `//nolint` where justified
   - Effort: 2-4 hours (initial), 4-8 hours (fixing existing violations)

### Priority 1 (High Value)

3. **Add container image runtime validation**
   - For training images: basic `python -c "import torch; print(torch.__version__)"` check
   - For Ray images: verify ray import and version
   - Add as post-build step in Konflux pipelines or separate GHA workflow
   - Effort: 4-8 hours

4. **Create .claude/rules/ directory with per-test-type rules**
   - `unit-tests.md`: Patterns for testing support library functions (fake clients, table-driven tests)
   - `e2e-tests.md`: Patterns for new E2E tests (tier selection, resource lifecycle, timeout conventions)
   - `upgrade-tests.md`: Pre/post-upgrade test patterns
   - `notebook-tests.md`: Jupyter notebook test conventions
   - Effort: 4-6 hours

5. **Add unit tests for untested support/ files**
   - Priority: `client.go`, `conditions.go`, `namespace.go`, `trainjob.go`, `utils.go`
   - Use existing `fakeclient.go` infrastructure
   - Effort: 8-16 hours

### Priority 2 (Nice-to-Have)

6. **Integrate Semgrep and Gitleaks into GHA PR workflow**
   - Both have config files but no CI workflow
   - Run on Go/Python file changes
   - Effort: 2-3 hours

7. **Enable Renovate for dependency management**
   - Currently disabled (`"enabled": false` in `renovate.json`)
   - Enable with conservative settings for security patches
   - Effort: 1-2 hours

8. **Add concurrency control and caching to GHA workflows**
   - `concurrency` group per workflow + PR
   - Go module cache via `setup-go` action
   - Effort: 1-2 hours

9. **Update pre-commit hook versions**
   - `pre-commit-hooks` at v2.3.0 (2019), latest is v4.x
   - `isort` at 5.11.5, latest is 5.13+
   - Effort: 30 minutes

10. **Add performance benchmarks for test infrastructure**
    - Benchmark namespace creation, resource submission, cleanup times
    - Track E2E test execution duration trends
    - Effort: 4-8 hours

## Comparison to Gold Standards

| Dimension | distributed-workloads | odh-dashboard (gold) | notebooks (gold) | kserve (gold) |
|-----------|----------------------|---------------------|------------------|--------------|
| Unit Tests | Support only (5/10) | Multi-layer (9/10) | N/A | Coverage enforced (9/10) |
| Integration/E2E | 4 suites, tiered (8.5/10) | Contract + E2E (9/10) | Image validation (8/10) | Multi-version (9/10) |
| Build Integration | Konflux + GHA (8/10) | Full CI/CD (9/10) | Image pipelines (8/10) | PR builds (8/10) |
| Image Testing | Scanning only (7/10) | N/A | 5-layer validation (10/10) | Runtime checks (8/10) |
| Coverage | None (1/10) | Enforced (9/10) | N/A | Enforced thresholds (9/10) |
| CI/CD | 49 pipelines (7.5/10) | Comprehensive (9/10) | Automated (8/10) | Multi-version (9/10) |
| Agent Rules | AGENTS.md (7/10) | .claude/rules/ (9/10) | N/A | N/A |
| Security | 7 tools (8/10) | Standard (7/10) | Standard (7/10) | Standard (7/10) |

## File Paths Reference

### CI/CD Configuration
- `.github/workflows/go-unit-test.yml` - Unit test workflow
- `.github/workflows/go-vet.yml` - Go vet static analysis
- `.github/workflows/verify_generated_files.yml` - Import verification
- `.github/workflows/build-and-push-test-images.yml` - Test image builds
- `.github/workflows/snyk-dockerfile-scan.yml` - Snyk Dockerfile scanning
- `.github/workflows/sync-main-to-stable.yml` - Branch sync automation
- `.tekton/*.yaml` - 40 Konflux/Tekton pipeline definitions

### Test Infrastructure
- `tests/common/support/` - Shared test library (37 Go files + 13 test files)
- `tests/trainer/` - Kubeflow Trainer v2 E2E tests (12 files)
- `tests/kfto/` - KFTO v1 E2E tests (8 files)
- `tests/odh/` - ODH integration tests (4 files)
- `tests/fms/` - FMS-HF-Tuning tests (4 files)

### Code Quality
- `.golangci.yml` - Linter configuration (3 linters)
- `.pre-commit-config.yaml` - Pre-commit hooks (6 hooks)
- `semgrep.yaml` - SAST rules (~64K lines)
- `.gitleaks.toml` - Secret detection config
- `.snyk` - Snyk policy file

### Container Images
- `images/runtime/training/` - 9 training runtime Dockerfiles
- `images/universal/training/` - 3 Training Hub Dockerfiles
- `images/runtime/ray/` - 4 Ray runtime Dockerfiles
- `images/tests/Dockerfile` - E2E test runner image

### Agent Rules
- `AGENTS.md` - Comprehensive test writing guidelines
- `CLAUDE.md` - Symlink to AGENTS.md
