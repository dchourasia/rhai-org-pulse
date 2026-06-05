---
repository: "red-hat-data-services/blackbox_exporter"
overall_score: 4.1
scorecard:
  - dimension: "Unit Tests"
    score: 6.0
    status: "Good prober coverage (58 tests, 0.58 ratio) but ICMP prober entirely untested"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "IPv6 testing via CircleCI machine executor, but no dedicated integration or E2E suites"
  - dimension: "Build Integration"
    score: 2.0
    status: "No PR-time image build validation; Dockerfile copies pre-built binary only"
  - dimension: "Image Testing"
    score: 1.0
    status: "No container runtime validation, no vulnerability scanning, no SBOM"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No codecov/coveralls integration, no coverage thresholds, no PR reporting"
  - dimension: "CI/CD Automation"
    score: 5.0
    status: "CircleCI for tests/build/publish, GitHub Actions for linting only; outdated toolchain"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules for test automation"
critical_gaps:
  - title: "No coverage tracking or enforcement"
    impact: "Cannot detect coverage regressions; unknown actual test coverage percentage"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "ICMP prober has zero test coverage"
    impact: "376 lines of network-critical code with no automated tests at all"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No container image security scanning"
    impact: "Vulnerable dependencies or base image issues not caught before deployment"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "No PR-time image build or runtime validation"
    impact: "Broken images discovered only at publish time or in production"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Outdated Go toolchain and linter versions"
    impact: "Go 1.18/1.19, golangci-lint v1.45.2 — missing security fixes and linter improvements"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No SAST, secret detection, or dependency vulnerability scanning"
    impact: "Security issues in code and dependencies not caught in CI"
    severity: "HIGH"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Immediate detection of known CVEs in dependencies and container images"
  - title: "Add codecov integration with coverage thresholds"
    effort: "2-3 hours"
    impact: "PR-level coverage visibility and regression prevention"
  - title: "Upgrade Go version and golangci-lint"
    effort: "2-4 hours"
    impact: "Security fixes, performance improvements, and better static analysis"
  - title: "Add GitHub Actions for unit tests (complement CircleCI)"
    effort: "2-3 hours"
    impact: "PR-visible test results, faster feedback loop for contributors"
recommendations:
  priority_0:
    - "Add coverage tracking (codecov/coveralls) with minimum threshold enforcement"
    - "Add container vulnerability scanning (Trivy) to CI pipeline"
    - "Write unit tests for ICMP prober (376 untested lines)"
    - "Add SAST scanning (CodeQL or gosec) to GitHub Actions"
  priority_1:
    - "Upgrade Go toolchain to 1.22+ and golangci-lint to v1.59+"
    - "Add PR-time Docker image build validation"
    - "Add container runtime startup tests"
    - "Create agent rules (.claude/rules/) for test patterns"
    - "Enable more golangci-lint linters beyond staticcheck"
  priority_2:
    - "Add SBOM generation for container images"
    - "Add image signing/attestation"
    - "Implement pre-commit hooks for local development quality"
    - "Add benchmark tests for performance-critical probers"
    - "Consolidate CI from CircleCI to GitHub Actions"
---

# Quality Analysis: blackbox_exporter

## Executive Summary

