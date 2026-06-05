---
repository: "opendatahub-io/batch-gateway"
overall_score: 7.2
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test-to-code ratio (1.87:1 LOC), table-driven tests with subtests, 48 unit test files covering all major packages"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Comprehensive E2E suite with 12 test files, matrix-driven CI across 6 storage backend combinations, Kind cluster deployment"
  - dimension: "Build Integration"
    score: 6.5
    status: "Konflux Tekton pipelines for PR and push, but no PR-time unit/lint gates — only image build validation"
  - dimension: "Image Testing"
    score: 5.5
    status: "Multi-stage Dockerfiles for 3 binaries, distroless runtime, but no container runtime validation or startup testing"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "Makefile targets for local coverage, but no CI coverage enforcement, no codecov/coveralls integration"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Well-organized workflows with concurrency control, Docker Bake multi-arch builds, automated releases, Dependabot"
  - dimension: "Agent Rules"
    score: 5.0
    status: "CLAUDE.md with code conventions and test style guidance, but no .claude/rules/ for per-test-type instructions"
critical_gaps:
  - title: "No CI coverage enforcement or tracking"
    impact: "Coverage regressions go undetected; no visibility into overall test health"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container vulnerability scanning in CI"
    impact: "Security vulnerabilities in dependencies and base images not caught until downstream"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-triggered unit test or lint workflow"
    impact: "Unit test failures and lint violations are only caught by pre-commit hooks, not enforced in CI on PRs"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "22 source packages with no unit tests"
    impact: "Shared utilities, converters, and batch_utils are untested — these are used by all three binaries"
    severity: "MEDIUM"
    effort: "12-16 hours"
  - title: "No container runtime validation"
    impact: "Image startup issues, missing dependencies, or entrypoint errors not caught until deployment"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add codecov integration to CI"
    effort: "2-4 hours"
    impact: "Gain visibility into coverage trends and enforce minimum thresholds on PRs"
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in Go dependencies and container base images before merge"
  - title: "Add PR-triggered unit test workflow"
    effort: "1-2 hours"
    impact: "Enforce test pass on every PR, catch regressions before merge"
  - title: "Create .claude/rules/ for test patterns"
    effort: "2-3 hours"
    impact: "Enable AI agents to generate tests following project conventions consistently"
recommendations:
  priority_0:
    - "Add a PR-triggered CI workflow that runs `make test` and `make lint` — currently only pre-commit hooks enforce this"
    - "Integrate codecov or coveralls with coverage thresholds (e.g., 70% minimum, no decrease on PRs)"
    - "Add Trivy or Grype container scanning to the ci-release workflow and Tekton pipelines"
  priority_1:
    - "Add unit tests for untested shared packages: batch_utils, converter, config, store, types"
    - "Add container startup validation in CI — build image, run it, verify health endpoint responds"
    - "Create .claude/rules/ directory with test-type-specific guidance (unit-tests.md, integration-tests.md, e2e-tests.md)"
    - "Add CodeQL or Semgrep SAST workflow for Go security analysis"
  priority_2:
    - "Add performance/benchmark regression testing in CI using existing `make bench` target"
    - "Add Helm chart validation to PR workflow (currently only in pre-commit)"
    - "Consider adding contract tests for the OpenAI-compatible API boundary"
    - "Add SBOM generation to container image builds"
---

# Quality Analysis: batch-gateway

## Executive Summary

- **Overall Score: 7.2/10**
- **Repository Type**: Go microservice (3 binaries: apiserver, batch-processor, batch-gc)
- **Primary Language**: Go 1.25+
- **Architecture**: OpenAI-compatible batch API gateway for llm-d, deployed via Helm to Kubernetes

### Key Strengths
- **Outstanding test-to-code ratio**: 32,240 test LOC vs 17,254 source LOC (1.87:1) with 60 test files
- **Comprehensive E2E infrastructure**: Kind cluster deployment with vLLM simulator, testing across 6 backend combinations (S3/fs, PostgreSQL/Redis/Valkey)
- **Well-structured CI/CD**: Docker Bake multi-arch builds, Tekton/Konflux pipelines, automated releases with binary packaging
- **Strong code quality gates**: golangci-lint v2 with 7 linters, custom depguard/forbidigo rules, gosec in pre-commit, Helm chart unit tests

