---
repository: "red-hat-data-services/llm-d-kv-cache"
overall_score: 5.9
scorecard:
  - dimension: "Unit Tests"
    score: 7.0
    status: "Solid Go unit tests across pkg/ with testify; benchmark tests present; but no coverage enforcement"
  - dimension: "Integration/E2E"
    score: 7.5
    status: "Testcontainers-based E2E on PR; integration tests for component interaction; Kind script for cluster-level testing"
  - dimension: "Build Integration"
    score: 4.0
    status: "No PR-time Konflux simulation; Dockerfile.konflux only in Tekton push/label trigger; 3 CI workflows disabled (target main_2)"
  - dimension: "Image Testing"
    score: 5.0
    status: "Multi-stage Dockerfile; smoke test stage in Konflux Dockerfile; Trivy on release only; no PR-time image scanning"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "No codecov/coveralls integration; no coverage flags in test commands; no coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 6.0
    status: "PR tests run for unit+E2E; nightly race detector; but lint/examples/UDS-tokenizer workflows disabled (main_2 branch)"
  - dimension: "Agent Rules"
    score: 1.0
    status: "No CLAUDE.md, no .claude/ directory, no AGENTS.md; Copilot setup present but minimal"
critical_gaps:
  - title: "Three CI workflows effectively disabled — targeting non-existent main_2 branch"
    impact: "Linting, examples testing, and UDS tokenizer integration tests never run on PRs to main"
    severity: "HIGH"
    effort: "1 hour"
  - title: "No test coverage tracking or enforcement"
    impact: "Coverage regressions go undetected; no baseline or trend visibility"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No PR-time container image scanning"
    impact: "Vulnerabilities only discovered at release time via Trivy; critical CVEs can ship"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "No PR-time Konflux build validation"
    impact: "Konflux build failures discovered post-merge; Dockerfile.konflux not tested in CI"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "No agent rules or AI test automation guidance"
    impact: "AI-assisted contributions have no guardrails for test quality, patterns, or standards"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "kv_connectors Python tests not wired into CI"
    impact: "fs_backend and performance tests exist but are never run automatically"
    severity: "MEDIUM"
    effort: "3-4 hours"
quick_wins:
  - title: "Fix disabled workflows — change main_2 to main in ci-lint, ci-examples, ci-uds-tokenizer"
    effort: "30 minutes"
    impact: "Immediately enables linting, examples verification, and Python integration tests on every PR"
  - title: "Add coverage generation flags to go test commands"
    effort: "1-2 hours"
    impact: "Generates coverage data; enables future codecov integration"
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catches container vulnerabilities before merge, not just at release"
  - title: "Create basic CLAUDE.md with testing standards"
    effort: "2-3 hours"
    impact: "Establishes test quality expectations for AI-assisted contributions"
recommendations:
  priority_0:
    - "Fix disabled CI workflows by changing branch target from main_2 to main (30 min fix, massive impact)"
    - "Add coverage generation (-coverprofile, -covermode=atomic) to unit-test Makefile target"
    - "Integrate codecov with coverage thresholds and PR status checks"
  priority_1:
    - "Move Trivy scanning from release-only to PR workflow for early vulnerability detection"
    - "Wire kv_connectors/llmd_fs_backend Python tests into CI pipeline"
    - "Add PR-time Dockerfile.konflux build validation via docker build --target test"
    - "Create .claude/rules/ with test standards for Go and Python components"
  priority_2:
    - "Add Kind-based cluster integration test to periodic CI (tests/kind-vllm-cpu.sh already exists)"
    - "Add SBOM generation to release pipeline"
    - "Implement contract tests between Go gRPC client and Python tokenizer service"
    - "Add mutation testing (go-mutesting) to periodic CI"
---

# Quality Analysis: llm-d-kv-cache

## Executive Summary

