---
repository: "opendatahub-io/llm-d-inference-scheduler"
overall_score: 7.6
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Extensive unit tests across all packages with race detection and coverage profiling"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "Multi-layer test strategy with hermetic integration, cluster integration, and Kind-based E2E"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR builds validated in CI; Konflux builds run separately via Tekton pipelines"
  - dimension: "Image Testing"
    score: 6.5
    status: "Multi-stage Dockerfiles with distroless base; Trivy scanning on release builds but not on PR"
  - dimension: "Coverage Tracking"
    score: 7.5
    status: "Per-component coverage with baseline comparison against main and release branches; no external service"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "Well-organized workflows with concurrency control, path filtering, caching, and Prow integration"
  - dimension: "Agent Rules"
    score: 8.0
    status: "Comprehensive AGENTS.md with code style, PR workflow, and operating rules; no .claude/rules/ directory"
critical_gaps:
  - title: "No Trivy scanning on PR builds"
    impact: "Vulnerabilities introduced in PRs are only discovered post-merge during release builds"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No external coverage service (Codecov/Coveralls)"
    impact: "Coverage trends not visible over time; PR coverage comments rely on custom script"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "No pre-commit hooks enforced by default"
    impact: "Developers may push unformatted or unlinted code; hooks exist but require manual install"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No SAST/CodeQL integration"
    impact: "Static analysis limited to golangci-lint; no dedicated security-focused static analysis"
    severity: "MEDIUM"
    effort: "3-4 hours"
quick_wins:
  - title: "Add Trivy scan step to PR checks workflow"
    effort: "2-3 hours"
    impact: "Catch CVEs before merge using existing trivy-scan composite action"
  - title: "Add Codecov integration for coverage trends"
    effort: "2-3 hours"
    impact: "Historical coverage tracking, PR comments, and ratchet enforcement"
  - title: "Add CodeQL workflow for SAST"
    effort: "2-3 hours"
    impact: "Automated security scanning beyond linting with GitHub Security tab integration"
  - title: "Create .claude/rules/ for test pattern guidance"
    effort: "3-4 hours"
    impact: "Standardize AI-generated tests to match existing Ginkgo/Gomega patterns"
recommendations:
  priority_0:
    - "Add Trivy container scanning to PR workflow using existing composite action"
    - "Add CodeQL or gosec SAST scanning workflow for security-focused static analysis"
  priority_1:
    - "Integrate Codecov for historical coverage tracking and PR enforcement"
    - "Add .claude/rules/ with test pattern rules for unit, integration, and E2E tests"
    - "Make pre-commit hooks install automatic (e.g., via Makefile post-install target)"
  priority_2:
    - "Add SBOM generation to container image builds"
    - "Add container image signing/attestation for supply chain security"
    - "Add performance regression testing beyond the tokenizer benchmark"
---

# Quality Analysis: llm-d-inference-scheduler

## Executive Summary

- **Overall Score: 7.6/10**
- **Repository Type**: Go service (Kubernetes-native inference router with EPP + sidecar)
- **Primary Language**: Go 1.25
- **Framework**: Kubernetes client-go, controller-runtime, Gateway API, gRPC/envoy ext_proc
- **Key Strengths**: Excellent test-to-code ratio (219 test files / 321 source files = 0.68), multi-layer test strategy (unit + hermetic integration + cluster integration + E2E), well-organized CI with path filtering and concurrency control, comprehensive AGENTS.md
- **Critical Gaps**: No Trivy scanning on PRs, no external coverage service, no SAST/CodeQL, pre-commit hooks require manual install
- **Agent Rules Status**: Present (AGENTS.md) but no `.claude/rules/` directory for test-specific patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Extensive unit tests across all packages with race detection and coverage profiling |
| Integration/E2E | 8.0/10 | Multi-layer test strategy: hermetic (envtest), cluster integration, Kind-based E2E |
| Build Integration | 7.0/10 | PR builds validated in CI; Konflux via separate Tekton pipelines on PR and push |
| Image Testing | 6.5/10 | Multi-stage Dockerfiles with distroless base; Trivy only on release builds |
| Coverage Tracking | 7.5/10 | Per-component coverage with baseline comparison; no external service (Codecov) |
| CI/CD Automation | 8.5/10 | Well-organized workflows with concurrency, path filtering, caching, Prow integration |
| Agent Rules | 8.0/10 | Comprehensive AGENTS.md; no .claude/rules/ for test pattern guidance |

