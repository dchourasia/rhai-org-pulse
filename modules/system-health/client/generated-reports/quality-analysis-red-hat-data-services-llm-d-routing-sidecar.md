---
repository: "red-hat-data-services/llm-d-routing-sidecar"
overall_score: 3.9
scorecard:
  - dimension: "Unit Tests"
    score: 5.0
    status: "Ginkgo/Gomega framework with tests for proxy forwarding, NIXL v1/v2 connectors, and SSRF allowlist. LMCache connector, TLS, errors, and signals have no tests."
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Kind-based E2E infrastructure exists but tests only verify pod status. Not automated in CI."
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time Docker build in GitHub CI. Tekton PR build is comment-triggered only (/build-konflux)."
  - dimension: "Image Testing"
    score: 2.0
    status: "Trivy scan on release only. No runtime validation, no image startup testing, no Testcontainers."
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage generation, no codecov/coveralls integration, no thresholds, no PR reporting."
  - dimension: "CI/CD Automation"
    score: 6.0
    status: "PR workflow runs lint + unit tests with Go caching. Strong Tekton push pipeline with 8 security scans. No concurrency control on PR workflow."
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no AGENTS.md, no .claude/ directory. Zero AI agent test guidance."
critical_gaps:
  - title: "No test coverage tracking"
    impact: "Cannot measure or enforce code coverage. Regressions can be introduced without visibility."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "LMCache connector has zero test coverage"
    impact: "Entire P/D protocol path (connector_lmcache.go, 88 lines) is untested. Bugs ship silently."
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "E2E tests only verify pod status"
    impact: "No functional validation of the sidecar proxy behavior in a real cluster. Critical integration bugs (routing, TLS, SSRF) not caught."
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No PR-time Docker image build validation"
    impact: "Dockerfile/Dockerfile.konflux divergence (CGO_ENABLED=0 vs 1, different base images) not caught until post-merge Konflux build."
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Trivy/security scanning absent from PR workflow"
    impact: "Vulnerabilities discovered only after merge in Tekton push pipeline. No shift-left security."
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI agents generating code or tests have no project-specific guidance. Inconsistent patterns, missed testing requirements."
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add coverage generation to make test"
    effort: "1-2 hours"
    impact: "Generate coverage profiles enabling codecov integration and visibility into test gaps."
  - title: "Add codecov integration to PR workflow"
    effort: "2-3 hours"
    impact: "Automated coverage reporting on every PR. Catch coverage regressions before merge."
  - title: "Add Docker build step to PR workflow"
    effort: "1-2 hours"
    impact: "Validate both Dockerfile and Dockerfile.konflux build successfully on every PR."
  - title: "Move Trivy scan to PR workflow"
    effort: "1 hour"
    impact: "Shift-left security scanning. Catch vulnerabilities before merge."
  - title: "Add concurrency control to PR workflow"
    effort: "30 minutes"
    impact: "Cancel stale CI runs when new commits are pushed. Save CI resources."
  - title: "Write unit tests for LMCache connector"
    effort: "3-4 hours"
    impact: "Cover an entire untested P/D protocol path (88 lines). Follow existing NIXL test patterns."
recommendations:
  priority_0:
    - "Add coverage generation (ginkgo --cover) and codecov integration to enforce minimum coverage thresholds"
    - "Write unit tests for connector_lmcache.go following the existing NIXL v1/v2 test patterns"
    - "Add Docker image build validation to PR workflow (both Dockerfile and Dockerfile.konflux)"
    - "Move Trivy scanning from release-only to PR workflow for shift-left security"
  priority_1:
    - "Expand E2E tests beyond pod-status check to validate proxy routing, prefill/decode handoff, TLS, and SSRF protection"
    - "Add unit tests for tls.go (certificate generation), errors.go (error response formatting), and status_response_writer.go"
    - "Automate Tekton PR build (remove comment-trigger requirement) or add Konflux build simulation to GitHub CI"
    - "Create comprehensive agent rules (.claude/rules/) for test automation guidance"
  priority_2:
    - "Add secret detection scanning (gitleaks or trufflehog) to PR workflow"
    - "Add integration tests using Testcontainers for sidecar container runtime validation"
    - "Add performance/load testing for the reverse proxy under concurrent prefill/decode requests"
    - "Consider adding multi-architecture build validation in PR workflow"