- **Overall Score: 5.9/10**
- **Repository Type**: Go library + Python gRPC service for LLM KV cache management
- **Primary Languages**: Go (core library, ~5,200 LOC), Python (UDS tokenizer service, CUDA connectors)
- **Key Strengths**: Good unit test coverage in Go pkg/ with testify/testcontainers; well-structured E2E with containerized dependencies; nightly race detector; comprehensive golangci-lint config (35+ linters); multi-architecture support; Tekton/Konflux integration for production builds
- **Critical Gaps**: Three CI workflows disabled (target `main_2` instead of `main`); zero coverage tracking; container scanning only at release time; no agent rules for AI-assisted development
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory, no AGENTS.md

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.0/10 | Solid Go unit tests across pkg/ with testify; benchmark tests; no coverage enforcement |
| Integration/E2E | 7.5/10 | Testcontainers E2E on PR; integration tests; Kind script available |
| **Build Integration** | **4.0/10** | **No PR-time Konflux simulation; Dockerfile.konflux untested in CI** |
| Image Testing | 5.0/10 | Multi-stage Dockerfile; smoke test in Konflux image; Trivy release-only |
| Coverage Tracking | 2.0/10 | No codecov; no coverage flags; no thresholds |
| CI/CD Automation | 6.0/10 | PR tests for unit+E2E; nightly race; but lint/examples/tokenizer disabled |
| Agent Rules | 1.0/10 | No test automation guidance for AI agents whatsoever |

## Critical Gaps

### 1. Three CI Workflows Effectively Disabled
- **Severity**: HIGH
- **Impact**: `ci-lint.yaml`, `ci-examples.yaml`, and `ci-uds-tokenizer.yaml` all trigger on PRs to `main_2` — a branch that doesn't exist. This means:
  - **Linting never runs on PRs** — golangci-lint with 35+ linters, pre-commit hooks, and clang-format are configured but never exercised
  - **Examples are never verified** — `hack/verify-examples.sh` is dead code in CI
  - **Python integration tests are never run** — `uds-tokenizer-service-test` exists but is never triggered
- **Effort**: 30 minutes — change `main_2` to `main` in three files

### 2. No Test Coverage Tracking
- **Severity**: HIGH
- **Impact**: The `go test -v ./pkg/...` command runs without `-coverprofile` or `-covermode` flags. No codecov, coveralls, or any coverage reporting exists. Coverage regressions are invisible.
- **Effort**: 4-6 hours (flags + codecov integration + threshold setup)

### 3. No PR-Time Container Image Scanning
- **Severity**: HIGH
- **Impact**: Trivy scanning exists but only runs in `ci-release.yaml` (on tag push). Vulnerabilities in base images or dependencies are only caught at release time, not during development.
- **Effort**: 2-3 hours

### 4. No PR-Time Konflux Build Validation
- **Severity**: MEDIUM
- **Impact**: `Dockerfile.konflux` (in services/uds_tokenizer) uses a different base image (`quay.io/aipcc/base-images/cpu:3.4`) and different build process than the dev Dockerfile. It is never built in GitHub CI — only via Tekton when triggered by labels/comments. Build issues in the Konflux path are discovered post-merge.
- **Effort**: 8-12 hours

### 5. kv_connectors Tests Not Wired Into CI
- **Severity**: MEDIUM
- **Impact**: `kv_connectors/llmd_fs_backend/tests/` contains unit tests (`test_fs_backend.py`, `test_priority_queue.py`, `test_obj_backend.py`) and performance tests (`test_stress.py`, `test_throughput.py`) — none of which are triggered by any CI workflow.
- **Effort**: 3-4 hours

### 6. No Agent Rules
- **Severity**: MEDIUM
- **Impact**: No `CLAUDE.md`, `.claude/` directory, or `AGENTS.md` exists. AI-assisted development has no guardrails for test quality, naming conventions, or required coverage levels. Only a minimal Copilot setup workflow exists.
- **Effort**: 4-6 hours

## Quick Wins

### 1. Fix Disabled Workflows (30 minutes, HIGH impact)
Change branch target from `main_2` to `main` in:
- `.github/workflows/ci-lint.yaml` (line 7)
- `.github/workflows/ci-examples.yaml` (line 7)
- `.github/workflows/ci-uds-tokenizer.yaml` (line 7)

This immediately enables linting, examples verification, and Python integration tests on every PR.

### 2. Add Coverage Generation (1-2 hours, HIGH impact)
Update the `unit-test-uds` Makefile target:
```makefile
unit-test-uds: check-go download-zmq
	@go test -v -coverprofile=coverage.out -covermode=atomic ./pkg/...
```