## Critical Gaps

### 1. No Trivy Scanning on PR Builds
- **Impact**: Vulnerabilities introduced in PRs are only caught post-merge during release/dev builds
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The `trivy-scan` composite action exists and runs on `ci-build-images.yaml` (release/dev), but `ci-pr-checks.yaml` does not build or scan container images. A PR could introduce a dependency with a critical CVE and it would not be detected until the image is built post-merge.
- **Fix**: Add a Docker build + Trivy scan step to `ci-pr-checks.yaml`, or create a dedicated PR security scan workflow.

### 2. No External Coverage Service
- **Impact**: Coverage trends not visible over time; no ratchet enforcement to prevent regression
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: The project has a custom `compare-coverage.sh` script that generates a coverage comparison table in GitHub Step Summary. This is useful but doesn't provide historical trend data, badge support, or automatic PR comments with line-level coverage diffs. No `.codecov.yml` or Coveralls integration exists.

### 3. Pre-commit Hooks Not Auto-installed
- **Impact**: Developers may push unformatted/unlinted code that fails CI
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: Git hooks exist in `hooks/pre-commit` (runs `make lint` and `make test`) and a `make install-hooks` target exists, but hook installation is manual. New contributors may not know to run it.

### 4. No SAST/CodeQL Integration
- **Impact**: Static security analysis limited to golangci-lint checks; no dedicated SAST tool
- **Severity**: MEDIUM
- **Effort**: 3-4 hours
- **Details**: While `golangci-lint` includes some security-relevant linters (e.g., `govet`, `staticcheck`), there's no dedicated CodeQL, gosec, or Semgrep workflow. `govulncheck` is run in CI (good for known CVEs in dependencies) but doesn't cover code-level vulnerabilities.

## Quick Wins

### 1. Add Trivy Scan to PR Workflow
- **Effort**: 2-3 hours
- **Impact**: Catch CVEs before merge
- **Implementation**: The `trivy-scan` composite action already exists at `.github/actions/trivy-scan/action.yaml`. Add a build-and-scan job to `ci-pr-checks.yaml`:
```yaml
  security-scan:
    needs: check-changes
    if: ${{ needs.check-changes.outputs.src == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Build EPP image for scanning
        run: docker build -f Dockerfile.epp -t epp-scan:pr .
      - uses: ./.github/actions/trivy-scan
        with:
          image: epp-scan:pr
```

### 2. Add Codecov Integration
- **Effort**: 2-3 hours
- **Impact**: Historical coverage tracking, PR comments, enforcement
- **Implementation**: Add `codecov/codecov-action` to `ci-pr-checks.yaml` after the unit test step, uploading `coverage/*.out` files.

### 3. Add CodeQL Workflow
- **Effort**: 2-3 hours
- **Impact**: Automated SAST with GitHub Security tab integration
- **Implementation**: Create `.github/workflows/codeql.yml` with standard Go CodeQL config.

