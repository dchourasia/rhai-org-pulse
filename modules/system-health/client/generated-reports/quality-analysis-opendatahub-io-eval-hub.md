---
repository: "opendatahub-io/eval-hub"
overall_score: 8.2
scorecard:
  - dimension: "Unit Tests"
    score: 9.0
    status: "Excellent test-to-code ratio (1.54:1 lines), 71 test files across all packages with Go standard testing"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "BDD-style FVT with godog, Gherkin feature files, MCP E2E shell scripts, Kubernetes test suites"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR-time Docker build + dry-run validation; no Konflux simulation but solid container smoke test"
  - dimension: "Image Testing"
    score: 7.5
    status: "Multi-stage Containerfile, multi-arch builds (amd64/arm64), image dry-run on PR; no Trivy scanning"
  - dimension: "Coverage Tracking"
    score: 8.5
    status: "Codecov integration with multi-profile upload (unit + FVT + init), range 50-75 thresholds"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "10 workflows, path-filtered CI, commit linting, automated releases, cross-platform build tests"
  - dimension: "Agent Rules"
    score: 8.5
    status: "CLAUDE.md, AGENTS.md, .claude/rules/ with service-specific rules, .claude/skills/ present"
critical_gaps:
  - title: "No container vulnerability scanning"
    impact: "CVEs in base images or dependencies may reach production undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No golangci-lint configuration"
    impact: "Missing advanced Go linting (only go vet runs); many common bugs uncaught at lint time"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Lighteval Dockerfile uses unpinned :latest base and broad pip install"
    impact: "Non-reproducible container builds and potential supply-chain risk"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add Trivy scanning to CI workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in container images and Go dependencies before merge"
  - title: "Add golangci-lint with curated linter set"
    effort: "2-3 hours"
    impact: "Catch bugs like unchecked errors, shadow variables, inefficient code"
  - title: "Pin lighteval Dockerfile base image to digest"
    effort: "30 minutes"
    impact: "Reproducible builds and traceable supply chain for evaluation container"
  - title: "Add Semgrep to CI (already has config)"
    effort: "1 hour"
    impact: "Enforce the comprehensive semgrep.yaml rules automatically on every PR"
recommendations:
  priority_0:
    - "Add Trivy container scanning to PR and push workflows for all Containerfiles"
    - "Integrate the existing semgrep.yaml into CI workflow to enforce SAST rules automatically"
  priority_1:
    - "Add golangci-lint with a curated set of linters (.golangci.yml) to CI"
    - "Add coverage enforcement thresholds (e.g. fail if coverage drops below current baseline)"
    - "Pin base images in containers/lighteval/Dockerfile to specific versions/digests"
  priority_2:
    - "Add SBOM generation to container builds (syft or docker buildx --sbom)"
    - "Add image signing/attestation with cosign for release images"
    - "Add performance/load testing for the REST API service"
---

# Quality Analysis: eval-hub

## Executive Summary

- **Overall Score: 8.2/10**
- **Repository Type**: Go REST API service with Python server wrapper and MCP server
- **Primary Language**: Go (with Python and shell scripts)
- **Framework**: Standard library `net/http`, godog for BDD, Prometheus metrics
- **Agent Rules Status**: Present and well-structured (CLAUDE.md, AGENTS.md, .claude/rules/)

**Key Strengths**: Exceptional test coverage with 71 Go test files across all packages (1.54:1 test-to-code ratio by line count), comprehensive BDD-style FVT suite with 10 Gherkin feature files (~4000 lines), multi-profile Codecov integration, PR-time Docker build validation with dry-run, 10+ CI workflows with path-filtering, cross-platform build test matrix, extensive security rules via Semgrep and Gitleaks, and well-documented agent rules.