### Critical Gaps
- No CI-enforced test coverage tracking or codecov integration
- No container vulnerability scanning (Trivy, Snyk, Grype) in any CI pipeline
- No PR-triggered unit test workflow — test enforcement relies solely on pre-commit hooks
- 22 source packages with no unit tests (interfaces, mocks, shared utilities)

### Agent Rules Status
- **Present**: CLAUDE.md with code conventions and test style guidance
- **Missing**: No `.claude/rules/` directory, no per-test-type agent rules

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent coverage with table-driven tests and subtests |
| Integration/E2E | 8.0/10 | Comprehensive matrix E2E across 6 storage backend combos |
| **Build Integration** | **6.5/10** | **Konflux pipelines present but no PR-time unit/lint gates** |
| Image Testing | 5.5/10 | Multi-stage distroless builds, no runtime validation |
| Coverage Tracking | 3.0/10 | Local targets only, no CI enforcement |
| CI/CD Automation | 8.0/10 | Well-organized with concurrency control and caching |
| Agent Rules | 5.0/10 | CLAUDE.md present, no structured .claude/rules/ |

## Critical Gaps

### 1. No CI Coverage Enforcement
- **Impact**: Coverage regressions silently merge; no PR-level feedback on test adequacy
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Makefile has `test-coverage` and `test-coverage-func` targets but they are local-only. No `.codecov.yml`, no coverage upload in any workflow. Teams have no visibility into coverage trends.

### 2. No Container Vulnerability Scanning
- **Impact**: CVEs in Go dependencies and UBI9 base images reach production undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No Trivy, Snyk, Grype, or any scanner in GitHub Actions or Tekton pipelines. The Konflux Dockerfiles use pinned UBI9 digests (good), but no scanning validates them. No `.trivyignore` file exists.

### 3. No PR-Triggered Unit Test Workflow
- **Impact**: A developer who skips pre-commit hooks can merge code that fails `make test`
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: The `pre-commit.yml` workflow runs pre-commit hooks on PRs which includes `go-unit-tests`, but this is an optional hook that can be skipped. There is no dedicated `ci-unit-tests.yml` workflow. The integration test workflow only runs on `push` to `main` and on schedule, not on PRs.

### 4. Untested Source Packages (22 packages)
- **Impact**: Shared utilities used by all three binaries have zero test coverage
- **Severity**: MEDIUM
- **Effort**: 12-16 hours
- **Notable untested packages**:
  - `internal/shared/batch_utils` (3 source files) — batch processing utilities
  - `internal/shared/converter` (2 source files) — data conversion logic
  - `internal/database/api` (4 source files) — database interface definitions
  - `internal/files_store/tracing` (1 file) — tracing wrapper
  - `internal/util/tls`, `internal/util/otel`, `internal/util/logging` — infrastructure utilities

### 5. No Container Runtime Validation
- **Impact**: Image startup failures, missing runtime dependencies, or broken entrypoints discovered only during deployment
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: CI builds images but never runs them to verify basic health. The E2E tests deploy to Kind but that only runs on push/schedule, not PRs.

## Quick Wins

### 1. Add codecov Integration (2-4 hours)
Add coverage generation and upload to CI:
```yaml
# In a new ci-tests.yml or existing workflow
- name: Run tests with coverage
  run: go test -race -coverprofile=coverage.out ./...
- name: Upload coverage
  uses: codecov/codecov-action@v5
  with:
    files: coverage.out
```
Create `.codecov.yml`:
```yaml
coverage:
  status:
    project:
      default:
        target: 70%
    patch:
      default:
        target: 80%
```