### 4. Create .claude/rules/ for Test Patterns
- **Effort**: 3-4 hours
- **Impact**: Standardize AI-generated tests across the repo
- **Implementation**: Create rules for Ginkgo/Gomega patterns (unit), envtest patterns (hermetic integration), and Kind E2E patterns matching existing test structure.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (20 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-pr-checks.yaml` | PR, push to main | Unit tests, hermetic integration, E2E, coverage comparison |
| `ci-lint.yaml` | PR, push to main | Go lint, format check, govulncheck |
| `ci-build-images.yaml` | Reusable (called by dev/release) | Build and push container images with Trivy scan |
| `ci-dev.yaml` | Push to main/release-* | Build dev images, push to GHCR |
| `ci-release.yaml` | Tag push, release published | Build release images, push to GHCR |
| `ci-signed-commits.yaml` | PR | Enforce signed commits |
| `check-typos.yaml` | PR, push | Typo checking with crate-ci/typos |
| `md-link-check.yml` | PR, push to main | Markdown link validation with lychee |
| `auto-assign.yaml` | PR opened | Auto-assign reviewers from OWNERS |
| `pr-kind-label.yaml` | PR | Label kind-based PR categories |
| `pr-size-labeler.yml` | PR opened/synced | Size labels (XS-XXL) |
| `non-main-gatekeeper.yml` | PR | Label non-main PRs with hold |
| `prow-github.yml` | Issue comment | Prow-style commands (/assign, /lgtm, etc.) |
| `prow-pr-automerge.yml` | PR labeled, scheduled | Auto-merge on LGTM |
| `prow-pr-remove-lgtm.yml` | PR events | Prow PR checks |
| `re-run-action.yml` | Issue comment | Re-run PR tests via comment |
| `release-notes-*.yaml` | Various | Release notes automation |
| `stale.yaml` / `unstale.yaml` | Scheduled | Stale issue management |

**Strengths**:
- Excellent concurrency control with `cancel-in-progress: true` on all PR workflows
- Smart path filtering via `dorny/paths-filter` — tests only run when Go/Docker/Makefile files change
- Go module and build cache persisted across runs (`actions/cache@v5`)
- Prow-style PR management commands
- Signed commit enforcement
- Typo and link checking

**Gaps**:
- No container image build/scan on PR (only on push to main and releases)
- No CodeQL/SAST workflow

### Test Coverage

**Unit Tests** (8.5/10):
- **219 test files** across the codebase (0.68 test-to-source ratio — excellent)
- Framework: Go standard `testing` + `github.com/stretchr/testify` + `github.com/onsi/ginkgo/v2` + `github.com/onsi/gomega`
- Race detection enabled (`-race` flag)
- Coverage profiling per component (`-coverprofile`)
- Separate test packages for EPP and sidecar
- Comprehensive plugin testing (scorers, filters, pickers, profile handlers, parsers)
- Benchmarks for tokenizer profiling

**Integration Tests** (8.0/10):
- **Hermetic integration tests** using `envtest` (controller-runtime) — no real cluster required
- **Cluster integration tests** for K8s datasource, data layer, runtime polling/notification
- Test harness with common test utilities (`test/integration/epp/harness.go`)
- Coverage profiling for integration tests
- Well-known config smoke tests

**E2E Tests** (8.0/10):
- Two E2E suites: GAIE E2E (`test/e2e/epp/`) and main E2E (`test/e2e/`)
- Kind cluster provisioned automatically for E2E tests
- vLLM simulator used for deterministic testing
- Tests cover: requests, configs, disruption scenarios, setup
- Sidecar has its own E2E suite (`test/sidecar/e2e/`)
- Builder container pattern ensures reproducible test environments

**Coverage Tracking** (7.5/10):
- Per-component coverage output (`coverage/epp.out`, `coverage/sidecar.out`)
- Custom `compare-coverage.sh` script compares PR coverage against main baseline
- Coverage comparison also runs against latest release branch
- Coverage published as GitHub Step Summary
- Coverage artifacts uploaded for release branches (400-day retention)
- HTML coverage reports available via `make coverage-report`
- **Gap**: No Codecov/Coveralls integration for historical trends or PR-level enforcement

### Code Quality

**Linting** (9/10):
- golangci-lint v2 with **24 linters enabled**:
  - `importas`, `bodyclose`, `copyloopvar`, `dupword`, `durationcheck`, `errcheck`, `fatcontext`, `ginkgolinter`, `goconst`, `gocritic`, `govet`, `ineffassign`, `loggercheck`, `makezero`, `misspell`, `nakedret`, `nilnil`, `perfsprint`, `prealloc`, `revive`, `staticcheck`, `unparam`, `unused`, `unconvert`
- Formatters: `goimports`, `gofmt`
- Custom import alias enforcement for internal packages
- Detailed revive rules for Go best practices
- `typos` checker for spelling errors
- `govulncheck` for known vulnerability detection
- `make lint` runs inside builder container for reproducibility

**Pre-commit Hooks** (6/10):
- Hooks exist at `hooks/pre-commit` (runs lint + test)
- `make install-hooks` target available
- **Not auto-installed** — requires manual `git config core.hooksPath hooks`

**Static Analysis** (7/10):
- `govulncheck` runs in CI (lint workflow) — good
- No CodeQL or dedicated SAST tool
- No Semgrep or gosec

### Build Integration

**PR Build Validation** (7.0/10):
- `make build` runs as part of lint workflow — validates compilation
- `make test-e2e` builds images and deploys to Kind cluster on PRs
- Konflux builds run via Tekton PipelineRuns on both PR and push events
- Separate Konflux configs for EPP and sidecar images
- Both community (distroless) and RHOAI (UBI9) Dockerfiles maintained

**Konflux/Tekton Integration**:
- 4 Tekton PipelineRuns in `.tekton/`:
  - `llm-d-inference-scheduler-pull-request.yaml` — PR build for EPP
  - `llm-d-inference-scheduler-push.yaml` — Push build for EPP
  - `odh-llm-d-routing-sidecar-pull-request.yaml` — PR build for sidecar
  - `odh-llm-d-routing-sidecar-push.yaml` — Push build for sidecar
- Uses centralized `odh-konflux-central` pipeline for multi-arch builds
- Separate images: `quay.io/opendatahub/llm-d-inference-scheduler` and `quay.io/opendatahub/llm-d-routing-sidecar`

### Container Images

**Dockerfiles** (6.5/10):
- **5 Dockerfiles**: `Dockerfile.epp`, `Dockerfile.sidecar`, `Dockerfile.epp.konflux`, `Dockerfile.sidecar.konflux`, `Dockerfile.builder`
- Multi-stage builds (build + runtime)
- Community images use `distroless/static:nonroot` base — minimal CVE surface
- RHOAI images use `ubi9/go-toolset` builder + `ubi9/ubi-minimal` runtime
- Non-root user (`65532:65532`)
- Build arguments for customizable base images (`BASE_IMAGE` override)
- Platform support via `BUILDPLATFORM`, `TARGETOS`, `TARGETARCH`
- FIPS-compatible builds for RHOAI sidecar (`-tags strictfipsruntime`)

**Builder Image**:
- Comprehensive builder container (`Dockerfile.builder`) with all tools pre-installed
- Includes: Go 1.25, golangci-lint, kubectl, kustomize, kind, typos, envtest, govulncheck, docker CLI + buildx, podman
- Ensures reproducible builds across developer machines and CI

**Security Scanning**:
- Trivy scanning via composite action on release/dev builds
- SARIF output uploaded to GitHub Security tab
- HIGH/CRITICAL severity threshold with exit-code 1 (fails build)
- **Gap**: Not run on PR builds

**Missing**:
- No SBOM generation
- No image signing/attestation (cosign, sigstore)
- No image startup validation test in CI

### Security Practices

| Practice | Status |
|----------|--------|
| Trivy vulnerability scanning | On release builds only |
| govulncheck | On every PR (lint workflow) |
| Signed commits | Enforced via CI workflow |
| DCO sign-off | Required (AGENTS.md + scripts) |
| Non-root containers | Yes (65532:65532) |
| Distroless base images | Yes (community images) |
| CodeQL/SAST | Not configured |
| Secret detection | Not configured |
| Dependency scanning | Via govulncheck |
| SBOM | Not configured |

### Agent Rules (Agentic Flow Quality)

**Status**: Present (AGENTS.md) — no `.claude/rules/` directory

**AGENTS.md Quality** (8/10):
- Clear description of project architecture and purpose
- Specific coding style guidelines (terse comments, no emojis, no temporal framing)
- Pull request discipline (minimalism, issue-tracking, no unrelated changes)
- Git workflow requirements (DCO sign-off, signed commits, imperative subject)
- Agent operating rules with clear allowed/ask-first/never categories
- Points to `make presubmit` as the pre-merge gate
- References `docs/architecture.md` for plugin model understanding

**Gaps**:
- No `.claude/rules/` directory for test-specific patterns
- No per-test-type guidance (unit vs integration vs E2E patterns)
- No Ginkgo/Gomega test template or example rules
- No envtest setup patterns for hermetic integration tests
- Gemini has `.gemini/settings.json` but no detailed rules

## Recommendations

### Priority 0 (Critical)

1. **Add Trivy container scanning to PR workflow** — The `trivy-scan` composite action already exists. Add a `security-scan` job to `ci-pr-checks.yaml` that builds and scans both EPP and sidecar images. This is a 2-3 hour task that closes the biggest security gap.

2. **Add CodeQL or gosec SAST scanning** — Create a dedicated `.github/workflows/codeql.yml` workflow. GitHub provides free CodeQL analysis for public repos. This catches code-level security issues that govulncheck and golangci-lint miss.

### Priority 1 (High Value)

3. **Integrate Codecov for coverage tracking** — The project already generates `.out` coverage files. Adding `codecov/codecov-action` to the PR workflow would provide historical trends, PR comments with line-level diffs, and configurable coverage ratchets. Create a `.codecov.yml` with component-level coverage targets.

4. **Create `.claude/rules/` for test automation guidance** — The project has excellent test patterns but no rules to guide AI code generation. Create rules for:
   - `unit-tests.md`: Go testing + testify patterns, table-driven tests, race detection
   - `integration-tests.md`: envtest setup, hermetic integration patterns, harness usage
   - `e2e-tests.md`: Ginkgo/Gomega E2E patterns, Kind cluster setup, vLLM simulator usage
   - `plugin-tests.md`: Scorer, filter, picker test patterns matching existing plugin tests

5. **Make pre-commit hooks auto-install** — Add a `make setup` or `make dev-setup` target that installs hooks automatically. Or add a Makefile guard that warns if hooks are not installed.

### Priority 2 (Nice-to-Have)

6. **Add SBOM generation** — Use `syft` or `trivy` to generate SBOMs during container builds. Important for supply chain security compliance.

7. **Add container image signing** — Integrate `cosign` for image signing and attestation. Particularly important for RHOAI images.

8. **Add performance regression testing** — The tokenizer benchmark exists but only runs manually. Create a CI job that runs benchmarks and compares against baseline to detect performance regressions.

## Comparison to Gold Standards

| Dimension | llm-d-inference-scheduler | odh-dashboard | notebooks | kserve |
|-----------|---------------------------|---------------|-----------|--------|
| Unit Tests | 8.5 - Extensive with race detection | 9.0 - Multi-layer | 7.0 | 9.0 - Coverage enforcement |
| Integration/E2E | 8.0 - Hermetic + Kind E2E | 9.0 - Contract tests | 7.0 | 9.0 - Multi-version |
| Build Integration | 7.0 - Konflux via Tekton | 7.0 | 8.0 | 7.0 |
| Image Testing | 6.5 - Trivy on release only | 7.0 | 9.0 - 5-layer validation | 7.0 |
| Coverage Tracking | 7.5 - Custom comparison script | 9.0 - Codecov | 6.0 | 9.0 - Enforcement |
| CI/CD Automation | 8.5 - Excellent path filtering | 9.0 | 8.0 | 8.0 |
| Agent Rules | 8.0 - AGENTS.md, no .claude/rules/ | 9.0 - Full rules | 5.0 | 6.0 |

## File Paths Reference

### CI/CD
- `.github/workflows/ci-pr-checks.yaml` — Main PR gate (unit, integration, E2E)
- `.github/workflows/ci-lint.yaml` — Lint, format, govulncheck
- `.github/workflows/ci-build-images.yaml` — Reusable image build workflow
- `.github/workflows/ci-dev.yaml` — Dev image builds on push
- `.github/workflows/ci-release.yaml` — Release image builds
- `.github/workflows/ci-signed-commits.yaml` — Signed commit enforcement
- `.github/actions/trivy-scan/action.yaml` — Trivy scanning composite action
- `.github/actions/docker-build-and-push/action.yml` — Docker build composite action

### Testing
- `pkg/**/*_test.go` — Unit tests (co-located with source)
- `test/integration/` — Integration tests (hermetic + cluster)
- `test/e2e/` — Main E2E test suite
- `test/e2e/epp/` — GAIE E2E test suite
- `test/sidecar/e2e/` — Sidecar E2E tests
- `test/profiling/tokenizerbench/` — Benchmark tests
- `test/testdata/` — Test fixtures and manifests
- `test/utils/` — Shared test utilities

### Code Quality
- `.golangci.yml` — 24 linters enabled with custom rules
- `.typos.toml` — Typo checker config
- `.lychee.toml` — Link checker config
- `hooks/pre-commit` — Git pre-commit hook

### Container Images
- `Dockerfile.epp` — Community EPP image (distroless)
- `Dockerfile.sidecar` — Community sidecar image (distroless)
- `Dockerfile.epp.konflux` — RHOAI EPP image (UBI9)
- `Dockerfile.sidecar.konflux` — RHOAI sidecar image (UBI9)
- `Dockerfile.builder` — Builder container with all tools
- `.tekton/` — Konflux/Tekton pipeline configurations

### Agent Rules
- `AGENTS.md` — Comprehensive agent operating rules
- `CLAUDE.md` — Duplicate of AGENTS.md content
- `.gemini/settings.json` — Gemini agent config

### Build System
- `Makefile` — Primary build system with containerized targets
- `Makefile.tools.mk` — Tool dependency management
- `Makefile.cluster.mk` — Cluster-specific targets
- `Makefile.kind.mk` — Kind development environment
- `Makefile.gen.mk` — Code generation targets
- `scripts/compare-coverage.sh` — Coverage comparison script
- `hack/test-e2e.sh` — E2E test runner