### 3. Add Trivy to PR Workflow (1-2 hours, MEDIUM impact)
Add a step to `ci-test.yaml` that builds and scans the image:
```yaml
- name: Run Trivy scan on E2E image
  uses: aquasecurity/trivy-action@v0.35.0
  with:
    image-ref: llm-d-uds-tokenizer:e2e-test
    format: table
    severity: HIGH,CRITICAL
    exit-code: 1
```

### 4. Create CLAUDE.md (2-3 hours, MEDIUM impact)
Establish basic test quality expectations for AI-assisted contributions, covering Go unit test patterns (testify, table-driven tests, t.Parallel), Python test patterns (pytest, fixtures), and E2E test expectations (Testcontainers).

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (26 workflows):

| Workflow | Trigger | Status |
|----------|---------|--------|
| `ci-test.yaml` | PR to main | ACTIVE — runs unit-test + e2e-test |
| `ci-lint.yaml` | PR to main_2 | DISABLED — linting never runs |
| `ci-examples.yaml` | PR to main_2 | DISABLED — examples never verified |
| `ci-uds-tokenizer.yaml` | PR to main_2 (path-filtered) | DISABLED — Python tests never run |
| `ci-nightly-race.yaml` | Cron daily 06:00 UTC | ACTIVE — race detector nightly |
| `ci-release.yaml` | Tag push / release | ACTIVE — build, push, Trivy |
| `ci-wheels.yaml` | Tag push | ACTIVE — CUDA wheel builds |
| `ci-signed-commits.yaml` | PR target | ACTIVE — commit signing check |
| `ci-dev-uds-tokenizer.yaml` | — | Dev tokenizer builds |
| `ci-release-uds-tokenizer.yaml` | — | Release tokenizer builds |
| `ci-pages-index.yaml` | — | Pages index |
| `prow-github.yml` | Issue comment | ACTIVE — Prow command support |
| `non-main-gatekeeper.yml` | PR | ACTIVE — reusable gatekeeper |
| Various utility | Various | Auto-assign, stale, size-label, link-checker, typo-checker, upstream-monitor |

**Strengths**:
- Unit and E2E tests run on every PR to main
- Nightly race detector catches data races
- Good caching (apt, Go modules, Docker layers via GHA cache)
- Mergify auto-comments pre-commit failures
- Prow commands for label-based workflows

**Weaknesses**:
- 3/4 test-related workflows are disabled (target `main_2`)
- No concurrency control on PR workflows (`ci-test.yaml` lacks concurrency group)
- No test result reporting (JUnit XML, test summary)

### Test Coverage

**Go Unit Tests** (24 test files, ~7,800 LOC):
- Strong coverage of `pkg/kvcache/kvblock/` (index, memory, valkey, redis, token processor)
- `pkg/kvevents/` well-tested (pool, subscriber manager, ZMQ subscriber, engine adapters)
- `pkg/tokenization/` tested (pool, UDS tokenizer client)
- Benchmark tests for vLLM adapter and ZMQ subscriber
- Uses testify/suite, testify/assert, testify/require, testify/mock

**E2E Tests** (3 test files, 666+ LOC):
- Testcontainers-based E2E for UDS tokenizer
- Tests multimodal input handling
- Suite-based test organization with proper setup/teardown
- Builds and runs tokenizer container image during test

**Integration Tests** (1 file, 142 LOC):
- Tests Pool + SubscriberManager component interaction
- Validates multi-pod event processing

**Python Tests**:
- `services/uds_tokenizer/tests/` — 2 test files (integration, renderer)
- `kv_connectors/llmd_fs_backend/tests/` — 4 unit tests + 2 performance tests
- Neither set runs in CI

**Test-to-Code Ratio**: ~1.5:1 (7,800 test LOC / 5,200 source LOC) — good ratio

**Profiling**: Benchmark test infrastructure exists at `tests/profiling/`

### Code Quality