### 2. Add Trivy Scanning (1-2 hours)
Add to ci-release workflow after image build:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/llm-d-incubation/batch-gateway-apiserver:${{ steps.meta.outputs.commit_sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 3. Add PR-Triggered Unit Test Workflow (1-2 hours)
Create `.github/workflows/ci-unit-tests.yml`:
```yaml
name: Unit Tests
on:
  pull_request:
  push:
    branches: [main, 'release-*']
concurrency:
  group: unit-tests-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod
      - run: make test
```

### 4. Create .claude/rules/ (2-3 hours)
Generate test-type-specific rules using the `/test-rules-generator` skill for consistent AI-generated tests.

## Detailed Findings

### CI/CD Pipeline

**Workflows (14 total):**
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pre-commit.yml` | PR + push | golangci-lint, pre-commit hooks, Helm lint |
| `ci-integration-tests.yml` | push + schedule (daily) | E2E tests across 6 backend combinations |
| `ci-release.yaml` | push to main + tags | Docker Bake multi-arch image build & push |
| `ci-dco-signoff.yml` | PR | DCO sign-off enforcement |
| `ci-signed-commits.yml` | PR | Signed commit verification |
| `create-release.yml` | workflow_dispatch | Binary release with checksums + Helm chart publishing |
| `auto-label-pr.yml` | PR | Auto-labeling |
| `prow-github.yml` | various | Prow bot integration |
| `prow-pr-automerge.yml` | PR review | Auto-merge with LGTM |
| `prow-pr-remove-lgtm.yml` | PR push | Remove LGTM on new commits |
| `stale.yml` / `unstale.yml` | schedule | Stale issue management |
| `non-main-gatekeeper.yml` | push | Branch protection |
| `copilot-setup-steps.yml` | dispatch | GitHub Copilot workspace setup |

**Tekton/Konflux Pipelines (6 total):**
- PR and push pipelines for all 3 components (apiserver, processor, gc)
- Uses centralized `odh-konflux-central` pipeline definition
- Builds using UBI9 base images with FIPS-compatible Go builds (`GOEXPERIMENT=strictfipsruntime`)

**Strengths:**
- Concurrency control on all workflows (`cancel-in-progress: true`)
- Docker Bake with registry-level build caching
- Multi-arch builds (amd64 + arm64) for upstream images
- Dependabot configured for Go modules, GitHub Actions, and Docker base images
- Automated issue creation on integration test failures

**Gaps:**
- No PR-triggered unit test or lint-only workflow
- Integration tests don't run on PRs (only push + schedule)
- No artifact caching for Go modules in integration test workflow (setup-go handles it but it's implicit)

### Test Coverage

**Unit Tests (48 files, ~20,240 LOC):**
- Framework: Go standard `testing` package
- Style: Table-driven tests with `t.Run()` subtests (per CLAUDE.md conventions)
- Coverage across all major domains:
  - `internal/apiserver/` — 7 test files (handlers, middleware, health, config)
  - `internal/processor/worker/` — 12 test files (comprehensive worker pipeline testing)
  - `internal/database/` — 5 test files (PostgreSQL, Redis data stores)
  - `internal/files_store/` — 5 test files (S3, filesystem, retry, IO)
  - `internal/gc/` — 3 test files (collector, reconciler, config)
  - `internal/util/` — 6 test files (semaphore, retry, redis, common)
  - `pkg/clients/` — 4 test files (HTTP client, inference client)

**Integration Tests (2 files):**
- `internal/files_store/s3/client_integration_test.go` — S3 client integration using Docker Compose
- `pkg/clients/inference/inference_client_integration_test.go` — Inference client with llm-d mock server
- Build-tagged with `integration` for separate execution

**E2E Tests (12 files, ~12,000 LOC):**
- Separate Go module in `test/e2e/` with own `go.mod`
- Tests against live Kind cluster with all dependencies (Redis/Valkey, PostgreSQL, MinIO, vLLM simulator)
- Coverage areas: batches, files, concurrent access, flow control, GC, Helm upgrades, multitenancy, observability, AIMD, processor graceful shutdown
- CI runs 6 matrix combinations testing different storage backends

**Helm Chart Tests (6 files):**
- `helm-unittest` plugin tests for deployments, configmaps, HTTPRoute, observability
- Comprehensive assertion coverage: replicas, security contexts, OTel env vars, TLS validation, image digests

### Code Quality

**Linting (Strong):**
- golangci-lint v2 with 7 linters: depguard, errcheck, forbidigo, gocritic, govet, staticcheck, unused
- Custom rules: depguard bans stdlib `log` in non-test code, forbidigo bans klog logging functions
- Custom ruleguard rules via `tools/rules.go`
- gosec (security scanner) in pre-commit hooks

**Pre-commit (Comprehensive):**
- 12 hooks across 3 repos:
  - Standard: trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-merge-conflict, check-case-conflict
  - Go: go-fmt, go-unit-tests, go-build, go-mod-tidy, go-vet, goimports, golangci-lint, gosec
  - Helm: helm-unittest
- Some hooks marked as optional (golangci-lint, gosec) — will skip if tool not installed locally

**Static Analysis:**
- gosec in pre-commit (optional) — not enforced in CI workflow
- No CodeQL or Semgrep SAST workflows
- No dedicated security scanning workflow

### Container Images

**Dockerfiles (6 total — 3 upstream + 3 Konflux):**

| Dockerfile | Base (build) | Base (runtime) | Purpose |
|-----------|--------------|----------------|---------|
| `Dockerfile.apiserver` | `quay.io/projectquay/golang:1.26` | `gcr.io/distroless/static:nonroot` | Upstream apiserver |
| `Dockerfile.processor` | `quay.io/projectquay/golang:1.26` | `gcr.io/distroless/static:nonroot` | Upstream processor |
| `Dockerfile.gc` | `quay.io/projectquay/golang:1.26` | `gcr.io/distroless/static:nonroot` | Upstream GC |
| `Dockerfile.apiserver.konflux` | `ubi9/go-toolset:1.25.8@sha256:...` | `ubi9/ubi-minimal:9.7@sha256:...` | Konflux/RHOAI apiserver |
| `Dockerfile.processor.konflux` | `ubi9/go-toolset:1.25.8@sha256:...` | `ubi9/ubi-minimal:9.7@sha256:...` | Konflux/RHOAI processor |
| `Dockerfile.gc.konflux` | `ubi9/go-toolset:1.25.8@sha256:...` | `ubi9/ubi-minimal:9.7@sha256:...` | Konflux/RHOAI GC |

**Strengths:**
- Multi-stage builds with dependency caching (`go mod download` as separate layer)
- Distroless/UBI-minimal runtime images (minimal attack surface)
- Non-root user execution (`USER 65532:65532` / `USER 1001:1001`)
- Konflux images use pinned digests for reproducibility
- FIPS-compatible builds via `GOEXPERIMENT=strictfipsruntime`
- OCI labels via Docker Bake
- `.dockerignore` excludes tests, docs, and build artifacts

**Gaps:**
- No vulnerability scanning on built images
- No SBOM generation
- No image signing/attestation (cosign)
- No runtime startup validation in CI
- Upstream Dockerfiles use unpinned tags (`golang:1.26`)

### Security

**Present:**
- DCO sign-off enforcement on PRs
- Signed commit verification
- gosec security scanner (pre-commit, optional)
- Non-root container execution
- Dependabot for dependency updates (Go, Actions, Docker)
- depguard restricting unsafe logging packages

**Missing:**
- No container vulnerability scanning (Trivy, Snyk, Grype)
- No CodeQL or SAST workflow
- No Gitleaks or secret detection
- No SBOM generation
- No image signing with cosign/sigstore
- No security scanning in Tekton pipelines

### Agent Rules (Agentic Flow Quality)

**Status**: Partial — CLAUDE.md present, no structured rules directory

**Present (CLAUDE.md):**
- Code conventions (logging, errors, interfaces, goroutines)
- Test style guidance: "Table-driven with subtests. Group tests for the same function under one TestXxx using t.Run()"
- Build & verify commands: `make build`, `make tidy`, `make pre-commit`
- Local testing commands: `make test`, `make test-integration`, `make dev-deploy`, `make test-e2e`

**Missing:**
- No `.claude/` directory
- No `.claude/rules/` with per-test-type rules (unit-tests.md, integration-tests.md, e2e-tests.md)
- No test fixture patterns or mock strategies documented for agents
- No guidance on which packages need tests vs. which are intentionally untested (interfaces, mocks)
- No Helm chart test patterns for agents

**Recommendation**: Use `/test-rules-generator` to create structured agent rules covering all test types.

## Recommendations

### Priority 0 (Critical)

1. **Add PR-triggered unit test and lint workflow** — Currently no CI enforcement of tests on PRs. Create `ci-unit-tests.yml` that runs `make test` and `make lint` on every PR.

2. **Integrate coverage tracking with enforcement** — Add codecov/coveralls to CI with minimum thresholds (70% project, 80% patch). Upload coverage reports from unit test runs.

3. **Add container vulnerability scanning** — Integrate Trivy into the ci-release workflow and Tekton pipelines. Set severity thresholds (CRITICAL/HIGH) and fail builds on violations.

### Priority 1 (High Value)

4. **Add unit tests for shared packages** — Focus on `internal/shared/batch_utils`, `internal/shared/converter`, `internal/database/api` — these are used by all three binaries and have zero test coverage.

5. **Add container runtime validation** — After image build in CI, run a quick startup test: build, run, curl health endpoint, verify exit code 0.

6. **Create .claude/rules/ directory** — Add structured agent rules for unit tests (table-driven, subtests, mocking patterns), integration tests (build tags, docker-compose), and E2E tests (Kind setup, test helpers).

7. **Add CodeQL SAST workflow** — Replace optional pre-commit gosec with a mandatory CI workflow for Go security analysis.

### Priority 2 (Nice-to-Have)

8. **Add benchmark regression testing** — The `make bench` target exists but isn't used in CI. Add periodic benchmark runs with threshold-based alerting.

9. **Run integration tests on PRs** — Currently integration tests only run on push to main and daily schedule. Consider running a subset (e.g., the default PostgreSQL+S3+Redis combo) on PRs that touch core packages.

10. **Add contract tests for OpenAI API boundary** — The apiserver implements OpenAI batch/files APIs. Contract tests would ensure compatibility as the API evolves.

11. **Add SBOM generation and image signing** — Integrate Syft for SBOM generation and cosign for image signing in the release pipeline.

12. **Add Gitleaks for secret detection** — Prevent accidental credential commits with a pre-commit hook and CI workflow.

## Comparison to Gold Standards

| Dimension | batch-gateway | odh-dashboard | notebooks | kserve |
|-----------|:---:|:---:|:---:|:---:|
| Unit test framework | Go testing (table-driven) | Jest + RTL | Pytest | Go testing |
| Test-to-code ratio | 1.87:1 | ~1:1 | ~0.5:1 | ~0.8:1 |
| E2E infrastructure | Kind + vLLM sim | Cypress + mock API | Image pipeline | Kind + envtest |
| Backend matrix testing | 6 combinations | N/A | Multi-image | Multi-version |
| Coverage enforcement | None | Codecov | None | Codecov (80%) |
| Container scanning | None | Trivy | None | Trivy |
| SAST | gosec (optional) | CodeQL | None | CodeQL |
| Pre-commit hooks | 12 hooks | ESLint + Prettier | None | golangci-lint |
| Helm chart tests | helm-unittest (6 files) | N/A | N/A | helm-unittest |
| Agent rules | CLAUDE.md only | CLAUDE.md + rules/ | None | None |
| Dependabot | Go + Actions + Docker | Actions | None | Go + Actions |
| Multi-arch builds | amd64 + arm64 | amd64 | Multi-arch | amd64 |

## File Paths Reference

### CI/CD
- `.github/workflows/pre-commit.yml` — Linting and pre-commit hooks (PR + push)
- `.github/workflows/ci-integration-tests.yml` — E2E tests with matrix (push + schedule)
- `.github/workflows/ci-release.yaml` — Docker Bake multi-arch image builds (push + tags)
- `.github/workflows/ci-dco-signoff.yml` — DCO sign-off check (PR)
- `.github/workflows/ci-signed-commits.yml` — Signed commit check (PR)
- `.github/workflows/create-release.yml` — Release automation (dispatch)
- `.tekton/odh-llm-d-batch-gateway-*` — Konflux Tekton pipelines (6 files)

### Testing
- `internal/*/` — 48 unit test files across all packages
- `test/e2e/` — 12 E2E test files with separate go.mod
- `charts/batch-gateway/tests/` — 6 Helm chart unit test files
- `pkg/clients/inference/docker-compose.test.yml` — Mock server for integration tests

### Code Quality
- `.golangci.yml` — 7 linters with custom depguard/forbidigo/ruleguard rules
- `.pre-commit-config.yaml` — 12 hooks (Go, YAML, Helm)
- `tools/rules.go` — Custom gocritic ruleguard rules
- `_typos.toml` — Typo detection configuration

### Container Images
- `docker/Dockerfile.{apiserver,processor,gc}` — Upstream multi-stage Dockerfiles
- `docker/Dockerfile.{apiserver,processor,gc}.konflux` — Konflux/RHOAI Dockerfiles (UBI9, FIPS)
- `docker-bake.hcl` — Docker Buildx Bake configuration (multi-arch, caching, labels)
- `.dockerignore` — Comprehensive exclusion list

### Agent Rules
- `CLAUDE.md` — Code conventions, test style, build commands