- **Overall Score: 4.1/10**
- **Repository**: [red-hat-data-services/blackbox_exporter](https://github.com/red-hat-data-services/blackbox_exporter) (fork of prometheus/blackbox_exporter)
- **Type**: Go CLI / Prometheus Exporter
- **Language**: Go 1.18-1.19 (outdated)
- **Default Branch**: master

### Key Strengths
- Solid unit test suite for core probers (HTTP, TCP, DNS, gRPC) with 58 test functions
- Table-driven test patterns in HTTP and config tests
- Dedicated IPv6 test job using CircleCI machine executor
- Multi-architecture Docker build support (amd64, armv7, arm64, ppc64le)
- yamllint configuration for YAML validation
- Dependabot configured for Go module updates

### Critical Gaps
- **Zero coverage tracking** — no codecov, no thresholds, no PR-level visibility
- **ICMP prober entirely untested** — 376 lines with no `icmp_test.go`
- **No security scanning** — no Trivy, no CodeQL, no secret detection, no dependency scanning
- **No container image testing** — Dockerfile copies pre-built binary, no runtime validation
- **Outdated toolchain** — Go 1.18/1.19, golangci-lint v1.45.2 with only `staticcheck` enabled
- **No agent rules** — no CLAUDE.md or `.claude/` directory

### Agent Rules Status: Missing
No agent rules exist. No `.claude/` directory, no `CLAUDE.md`, no test automation guidance for AI agents.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6.0/10 | Good prober coverage (58 tests, 0.58 ratio) but ICMP entirely untested |
| Integration/E2E | 3.0/10 | IPv6 testing via CircleCI machine executor, no dedicated suites |
| **Build Integration** | **2.0/10** | **No PR-time image build; Dockerfile copies pre-built binary** |
| Image Testing | 1.0/10 | No runtime validation, no vulnerability scanning, no SBOM |
| Coverage Tracking | 1.0/10 | No codecov, no thresholds, no PR reporting |
| CI/CD Automation | 5.0/10 | CircleCI + GitHub Actions linting, outdated toolchain versions |
| Agent Rules | 0.0/10 | No agent rules, no .claude/ directory |

## Critical Gaps

### 1. No Coverage Tracking or Enforcement
- **Impact**: Cannot detect coverage regressions; unknown actual test coverage percentage
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No `codecov.yml`, no `.coveragerc`, no coverage generation flags in Makefile. The `make test` target runs tests with `-race` but does not generate coverage profiles.

### 2. ICMP Prober Has Zero Test Coverage
- **Impact**: 376 lines of network-critical code with no automated tests
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: `prober/icmp.go` (376 lines) has no corresponding `prober/icmp_test.go`. This is the most complex prober (raw socket operations, platform-specific behavior) and is completely untested. Every other prober (HTTP, TCP, DNS, gRPC) has comprehensive tests.

### 3. No Container Image Security Scanning
- **Impact**: Vulnerable dependencies or base image issues not caught before deployment
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: No Trivy, Snyk, or any container scanning tool in CI. The Dockerfile uses `quay.io/prometheus/busybox-${OS}-${ARCH}:latest` as base — vulnerabilities in this base image would go undetected.

### 4. No PR-Time Image Build or Runtime Validation
- **Impact**: Broken images discovered only at publish time or in production
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The Dockerfile is a simple COPY of a pre-built binary — no multi-stage build, no health checks, no startup tests. PR workflows do not build or test the container image.

### 5. Outdated Go Toolchain and Linter Versions
- **Impact**: Missing security fixes, linter improvements, and language features
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: 
  - `go.mod`: Go 1.18
  - `.promu.yml` / `.circleci/config.yml`: Go 1.19
  - `golangci-lint`: v1.45.2 (current is v1.59+)
  - Only `staticcheck` linter enabled out of 100+ available linters

### 6. No SAST, Secret Detection, or Dependency Vulnerability Scanning
- **Impact**: Security issues in code and dependencies not caught in CI
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No CodeQL, no gosec, no Gitleaks, no dependency vulnerability alerts configured in CI. Dependabot is set to monthly `gomod` updates only — it does not scan for CVEs.

## Quick Wins

### 1. Add Trivy Scanning to PR Workflow (1-2 hours)
Early detection of known CVEs in dependencies and container images.

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [pull_request]
jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
```

### 2. Add Codecov Integration (2-3 hours)
PR-level coverage visibility and regression prevention.

```yaml
# Add to CircleCI test job
- run: |
    go test -race -coverprofile=coverage.txt -covermode=atomic ./...
    bash <(curl -s https://codecov.io/bash)
```

### 3. Upgrade Go Version and golangci-lint (2-4 hours)
Security fixes, performance improvements, and better static analysis.

```yaml
# .golangci.yml - enable more linters
linters:
  enable:
    - staticcheck
    - govet
    - errcheck
    - gosimple
    - ineffassign
    - unused
    - gosec
    - gocritic
```

### 4. Add GitHub Actions for Unit Tests (2-3 hours)
PR-visible test results, faster feedback for contributors.

```yaml
# .github/workflows/test.yml
name: Tests
on: [pull_request, push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go test -race -coverprofile=coverage.txt ./...
      - uses: codecov/codecov-action@v4
```

## Detailed Findings

### CI/CD Pipeline

**Dual CI System**: The repository uses both CircleCI and GitHub Actions, but in a fragmented way:

| System | Purpose | Triggers |
|--------|---------|----------|
| CircleCI | Tests, IPv6 tests, build, publish | All branches/tags |
| GitHub Actions | golangci-lint only | Push (Go files) + PR |

**CircleCI Workflows**:
- `test`: Runs `make` (which includes style, license check, lint, yamllint, unused package check, build, test)
- `test-ipv6`: Uses machine executor for IPv6 network tests — good practice for a network prober
- `build`: Uses Prometheus orb for cross-platform builds
- `publish_master` / `publish_release`: Automated publishing with proper gating

**GitHub Actions Workflows**:
- Only `golangci-lint.yml` — runs lint on Go file changes and PRs
- Uses outdated actions (`actions/checkout@v3`, `actions/setup-go@v2`)

**Missing CI Features**:
- No concurrency control on workflows
- No caching configuration (Go modules, build artifacts)
- No test result reporting (JUnit XML only in CircleCI)
- No branch protection workflow requirements visible

### Test Coverage

**Test Files**: 9 test files with 3,990 lines of test code

| File | Lines | Test Functions | Pattern |
|------|-------|----------------|---------|
| `prober/http_test.go` | 1,407 | 25 | Table-driven (6 subtests) |
| `prober/tcp_test.go` | 685 | 9 | Individual test functions |
| `prober/dns_test.go` | 657 | 5 | Individual test functions |
| `prober/grpc_test.go` | 416 | 6 | Individual test functions |
| `prober/utils_test.go` | 254 | 1 | Individual test function |
| `config/config_test.go` | 216 | 4 | Table-driven (2 subtests) |
| `prober/handler_test.go` | 205 | 5 | Individual test functions |
| `prober/history_test.go` | 81 | 2 | Individual test functions |
| `main_test.go` | 69 | 1 | Individual test function |

**Test-to-Code Ratio**: 0.58 (3,990 test lines / 6,911 source lines) — moderate

**Test Quality**:
- Uses standard `testing` package (no external test framework)
- Table-driven tests in HTTP and config tests
- Real HTTP server setup (`httptest.NewServer`) for HTTP prober tests
- TLS certificate testing with proper cert generation
- Race detection enabled on amd64 via `-race` flag

**Untested Modules**:
- `prober/icmp.go` (376 lines) — **completely untested**
- `prober/tls.go` (85 lines) — no dedicated tests (partially covered by other prober tests)
- `prober/prober.go` (48 lines) — type definitions, minimal logic

**Test Data**:
- 17 YAML testdata files in `config/testdata/` for config validation testing
- Good coverage of invalid config scenarios (bad regexps, invalid types, mismatches)

### Code Quality

**Linting**: Minimal configuration
- `.golangci.yml`: Only `staticcheck` enabled, all other linters disabled
- `golangci-lint` v1.45.2 (significantly outdated)
- Makefile includes `gofmt`, `go vet`, license check, and yamllint
- `.yamllint` configured with reasonable rules

**Pre-commit Hooks**: None — no `.pre-commit-config.yaml`

**Static Analysis**: No SAST tools (no CodeQL, no gosec, no Semgrep)

**Formatting**: `gofmt` enforced via `make style` target

### Container Images

**Dockerfile Analysis**:
- Simple single-stage: copies pre-built binary from `.build/` directory
- Uses `quay.io/prometheus/busybox-${OS}-${ARCH}:latest` base image
- Supports multi-architecture builds via build args (ARCH, OS)
- Exposes port 9115
- Proper ENTRYPOINT/CMD separation

**Missing Container Practices**:
- No multi-stage build (binary built outside Dockerfile)
- No HEALTHCHECK instruction
- No USER instruction (runs as root)
- No vulnerability scanning
- No SBOM generation
- No image signing or attestation
- No runtime validation tests

### Security

**Current Security Measures**:
- `SECURITY.md` pointing to Prometheus security policy
- Dependabot for monthly Go module updates
- Race detection in tests
- License header checking

**Missing Security Practices**:
- No CodeQL or gosec SAST scanning
- No Gitleaks or TruffleHog for secret detection
- No dependency vulnerability scanning (Dependabot only does updates, not CVE alerts)
- No container image scanning (Trivy, Snyk)
- No supply chain security (SLSA, Sigstore)

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: All test types lack agent rules (unit, integration, e2e)
- **Recommendation**: Generate test rules with `/test-rules-generator` for Go testing patterns specific to this Prometheus exporter

## Recommendations

### Priority 0 (Critical)

1. **Add coverage tracking** — Integrate codecov/coveralls with minimum threshold (e.g., 60%) and PR commenting. Generate coverage profiles in CI.

2. **Add container vulnerability scanning** — Add Trivy filesystem scanning to GitHub Actions. Add container image scanning to the Docker build pipeline.

3. **Write ICMP prober tests** — The ICMP prober is 376 lines of untested network code. Given it handles raw sockets and platform-specific behavior, this is a significant risk.

4. **Add SAST scanning** — Enable CodeQL for Go or add gosec to the golangci-lint configuration. Add secret detection with Gitleaks.

### Priority 1 (High Value)

5. **Upgrade Go toolchain** — Move to Go 1.22+ across `go.mod`, `.promu.yml`, and `.circleci/config.yml`. Update golangci-lint to v1.59+ and enable more linters (errcheck, gosec, gocritic, ineffassign).

6. **Add PR-time Docker image validation** — Build the container image in PR workflows, add a basic startup test (e.g., `docker run --rm blackbox_exporter --version`).

7. **Add container runtime startup tests** — Verify the container starts correctly, serves metrics on `:9115/metrics`, and can load configuration.

8. **Create agent rules** — Add `.claude/rules/` with Go unit test patterns, prober testing patterns, and config validation test patterns for this exporter.

9. **Enable more golangci-lint linters** — Currently only `staticcheck` is enabled. Add `govet`, `errcheck`, `gosimple`, `ineffassign`, `unused`, `gosec`, `gocritic` at minimum.

### Priority 2 (Nice-to-Have)

10. **Add SBOM generation** — Use `syft` or `cosign` to generate SBOMs for container images.

11. **Add image signing** — Use Sigstore/cosign for image attestation.

12. **Implement pre-commit hooks** — Add `.pre-commit-config.yaml` with `gofmt`, `go vet`, `golangci-lint`, and `yamllint`.

13. **Add benchmark tests** — Add `Benchmark*` functions for performance-critical probers (HTTP, DNS).

14. **Consolidate CI to GitHub Actions** — Consider migrating CircleCI workflows to GitHub Actions for a single CI platform and better GitHub integration.

## Comparison to Gold Standards

| Dimension | blackbox_exporter | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|-----------|------------------|----------------------|-------------------|---------------|
| Unit Tests | 6/10 — 58 tests, ICMP gap | 9/10 — Comprehensive Jest+RTL | 7/10 — Notebook-level tests | 9/10 — Extensive Go tests |
| Integration/E2E | 3/10 — IPv6 tests only | 9/10 — Cypress E2E + contracts | 8/10 — Multi-runtime E2E | 9/10 — Multi-version E2E |
| Build Integration | 2/10 — No PR image build | 8/10 — Full PR build validation | 7/10 — Image build in PR | 7/10 — Manifests validated |
| Image Testing | 1/10 — No runtime tests | 7/10 — Container startup tests | 9/10 — 5-layer validation | 6/10 — Basic image tests |
| Coverage Tracking | 1/10 — None | 8/10 — Codecov enforced | 6/10 — Coverage generated | 9/10 — Codecov + thresholds |
| CI/CD Automation | 5/10 — Split CircleCI/GHA | 9/10 — Unified GHA | 8/10 — GHA + Prow | 9/10 — GHA with matrix |
| Agent Rules | 0/10 — None | 8/10 — Comprehensive rules | 3/10 — Basic CLAUDE.md | 2/10 — Minimal |
| **Overall** | **4.1/10** | **8.5/10** | **7.0/10** | **7.5/10** |

## Red Hat Fork Considerations

This is a `red-hat-data-services` fork of the upstream `prometheus/blackbox_exporter`. Key observations:

- **Single branch** (`master`) — appears to be a direct mirror or minimal-delta fork
- **No Red Hat-specific CI** — no Konflux, no Tekton pipelines, no RHDS-specific workflows
- **No downstream testing** — no RHOAI integration tests, no downstream configuration validation
- **Upstream alignment** — the fork tracks upstream Prometheus tooling (promu, Prometheus orb)

For a component used in Red Hat AI/Data Services, the lack of Red Hat-specific quality infrastructure (Konflux builds, downstream testing, RHDS-specific configs) is a notable gap.

## File Paths Reference

| Category | Path | Status |
|----------|------|--------|
| CI - CircleCI | `.circleci/config.yml` | Active (test, ipv6, build, publish) |
| CI - GitHub Actions | `.github/workflows/golangci-lint.yml` | Active (lint only) |
| Linting | `.golangci.yml` | Minimal (staticcheck only) |
| YAML Lint | `.yamllint` | Configured |
| Dockerfile | `Dockerfile` | Simple COPY-based |
| Build | `Makefile`, `Makefile.common` | Prometheus standard |
| Build Config | `.promu.yml` | Go 1.19, static linking |
| Dependabot | `.github/dependabot.yml` | Monthly gomod updates |
| Test Data | `config/testdata/*.yml` | 17 test config files |
| Security Policy | `SECURITY.md` | Links to Prometheus policy |
| Agent Rules | `.claude/` | **Missing** |
| Coverage Config | `.codecov.yml` | **Missing** |
| Pre-commit | `.pre-commit-config.yaml` | **Missing** |
| Security Scanning | `.github/workflows/codeql.yml` | **Missing** |
