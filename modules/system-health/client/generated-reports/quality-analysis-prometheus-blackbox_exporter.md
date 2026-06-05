---
repository: "prometheus/blackbox_exporter"
overall_score: 6.2
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Strong test suite with 85 test functions, 1.43:1 test-to-code ratio, table-driven tests"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "IPv6 integration tests in CI; no E2E deployment or container-level testing"
  - dimension: "Build Integration"
    score: 4.0
    status: "Multi-arch binary builds via promu; no PR-time image build or startup validation"
  - dimension: "Image Testing"
    score: 3.0
    status: "Two Dockerfile variants (busybox + distroless) but no runtime validation or startup tests"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No codecov/coveralls integration, no coverage thresholds, no PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Well-structured workflows with pinned actions, govulncheck, golangci-lint, parallel builds"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory; no AI-assisted development guidance"
critical_gaps:
  - title: "No test coverage tracking or enforcement"
    impact: "Impossible to identify regressions or uncovered code paths; no visibility into coverage trends"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container image runtime validation"
    impact: "Image build/startup failures not caught until deployment; two Dockerfile variants completely untested"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No ICMP prober tests"
    impact: "370-line icmp.go has zero test coverage; ICMP probing is a core feature"
    severity: "HIGH"
    effort: "6-8 hours"
  - title: "No security scanning (Trivy/Snyk/SAST) in CI"
    impact: "Vulnerability detection relies solely on govulncheck for Go deps; no container image scanning"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No pre-commit hooks"
    impact: "Code quality checks only run in CI, not locally before commit"
    severity: "LOW"
    effort: "1-2 hours"
quick_wins:
  - title: "Add codecov integration with coverage thresholds"
    effort: "2-4 hours"
    impact: "Instant visibility into test coverage; block PRs that decrease coverage"
  - title: "Add Trivy container image scanning to CI"
    effort: "1-2 hours"
    impact: "Catch CVEs in base images (busybox, distroless) before release"
  - title: "Add ICMP prober unit tests"
    effort: "4-6 hours"
    impact: "Cover 370 lines of currently untested core functionality"
  - title: "Add container startup smoke test"
    effort: "2-3 hours"
    impact: "Validate both Dockerfile variants build and start correctly on PRs"
recommendations:
  priority_0:
    - "Add codecov/coveralls integration with coverage threshold enforcement on PRs"
    - "Write unit tests for prober/icmp.go (370 lines, 0% coverage, core feature)"
    - "Add container image build and startup validation to PR workflow"
  priority_1:
    - "Add Trivy scanning for container images in CI"
    - "Add E2E smoke tests that exercise the full exporter lifecycle (build, start, probe, metrics)"
    - "Create .claude/rules/ with test automation guidance for contributors"
  priority_2:
    - "Add pre-commit hooks for gofmt, yamllint, license checks"
    - "Add SBOM generation and image signing with cosign"
    - "Add fuzz testing for config parsing and query_response parsing"
---

# Quality Analysis: prometheus/blackbox_exporter

## Executive Summary

- **Overall Score: 6.2/10**
- **Repository Type**: Go CLI tool / Prometheus exporter
- **Primary Language**: Go 1.25+
- **Framework**: Prometheus client_golang, promu build system
- **Key Strengths**: Strong unit test suite (85 test functions, 1.43:1 test-to-code ratio), well-structured CI with security-hardened workflows, govulncheck for vulnerability detection, dedicated IPv6 testing
- **Critical Gaps**: No coverage tracking whatsoever, no container image testing, no ICMP prober tests (370 LOC untested), no security scanning for images
- **Agent Rules Status**: Missing - No CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Strong test suite: 85 test functions, 5918 test LOC vs 4154 source LOC (1.43:1 ratio), table-driven tests with subtests |
| Integration/E2E | 5.0/10 | IPv6 integration tests in Docker; no full E2E deployment or lifecycle testing |
| **Build Integration** | **4.0/10** | **Multi-arch binary builds via promu with 4-way parallelism; no PR-time image build validation** |
| Image Testing | 3.0/10 | Two Dockerfile variants (busybox + distroless) with multi-arch support but zero runtime validation |
| Coverage Tracking | 1.0/10 | No codecov, coveralls, or any coverage reporting; no thresholds; no PR-level coverage feedback |
| CI/CD Automation | 8.0/10 | Well-organized: CI, golangci-lint, govulncheck, stale PR management; pinned actions with SHA hashes |
| Agent Rules | 0.0/10 | No AI-assisted development guidance whatsoever |

## Critical Gaps

