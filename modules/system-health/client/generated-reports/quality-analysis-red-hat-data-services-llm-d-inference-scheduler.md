---
repository: "red-hat-data-services/llm-d-inference-scheduler"
overall_score: 7.6
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Excellent test-to-code ratio (1.2:1 LOC), 166 test files covering 271 source files with race detection and coverage profiling"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Comprehensive Kind-based E2E with Ginkgo, integration tests with build tags, sidecar E2E, multi-scenario coverage (PD, DP, disagg)"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR builds validated via container-in-container builder pattern; Konflux pipelines are label/comment-triggered, not automatic on every PR"
  - dimension: "Image Testing"
    score: 6.5
    status: "Multi-stage distroless Dockerfiles with Trivy scanning on release builds; no PR-time image build or runtime validation"
  - dimension: "Coverage Tracking"
    score: 8.0
    status: "Custom coverage comparison against main and release branches with GitHub step summaries; no external coverage service (codecov/coveralls)"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "Well-organized workflows with path filtering, Go caching, signed commit enforcement, typo checks, Dependabot + Renovate, release automation"
  - dimension: "Agent Rules"
    score: 1.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory; no AI-assisted test creation guidance"
critical_gaps:
  - title: "No external coverage service integration"
    impact: "Coverage trends not visible to reviewers in PR comments; no historical tracking or per-PR enforcement thresholds"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No SAST/CodeQL integration"
    impact: "No static application security testing in CI; security vulnerabilities may go undetected in code patterns"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Trivy scanning only runs on release builds, not PR builds"
    impact: "Vulnerabilities introduced by dependency changes or base image updates are not caught until post-merge release"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI coding agents lack guidance on test patterns, frameworks, and quality standards specific to this project"
    severity: "MEDIUM"
    effort: "3-5 hours"
  - title: "Konflux builds are not automatically triggered on every PR"
    impact: "Konflux build failures may be discovered only after merge if developers forget to trigger manually"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catch container vulnerabilities before merge instead of only at release time"
  - title: "Add codecov.io integration"
    effort: "2-3 hours"
    impact: "Per-PR coverage reports with inline annotations, historical tracking, and configurable thresholds"
  - title: "Add CodeQL or gosec workflow"
    effort: "2-3 hours"
    impact: "Automated static security analysis catches injection, overflow, and insecure patterns"
  - title: "Create basic agent rules (.claude/rules/)"
    effort: "2-3 hours"
    impact: "Standardize AI-generated test quality with project-specific patterns and conventions"
recommendations:
  priority_0:
    - "Add SAST scanning (CodeQL or gosec) to PR workflow to catch security issues before merge"
    - "Move Trivy container scanning from release-only to PR-time to catch vulnerabilities early"
  priority_1:
    - "Integrate codecov.io or coveralls for visible, enforceable coverage tracking per PR"
    - "Create comprehensive agent rules for test automation (.claude/rules/) covering unit, integration, and E2E patterns"
    - "Auto-trigger Konflux builds on all PRs instead of requiring label/comment triggers"
  priority_2:
    - "Add secret detection (gitleaks) to prevent credential leaks"
    - "Add SBOM generation to container builds for supply chain transparency"
    - "Add performance regression testing for scheduler/routing latency"
    - "Create pre-commit-config.yaml for standardized local checks beyond the custom hooks/pre-commit"
---

# Quality Analysis: llm-d-inference-scheduler

## Executive Summary

- **Overall Score: 7.6/10**
- **Repository Type**: Go-based Kubernetes inference scheduling system (EPP + routing sidecar)
- **Primary Language**: Go 1.25 with Ginkgo/Gomega + testify test frameworks
- **Key Strengths**: Exceptional test-to-code ratio, comprehensive E2E infrastructure with Kind clusters, custom coverage comparison against baseline branches, well-organized CI/CD with caching and path filtering
- **Critical Gaps**: No SAST/CodeQL, Trivy only on releases, no codecov integration, no agent rules
- **Agent Rules Status**: Missing - no CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Excellent test-to-code ratio (1.2:1 LOC), race detection, coverage profiling |
| Integration/E2E | 8.0/10 | Kind-based E2E, integration tests with build tags, multi-scenario coverage |
| **Build Integration** | **7.0/10** | **Builder container pattern; Konflux via label/comment trigger only** |
| Image Testing | 6.5/10 | Trivy on release; no PR-time image scanning or runtime validation |
| Coverage Tracking | 8.0/10 | Custom baseline comparison; no external service (codecov/coveralls) |
| CI/CD Automation | 8.5/10 | Path filtering, Go caching, signed commits, Dependabot + Renovate |
| Agent Rules | 1.0/10 | No AI-assisted development guidance exists |

## Critical Gaps