**Linting** (golangci-lint v2):
- **35+ linters enabled** including: gosec, govet, errcheck, staticcheck, bodyclose, contextcheck, errorlint, revive, nestif, varnamelen, and many more
- Formatter configuration with gofumpt and goimports
- Strict error handling checks (errcheck, nilerr, nilnil, noctx)
- Concurrency checks (tparallel)
- BUT: **never runs on PRs** due to `main_2` branch target

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- ruff-check + ruff-format for Python
- typos for spell-checking
- clang-format for C++/CUDA
- actionlint for GitHub Actions validation
- uv pip-compile for requirements locking
- Supports both local (pre-commit) and CI (manual) stages

**License Checking**: Apache 2.0 headers enforced via SkyWalking Eyes

**Dependency Management**:
- Dependabot for Go modules, GitHub Actions, Docker images (weekly)
- Renovate extending Konflux central config
- Dual dependency management is redundant but ensures coverage

### Container Images

**Dockerfiles**:
1. **Root `Dockerfile`** — Go application (multi-stage: golang builder → UBI9 runtime)
2. **`services/uds_tokenizer/Dockerfile`** — Python gRPC server
3. **`services/uds_tokenizer/Dockerfile.konflux`** — Production Konflux build with **smoke test stage** (validates imports)
4. **`kv_connectors/llmd_fs_backend/Dockerfile.dev`** — Development container
5. **`kv_connectors/llmd_fs_backend/Dockerfile.wheel`** — CUDA wheel builder

**Strengths**:
- Multi-stage builds for minimal runtime images
- Non-root user (65532) in all runtime images
- `.dockerignore` configured
- Smoke test stage in Konflux Dockerfile validates critical imports
- Multi-architecture support (amd64, arm64) in release and Tekton pipelines

**Weaknesses**:
- No health check in main Dockerfile
- No Trivy scanning on PR-built images
- Root Dockerfile uses UBI9 latest (unpinned)
- No SBOM generation

### Security

**Present**:
- Trivy vulnerability scanning (HIGH, CRITICAL) — release-only
- Signed commit verification
- Non-root containers
- gosec lint rule enabled (but workflow disabled)
- Dependabot + Renovate for dependency updates

**Missing**:
- No SAST/CodeQL integration
- No secret detection (Gitleaks, TruffleHog)
- No PR-time vulnerability scanning
- No dependency license scanning in CI
- No image signing/attestation

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no test type rules exist
- **Quality**: N/A
- **Details**:
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory (no rules, no skills)
  - A `copilot-setup-steps.yml` exists but only installs `gh-aw` — no test guidance
  - No testing standards documentation in `docs/`
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering:
  - Go unit test patterns (testify, table-driven, t.Parallel)
  - Python pytest patterns (fixtures, conftest.py)
  - E2E patterns (Testcontainers, suite setup/teardown)
  - gRPC test patterns (proto-based testing)
  - C++/CUDA code testing expectations

## Recommendations

### Priority 0 (Critical)
1. **Fix disabled CI workflows** — Change `main_2` → `main` in `ci-lint.yaml`, `ci-examples.yaml`, `ci-uds-tokenizer.yaml` (30 min)
2. **Add coverage generation** — Add `-coverprofile` and `-covermode=atomic` to Go test commands (1 hour)
3. **Integrate codecov** — Upload coverage artifacts, set thresholds, enable PR status checks (3-4 hours)

### Priority 1 (High Value)
4. **Move Trivy scanning to PR workflow** — Add to `ci-test.yaml` (2 hours)
5. **Wire kv_connectors Python tests into CI** — New workflow or extend existing one (3 hours)
6. **Add Konflux Dockerfile build to PR CI** — `docker build --target test` validates smoke stage (4 hours)
7. **Add concurrency control to CI workflows** — Prevent duplicate runs (1 hour)
8. **Create agent rules** — `.claude/rules/` with Go, Python, E2E, and gRPC testing standards (4-6 hours)