### 1. No Test Coverage Tracking or Enforcement
- **Impact**: Cannot identify coverage regressions or untested code paths
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No `.codecov.yml`, no `coverprofile` flags in Makefile test targets, no coverage reporting in CI. There is literally no way to know what percentage of code is tested.
- **Evidence**: `grep -r 'coverage\|codecov\|coveralls\|coverprofile' .github/ Makefile Makefile.common` returns empty

### 2. No Container Image Runtime Validation
- **Impact**: Both Dockerfile variants (busybox and distroless) could produce broken images with no CI detection
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The CI builds multi-arch binaries via promu but never builds or tests Docker images on PRs. Image validation only happens implicitly at release time. No startup tests, no health check validation, no metrics endpoint verification.

### 3. No ICMP Prober Tests (370 LOC, 0% Coverage)
- **Impact**: The ICMP prober is a core feature with complex platform-specific logic (raw sockets, privileged vs unprivileged ICMP) that has zero test coverage
- **Severity**: HIGH
- **Effort**: 6-8 hours
- **Details**: `prober/icmp.go` is 370 lines with no corresponding `prober/icmp_test.go`. Other probers have extensive tests (HTTP: 2096 LOC, TCP: 825 LOC, DNS: 657 LOC). ICMP testing may require privileged containers or mock sockets.

### 4. No Container Security Scanning
- **Impact**: CVEs in base images (busybox, distroless) not detected until downstream consumers scan
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: No Trivy, Snyk, or any container scanning configured. The project has `govulncheck` for Go dependency vulnerabilities, which is good, but container-level scanning is absent. No SBOM generation, no image signing.

### 5. No Pre-commit Hooks
- **Impact**: Contributors must wait for CI to catch formatting, linting, and license issues
- **Severity**: LOW
- **Effort**: 1-2 hours
- **Details**: No `.pre-commit-config.yaml`. The Makefile has `style`, `check_license`, and `lint` targets that could be wired up as pre-commit hooks.

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- **Impact**: Instant visibility into test coverage with PR-level feedback
- **Implementation**:
  1. Add `-coverprofile=coverage.out` to test commands in Makefile.common
  2. Add codecov upload step to CI workflow
  3. Create `.codecov.yml` with threshold configuration

```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: auto
        threshold: 2%
    patch:
      default:
        target: 80%
```

### 2. Add Trivy Container Scanning (1-2 hours)
- **Impact**: Catch CVEs in busybox and distroless base images
- **Implementation**: Add a Trivy scanning step to CI workflow

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'prom/blackbox-exporter:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 3. Add Container Startup Smoke Test (2-3 hours)
- **Impact**: Validate both Dockerfile variants produce working images
- **Implementation**: Build image and verify it starts and serves metrics

```yaml
- name: Build and test Docker image
  run: |
    docker build -t bbe-test .
    docker run -d --name bbe-test -p 9115:9115 bbe-test
    sleep 2
    curl -f http://localhost:9115/metrics || exit 1
    docker stop bbe-test
```

### 4. Add ICMP Prober Tests (4-6 hours)
- **Impact**: Cover 370 lines of core, untested functionality
- **Implementation**: Use mock ICMP connections or test with unprivileged ICMP where possible

## Detailed Findings

### CI/CD Pipeline