---

# Quality Analysis: llm-d-routing-sidecar

## Executive Summary

- **Overall Score: 3.9/10**
- **Repository Type**: Go reverse-proxy sidecar for disaggregated LLM inference (prefill/decode)
- **Primary Language**: Go 1.24, Ginkgo v2 / Gomega testing framework
- **Key Strengths**: Solid linting configuration (18+ golangci-lint rules), pre-commit hooks, comprehensive Tekton push pipeline with 8 security scan stages, well-structured proxy code with SSRF protection
- **Critical Gaps**: No coverage tracking, LMCache connector untested, E2E tests are skeletal, no PR-time image build validation, security scanning only post-merge
- **Agent Rules Status**: Missing - no CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 5.0/10 | Ginkgo/Gomega tests for proxy, NIXL v1/v2, allowlist. LMCache, TLS, errors untested. |
| Integration/E2E | 3.0/10 | Kind infrastructure exists, but tests only check pod status. Not in CI. |
| **Build Integration** | **3.0/10** | **No PR-time Docker build. Tekton PR requires `/build-konflux` comment trigger.** |
| Image Testing | 2.0/10 | Trivy on release only. No runtime validation or startup testing. |
| Coverage Tracking | 1.0/10 | Zero coverage infrastructure. No generation, no reporting, no thresholds. |
| CI/CD Automation | 6.0/10 | PR runs lint + test with Go caching. Strong Tekton push pipeline. No concurrency control. |
| Agent Rules | 0.0/10 | No AI agent rules, no test automation guidance, no .claude/ directory. |

## Critical Gaps

### 1. No Test Coverage Tracking
- **Impact**: Cannot measure code coverage or catch regressions. Unknown how much of the codebase is exercised by tests.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The `make test` target runs `ginkgo -v ./internal/...` without `--cover` or `--coverprofile`. No codecov.yml, no .coveragerc, no coverage threshold enforcement. PRs merge with zero visibility into coverage impact.

### 2. LMCache Connector Has Zero Test Coverage
- **Impact**: The entire LMCache P/D protocol path (`connector_lmcache.go`, 88 lines) ships without any test validation. Bugs in this connector would reach production undetected.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: NIXL v1 and v2 connectors both have dedicated test files with thorough assertions. The LMCache connector follows a similar pattern (read body, modify, forward to prefiller, then decoder) but has zero test coverage. The existing mock infrastructure (`test/mock/chat_completions_handler.go`) supports this connector type and could be reused.

### 3. E2E Tests Only Verify Pod Status
- **Impact**: No functional E2E validation of the sidecar's core behavior (request routing, prefill/decode handoff, protocol negotiation, TLS, SSRF protection). Critical integration bugs not caught.
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: `test/e2e/e2e_test.go` contains a single test case that checks if a qwen pod reaches "Running" status. No HTTP requests are made to the sidecar, no proxy behavior is validated. The Kind cluster infrastructure (kustomize overlays, RBAC configs, gateway configs) is in place but underutilized.

### 4. No PR-Time Docker Image Build Validation
- **Impact**: The two Dockerfiles diverge significantly (CGO_ENABLED=0 vs CGO_ENABLED=1, ubi9/ubi-micro vs ubi9/ubi base images, `go build` vs `go build -mod=mod`). Build failures discovered only post-merge.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: `ci-pr-checks.yaml` runs lint and test only. `ci-release.yaml` builds the image only on tag/release. The Tekton PR pipeline (`odh-llm-d-routing-sidecar-pull-request.yaml`) requires a `/build-konflux` comment to trigger. This means a PR can merge with a broken Dockerfile.

