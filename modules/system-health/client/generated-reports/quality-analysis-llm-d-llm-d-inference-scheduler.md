---
repository: "llm-d/llm-d-inference-scheduler"
overall_score: 8.7
scorecard:
  - dimension: "Unit Tests"
    score: 9.0
    status: "Exceptional — 1.19 test-to-code ratio (65,924 test LOC vs 55,423 source), 218 test files covering all packages with race detection and benchmarks"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Hermetic envtest + full-cluster integration + multi-suite E2E (GAIE traffic/metrics, router PD/shared-storage/disruption) on Kind clusters"
  - dimension: "Build Integration"
    score: 8.0
    status: "PR-time image builds, builder container, Helm chart validation, E2E image deployment — no Konflux simulation"
  - dimension: "Image Testing"
    score: 8.0
    status: "Multi-stage distroless builds, multi-arch (AMD64/ARM64), Trivy scanning with severity gate, SARIF upload — no SBOM"
  - dimension: "Coverage Tracking"
    score: 8.0
    status: "Custom coverage comparison against main/release baselines with PR regression detection — threshold currently 0 (report-only)"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "21 workflows with concurrency control, path filtering, Go caching, presubmit gate, Prow integration, release automation"
  - dimension: "Agent Rules"
    score: 4.0
    status: "AGENTS.md with solid coding/PR guidelines — no .claude/rules/ directory or test-specific creation rules"
critical_gaps:
  - title: "No SAST/CodeQL integration"
    impact: "Static analysis for security vulnerabilities (injection, buffer overflows, crypto weaknesses) not automated — relies solely on linting"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No secret detection tooling"
    impact: "No gitleaks/TruffleHog — accidental credential commits could go unnoticed until dependency review catches downstream effects"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "Coverage threshold set to 0"
    impact: "Coverage regression detection works, but no minimum floor enforced — a component could drop to 10% and only the delta matters"
    severity: "MEDIUM"
    effort: "30 minutes"
  - title: "No test-specific agent rules (.claude/rules/)"
    impact: "AI-generated tests lack project-specific guidance on test patterns, fixtures, test utilities (testutil, igwtestutils), and framework conventions (Ginkgo/Gomega)"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add CodeQL/SAST scanning workflow"
    effort: "2-4 hours"
    impact: "Automated static security analysis catching vulnerability patterns Go linters miss"
  - title: "Add gitleaks for secret detection"
    effort: "1-2 hours"
    impact: "Pre-commit and CI-time detection of accidentally committed credentials"
  - title: "Set COVERAGE_THRESHOLD to a meaningful floor (e.g. 50%)"
    effort: "30 minutes"
    impact: "Prevent silent coverage erosion below an acceptable minimum"
  - title: "Generate .claude/rules/ with test creation guidelines"
    effort: "2-3 hours"
    impact: "Consistent AI-generated tests following project conventions (Ginkgo/Gomega, table-driven, testutil wrappers)"
  - title: "Add SBOM generation to image builds"
    effort: "1-2 hours"
    impact: "Supply chain transparency and compliance readiness"
recommendations:
  priority_0:
    - "Add CodeQL or Semgrep SAST scanning to PR workflows"
    - "Add gitleaks secret detection to pre-commit hooks and CI"
  priority_1:
    - "Set coverage threshold > 0 to enforce minimum coverage floor per component"
    - "Create .claude/rules/ with test creation rules for unit, integration, and E2E patterns"
    - "Add SBOM generation (syft/cosign) to image build pipeline"
  priority_2:
    - "Add image signing/attestation with cosign for supply chain security"
    - "Add fuzz testing for parsing code (OpenAI, Anthropic, vLLM parsers)"
    - "Consider adding contract tests for the plugin interface boundaries"
---

# Quality Analysis: llm-d-inference-scheduler

## Executive Summary