### 1. No SAST/CodeQL Integration
- **Impact**: Security vulnerabilities in code patterns (injection, overflow, insecure crypto) go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No CodeQL, gosec, Semgrep, or any SAST tool is configured in CI workflows

### 2. Trivy Scanning Only on Release Builds
- **Impact**: Container vulnerabilities from dependency updates or base image changes aren't caught until release time
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Details**: The `trivy-scan` action exists and works well but is only invoked from `ci-build-images.yaml` (called by `ci-dev.yaml` and `ci-release.yaml`), not from `ci-pr-checks.yaml`

### 3. No External Coverage Service
- **Impact**: No per-PR coverage annotations, no historical trend tracking, no configurable enforcement thresholds
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: The project has an impressive custom `compare-coverage.sh` script that compares against main and release branches, but there's no codecov.io or coveralls integration for reviewer-visible inline coverage feedback

### 4. No Agent Rules
- **Impact**: AI coding agents generate tests without knowledge of project-specific patterns, frameworks, or quality standards
- **Severity**: MEDIUM
- **Effort**: 3-5 hours
- **Details**: No `.claude/` directory, `CLAUDE.md`, or `AGENTS.md` exists

### 5. Konflux Builds Not Auto-Triggered on PRs
- **Impact**: Build failures in Konflux (hermetic, multi-arch) may be discovered only post-merge
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: `.tekton/` pipelines use `on-comment: "^/build-epp"` and `on-label: "[kfbuild-all, kfbuild-epp]"` triggers, requiring manual action

## Quick Wins

### 1. Add Trivy Scanning to PR Workflow (1-2 hours)
Add a container build + Trivy scan step to `ci-pr-checks.yaml`:
```yaml
- name: Build EPP image for scanning
  run: make image-build-epp
- name: Run Trivy scan
  uses: ./.github/actions/trivy-scan
  with:
    image: ${{ env.EPP_IMAGE }}
```

### 2. Add Codecov Integration (2-3 hours)
- Create `.codecov.yml` with coverage targets
- Add codecov upload step to `ci-pr-checks.yaml` after unit tests
- Get immediate PR-level coverage annotations

### 3. Add CodeQL Workflow (2-3 hours)
```yaml
name: CodeQL Analysis
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: github/codeql-action/init@v3
        with:
          languages: go
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
```

### 4. Create Basic Agent Rules (2-3 hours)
Create `.claude/rules/unit-tests.md` with Ginkgo/Gomega patterns, table-driven test conventions, and mocking strategies used in this repo.

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- **Path filtering**: `ci-pr-checks.yaml` uses `dorny/paths-filter` to skip CI for non-code changes (docs-only PRs)
- **Docker volume caching**: Go module and build caches are persisted via Docker volumes + `actions/cache`, reducing build times
- **Builder container pattern**: All build/test/lint operations run inside a consistent `Dockerfile.builder` container, ensuring reproducibility across local and CI environments
- **Signed commit enforcement**: `ci-signed-commits.yaml` uses `1Password/check-signed-commits-action`
- **Typo checking**: Both CI (`crate-ci/typos`) and lint (`typos` in builder) catch spelling errors
- **Dependabot + Renovate**: Dual dependency management - Dependabot for Go modules, GitHub Actions, and Docker images; Renovate for Konflux-specific dependencies
- **Release automation**: Clean tag-based release workflow with image builds and Trivy scanning

**Workflow Inventory:**
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-pr-checks.yaml` | PR + push to main | Lint, build, unit tests, E2E, coverage comparison |
| `ci-dev.yaml` | Push to main/release-* | Build + push dev images with Trivy |
| `ci-build-images.yaml` | Reusable (workflow_call) | Build + push + Trivy scan for EPP and sidecar |
| `ci-release.yaml` | Tags/releases | Build + push release images |
| `ci-signed-commits.yaml` | PR target | Enforce signed commits |
| `check-typos.yaml` | PR + push | Spell checking |
| `md-link-check.yml` | PR | Markdown link validation |
| `auto-assign.yaml` | Various | Auto-assign reviewers |
| `pr-kind-label.yaml` | PR | Label enforcement |
| `stale.yaml` / `unstale.yaml` | Scheduled | Issue/PR staleness management |

**Gaps:**
- No SAST/security scanning in PR workflow
- No Trivy scanning on PRs
- No pre-commit-config.yaml (uses custom `hooks/pre-commit` instead)

### Test Coverage

**Unit Tests (8.5/10):**
- 166 test files covering 271 source files (0.61:1 file ratio)
- ~51,009 lines of test code vs ~42,282 lines of source code (1.21:1 LOC ratio - excellent)
- Uses both Ginkgo/Gomega (for E2E, proxy tests) and standard Go testing + testify (for unit tests)
- Race detection enabled (`-race` flag)
- Coverage profiling per component (`epp.out`, `sidecar.out`)
- Comprehensive mock/fake infrastructure (10+ mock files across packages)
- Dedicated benchmark tests (`test/profiling/tokenizerbench/`)

**Integration Tests (8.0/10):**
- Build-tag guarded (`//go:build integration_tests`) ensuring separation from unit tests
- Uses real HTTP requests to validate endpoint picker behavior
- Requires running cluster (KUBECONFIG), providing realistic validation
- Coverage profiling for integration tests (`integration.out`)