### 5. Security Scanning Absent from PR Workflow
- **Impact**: Vulnerabilities in dependencies or base images are only discovered after merge, in the Tekton push pipeline. No shift-left security.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: The Trivy composite action exists at `.github/actions/trivy-scan/` but is only used in `ci-release.yaml`. The comprehensive security scanning (Clair, Snyk, Coverity, ClamAV, shell-check, unicode-check, RPM signature) runs only in the Tekton push pipeline.

### 6. No Agent Rules for AI-Assisted Development
- **Impact**: AI agents generating code or tests have no project-specific patterns, testing requirements, or quality gates to follow.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: No `CLAUDE.md`, `AGENTS.md`, or `.claude/` directory. AI agents would not know about the Ginkgo/Gomega test patterns, the mock infrastructure, the connector protocol patterns, or SSRF protection testing requirements.

## Quick Wins

### 1. Add Coverage Generation to `make test` (1-2 hours)
```makefile
test: ## Run tests with coverage
	@printf "\033[33;1m==== Running tests ====\033[0m\n"
	go install github.com/onsi/ginkgo/v2/ginkgo@latest
	ginkgo -v --cover --coverprofile=coverage.out ./internal/...
	go tool cover -func=coverage.out
```

### 2. Add Codecov to PR Workflow (2-3 hours)
```yaml
      - name: Run go test with coverage
        run: make test
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: coverage.out
          fail_ci_if_error: true
```

### 3. Add Docker Build to PR Workflow (1-2 hours)
```yaml
      - name: Build Docker image (dev)
        run: docker build -t test-dev .
      - name: Build Docker image (Konflux)
        run: docker build -f Dockerfile.konflux -t test-konflux .
```

### 4. Move Trivy to PR Workflow (1 hour)
```yaml
      - name: Build test image
        run: docker build -t sidecar-test .
      - name: Run Trivy scan
        uses: ./.github/actions/trivy-scan
        with:
          image: sidecar-test
```

### 5. Add Concurrency Control (30 minutes)
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

### 6. Write LMCache Connector Tests (3-4 hours)
Follow the existing pattern in `connector_nixlv2_test.go`:
- Create `connector_lmcache_test.go`
- Test prefill request with max_tokens=1 modification
- Test decode request with original body forwarding
- Test error handling for malformed requests and prefiller failures

## Detailed Findings

### CI/CD Pipeline

**GitHub Actions Workflows:**

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `ci-pr-checks.yaml` | PR to main | Checkout, Go setup (1.24, cached), markdown link checker, golangci-lint v2.1.6, `make test` |
| `ci-release.yaml` | Tag push / release published | Checkout, Docker build+push (ghcr.io/llm-d), Trivy scan |

**Composite Actions:** `docker-build-and-push`, `go-test`, `markdown-link-checker`, `push-image`, `trivy-scan`

**Tekton/Konflux Pipelines:**

| Pipeline | Trigger | Key Tasks |
|----------|---------|-----------|
| `odh-llm-d-routing-sidecar-pull-request.yaml` | `/build-konflux` comment on PR | Multi-arch build (x86_64 + arm64), hermetic, go mod prefetch |
| `llm-d-routing-sidecar-push.yaml` | Push to release-0.3 | Full build + 8 security scans (Clair, Snyk, Coverity, ClamAV, shell-check, unicode-check, RPM signature, deprecated base image) + SBOM |

**Gaps:**
- No concurrency control on PR workflow
- No E2E tests in any CI pipeline
- No image build on PR in GitHub CI
- Tekton PR build requires manual trigger
- No notification/alerting on GitHub CI failures (Tekton has Slack notifications)

### Test Coverage

**Framework**: Ginkgo v2 + Gomega (BDD-style)

**Test File Inventory:**

