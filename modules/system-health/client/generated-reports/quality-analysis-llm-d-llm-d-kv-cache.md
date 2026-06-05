---
repository: "llm-d/llm-d-kv-cache"
overall_score: 5.8
scorecard:
  - dimension: "Unit Tests"
    score: 8.0
    status: "Excellent Go test coverage (84% test-to-code LOC ratio) with testify and benchmark tests"
  - dimension: "Integration/E2E"
    score: 7.0
    status: "Good E2E suite using testcontainers-go and Ginkgo, path-filtered Python integration tests"
  - dimension: "Build Integration"
    score: 4.0
    status: "No PR-time Konflux simulation, no manifest validation, limited image validation"
  - dimension: "Image Testing"
    score: 5.0
    status: "Multi-stage Dockerfiles with multi-arch support, but no runtime startup validation or SBOM"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage generation, no codecov integration, no thresholds or PR reporting"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Comprehensive PR workflows, nightly race detection, Trivy scanning on releases"
  - dimension: "Agent Rules"
    score: 1.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory — zero AI agent guidance"
critical_gaps:
  - title: "No test coverage tracking or enforcement"
    impact: "Cannot detect coverage regressions; no visibility into untested code paths"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No PR-time build integration testing"
    impact: "Build failures discovered only after merge in Konflux/production pipelines"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No CodeQL/SAST or secret detection"
    impact: "Security vulnerabilities and leaked secrets may go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI-generated code lacks project-specific testing patterns and quality standards"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "No dependency update automation (Dependabot/Renovate)"
    impact: "Dependencies can become stale with known vulnerabilities"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add codecov integration with coverage generation"
    effort: "2-4 hours"
    impact: "Immediate visibility into test coverage; enables enforcement of coverage thresholds on PRs"
  - title: "Add CodeQL SAST workflow"
    effort: "1-2 hours"
    impact: "Automated security analysis for Go code on every PR"
  - title: "Enable Dependabot for Go modules and Python deps"
    effort: "30 minutes"
    impact: "Automated dependency updates and vulnerability alerts"
  - title: "Add concurrency control to PR workflows"
    effort: "30 minutes"
    impact: "Prevents redundant CI runs on rapid pushes, saves runner time"
  - title: "Create basic .claude/rules/ for test patterns"
    effort: "2-3 hours"
    impact: "Consistent AI-generated tests matching project conventions"
recommendations:
  priority_0:
    - "Add Go coverage generation (`go test -coverprofile`) and integrate codecov with PR reporting and minimum threshold enforcement"
    - "Add CodeQL/SAST workflow for Go and Python source code analysis"
    - "Add gitleaks or similar secret detection to PR workflows"
  priority_1:
    - "Add PR-time Docker image build validation with startup smoke test"
    - "Create comprehensive agent rules (.claude/rules/) covering unit, integration, and E2E test patterns"
    - "Enable Dependabot for automated dependency updates"
    - "Add concurrency control to all PR-triggered workflows"
  priority_2:
    - "Add SBOM generation and image signing/attestation for release images"
    - "Implement PR-time Konflux build simulation"
    - "Add Trivy scanning to PR workflow (not just releases)"
    - "Add Python coverage tracking for UDS tokenizer and fs_backend tests"
---

# Quality Analysis: llm-d-kv-cache

## Executive Summary