- **Overall Score: 8.7/10**
- **Repository Type**: Go service — Kubernetes-native LLM inference request router (Endpoint Picker + disaggregated sidecar)
- **Module**: `github.com/llm-d/llm-d-router`
- **Primary Language**: Go 1.25
- **Key Strengths**: Exceptional test coverage (more test code than source code), comprehensive multi-layer E2E testing with Kind clusters, strong CI/CD automation with 21 workflows, sophisticated coverage regression detection, well-configured linting with 24+ linters, Trivy security scanning on all images
- **Critical Gaps**: No SAST/CodeQL, no secret detection, coverage threshold at 0, no test-specific agent rules
- **Agent Rules Status**: Present (AGENTS.md) but Incomplete — no `.claude/rules/` directory with test creation guidance

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.0/10 | Exceptional — 1.19 test-to-code ratio, 218 test files, race detection, benchmarks |
| Integration/E2E | 9.0/10 | Hermetic envtest + full-cluster + multi-suite Kind E2E (8 matrix configurations) |
| **Build Integration** | **8.0/10** | **PR-time image builds, builder container, Helm validation — no Konflux simulation** |
| Image Testing | 8.0/10 | Multi-stage distroless, multi-arch, Trivy gate — no SBOM generation |
| Coverage Tracking | 8.0/10 | Custom baseline comparison, PR regression detection — threshold at 0 |
| CI/CD Automation | 9.5/10 | 21 workflows, concurrency control, path filtering, Prow integration |
| Agent Rules | 4.0/10 | AGENTS.md with coding guidelines — no test-specific rules |

## Critical Gaps

### 1. No SAST/CodeQL Integration
- **Impact**: Static analysis for security vulnerability patterns (injection, crypto weaknesses, unsafe operations) is not automated. The project relies on golangci-lint's security-adjacent checks (errcheck, gocritic) but these don't cover the depth of dedicated SAST tools.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Recommendation**: Add GitHub CodeQL or Semgrep to PR workflows

### 2. No Secret Detection Tooling
- **Impact**: No gitleaks, TruffleHog, or equivalent. Accidental credential commits in a multi-contributor open-source project could go unnoticed.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Recommendation**: Add gitleaks to pre-commit hooks and CI

### 3. Coverage Threshold Set to 0 (Report-Only)
- **Impact**: The sophisticated coverage comparison system detects regressions (delta), but no minimum floor is enforced. A component could theoretically drop to very low coverage as long as the delta stays within the 2.0pp tolerance.
- **Severity**: MEDIUM
- **Effort**: 30 minutes
- **Recommendation**: Set `COVERAGE_THRESHOLD` to a meaningful floor (50-60%)

### 4. No Test-Specific Agent Rules
- **Impact**: AI-assisted development lacks project-specific guidance on test patterns, framework conventions (Ginkgo/Gomega vs standard testing), test utility usage (`testutil`, `igwtestutils`), and test data management patterns.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Recommendation**: Create `.claude/rules/` with unit, integration, and E2E test creation rules

## Quick Wins

### 1. Add CodeQL/SAST Scanning
- **Effort**: 2-4 hours
- **Impact**: Automated security vulnerability detection beyond linting
- **Implementation**: Add `.github/workflows/codeql.yml`:
```yaml
name: CodeQL
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: github/codeql-action/init@v4
        with:
          languages: go
      - uses: github/codeql-action/autobuild@v4
      - uses: github/codeql-action/analyze@v4
```

### 2. Add Gitleaks Secret Detection
- **Effort**: 1-2 hours
- **Impact**: Prevent accidental credential exposure
- **Implementation**: Add to pre-commit hooks and CI workflow

### 3. Set Coverage Threshold
- **Effort**: 30 minutes
- **Impact**: Prevent silent coverage erosion
- **Implementation**: Change `COVERAGE_THRESHOLD ?= 0` to `COVERAGE_THRESHOLD ?= 50` in Makefile

### 4. Generate Test Creation Agent Rules
- **Effort**: 2-3 hours
- **Impact**: Consistent AI-generated tests
- **Implementation**: Use `/test-rules-generator` to create `.claude/rules/` with patterns from existing tests

### 5. Add SBOM Generation
- **Effort**: 1-2 hours
- **Impact**: Supply chain transparency
- **Implementation**: Add syft/cosign step to `ci-build-images.yaml`

## Detailed Findings