| Test File | Source File | Lines | What's Tested |
|-----------|------------|-------|---------------|
| `proxy_test.go` | `proxy.go`, `chat_completions.go`, `connector_nixl.go` | 257 | Reverse proxy forwarding across 5 paths (chat completions, completions, embeddings, score, healthz) with both secure and insecure modes. NIXL v1 prefill/decode handoff. |
| `connector_nixlv2_test.go` | `connector_nixlv2.go` | 196 | NIXL v2 protocol with kv_transfer_params structure. Backward-compatible and standard header behaviors. |
| `allowlist_test.go` | `allowlist.go` | 92 | SSRF protection: disabled mode (allow all), enabled mode (allowlist enforcement), host:port parsing, IPv6 support. |
| `proxy_suite_test.go` | (suite setup) | 28 | Ginkgo suite registration. |

**Test-to-Code Ratio**: ~573 test lines / ~1,498 source lines = **0.38** (below the 0.5+ target for critical infrastructure)

**Untested Source Files:**

| File | Lines | Risk |
|------|-------|------|
| `connector_lmcache.go` | 88 | **HIGH** - Entire P/D protocol path untested |
| `errors.go` | 78 | MEDIUM - Error response formatting (tested indirectly) |
| `tls.go` | 72 | MEDIUM - Self-signed certificate generation |
| `status_response_writer.go` | 47 | LOW - Simple buffered writer (tested indirectly via connector tests) |
| `main.go` | 109 | LOW - CLI entry point with flag parsing |
| `internal/signals/` | ~30 | LOW - OS signal handling |

**Mock Infrastructure**: Well-designed mocks in `test/mock/`:
- `chat_completions_handler.go` - Simulates prefill and decode backends, supports all connector types
- `generic_handler.go` - Generic HTTP handler for testing

### Code Quality

**Linting (`.golangci.yml`)**: Version 2 config with 18 linters enabled:
- Code correctness: `govet`, `errcheck`, `ineffassign`, `unused`, `unconvert`
- Performance: `perfsprint`, `prealloc`, `makezero`
- Style: `goimports`, `gofmt`, `goconst`, `nakedret`
- Go-specific: `copyloopvar`, `durationcheck`, `fatcontext`, `loggercheck`
- Domain-specific: `ginkgolinter` (validates Ginkgo/Gomega usage)
- Text: `dupword`, `misspell`
- Design: `revive`, `gocritic`, `unparam`

**Pre-commit Hooks (`.pre-commit-config.yaml`)**:
- `trailing-whitespace`, `end-of-file-fixer`, `check-yaml` (pre-commit-hooks v5.0.0)
- `go-fmt`, `golangci-lint` (pre-commit-golang v0.5.1)

**Git Hooks**: Custom `hooks/pre-commit` script that runs `make lint` + `make test`. Installed via `make install-hooks` (`git config core.hooksPath hooks`).

**Strengths**: Comprehensive linting with Ginkgo-specific linter. Pre-commit hooks enforce quality locally. Good code organization.

### Container Images

**Dockerfiles:**

| File | Base Image | CGO | Notes |
|------|-----------|-----|-------|
| `Dockerfile` | `ubi9/go-toolset:1.24` → `ubi9/ubi-micro:latest` | Disabled (CGO_ENABLED=0) | Dev/GitHub CI builds. Minimal runtime image. |
| `Dockerfile.konflux` | `ubi9/go-toolset:1.24@sha256:...` → `ubi9/ubi:latest` | Enabled (CGO_ENABLED=1) | Production Konflux builds. Pinned builder, larger runtime. Uses `go build -mod=mod`. |

**Divergence Risks:**
- CGO_ENABLED differs (0 vs 1) - could cause runtime behavior differences
- Base image differs (ubi-micro vs ubi) - different system libraries available
- Dockerfile.konflux uses `-mod=mod` flag - module handling differs
- No automated test validates both build successfully on PRs

**Security:**
- Both run as non-root (USER 65532:65532)
- Multi-stage builds to minimize attack surface
- Konflux Dockerfile uses pinned digest for builder image

### Security