- **Overall Score: 5.8/10**
- **Repository Type**: Go library/service + Python services + C++/CUDA native code
- **Languages**: Go (primary), Python, C++/CUDA
- **Framework**: Kubernetes ecosystem (client-go, controller-runtime)
- **Key Strengths**: Excellent Go unit test coverage (84% LOC ratio), comprehensive linting (40+ golangci-lint checks), well-structured CI/CD with nightly race detection, multi-architecture Docker builds
- **Critical Gaps**: Zero test coverage tracking/enforcement, no SAST/CodeQL, no secret detection, no agent rules
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or `.claude/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8/10 | Excellent Go test coverage (84% test-to-code LOC ratio) with testify and benchmark tests |
| Integration/E2E | 7/10 | Good E2E suite using testcontainers-go and Ginkgo, path-filtered Python integration tests |
| **Build Integration** | **4/10** | **No PR-time Konflux simulation, no manifest validation, limited image validation** |
| Image Testing | 5/10 | Multi-stage Dockerfiles with multi-arch support, but no runtime startup validation or SBOM |
| Coverage Tracking | 1/10 | No coverage generation, no codecov integration, no thresholds or PR reporting |
| CI/CD Automation | 8/10 | Comprehensive PR workflows, nightly race detection, Trivy scanning on releases |
| Agent Rules | 1/10 | No CLAUDE.md, AGENTS.md, or `.claude/` directory — zero AI agent guidance |

## Critical Gaps

### 1. No Test Coverage Tracking or Enforcement
- **Impact**: Cannot detect coverage regressions; no visibility into untested code paths across Go or Python
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: `go test` runs without `-coverprofile`. No `.codecov.yml`. No coverage threshold enforcement on PRs. The high test-to-code ratio suggests actual coverage may be good, but without measurement it's invisible and unenforceable.

### 2. No PR-Time Build Integration Testing
- **Impact**: Build failures discovered only after merge in Konflux/production pipelines
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Details**: The PR workflow builds the UDS tokenizer Docker image for E2E tests, but does not validate the main `Dockerfile` build, kustomize manifests (`deploy/`), or Helm charts (`vllm-setup-helm/`). Build issues in the primary Go service image are only caught at release time.

### 3. No CodeQL/SAST or Secret Detection
- **Impact**: Security vulnerabilities and leaked secrets may go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: While `gosec` is enabled as a golangci-lint plugin, there is no dedicated SAST workflow (CodeQL, Semgrep) for deeper analysis. No `gitleaks` or `TruffleHog` for secret detection. The Trivy scan only runs on release images, not on PRs.

### 4. No Agent Rules for AI-Assisted Development
- **Impact**: AI-generated code lacks project-specific testing patterns and quality standards
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: No `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`. AI agents have no guidance on test naming conventions, framework usage (testify vs Ginkgo), mock patterns, or coverage expectations.

### 5. No Dependency Update Automation
- **Impact**: Dependencies can become stale with known vulnerabilities
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No Dependabot or Renovate configuration. Go modules and Python dependencies are updated manually. The `go.mod` shows Go 1.25 and recent dependencies, but there's no automated process to keep them current.

## Quick Wins

### 1. Add Codecov Integration with Coverage Generation (2-4 hours)
Add `-coverprofile=coverage.out` to `go test` and upload to codecov:

```yaml
# In ci-test.yaml, modify the unit-test job:
- name: Run unit tests with coverage
  run: |
    go test -v -coverprofile=coverage.out ./pkg/...
    go tool cover -func=coverage.out

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v5
  with:
    files: coverage.out
    fail_ci_if_error: false
```

### 2. Add CodeQL SAST Workflow (1-2 hours)
```yaml
name: CodeQL Analysis
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 8 * * 1'
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v6
      - uses: github/codeql-action/init@v3
        with:
          languages: go, python
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
```

### 3. Enable Dependabot (30 minutes)
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: gomod
    directory: /
    schedule:
      interval: weekly
  - package-ecosystem: pip
    directory: /services/uds_tokenizer
    schedule:
      interval: weekly
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

### 4. Add Concurrency Control (30 minutes)
Add to each PR workflow:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}
  cancel-in-progress: true
```