### Priority 2 (Nice-to-Have)
9. **Add Kind-based integration test to periodic CI** — Script already exists at `tests/kind-vllm-cpu.sh` (4-6 hours)
10. **Add SBOM generation** — Integrate Syft or similar in release pipeline (2 hours)
11. **Add CodeQL/SAST scanning** — GitHub-native security analysis (2-3 hours)
12. **Add secret detection** — Gitleaks in pre-commit + CI (1-2 hours)
13. **Add mutation testing** — go-mutesting for unit test quality validation (4-6 hours)
14. **Pin base image tags** — Replace `ubi9:latest` with specific version in root Dockerfile (30 min)
15. **Add contract tests** — Validate Go gRPC client ↔ Python tokenizer service contract (8-12 hours)
16. **Add JUnit XML test reporting** — Enable test result summaries in GitHub Actions (2 hours)

## Comparison to Gold Standards

| Dimension | llm-d-kv-cache | odh-dashboard | notebooks | kserve |
|-----------|----------------|---------------|-----------|--------|
| Unit Tests | 7.0 — Good ratio, testify | 9.0 — Jest+RTL, high coverage | 7.0 — Varied | 9.0 — envtest, comprehensive |
| Integration/E2E | 7.5 — Testcontainers E2E | 9.0 — Cypress, contract tests | 8.0 — Image validation | 9.0 — Multi-version |
| Build Integration | 4.0 — Konflux untested in CI | 8.0 — PR build validation | 7.0 — Image pipeline | 8.0 — Prow integration |
| Image Testing | 5.0 — Smoke test in Konflux only | 8.0 — Multi-layer validation | 9.0 — 5-layer testing | 7.0 — Image tests |
| Coverage | 2.0 — None | 9.0 — Codecov enforced | 6.0 — Basic | 9.0 — Enforcement |
| CI/CD | 6.0 — 3 workflows disabled | 9.0 — Comprehensive | 8.0 — Well-organized | 9.0 — Prow + Actions |
| Agent Rules | 1.0 — None | 8.0 — Comprehensive rules | 3.0 — Basic | 4.0 — Minimal |

## File Paths Reference

### CI/CD
- `.github/workflows/ci-test.yaml` — PR unit + E2E tests (ACTIVE)
- `.github/workflows/ci-lint.yaml` — Linting (DISABLED — targets main_2)
- `.github/workflows/ci-examples.yaml` — Examples verification (DISABLED — targets main_2)
- `.github/workflows/ci-uds-tokenizer.yaml` — Python integration tests (DISABLED — targets main_2)
- `.github/workflows/ci-nightly-race.yaml` — Nightly race detector (ACTIVE)
- `.github/workflows/ci-release.yaml` — Release build + Trivy (ACTIVE)
- `.tekton/odh-llm-d-kv-cache-pull-request.yaml` — Konflux PR pipeline

### Testing
- `pkg/kvcache/*_test.go` — Core KV cache unit tests (14 files)
- `pkg/kvevents/*_test.go` — Event system unit tests (6 files)
- `pkg/tokenization/*_test.go` — Tokenization unit tests (2 files)
- `pkg/utils/slices_test.go` — Utility tests
- `tests/e2e/uds_tokenizer/` — Testcontainers-based E2E (3 files)
- `tests/integration/kv_events_test.go` — Component integration
- `tests/profiling/` — Benchmark infrastructure
- `services/uds_tokenizer/tests/` — Python integration tests (NOT IN CI)
- `kv_connectors/llmd_fs_backend/tests/` — Python unit + perf tests (NOT IN CI)

### Code Quality
- `.golangci.yml` — 35+ linters enabled
- `.pre-commit-config.yaml` — ruff, typos, clang-format, actionlint
- `.licenserc.yaml` — Apache 2.0 header enforcement
- `.clang-format` — C++/CUDA formatting
- `_typos.toml` — Spell-check configuration

### Container Images
- `Dockerfile` — Main Go application
- `services/uds_tokenizer/Dockerfile` — Dev tokenizer image
- `services/uds_tokenizer/Dockerfile.konflux` — Production tokenizer (with smoke test)
- `kv_connectors/llmd_fs_backend/Dockerfile.dev` — FS backend dev image
- `kv_connectors/llmd_fs_backend/Dockerfile.wheel` — CUDA wheel builder

### Security
- `.github/actions/trivy-scan/action.yml` — Trivy composite action
- `.github/workflows/ci-signed-commits.yaml` — Commit signing
- `.github/dependabot.yml` — Dependency updates
- `.github/renovate.json` — Konflux dependency updates