**Application-Level Security:**
- **SSRF Protection**: Built into the proxy via `AllowlistValidator`. Validates prefill target URLs against Kubernetes InferencePool pod allowlist. Well-tested.
- **TLS Support**: Self-signed cert generation, configurable per-connection TLS for prefiller and decoder. Strong cipher suite configuration (TLS 1.2+, ECDHE only).

**CI/CD Security Scanning:**

| Tool | Where | When |
|------|-------|------|
| Trivy (HIGH, CRITICAL) | GitHub Actions | Release only |
| Clair vulnerability scan | Tekton push | Post-merge |
| Snyk SAST | Tekton push | Post-merge |
| Coverity SAST | Tekton push | Post-merge |
| ClamAV malware scan | Tekton push | Post-merge |
| Shell-check | Tekton push | Post-merge |
| Unicode-check | Tekton push | Post-merge |
| RPM signature scan | Tekton push | Post-merge |
| Deprecated base image check | Tekton push | Post-merge |
| Ecosystem cert preflight | Tekton push | Post-merge |

**Gaps:**
- No security scanning in GitHub PR workflow
- No secret detection (gitleaks, trufflehog)
- No SBOM generation in GitHub CI (only Tekton)
- All comprehensive scanning is post-merge only

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no test type rules exist
- **Quality**: N/A
- **Gaps**:
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory
  - No `.claude/rules/` for test creation rules
  - No documentation of test patterns, mock usage, or connector test conventions
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering:
  - Unit test patterns (Ginkgo `Describe`/`It`/`BeforeEach`, Gomega matchers)
  - Mock infrastructure usage (`test/mock/` handlers)
  - Connector protocol testing patterns (prefill/decode handoff verification)
  - SSRF protection test patterns
  - E2E test conventions (Kind cluster, kustomize overlays)

## Recommendations

### Priority 0 (Critical)

1. **Add coverage generation and codecov integration** (2-4 hours)
   - Modify `make test` to generate coverage profiles
   - Add codecov GitHub Action to PR workflow
   - Set initial coverage threshold (e.g., 40%) and ratchet upward

2. **Write unit tests for `connector_lmcache.go`** (4-6 hours)
   - Follow the NIXL v2 test pattern in `connector_nixlv2_test.go`
   - Test max_tokens modification for prefill request
   - Test original body forwarding to decoder
   - Test error handling (invalid JSON, prefiller failures)

3. **Add Docker image build validation to PR workflow** (2-4 hours)
   - Build both `Dockerfile` and `Dockerfile.konflux` on every PR
   - Catch divergence-related build failures before merge

4. **Move Trivy scanning to PR workflow** (1 hour)
   - Reuse existing `.github/actions/trivy-scan` composite action
   - Scan the dev image built on PR

### Priority 1 (High Value)

5. **Expand E2E tests to validate proxy behavior** (8-16 hours)
   - Send actual HTTP requests to the sidecar in the Kind cluster
   - Test prefill/decode routing with mock vLLM pods
   - Test SSRF protection with unauthorized prefill targets
   - Test TLS mode
   - Automate E2E in CI (at least nightly/periodic)

6. **Add unit tests for untested modules** (4-6 hours)
   - `tls.go`: Test certificate generation and validation
   - `errors.go`: Test error response format matches vLLM contract
   - `status_response_writer.go`: Test buffered write behavior

7. **Automate Tekton PR build or add Konflux simulation** (4-8 hours)
   - Remove `/build-konflux` comment trigger for auto-run on PR
   - Or: Add a GitHub Actions step that simulates the Konflux hermetic build

8. **Create agent rules for AI-assisted development** (2-4 hours)
   - Create `.claude/rules/unit-tests.md` with Ginkgo patterns
   - Create `.claude/rules/e2e-tests.md` with Kind cluster patterns
   - Document mock infrastructure usage and connector test conventions

### Priority 2 (Nice-to-Have)

9. **Add secret detection** (1-2 hours)
   - Add gitleaks or trufflehog to PR workflow
   - Configure for Go project patterns

10. **Add integration tests with Testcontainers** (8-12 hours)
    - Test sidecar container startup and health endpoint
    - Test with containerized mock vLLM backends
    - Validate both Dockerfile variants produce working images