**Workflows (5 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR + push to master/release + tags | Go tests, IPv6 tests, multi-arch builds, publish |
| `golangci-lint.yml` | PR + push | Linting with golangci-lint v2.11.4 |
| `govulncheck.yml` | PR (VERSION changes) + push + daily cron | Go vulnerability checking |
| `container_description.yml` | Push (README changes) | Sync README to Docker Hub + Quay |
| `stale.yml` | Daily cron | Mark stale PRs (60 days) |

**Strengths:**
- All actions pinned to SHA hashes (supply chain security)
- `persist-credentials: false` on all checkouts (5/5 workflows)
- Explicit `permissions` blocks on all workflows (least privilege)
- Parallel 4-thread builds via promu matrix strategy
- Dedicated IPv6 test job with Docker network reconfiguration
- Dependabot configured for monthly Go module updates
- `govulncheck` runs daily on a schedule for proactive vulnerability detection

**Weaknesses:**
- No concurrency control (duplicate workflows can run simultaneously)
- No caching of Go modules or build artifacts
- No PR-time Docker image builds
- No test result reporting (JUnit XML support exists in Makefile.common via gotestsum but not used in GitHub Actions)

### Test Coverage

**Test Inventory:**

| File | Test Functions | Lines | Focus |
|------|---------------|-------|-------|
| `prober/http_test.go` | 33 | 2096 | HTTP probing: status codes, redirects, TLS, compression, headers, HTTP/3 |
| `prober/tcp_test.go` | 12 | 825 | TCP connections, TLS, query-response patterns |
| `prober/dns_test.go` | 5 | 657 | DNS resolution, record types, DNSSEC |
| `prober/grpc_test.go` | 8 | 574 | gRPC health checking, TLS |
| `prober/handler_test.go` | 8 | 397 | Probe handler dispatch, timeouts |
| `prober/websocket_test.go` | 2 | 319 | WebSocket probing |
| `config/config_test.go` | 6 | 307 | Config loading, validation (24 testdata files) |
| `prober/utils_test.go` | 2 | 302 | IP resolution, preferred IP protocol |
| `prober/history_test.go` | 5 | 187 | Probe history ring buffer |
| `config/reload_test.go` | 1 | 109 | Hot reload functionality |
| `prober/unix_test.go` | 2 | 76 | Unix socket probing |
| `main_test.go` | 1 | 69 | Version info output |

**Test Quality:**
- Table-driven tests with subtests (`t.Run`) used extensively (10+ locations in HTTP tests)
- Real network listeners and httptest servers (no mocking frameworks)
- TLS certificate generation and validation in tests
- Context timeout testing throughout
- Prometheus registry validation (metric correctness)
- 24 testdata YAML files for config validation

**Coverage Gaps:**
- **prober/icmp.go** (370 LOC): Zero tests. Most complex prober with raw socket handling, platform-specific code
- **prober/query_response.go** (202 LOC): No dedicated tests (partially covered via TCP/Unix tests)
- **prober/tls.go** (98 LOC): No dedicated tests (partially covered via HTTP/TCP TLS tests)
- **prober/prober.go** (54 LOC): No dedicated tests (registry of probers)
- No fuzz testing despite parsing YAML configs and query-response patterns
- No benchmark tests

### Code Quality

**Linting:**
- golangci-lint v2.11.4 configured with v2 config format
- 3 linters enabled: `misspell`, `sloglint`, `staticcheck`
- Relatively minimal linter set - many available linters not enabled (errcheck, govet, ineffassign, etc.)
- Exclusion presets: comments, common-false-positives, legacy, std-error-handling

**YAML Linting:**
- `.yamllint` configured with custom rules
- Integrated via Makefile.common `yamllint` target

**Code Formatting:**
- `gofmt` enforced in CI via `make style`
- golangci-lint format step also available

**Static Analysis:**
- `go vet` available via Makefile.common but not explicitly in CI workflow (may run via `make style`)
- `govulncheck` for Go dependency vulnerabilities (daily + PR-triggered)
- No CodeQL, gosec, or Semgrep

### Container Images

**Dockerfile Analysis:**

| Variant | Base Image | Purpose |
|---------|-----------|---------|
| `Dockerfile` | `quay.io/prometheus/busybox-${OS}-${ARCH}:latest` | Standard variant with busybox shell |
| `Dockerfile.distroless` | `gcr.io/distroless/static-debian13:nonroot` | Minimal distroless variant |

**Strengths:**
- Two image variants (standard + distroless) for different security requirements
- Multi-arch support: amd64, arm64, armv7, ppc64le, riscv64, s390x
- Distroless image runs as nonroot user (UID 65532)
- Proper OCI labels (maintainer, vendor, source, documentation, license)
- `.dockerignore` present

**Weaknesses:**
- No multi-stage builds (binary pre-built by promu, COPY'd in)
- No HEALTHCHECK instruction in either Dockerfile
- No image scanning in CI
- No SBOM generation
- No image signing or attestation
- No startup validation
- Busybox variant uses `:latest` tag (not pinned)

### Security

**Strengths:**
- `govulncheck` for Go dependency vulnerability scanning (daily cron + PR-triggered)
- `SECURITY.md` with vulnerability reporting process
- Dependabot for monthly dependency updates
- All GitHub Actions pinned to SHA hashes (supply chain security)
- `persist-credentials: false` on all checkouts
- Explicit, minimal `permissions` blocks
- Distroless image variant available (reduced attack surface)

**Weaknesses:**
- No container image vulnerability scanning (Trivy/Snyk)
- No SAST (CodeQL, gosec, Semgrep)
- No secret detection (Gitleaks, TruffleHog)
- No SBOM generation
- No image signing (cosign)
- No dependency license scanning

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None
- **Details**: No `CLAUDE.md`, `AGENTS.md`, or `.claude/` directory exists. No test automation guidance, test patterns, or quality checklists for AI-assisted development.
- **Gap**: Contributors using AI coding assistants have no project-specific guidance on test patterns (table-driven tests, real network listeners, Prometheus registry validation), prober test conventions, or quality gates.
- **Recommendation**: Generate test automation rules with `/test-rules-generator` covering unit test patterns, prober testing conventions, and config validation test patterns.

## Recommendations

### Priority 0 (Critical)

1. **Add coverage tracking with codecov** - The project has a strong test suite but zero visibility into what's covered. Add `-coverprofile` to test runs and integrate codecov with threshold enforcement. This is the single highest-ROI improvement.

2. **Write tests for prober/icmp.go** - 370 lines of core functionality with raw socket handling, platform-specific behavior, and complex logic has zero test coverage. This is a significant risk for a monitoring tool.

3. **Add container image build + startup validation to PR workflow** - Both Dockerfile variants should be built and smoke-tested on PRs to prevent broken images from being published.

### Priority 1 (High Value)

4. **Add Trivy container image scanning** - Catch CVEs in base images. The project already has govulncheck for Go deps; container scanning completes the picture.

5. **Add E2E smoke tests** - Build the binary, start the exporter, send probe requests, verify metrics output. Tests should cover at least HTTP, TCP, and DNS probing.

6. **Create agent rules (.claude/rules/)** - Document the project's testing conventions: table-driven tests, real network listeners (no mocking), Prometheus registry validation patterns, testdata file organization.

7. **Expand golangci-lint configuration** - Only 3 linters enabled. Consider adding: `errcheck`, `govet`, `ineffassign`, `gosec`, `bodyclose`, `noctx`, `exportloopref`.

### Priority 2 (Nice-to-Have)

8. **Add pre-commit hooks** - Wire existing Makefile targets (`style`, `check_license`, `lint`) into `.pre-commit-config.yaml`.

9. **Add fuzz testing** - Config parsing (`config.go`, 698 LOC) and query-response pattern matching (`query_response.go`, 202 LOC) are good candidates for Go's native fuzzing.

10. **Add SBOM generation and image signing** - Use cosign for image attestation and syft for SBOM generation to improve supply chain security.

11. **Add HEALTHCHECK to Dockerfiles** - Both variants lack container health checks, making orchestration harder.

12. **Add concurrency control to workflows** - Prevent duplicate workflow runs on rapid pushes with `concurrency` groups.

## Comparison to Gold Standards

| Dimension | blackbox_exporter | odh-dashboard (Gold) | notebooks (Gold) | Gap |
|-----------|------------------|---------------------|-----------------|-----|
| Unit Tests | 8.5 - Strong, table-driven | 9.0 - Multi-layer | 7.0 - Focused | Minor |
| Integration/E2E | 5.0 - IPv6 only | 9.5 - Cypress E2E | 8.0 - Multi-runtime | Large |
| Build Integration | 4.0 - Binary only | 9.0 - Full pipeline | 8.5 - Image pipeline | Large |
| Image Testing | 3.0 - None | 8.0 - Runtime validation | 9.5 - 5-layer validation | Critical |
| Coverage Tracking | 1.0 - None | 9.0 - Enforced thresholds | 6.0 - Partial | Critical |
| CI/CD Automation | 8.0 - Well-structured | 9.5 - Comprehensive | 8.5 - Automated | Minor |
| Security Scanning | 5.0 - govulncheck only | 8.5 - Multi-tool | 7.5 - Trivy + cosign | Moderate |
| Agent Rules | 0.0 - None | 8.0 - Comprehensive | 3.0 - Basic | Large |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - Main CI: tests, builds, publish
- `.github/workflows/golangci-lint.yml` - Linting
- `.github/workflows/govulncheck.yml` - Vulnerability scanning
- `.github/workflows/container_description.yml` - README sync
- `.github/workflows/stale.yml` - Stale PR management
- `.github/dependabot.yml` - Dependency updates
- `Makefile` + `Makefile.common` - Build system
- `.promu.yml` - promu build configuration

### Testing
- `prober/http_test.go` (2096 LOC, 33 tests) - HTTP prober tests
- `prober/tcp_test.go` (825 LOC, 12 tests) - TCP prober tests
- `prober/dns_test.go` (657 LOC, 5 tests) - DNS prober tests
- `prober/grpc_test.go` (574 LOC, 8 tests) - gRPC prober tests
- `prober/handler_test.go` (397 LOC, 8 tests) - Handler tests
- `config/config_test.go` (307 LOC, 6 tests) - Config validation
- `config/testdata/` - 24 test fixture YAML files
- **MISSING**: `prober/icmp_test.go` - ICMP prober has no tests

### Code Quality
- `.golangci.yml` - golangci-lint v2 config (3 linters)
- `.yamllint` - YAML linting rules

### Container Images
- `Dockerfile` - Busybox-based image
- `Dockerfile.distroless` - Distroless image
- `.dockerignore` - Docker build exclusions

### Security
- `SECURITY.md` - Vulnerability reporting policy