**Critical Gaps**: No container vulnerability scanning (Trivy/Snyk), no advanced Go linting (golangci-lint), and Semgrep rules exist but aren't enforced in CI.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.0/10 | 71 test files, 24,785 LOC tests vs. 16,088 LOC source (1.54:1 ratio) |
| Integration/E2E | 9.0/10 | BDD FVT with godog, MCP E2E scripts, Kubernetes tests, Python server tests |
| Build Integration | 7.0/10 | PR Docker build + dry-run; no Konflux simulation |
| Image Testing | 7.5/10 | Multi-arch builds, dry-run validation; no vulnerability scanning |
| Coverage Tracking | 8.5/10 | Codecov with 3 coverage profiles, range 50-75 thresholds |
| CI/CD Automation | 9.0/10 | 10 workflows, path-filtered, commit lint, automated releases |
| Agent Rules | 8.5/10 | CLAUDE.md + AGENTS.md + .claude/rules/ + .claude/skills/ |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: CVEs in UBI9 base images, Go dependencies, or Python packages may reach production undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Neither the main Containerfile nor `containers/lighteval/Dockerfile` has Trivy, Grype, or Snyk scanning in CI. The project uses `registry.access.redhat.com/ubi9/go-toolset:1.26` and `ubi9/ubi-minimal:latest` but never validates these for known CVEs.

### 2. No golangci-lint Configuration
- **Impact**: Only `go vet` runs for linting — misses common bugs (unchecked errors, variable shadowing, inefficient string operations, unused parameters)
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: The Makefile `lint` target is just `go vet ./...`. Gold-standard Go repos use golangci-lint with 20+ linters enabled.

### 3. Semgrep Rules Exist But Not Enforced in CI
- **Impact**: The comprehensive `semgrep.yaml` (1871 lines, covering Go/Python/TS/YAML/Dockerfile/Shell) is never run automatically — security findings rely entirely on manual runs
- **Severity**: MEDIUM
- **Effort**: 1 hour
- **Details**: `semgrep.yaml` exists at repo root with excellent coverage but no workflow invokes it.

## Quick Wins

### 1. Add Trivy Scanning to CI (1-2 hours)
Add a step to the `ci.yml` workflow:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

### 2. Add golangci-lint (2-3 hours)
Create `.golangci.yml` and update CI:
```yaml
- name: Run golangci-lint
  uses: golangci/golangci-lint-action@v6
  with:
    version: latest
```

### 3. Enforce Semgrep in CI (1 hour)
```yaml
- name: Run Semgrep
  uses: semgrep/semgrep-action@v1
  with:
    config: semgrep.yaml
```