### CI/CD Pipeline

**Outstanding.** 21 workflows covering the full development lifecycle:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-pr-checks.yaml` | PR + push to main | Unit tests, hermetic integration, coverage comparison, 8-matrix E2E |
| `ci-lint.yaml` | PR + push | Build verification, golangci-lint, govulncheck |
| `ci-dev.yaml` | Push to main/release | Dev image build and push |
| `ci-build-images.yaml` | Reusable | Image build with Trivy scan gate |
| `ci-dependency-review.yaml` | PR | Dependency review (fail on HIGH) |
| `ci-signed-commits.yaml` | PR | Signed commit enforcement |
| `check-typos.yaml` | PR + push | Typos checker |
| `md-link-check.yml` | PR + push | Markdown link validation |
| `prow-*.yml` | Various | Prow bot integration (automerge, LGTM) |
| `auto-assign.yaml` | PR | Reviewer auto-assignment |
| `release-notes-*.yaml` | Various | Automated release notes |
| `stale.yaml` / `unstale.yaml` | Scheduled | Issue/PR staleness management |

**Strengths:**
- Concurrency groups with `cancel-in-progress: true` on all PR workflows
- Path filtering via `dorny/paths-filter` — tests only run when source changes
- Go module and build caching with `actions/cache`
- Builder container approach — consistent tooling across local and CI
- `make presubmit` gate with branch check, signed-commits check, go-mod check, format, lint, vulncheck

**E2E Test Matrix (8 configurations on PR):**
- GAIE: traffic, metrics
- Router: pd, pd-shared-storage-deprecated, pd-shared-storage-disagg, pd-metrics, extended, disruption

### Test Coverage

**Exceptional.** More test code than source code.

| Metric | Value |
|--------|-------|
| Source files (.go) | 359 |
| Test files (_test.go) | 218 |
| Source LOC | 55,423 |
| Test LOC | 65,924 |
| Test-to-code ratio (LOC) | **1.19** |
| Test-to-code ratio (files) | 0.61 |

**Unit Tests (pkg/):**
- EPP: scheduler, scheduling plugins (14 scorer types, 3 filter types, 4 profile handlers), request handlers, server, datastore, config loader, flow control (controller, eviction, registry, fairness, ordering), metrics, metadata, data layer
- Sidecar: proxy, connectors (nixl, sglang, epd, shared-storage), decode, allowlist, chat completions, data parallel, cached tokens usage rewriter
- Common: certs, envoy, error, logging, routing

**Integration Tests:**
- Hermetic (envtest-based, no cluster): datalayer, grpc, hermetic, k8s datasource, runtime polling/notification, request attribute reporter, config smoke, well-known configs
- Cluster-requiring: full integration suite with test utilities

**E2E Tests:**
- GAIE suite: `test/e2e/` — traffic routing, configs, disruption, metrics, leader election (811 LOC e2e_test.go)
- Router/sidecar suite: `test/e2e/epp/` — endpoint picker E2E, `test/sidecar/e2e/` — sidecar E2E
- Kind cluster provisioning, image loading, namespace isolation

**Benchmarks:** Tokenizer benchmarks (`test/profiling/tokenizerbench/`), scheduler benchmarks (`scheduler_bench_test.go`)

**Coverage Tracking:**
- Custom `scripts/compare-coverage.sh` — compares coverage profiles against main and release baselines
- Per-component coverage profiles: `epp.out`, `sidecar.out`, `integration.out`, `integration-hermetic.out`
- PR-time regression detection with markdown summary in GitHub Actions
- Main branch baseline cached for comparison
- Release branch baselines stored as artifacts (400-day retention)
- Configurable regression tolerance (default 2.0pp)

### Code Quality

**Strong.** Comprehensive linting and quality tooling.

**golangci-lint v2** (`.golangci.yml`) — 24+ linters enabled:
- Code correctness: errcheck, govet, staticcheck, unused, ineffassign, unconvert
- Performance: prealloc, perfsprint
- Style: revive (17 rules), importas (custom aliases), goconst, nakedret
- Testing: ginkgolinter
- Bug detection: copyloopvar, dupword, durationcheck, fatcontext, makezero, nilnil, bodyclose, unparam
- Formatters: goimports, gofmt
- Zero tolerance: max-issues-per-linter=0, max-same-issues=0

**Additional quality tools:**
- `typos` (crate-ci/typos v1.46.3) — spell checker with custom dictionary
- `govulncheck` — Go vulnerability checker (run on PRs + presubmit)
- `go mod tidy -diff` — Verify clean dependencies
- Markdown link checker (lychee)
- Local pre-commit hooks (`hooks/pre-commit` — runs lint + test)

### Container Images

**Well-designed.** Three Dockerfiles with security-conscious defaults:

| Image | Dockerfile | Purpose |
|-------|-----------|---------|
| EPP | `Dockerfile.epp` | Endpoint picker service |
| Sidecar | `Dockerfile.sidecar` | Disaggregated inference sidecar |
| Builder | `Dockerfile.builder` | CI/development tooling container |

**Security features:**
- Base image: `gcr.io/distroless/static:nonroot` (minimal CVE surface)
- Non-root user: `65532:65532`
- Overridable base image via `BASE_IMAGE` build arg (e.g., UBI for Red Hat builds)
- Multi-stage builds — only binary copied to runtime stage
- Stripped binaries (ldflags `-s -w`)

**Multi-architecture:** AMD64 + ARM64 via Docker buildx with `BUILDPLATFORM`/`TARGETARCH`

**Trivy scanning:** Custom `.github/actions/trivy-scan/` action:
- Scans every image before push
- Severity gate: HIGH,CRITICAL (exit-code 1)
- SARIF output uploaded to GitHub Security tab
- Configurable severity threshold

### Security Practices

| Practice | Status | Notes |
|----------|--------|-------|
| Container scanning (Trivy) | ✅ Present | HIGH/CRITICAL gate on all images |
| Dependency review | ✅ Present | actions/dependency-review-action, fail on high |
| govulncheck | ✅ Present | On PRs and presubmit |
| Signed commits | ✅ Present | 1Password/check-signed-commits-action |
| Non-root containers | ✅ Present | distroless/static:nonroot |
| SAST/CodeQL | ❌ Missing | No static security analysis |
| Secret detection | ❌ Missing | No gitleaks/TruffleHog |
| SBOM generation | ❌ Missing | No syft/cosign |
| Image signing | ❌ Missing | No cosign attestation |

### Agent Rules (Agentic Flow Quality)

- **Status**: Present but Incomplete
- **AGENTS.md**: Comprehensive coding guidelines covering:
  - Working in the codebase (verify behavior, read analogous code, define checkable outcomes)
  - Pull request practices (minimalism, issue tracking, scope control)
  - Code style (standard Go, terse comments, no emojis)
  - Git workflow (DCO sign-off, no co-author trailers)
  - Operating rules (allowed/ask-first/never actions)
- **CLAUDE.md**: Symlink to AGENTS.md
- **`.claude/` directory**: Not present
- **`.claude/rules/`**: Not present
- **Test creation guidance**: None — no framework-specific patterns for unit tests (table-driven Go), Ginkgo/Gomega integration tests, or Kind-based E2E tests

**Coverage gaps in agent rules:**
- No unit test creation rules (patterns for table-driven tests, mocking strategies, testutil usage)
- No integration test rules (envtest setup, hermetic patterns, test harness usage)
- No E2E test rules (Kind cluster setup, label-based filtering, test data management)
- No plugin test rules (filter/scorer/profile handler test patterns)

## Recommendations

### Priority 0 (Critical)
1. **Add CodeQL or Semgrep SAST scanning** — Static security analysis covering injection, crypto, and unsafe operations that linting doesn't catch
2. **Add gitleaks secret detection** — Essential for an open-source multi-contributor project

### Priority 1 (High Value)
3. **Set coverage threshold > 0** — Change `COVERAGE_THRESHOLD ?= 0` to enforce a minimum floor per component
4. **Create `.claude/rules/` with test creation rules** — Use `/test-rules-generator` to generate framework-specific guidance from existing test patterns
5. **Add SBOM generation** — Supply chain transparency with syft integrated into the build pipeline

### Priority 2 (Nice-to-Have)
6. **Add image signing/attestation** — cosign for supply chain provenance
7. **Add fuzz testing** — For parsing code (OpenAI, Anthropic, vLLM, Vertex AI parsers in `pkg/epp/framework/plugins/requesthandling/parsers/`)
8. **Add contract tests** — For plugin interface boundaries (scheduler, flow control, data layer)
9. **Consider pre-commit hooks via `.pre-commit-config.yaml`** — Standardize hook installation (currently custom `hooks/pre-commit` with manual `make install-hooks`)

## Comparison to Gold Standards

| Dimension | llm-d-inference-scheduler | odh-dashboard | notebooks | kserve |
|-----------|--------------------------|---------------|-----------|--------|
| Test-to-code ratio | **1.19** (exceptional) | ~0.8 | ~0.5 | ~0.7 |
| Unit test framework | Go testing + Ginkgo/Gomega | Jest + RTL | pytest | Go testing |
| Integration tests | Hermetic envtest + cluster | Cypress | Image validation | envtest |
| E2E tests | 8-matrix Kind suites | Multi-browser | Multi-platform | Multi-version |
| Coverage tracking | Custom baseline comparison | Codecov | Manual | Codecov |
| Coverage enforcement | PR regression gate | PR threshold | None | PR threshold |
| Container scanning | Trivy (HIGH/CRITICAL) | None | Trivy | Trivy |
| SAST/CodeQL | ❌ Missing | ❌ Missing | ❌ Missing | ✅ Present |
| Secret detection | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing |
| Agent rules | AGENTS.md (no test rules) | Full .claude/rules/ | None | None |
| Linting depth | 24+ linters | ESLint + Stylelint | flake8 | golangci-lint |
| Pre-commit hooks | Custom (hooks/) | .pre-commit-config | None | None |
| Multi-arch images | ✅ AMD64/ARM64 | ❌ AMD64 only | ✅ Multi-arch | ✅ Multi-arch |
| Signed commits | ✅ Enforced | ❌ Not enforced | ❌ Not enforced | ❌ Not enforced |

## File Paths Reference

### CI/CD
- `.github/workflows/ci-pr-checks.yaml` — Main PR gate (tests, coverage, E2E)
- `.github/workflows/ci-lint.yaml` — Linting and build verification
- `.github/workflows/ci-build-images.yaml` — Image build with Trivy gate
- `.github/workflows/ci-dev.yaml` — Dev image builds
- `.github/workflows/ci-dependency-review.yaml` — Dependency scanning
- `.github/workflows/ci-signed-commits.yaml` — Signed commit enforcement
- `.github/actions/trivy-scan/action.yml` — Custom Trivy scan action
- `.github/actions/docker-build-and-push/action.yml` — Image build action
- `Makefile` — Primary build system (+ Makefile.tools.mk, Makefile.cluster.mk, Makefile.kind.mk, Makefile.gen.mk)

### Testing
- `pkg/**/*_test.go` — Unit tests (187 files in pkg/)
- `test/integration/` — Integration tests (hermetic + cluster)
- `test/e2e/` — GAIE E2E tests
- `test/e2e/epp/` — EPP-specific E2E tests
- `test/sidecar/e2e/` — Sidecar E2E tests
- `test/profiling/tokenizerbench/` — Tokenizer benchmarks
- `test/testdata/` — Shared test data (YAML manifests)
- `scripts/compare-coverage.sh` — Coverage comparison tool

### Code Quality
- `.golangci.yml` — golangci-lint configuration (24+ linters)
- `.typos.toml` — Typos checker configuration
- `hooks/pre-commit` — Local pre-commit hook

### Container Images
- `Dockerfile.epp` — EPP image (distroless, multi-arch)
- `Dockerfile.sidecar` — Sidecar image
- `Dockerfile.builder` — Builder container with all CI tools

### Agent Rules
- `AGENTS.md` — Agent coding guidelines
- `CLAUDE.md` — Symlink to AGENTS.md