**E2E Tests (8.0/10):**
- Full Kind cluster lifecycle management (create, load images, test, cleanup)
- Tests multiple deployment topologies: simple, PD disaggregation, data parallel, E/P/D disagg, EPD unified
- Validates completions, chat completions, multimodal (image, video, audio), embeddings
- Sidecar has its own E2E suite (`test/sidecar/e2e/`)
- Debug-friendly: dumps pod logs and events on failure, supports `E2E_KEEP_CLUSTER_ON_FAILURE`
- Configurable via environment variables (port, timeout, namespace, K8S context)

**Coverage Tracking (8.0/10):**
- Custom `compare-coverage.sh` script comparing PR coverage against main baseline
- Release branch coverage baselines stored as GitHub artifacts (400-day retention)
- Coverage comparison appears in GitHub Step Summary
- Currently report-only mode (threshold = 0), no hard enforcement
- No external coverage service (codecov/coveralls)

### Code Quality

**Linting (Strong):**
- golangci-lint v2 with 20+ linters enabled including:
  - `bodyclose`, `errcheck`, `govet`, `staticcheck`, `revive`, `unparam`, `unused`
  - `ginkgolinter` for Ginkgo/Gomega best practices
  - `perfsprint`, `prealloc` for performance
  - `misspell`, `dupword` for text quality
- Smart exclusions: test files exempt from `goconst`/`prealloc`, package naming exceptions for upstream compatibility
- Formatting with `goimports` + `gofmt`
- `typos` spell checker integrated into lint step

**Pre-commit Hooks:**
- Custom `hooks/pre-commit` script runs `make lint` and `make test`
- Must be manually activated (`git config core.hooksPath hooks`)
- No `.pre-commit-config.yaml` for the pre-commit framework

**Static Analysis:**
- No SAST tools (CodeQL, gosec, Semgrep) configured
- No secret detection (gitleaks, TruffleHog)

### Container Images

**Build Process (Strong):**
- Multi-stage Dockerfiles for EPP and sidecar
- Distroless base image (`gcr.io/distroless/static:nonroot`) for minimal CVE surface
- Configurable base image via build args (supports UBI9 for Konflux)
- Non-root user (65532:65532)
- Cross-platform support via BUILDPLATFORM/TARGETARCH
- Stripped binaries (`-s -w` ldflags) with embedded version info
- Separate Konflux Dockerfiles (`Dockerfile.epp.konflux`, `Dockerfile.sidecar.konflux`) with pinned SHA digests

**Konflux Integration:**
- Hermetic builds with pre-fetched dependencies (gomod, generic, RPM)
- Multi-architecture (x86_64, arm64)
- Source image builds enabled
- SBOM generation via `prefetch-input` RPM config
- Image expiry (5 days for PRs)

**Gaps:**
- No PR-time container builds or Trivy scans in GitHub Actions
- No container runtime validation (startup, health check tests)
- Konflux pipelines require manual trigger

### Security

**Strengths:**
- Trivy scanning with `exit-code: 1` (fails on HIGH/CRITICAL) on release builds
- Signed commit enforcement
- Dependabot security updates with grouped PRs
- Distroless base images minimize attack surface
- Non-root container users
- CVE-specific Go toolchain pinning (go1.25.8 for CVE-2025-61729)

**Gaps:**
- No SAST/CodeQL for code-level security analysis
- No secret detection tooling
- No dependency vulnerability scanning in PR workflow (Trivy only at release)
- No SBOM generation for GitHub Actions builds (only Konflux)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no `.claude/` directory, `CLAUDE.md`, or `AGENTS.md`
- **Quality**: N/A
- **Gaps**: No test automation guidance for AI agents exists
- **Recommendation**: Generate comprehensive rules with `/test-rules-generator` covering:
  - Unit test patterns (Ginkgo/Gomega + testify conventions)
  - Integration test patterns (build tags, real HTTP validation)
  - E2E test patterns (Kind cluster setup, YAML manifests, environment variables)
  - Mocking strategies (custom fakes in `pkg/epp/backend/metrics/fake.go`, interface mocks)
  - Coverage requirements and enforcement expectations

## Recommendations

### Priority 0 (Critical)

1. **Add SAST scanning to PR workflow** - Implement CodeQL or gosec to catch security vulnerabilities in Go code before merge
2. **Move Trivy scanning to PR workflow** - Add container build + scan step to `ci-pr-checks.yaml` so vulnerabilities are caught before merge, not just at release