### 5. Create Basic Agent Rules (2-3 hours)
Create `.claude/rules/` with test patterns for Go (testify, table-driven tests) and Python (pytest fixtures, conftest patterns).

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (23 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-test.yaml` | PR (main, dev) | Unit tests + E2E tests (parallel jobs) |
| `ci-lint.yaml` | PR (main, dev) | Pre-commit hooks, golangci-lint, ruff, clang-format |
| `ci-uds-tokenizer.yaml` | PR (path-filtered) | Python integration tests |
| `ci-examples.yaml` | PR (main) | Build and verify all Go examples |
| `ci-signed-commits.yaml` | PR | Signed commit verification |
| `ci-nightly-race.yaml` | Schedule (daily 06:00 UTC) | Go race detector |
| `ci-release.yaml` | Tag/release | Docker image build + Trivy scan |
| `ci-release-uds-tokenizer.yaml` | Tag/release | UDS tokenizer image + Trivy scan |
| `ci-dev-uds-tokenizer.yaml` | Push to main | Dev image build + Trivy scan |
| `ci-wheels.yaml` | Tag | CUDA wheel builds (multi-arch, multi-CUDA) |
| `ci-pages-index.yaml` | Release | Publish PyPI pages index |

**Strengths**:
- Well-separated concerns across workflows
- Good use of caching (apt, Go modules, Docker layer GHA cache)
- Path-filtered workflows reduce unnecessary CI runs
- Nightly race detection catches concurrency bugs proactively
- Prow integration for Kubernetes-style PR management

**Weaknesses**:
- No concurrency control on PR workflows — rapid pushes trigger redundant runs
- No coverage reporting step in test workflows
- Trivy scanning only on release/dev builds, not on PRs
- No workflow for the main Go Dockerfile on PRs

### Test Coverage

**Go Tests (30 test files, 8,447 LOC)**:

| Package | Test Files | Key Tests |
|---------|-----------|-----------|
| `pkg/kvcache/kvblock/` | 10 | index, in_memory, redis, valkey, token_processor, cost_aware_memory, extra_keys, traced_index, instrumented_index |
| `pkg/kvcache/` | 4 | indexer, kvblock_scorer, traced_scorer, export, metrics/collector |
| `pkg/kvevents/` | 4 | zmq_subscriber, subscriber_manager, pool |
| `pkg/kvevents/engineadapter/` | 3 | vllm_adapter, sglang_adapter, common |
| `pkg/tokenization/` | 2 | pool, uds_tokenizer |
| `pkg/utils/` | 1 | slices |
| `tests/e2e/uds_tokenizer/` | 3 | UDS E2E suite (Ginkgo) |
| `tests/integration/` | 1 | kv_events integration |
| `tests/profiling/` | 1 | index benchmark |

**Benchmark Tests**: `zmq_subscriber_bench_test.go`, `vllm_adapter_bench_test.go`, `index_benchmark_test.go`

**Python Tests (10 test files)**:

| Component | Test Files | Type |
|-----------|-----------|------|
| `services/uds_tokenizer/tests/` | 2 | Unit (renderer) + integration |
| `kv_connectors/llmd_fs_backend/tests/` | 5 | Unit (fs, gds, obj, priority_queue, storage_events) |
| `kv_connectors/llmd_fs_backend/tests/performance/` | 2 | Performance (throughput, stress) |
| `kv_connectors/pvc_evictor/tests/` | 1 | Unit (deleter) |

**Test-to-Code Ratio**:
- Go: 30 test files / 50 source files = **60% file coverage**
- Go LOC: 8,447 test / 9,999 source = **84.5% LOC ratio** (excellent)
- Python: 10 test files / 37 source files = **27% file coverage** (needs improvement)

**Testing Frameworks**:
- Go: `testing` stdlib, `testify` (assert/require), `testcontainers-go`, Ginkgo/Gomega
- Python: `pytest` with fixtures and `conftest.py`

**Test Data**: `pkg/tokenization/testdata/` with model configs (tokenizer.json, config.json, special_tokens_map.json)

### Code Quality

**Go Linting** — golangci-lint v2.9.0 with **40+ linters** (excellent):

Key enabled linters: `gosec`, `govet`, `gocritic` (all tags), `staticcheck` (all checks), `errcheck`, `errorlint`, `bodyclose`, `contextcheck`, `ineffassign`, `revive`, `varnamelen`, `lll` (130 char), `prealloc`, `tparallel`, `testpackage`, `promlinter`

Formatters: `gofumpt`, `goimports`

**Python Linting** — Ruff:
- Target: Python 3.12
- Rules: pycodestyle, Pyflakes, pyupgrade, bugbear, simplify, isort, logging-format
- Line length: 120

**C++/CUDA** — clang-format for 18 C++/CUDA source files

**Pre-commit Hooks**:
- `.pre-commit-config.yaml` with ruff, typos, clang-format, actionlint, pip-compile
- `hooks/pre-commit.sh` runs `make lint` + `make test`
- Install via `make install-hooks`

**Static Analysis**:
- `gosec` enabled via golangci-lint
- `gocritic` with diagnostic, experimental, opinionated, performance, and style tags
- No CodeQL or Semgrep
- No gitleaks for secret detection

### Container Images

**Dockerfiles** (5 total):

| File | Purpose | Multi-stage | Non-root |
|------|---------|-------------|----------|
| `Dockerfile` | Main Go KV cache manager | Yes (builder + UBI9) | Yes (65532) |
| `services/uds_tokenizer/Dockerfile` | Python gRPC tokenizer | Yes (builder + slim) | Yes (65532) |
| `kv_connectors/pvc_evictor/Dockerfile` | PVC evictor | - | - |
| `kv_connectors/llmd_fs_backend/Dockerfile.dev` | FS backend dev | - | - |
| `kv_connectors/llmd_fs_backend/Dockerfile.wheel` | CUDA wheel builder | - | - |

**Multi-architecture**: `linux/amd64,linux/arm64` for release images

**Security**:
- Trivy scanning on release and dev images (HIGH/CRITICAL severity)
- Non-root user in production images
- No SBOM generation
- No image signing or attestation
- No Trivy on PRs

### Security

| Practice | Status | Details |
|----------|--------|---------|
| Container scanning (Trivy) | Partial | Release/dev only, not on PRs |
| SAST (CodeQL/gosec) | Partial | gosec via lint, no CodeQL |
| Secret detection | Missing | No gitleaks/TruffleHog |
| Signed commits | Present | Reusable workflow from llm-d-infra |
| Dependency scanning | Missing | No Dependabot/Renovate |
| Non-root containers | Present | UID 65532 in production images |
| SBOM generation | Missing | — |
| Image signing | Missing | — |

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Does not exist
- **.claude/rules/**: Does not exist
- **Coverage**: No test types have rules
- **Quality**: N/A — no rules exist
- **Gaps**: All test type rules missing (unit-tests, integration-tests, e2e-tests, benchmark-tests)
- **Copilot**: Has `copilot-setup-steps.yml` but only installs `gh-aw` extension — no coding guidance
- **Recommendation**: Generate comprehensive rules with `/test-rules-generator` covering:
  - Go unit test patterns (testify, table-driven, test isolation)
  - Go E2E patterns (Ginkgo suites, testcontainers)
  - Python test patterns (pytest, fixtures, conftest)
  - Benchmark test patterns

## Recommendations

### Priority 0 (Critical)

1. **Add test coverage generation and enforcement**
   - Add `-coverprofile=coverage.out` to Go test commands
   - Integrate codecov with PR reporting
   - Set minimum coverage threshold (suggest 70% initially)
   - Add Python coverage via `pytest-cov` for UDS tokenizer and fs_backend
   - Effort: 4-6 hours

2. **Add CodeQL/SAST security analysis**
   - Add CodeQL workflow for Go and Python
   - Run on PRs and weekly schedule
   - Enable security-events write permission
   - Effort: 1-2 hours

3. **Add secret detection**
   - Add gitleaks to PR workflow or pre-commit hooks
   - Effort: 1 hour

### Priority 1 (High Value)

4. **Add PR-time Docker image build validation**
   - Build main `Dockerfile` on PRs (not just UDS tokenizer)
   - Add startup smoke test for built image
   - Validate kustomize manifests build correctly
   - Effort: 4-6 hours

5. **Create comprehensive agent rules**
   - `.claude/rules/unit-tests.md` — Go testify patterns, table-driven tests, test isolation
   - `.claude/rules/e2e-tests.md` — Ginkgo suites, testcontainers patterns
   - `.claude/rules/python-tests.md` — pytest, fixtures, conftest patterns
   - `.claude/rules/benchmarks.md` — Go benchmark patterns, performance regression detection
   - Effort: 4-6 hours

6. **Enable Dependabot**
   - Go modules, pip (UDS tokenizer, fs_backend), GitHub Actions
   - Effort: 30 minutes

7. **Add concurrency control to PR workflows**
   - Prevent redundant CI runs on rapid pushes
   - Effort: 30 minutes

### Priority 2 (Nice-to-Have)

8. **Add SBOM generation for release images**
   - Use Syft or Trivy for SBOM generation
   - Attach SBOMs to releases alongside wheels
   - Effort: 2-3 hours

9. **Add Trivy scanning to PR workflow**
   - Catch vulnerability issues before merge, not just at release
   - Effort: 2 hours

10. **Add image signing/attestation**
    - Use cosign for image signing
    - Generate provenance attestations
    - Effort: 4-6 hours

11. **Add Python coverage tracking**
    - `pytest-cov` for UDS tokenizer and fs_backend test suites
    - Integrate with codecov alongside Go coverage
    - Effort: 2-3 hours

12. **Implement PR-time Konflux build simulation**
    - Validate builds match production pipeline
    - Effort: 8-12 hours

## Comparison to Gold Standards

| Dimension | llm-d-kv-cache | odh-dashboard | notebooks | kserve |
|-----------|---------------|---------------|-----------|--------|
| Unit Tests | 8/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 7/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 4/10 | 8/10 | 7/10 | 7/10 |
| Image Testing | 5/10 | 7/10 | 9/10 | 7/10 |
| Coverage Tracking | 1/10 | 9/10 | 5/10 | 9/10 |
| CI/CD Automation | 8/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 1/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **5.8** | **8.7** | **7.1** | **7.8** |

**Key Differentiators**:
- **vs odh-dashboard**: Missing coverage enforcement, contract tests, and agent rules that odh-dashboard excels at
- **vs notebooks**: Missing the 5-layer image validation strategy that notebooks pioneered
- **vs kserve**: Missing coverage enforcement and multi-version testing, though has comparable lint depth

## File Paths Reference

### CI/CD
- `.github/workflows/ci-test.yaml` — Unit + E2E tests
- `.github/workflows/ci-lint.yaml` — Lint (golangci-lint, ruff, pre-commit)
- `.github/workflows/ci-uds-tokenizer.yaml` — Python integration tests
- `.github/workflows/ci-examples.yaml` — Example verification
- `.github/workflows/ci-nightly-race.yaml` — Nightly race detection
- `.github/workflows/ci-release.yaml` — Release image build
- `.github/workflows/ci-release-uds-tokenizer.yaml` — UDS tokenizer release
- `.github/workflows/ci-dev-uds-tokenizer.yaml` — Dev image build
- `.github/workflows/ci-wheels.yaml` — CUDA wheel builds
- `.github/actions/trivy-scan/action.yml` — Trivy composite action
- `.github/actions/docker-build-and-push/action.yml` — Docker build composite

### Testing
- `pkg/kvcache/kvblock/*_test.go` — KV block index tests
- `pkg/kvcache/*_test.go` — KV cache indexer and scorer tests
- `pkg/kvevents/*_test.go` — KV event subscriber tests
- `pkg/tokenization/*_test.go` — Tokenization pool and UDS tests
- `tests/e2e/uds_tokenizer/` — E2E test suite (Ginkgo)
- `tests/integration/kv_events_test.go` — Integration tests
- `tests/profiling/` — Benchmark tests
- `services/uds_tokenizer/tests/` — Python unit + integration tests
- `kv_connectors/llmd_fs_backend/tests/` — FS backend tests
- `kv_connectors/pvc_evictor/tests/` — Evictor tests

### Code Quality
- `.golangci.yml` — golangci-lint config (40+ linters)
- `ruff.toml` — Python linter config
- `.pre-commit-config.yaml` — Pre-commit hooks
- `hooks/pre-commit.sh` — Git hook script

### Container Images
- `Dockerfile` — Main Go KV cache manager
- `services/uds_tokenizer/Dockerfile` — Python gRPC tokenizer
- `kv_connectors/pvc_evictor/Dockerfile` — PVC evictor
- `kv_connectors/llmd_fs_backend/Dockerfile.dev` — FS backend dev
- `kv_connectors/llmd_fs_backend/Dockerfile.wheel` — CUDA wheel builder

### Build
- `Makefile` — Build, test, lint, deploy targets
- `go.mod` — Go module (Go 1.25)
- `deploy/kustomization.yaml` — Kubernetes deployment
- `vllm-setup-helm/` — Helm chart

### Security
- `.github/workflows/ci-signed-commits.yaml` — Signed commit enforcement
- `.github/actions/trivy-scan/action.yml` — Trivy scanning