### 4. Pin Lighteval Dockerfile Base Image (30 minutes)
Change `FROM registry.redhat.io/ubi9/python-312:latest` to a specific version/digest.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (10 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push/PR to main, develop | Quality checks, tests, coverage, Docker build |
| `ci-mcp.yml` | push/PR (path-filtered) | MCP-specific quality checks + cross-platform builds |
| `ci-python-server.yml` | PR (path-filtered) | Python server wheel build + pytest |
| `commitlint.yml` | PR to main | Conventional commit enforcement via commitizen |
| `publish-python-server.yml` | push main/tags | Multi-platform wheel build + PyPI publish |
| `release-mcp.yml` | tag push (v*) | Cross-platform binary release with checksums |
| `required-reviewer-approvals.yml` | PR review | Enforce required reviewer approvals |
| `check-trustyai-service-operator-configmap-sync.yml` | push/PR | Verify ConfigMap sync with operator |
| `sync-branch-stable.yaml` | push to main | Auto-sync to stable branch |
| `sync-branch-incubation.yaml` | push to main | Auto-sync to incubation branch |

**Strengths**:
- Path-filtered CI (MCP and Python workflows only trigger on relevant file changes)
- Action versions pinned with SHA hashes (excellent supply chain security)
- Docker build validates on PR (build + dry-run), pushes multi-arch on merge
- Multi-architecture support (linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64)
- Coverage uploaded as 3 separate profiles: unit, FVT, init
- Commit messages enforced via commitizen

**Gaps**:
- No concurrency control on workflows (parallel runs for same PR)
- No Semgrep or Trivy step in any workflow
- No caching of Go module downloads (relies on `actions/setup-go` cache)

### Test Coverage

**Unit Tests (Go):**
- 71 test files across all packages
- 24,785 lines of test code vs. 16,088 lines of source code (1.54:1 ratio — excellent)
- Covers: handlers, storage (SQL), config, server, middleware, CORS, runtime, auth, logging, platform detection, MCP server, sidecar proxy/auth/handlers, validation, service errors
- Uses Go standard `testing` package
- Race detection enabled (`-race` flag)
- Export test files for white-box testing of internal packages

**FVT Tests (BDD):**
- 10 Gherkin feature files with ~4000 lines of scenarios
- godog framework with step definitions
- Covers: health, evaluations, evaluation jobs, evaluation local jobs, collections, providers, GPU resources, metrics
- Tag-based filtering: `@cluster`, `@local_runtime`, `@mlflow`, `@negative`, `@gha-wheel-sanity`
- Tests run against real HTTP server (start → test → stop pattern)
- JUnit XML output for CI reporting

**MCP E2E Tests:**
- 4 comprehensive shell scripts (~68KB total):
  - `part1_stdio_transport.sh` — stdio transport tests
  - `part2_http_transport.sh` — HTTP transport tests
  - `part3_error_scenarios.sh` — error handling scenarios
  - `part4_e2e_workflow.sh` — end-to-end workflows

**Cross-Platform Build Tests (Makefile):**
- 13+ test targets for MCP binary validation
- Binary existence, file type, architecture, naming convention checks
- Version metadata verification
- Static linking verification for Linux binaries
- Container build and HTTP response verification
- SHA256 checksum generation and verification
- Homebrew formula syntax validation
- Native smoke tests

**Python Server Tests:**
- 3 test files: `test_main.py`, `test_integration.py`, `test_get_binary_path.py`
- pytest with unit/integration markers
- Runs in CI via `ci-python-server.yml`

**Kubernetes Tests:**
- Dedicated `tests/kubernetes/` directory with feature files
- Tests for Kubernetes resource scenarios

### Code Quality

**Formatting & Linting:**
- `go fmt` enforced in CI (diff check — fails if not formatted)
- `go vet` runs as lint step
- No golangci-lint (significant gap)
- Ruff for Python linting and formatting (configured in pyproject.toml and pre-commit)
- mypy type checking for Python (pre-commit hook)
- Redocly CLI for API documentation linting

**Pre-commit Hooks (.pre-commit-config.yaml):**
- Ruff linting + formatting (Python)
- Standard hooks: trailing-whitespace, end-of-file, check-yaml, check-json, check-toml, check-merge-conflict, check-added-large-files (1MB limit), debug-statements
- No-commit-to-main protection (pre-push)
- Commitizen conventional commit validation (commit-msg)
- Local hooks: mypy type checking, pytest unit tests, Go unit + FVT tests

**Static Analysis:**
- Gosec security scanner with SARIF output → GitHub Security tab integration
- Semgrep config (1871 lines) covering Go, Python, TypeScript, YAML, Dockerfile, Shell — but NOT enforced in CI
- Gitleaks for secret detection (`.gitleaks.toml` with comprehensive allowlists)
- `.gitleaksignore` for known false positives

**Commit Conventions:**
- Conventional Commits enforced via commitizen
- commitlint workflow on PRs
- `.cz.toml` configuration
- AI attribution trailer convention documented

### Container Images

**Main Containerfile:**
- Multi-stage build (builder → runtime)
- Base: `ubi9/go-toolset:1.26` (builder), `ubi9/ubi-minimal:latest` (runtime)
- Multi-platform support via `$BUILDPLATFORM` / `$TARGETPLATFORM`
- Non-root user (UID 1000, numeric for Kubernetes `runAsNonRoot`)
- Dependency layer caching (go.mod/go.sum copied first)
- Builds 4 binaries: eval-hub, eval-runtime-sidecar, eval-runtime-init, evalhub-mcp
- OCI image labels with version, date, author metadata
- CGO_ENABLED=0 for static linking

**PR Validation:**
- Docker build on every PR
- Dry-run test: `docker run --rm evalhub:pr-check /app/eval-hub --local --help`
- Multi-arch push (amd64/arm64) on merge with quay.io registry
- Digest-based dry-run on push as well

**Lighteval Container (`containers/lighteval/Dockerfile`):**
- Uses `ubi9/python-312:latest` (unpinned — supply chain risk)
- Broad `pip install` with `>=` version constraints (non-reproducible)
- No vulnerability scanning

**Gaps:**
- No Trivy/Grype/Snyk scanning on any image
- No SBOM generation
- No image signing (cosign)
- Lighteval Dockerfile not pinned

### Security

**Strengths:**
- Gosec SAST integrated in CI with SARIF → GitHub Security tab
- Comprehensive Semgrep rules (1871 lines covering 9 categories)
- Gitleaks secret detection with `.gitleaks.toml`
- GitHub Actions pinned to SHA hashes
- Non-root container user
- Static binary builds (no external runtime dependencies)
- Auth module with RBAC rules and testdata

**Gaps:**
- Semgrep rules not enforced in CI
- No container image scanning
- No dependency scanning (e.g., `go list -m all` + vulnerability database)
- No CodeQL workflow

### Agent Rules (Agentic Flow Quality)

**Status**: Present and well-structured

**Files Found:**
- `CLAUDE.md` (root) — References AGENTS.md, CVE fixing guidance
- `AGENTS.md` (root) — Comprehensive developer guide: build commands, testing commands, architecture overview, configuration, testing strategy, commit conventions
- `.claude/rules/evalhub-service.md` — Service-specific build/test/architecture/testing strategy rules with path filters
- `.claude/rules/evalhub-mcp-service.md` — MCP-specific rules with path filters
- `.claude/skills/fix-fvt-test/` — Custom skill for FVT test fixing

**Quality Assessment:**
- Rules are comprehensive and actionable with specific commands and code examples
- Path-based scoping (`.claude/rules/` files have `paths:` frontmatter)
- Architecture patterns well-documented (ExecutionContext, routing, configuration)
- Testing strategy documented with tag system and parallel test guidance
- Commit conventions with AI attribution trailers

**Gaps:**
- No dedicated unit test creation rules (patterns, naming conventions, test data management)
- No E2E test creation rules
- No rules for Python-side testing patterns
- No rules for container/image testing patterns

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning** — Add Trivy or Grype scanning for the main Containerfile and lighteval Dockerfile in CI. Estimated: 2-4 hours.

2. **Enforce Semgrep rules in CI** — The comprehensive `semgrep.yaml` is already written; add a CI step to enforce it. The rules cover Go, Python, Kubernetes YAML, GitHub Actions, Dockerfiles, and shell scripts. Estimated: 1 hour.

### Priority 1 (High Value)

3. **Add golangci-lint** — Replace `go vet` with golangci-lint configured with errcheck, staticcheck, gosimple, unused, ineffassign, govet, stylecheck at minimum. Estimated: 2-3 hours.

4. **Add coverage enforcement thresholds** — The codecov.yml has range 50-75 but no patch or project coverage requirements. Add `status` checks to fail PRs that decrease coverage. Estimated: 1 hour.

5. **Pin base images** — Pin `containers/lighteval/Dockerfile` base image to specific digest. Pin `ubi9/ubi-minimal:latest` in main Containerfile to specific version. Estimated: 30 minutes.

6. **Add concurrency control to CI workflows** — Prevent redundant workflow runs on updated PRs:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

### Priority 2 (Nice-to-Have)

7. **Add SBOM generation** — Use syft or Docker BuildKit `--sbom` flag to generate Software Bill of Materials for release images.

8. **Add image signing** — Use cosign to sign release images pushed to quay.io.

9. **Add performance testing** — Benchmark API response times and throughput for the REST endpoints (e.g., with k6 or vegeta).

10. **Add CodeQL analysis** — Complement Gosec with GitHub CodeQL for deeper semantic analysis.

11. **Expand agent rules** — Add `.claude/rules/` files for unit test creation patterns, Python testing conventions, and container testing guidance. Consider using `/test-rules-generator` to auto-generate these.

## Comparison to Gold Standards

| Dimension | eval-hub | odh-dashboard | notebooks | kserve |
|-----------|----------|---------------|-----------|--------|
| Unit Tests | 9.0 (71 files, 1.54:1 ratio) | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 9.0 (BDD + MCP E2E) | 9.5 (Cypress + contract) | 8.0 | 9.0 |
| Build Integration | 7.0 (Docker dry-run) | 8.0 (multi-mode) | 8.5 | 7.0 |
| Image Testing | 7.5 (multi-arch, dry-run) | 7.0 | 9.5 (5-layer) | 7.0 |
| Coverage Tracking | 8.5 (3-profile Codecov) | 9.0 (enforcement) | 6.0 | 9.5 (thresholds) |
| CI/CD Automation | 9.0 (10 workflows) | 9.0 | 8.0 | 9.0 |
| Security Scanning | 6.5 (Gosec only in CI) | 7.0 | 7.0 | 8.0 |
| Agent Rules | 8.5 (comprehensive) | 9.0 | 3.0 | 2.0 |
| **Overall** | **8.2** | **8.5** | **7.5** | **7.8** |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` — Main CI (quality checks, tests, coverage, Docker)
- `.github/workflows/ci-mcp.yml` — MCP-specific CI (path-filtered)
- `.github/workflows/ci-python-server.yml` — Python server CI (path-filtered)
- `.github/workflows/commitlint.yml` — Commit message linting
- `.github/workflows/release-mcp.yml` — MCP binary release
- `.github/workflows/publish-python-server.yml` — Python wheel publishing

### Testing
- `tests/features/*.feature` — BDD FVT scenarios (10 files)
- `tests/features/*_test.go` — FVT step definitions and suite
- `tests/mcp/scripts/*.sh` — MCP E2E test scripts (4 files)
- `tests/kubernetes/` — Kubernetes test infrastructure
- `tests/mlflow/` — MLflow integration tests
- `python-server/tests/` — Python server tests (3 files)
- `auth/*_test.go` — Auth module tests
- `internal/**/*_test.go` — Internal package tests
- `pkg/**/*_test.go` — Public package tests

### Code Quality
- `.pre-commit-config.yaml` — Pre-commit hooks (Ruff, mypy, Go tests, commitizen)
- `semgrep.yaml` — Comprehensive SAST rules (1871 lines, NOT enforced in CI)
- `.gitleaks.toml` — Secret detection configuration
- `.cz.toml` — Commitizen configuration
- `.markdownlint.json` — Markdown linting
- `python-server/pyproject.toml` — Python tool configuration (Ruff, pytest, mypy)

### Container Images
- `Containerfile` — Main multi-stage build (4 binaries)
- `containers/lighteval/Dockerfile` — Lighteval evaluation container
- `.dockerignore` — Docker build exclusions

### Coverage
- `codecov.yml` — Codecov configuration (range 50-75)

### Agent Rules
- `CLAUDE.md` — Root agent instructions
- `AGENTS.md` — Comprehensive development guide
- `.claude/rules/evalhub-service.md` — EvalHub service rules
- `.claude/rules/evalhub-mcp-service.md` — MCP service rules
- `.claude/skills/fix-fvt-test/` — Custom FVT fix skill