### Priority 1 (High Value)

3. **Integrate codecov.io** - Add coverage upload and PR annotations for reviewer-visible coverage feedback with configurable thresholds
4. **Create agent rules** - Add `.claude/rules/` directory with unit-tests.md, integration-tests.md, and e2e-tests.md covering project-specific patterns
5. **Auto-trigger Konflux builds** - Change Tekton pipeline triggers from label/comment-based to automatic PR triggers to prevent post-merge build failures
6. **Add secret detection** - Configure gitleaks or TruffleHog to prevent credential leaks in commits

### Priority 2 (Nice-to-Have)

7. **Add SBOM generation** - Generate Software Bill of Materials for GitHub Actions builds (already done for Konflux)
8. **Standardize pre-commit** - Migrate custom `hooks/pre-commit` to `.pre-commit-config.yaml` for easier developer onboarding
9. **Add performance regression tests** - Benchmark scheduler latency and routing performance with automated regression detection
10. **Enable coverage enforcement** - Set `COVERAGE_THRESHOLD` to a non-zero value in `compare-coverage.sh` to prevent regressions

## Comparison to Gold Standards

| Dimension | llm-d-inference-scheduler | odh-dashboard | notebooks | kserve |
|-----------|--------------------------|---------------|-----------|--------|
| Unit Test Coverage | Strong (1.2:1 LOC ratio) | Strong | Moderate | Strong |
| Integration Tests | Build-tag guarded, real HTTP | Multi-layer | Image-focused | envtest-based |
| E2E Tests | Kind cluster, multi-topology | Cypress + API | Multi-image | Multi-version |
| Coverage Tracking | Custom baseline comparison | Codecov enforced | None | Codecov enforced |
| Container Scanning | Trivy (release only) | Trivy (PR + release) | Multi-layer validation | Trivy (PR) |
| SAST | None | CodeQL | None | CodeQL |
| Agent Rules | None | Comprehensive | None | Basic |
| CI Caching | Docker volumes + actions/cache | actions/cache | Layer caching | actions/cache |
| Pre-commit | Custom script | .pre-commit-config | None | .pre-commit-config |
| Dependency Management | Dependabot + Renovate | Dependabot | Dependabot | Dependabot |

## File Paths Reference

### CI/CD
- `.github/workflows/ci-pr-checks.yaml` - Main PR checks (lint, build, test, coverage)
- `.github/workflows/ci-build-images.yaml` - Reusable image build + Trivy workflow
- `.github/workflows/ci-dev.yaml` - Dev image builds on main/release pushes
- `.github/workflows/ci-release.yaml` - Release image builds on tags
- `.github/workflows/ci-signed-commits.yaml` - Signed commit enforcement
- `.github/workflows/check-typos.yaml` - Typo checking
- `.github/actions/trivy-scan/action.yaml` - Trivy scan composite action
- `.tekton/odh-llm-d-inference-scheduler-pull-request.yaml` - Konflux EPP pipeline
- `.tekton/odh-llm-d-routing-sidecar-pull-request.yaml` - Konflux sidecar pipeline

### Testing
- `test/e2e/` - E2E tests (Ginkgo/Gomega, Kind cluster)
- `test/integration/` - Integration tests (build-tag guarded)
- `test/sidecar/e2e/` - Sidecar E2E tests
- `test/profiling/tokenizerbench/` - Benchmark tests
- `test/utils/` - Shared test utilities
- `test/sidecar/mock/` - Sidecar mock handlers
- `pkg/epp/backend/metrics/fake.go` - Metric fake implementations

### Code Quality
- `.golangci.yml` - golangci-lint v2 config (20+ linters)
- `.typos.toml` - Typos spell checker config
- `hooks/pre-commit` - Custom pre-commit hook

### Container Images
- `Dockerfile.epp` - EPP production image (distroless)
- `Dockerfile.sidecar` - Sidecar production image (distroless)
- `Dockerfile.epp.konflux` - EPP Konflux image (UBI9)
- `Dockerfile.sidecar.konflux` - Sidecar Konflux image (UBI9)
- `Dockerfile.builder` - Builder container with all development tools

### Build
- `Makefile` - Main Makefile with all targets
- `Makefile.tools.mk` - Tool checks
- `Makefile.cluster.mk` - Cluster-specific targets
- `Makefile.kind.mk` - Kind development environment

### Dependencies
- `.github/dependabot.yml` - Dependabot config (Go, Actions, Docker)
- `.github/renovate.json` - Renovate config (Konflux dependencies)
- `go.mod` / `go.sum` - Go module dependencies

### Coverage
- `scripts/compare-coverage.sh` - Coverage baseline comparison script