11. **Add performance/load testing** (8-16 hours)
    - Benchmark proxy latency and throughput under concurrent requests
    - Test LRU cache behavior under load (prefiller proxy cache, size 16)
    - Identify bottlenecks in prefill/decode handoff

12. **Add concurrency control to PR workflow** (30 minutes)
    - Cancel stale CI runs on new pushes to the same PR

## Comparison to Gold Standards

| Dimension | llm-d-routing-sidecar | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|-----------|----------------------|---------------------|-----------------|---------------|
| Unit Test Framework | Ginkgo/Gomega | Jest/React Testing Library | pytest | Go testing + Ginkgo |
| Test-to-Code Ratio | 0.38 | 0.8+ | 0.6+ | 0.7+ |
| Coverage Tracking | None | Codecov with thresholds | Coverage reports | Codecov enforced |
| E2E Tests | Skeletal (pod status) | Cypress, comprehensive | Image validation suite | Multi-version E2E |
| E2E in CI | No | Yes (PR) | Yes (periodic) | Yes (PR + periodic) |
| PR Image Build | No | Yes | Yes | Yes |
| Security Scanning (PR) | No | Yes (CodeQL) | Yes (Trivy) | Yes (multiple) |
| Security Scanning (Post-merge) | 8 Tekton scans | CodeQL + Snyk | Trivy | Multiple tools |
| Pre-commit Hooks | Yes (lint + test) | Yes | Yes | Yes |
| Linting | 18 golangci-lint rules | ESLint comprehensive | Linting suite | golangci-lint |
| Agent Rules | None | Comprehensive | Partial | Partial |
| Contract Tests | None | Yes | N/A | Yes |

## File Paths Reference

### CI/CD
- `.github/workflows/ci-pr-checks.yaml` - PR lint and test workflow
- `.github/workflows/ci-release.yaml` - Release build and scan workflow
- `.github/actions/trivy-scan/action.yml` - Trivy composite action
- `.github/actions/docker-build-and-push/` - Docker build composite action
- `.tekton/odh-llm-d-routing-sidecar-pull-request.yaml` - Tekton PR pipeline (comment-triggered)
- `.tekton/llm-d-routing-sidecar-push.yaml` - Tekton push pipeline (comprehensive)

### Testing
- `internal/proxy/proxy_test.go` - Proxy forwarding and NIXL v1 tests
- `internal/proxy/connector_nixlv2_test.go` - NIXL v2 protocol tests
- `internal/proxy/allowlist_test.go` - SSRF protection tests
- `internal/proxy/proxy_suite_test.go` - Ginkgo suite setup
- `test/e2e/e2e_test.go` - E2E test (pod status only)
- `test/mock/chat_completions_handler.go` - Mock handler infrastructure
- `test/config/` - Kustomize overlays for Kind and NIXL testing

### Code Quality
- `.golangci.yml` - 18-linter configuration (v2 format)
- `.pre-commit-config.yaml` - Pre-commit hooks (whitespace, YAML, go-fmt, lint)
- `hooks/pre-commit` - Git hook running lint + test

### Container Images
- `Dockerfile` - Dev/GitHub CI image (CGO_ENABLED=0, ubi-micro)
- `Dockerfile.konflux` - Production Konflux image (CGO_ENABLED=1, ubi, pinned)

### Source Code (Core)
- `internal/proxy/proxy.go` - Reverse proxy server (315 lines)
- `internal/proxy/allowlist.go` - SSRF protection via K8s allowlist (386 lines)
- `internal/proxy/connector_nixlv2.go` - NIXL v2 P/D protocol (165 lines)
- `internal/proxy/connector_nixl.go` - NIXL v1 P/D protocol (178 lines)
- `internal/proxy/connector_lmcache.go` - LMCache P/D protocol (88 lines, **untested**)
- `cmd/llm-d-routing-sidecar/main.go` - CLI entry point (109 lines)
