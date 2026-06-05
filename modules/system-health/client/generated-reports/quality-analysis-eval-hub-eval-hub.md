---
repository: "eval-hub/eval-hub"
overall_score: 7.6
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "514 test functions across 77 test files with excellent test-to-code ratio (1.58x lines of test vs source)"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "186 BDD scenarios via godog FVT, Kubernetes and MLflow integration suites, plus MCP E2E shell tests"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR-time Docker build with dry-run validation; multi-arch push on merge; no Konflux simulation"
  - dimension: "Image Testing"
    score: 7.0
    status: "Multi-stage Containerfile with dry-run on PR; multi-arch (amd64/arm64) push; no Trivy/Snyk scanning"
  - dimension: "Coverage Tracking"
    score: 7.5
    status: "Codecov integration with unit + FVT coverage profiles; range 50-75% thresholds; no PR enforcement gate"
  - dimension: "CI/CD Automation"
    score: 8.5
    status: "Well-organized workflows for main service, MCP, Python server; cross-platform wheel build/validation pipeline"
  - dimension: "Agent Rules"
    score: 7.0
    status: "CLAUDE.md, AGENTS.md, and .claude/rules/ with service-specific rules; missing dedicated test-type rules"
critical_gaps:
  - title: "No container vulnerability scanning (Trivy/Snyk/Grype)"
    impact: "CVEs in base images or dependencies go undetected until deployment or external audit"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No coverage enforcement gate on PRs"
    impact: "Coverage can silently regress without blocking merges; codecov range is informational only"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "Gosec runs with -no-fail flag"
    impact: "Security findings are uploaded to GitHub Security tab but never block CI; vulnerabilities can be merged"
    severity: "HIGH"
    effort: "1 hour"
  - title: "No dedicated golangci-lint configuration"
    impact: "Only go vet runs as linter; misses many code quality issues (errcheck, staticcheck, gosimple, etc.)"
    severity: "MEDIUM"
    effort: "3-4 hours"
quick_wins:
  - title: "Add Trivy container scanning to CI workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in base images and dependencies before merge"
  - title: "Enable codecov PR status checks with minimum threshold"
    effort: "30 minutes"
    impact: "Prevent coverage regression on every PR"
  - title: "Remove -no-fail from Gosec and enforce security checks"
    effort: "30 minutes"
    impact: "Block PRs with known security issues"
  - title: "Add golangci-lint with standard linter set"
    effort: "2-3 hours"
    impact: "Catch code quality issues (unused vars, unchecked errors, complexity)"
recommendations:
  priority_0:
    - "Add container vulnerability scanning (Trivy) to PR and push workflows"
    - "Enable codecov coverage gates to enforce minimum coverage on PRs"
    - "Make Gosec security scan fail CI when issues are found (remove -no-fail)"
  priority_1:
    - "Adopt golangci-lint with a comprehensive linter configuration"
    - "Add dedicated agent rules for test creation patterns (.claude/rules/unit-tests.md, fvt-tests.md)"
    - "Add SBOM generation to container builds"
  priority_2:
    - "Add performance/load testing for the API service"
    - "Add contract testing between eval-hub API and MCP server"
    - "Add secret detection (Gitleaks) to pre-commit and CI"
---

# Quality Analysis: eval-hub

## Executive Summary

- **Overall Score: 7.6/10**
- **Repository Type**: Go REST API service + MCP server + Python packaging wrapper
- **Primary Language**: Go (with Python server wrapper and shell-based MCP E2E tests)
- **Framework**: Standard library `net/http` (no web framework), godog BDD testing

**Key Strengths**:
- Excellent test-to-code ratio: 25,899 lines of test code vs 16,449 lines of source (1.58x)
- 514 Go test functions + 186 BDD scenarios providing comprehensive functional coverage
- Sophisticated cross-platform build pipeline (Go binaries, Python wheels, Docker multi-arch)
- PR-time Docker build with dry-run validation ensures images are buildable before merge
- Good agent rules foundation with CLAUDE.md, AGENTS.md, and service-specific .claude/rules/

**Critical Gaps**:
- No container vulnerability scanning (Trivy/Snyk) anywhere in CI
- Gosec security scanner runs with `-no-fail` so it never blocks CI
- No coverage enforcement — codecov uploads data but doesn't gate PRs
- No golangci-lint — only `go vet` runs, missing many code quality checks

**Agent Rules Status**: Present and service-specific, but incomplete — no dedicated test pattern rules

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | 514 test functions, excellent coverage ratio, race detection enabled |
| Integration/E2E | 8.0/10 | 186 BDD scenarios, Kubernetes/MLflow suites, MCP E2E shell tests |
| **Build Integration** | **7.0/10** | **PR Docker build + dry-run; multi-arch push; no Konflux simulation** |
| Image Testing | 7.0/10 | Multi-stage build, dry-run validation; no vulnerability scanning |
| Coverage Tracking | 7.5/10 | Codecov with unit + FVT profiles; no PR enforcement gate |
| CI/CD Automation | 8.5/10 | Well-organized multi-service workflows; cross-platform pipeline |
| Agent Rules | 7.0/10 | Service rules present; missing dedicated test-type rules |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: CVEs in the UBI9 base image, Go dependencies, or runtime components go undetected until production deployment or external audit
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Neither the PR workflow nor the push workflow includes Trivy, Snyk, or Grype scanning. The Containerfile uses `registry.access.redhat.com/ubi9/ubi-minimal:latest` and `ubi9/go-toolset:1.26`, which should be regularly scanned.
- **Fix**: Add `aquasecurity/trivy-action` to both `docker-build-check` and `docker-build-push` jobs

### 2. Security Scanner Doesn't Block CI
- **Impact**: Gosec findings are uploaded to GitHub Security tab for visibility but the `-no-fail` flag means PRs with security issues are never blocked
- **Severity**: HIGH
- **Effort**: 1 hour
- **Details**: In `ci.yml`, the Gosec step uses `args: '-no-fail -fmt sarif -out gosec-results.sarif ./...'`. This makes security scanning purely informational.
- **Fix**: Remove `-no-fail` or add severity thresholds (e.g., fail on HIGH/CRITICAL only)

### 3. No Coverage Enforcement on PRs
- **Impact**: Test coverage can silently regress without any CI gate; the codecov range (50-75%) only colors the badge
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Details**: `codecov.yml` sets `range: 50..75` for display colors but does not configure `status` checks. Coverage is uploaded to Codecov but no PR status check blocks merges on regression.
- **Fix**: Add `status` configuration to `codecov.yml`:
  ```yaml
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

### 4. No golangci-lint Configuration
- **Impact**: Only `go vet` runs as a linter, missing many valuable checks: errcheck, staticcheck, gosimple, ineffassign, unused, bodyclose, etc.
- **Severity**: MEDIUM
- **Effort**: 3-4 hours
- **Details**: The Makefile `lint` target is simply `go vet ./...`. No `.golangci.yaml` exists. Projects like odh-dashboard and kserve use golangci-lint with 15+ linters enabled.
- **Fix**: Create `.golangci.yaml` with standard linters and add `golangci-lint run` to CI

## Quick Wins

### 1. Add Trivy Container Scanning (1-2 hours)
Add to the `docker-build-check` job in `ci.yml`:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: evalhub:pr-check
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

### 2. Enable Codecov PR Status Checks (30 minutes)
Update `codecov.yml` to add project and patch coverage gates.

### 3. Remove -no-fail from Gosec (30 minutes)
Change the Gosec args from `'-no-fail -fmt sarif ...'` to `'-fmt sarif ...'` so security issues block CI.

### 4. Add golangci-lint (2-3 hours)
Create `.golangci.yaml` and replace `make lint` with `golangci-lint run`.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (8 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR + push (main/develop) + tags | Main CI: quality checks, security scan, Docker build |
| `ci-mcp.yml` | PR + push (MCP paths) | MCP service CI: format, vet, unit tests, platform builds |
| `ci-python-server.yml` | PR (python-server paths) | Python server: build wheel, run tests |
| `commitlint.yml` | PR (main) | Conventional commit lint via commitizen |
| `required-reviewer-approvals.yml` | PR events + reviews | Verify all requested reviewers approved |
| `publish-python-server.yml` | push (main) + tags + dispatch | Cross-platform wheel build, validation, PyPI publish |
| `release-mcp.yml` | tags (v*) | MCP binary release with checksums |
| `check-trustyai-service-operator-configmap-sync.yml` | push (main) + nightly + dispatch | External ConfigMap sync check |

**Strengths**:
- Path-filtered workflows for MCP and Python server avoid unnecessary CI runs
- Pinned action versions with commit SHAs (not tags) — excellent supply chain security
- Docker build on PR with dry-run validation (`docker run --rm evalhub:pr-check /app/eval-hub --local --help`)
- Cross-platform wheel validation on real runners (Linux, macOS arm64, Windows)
- Required reviewer approvals with custom script
- Conventional commit enforcement

**Weaknesses**:
- No concurrency control on CI workflows (parallel PR pushes can conflict)
- No workflow-level caching beyond Go module cache
- No test result artifact uploads (JUnit XML) for PR annotations

### Test Coverage

**Unit Tests** (8.5/10):
- 514 test functions across 77 `*_test.go` files
- Test-to-code ratio: 1.58x (25,899 test lines / 16,449 source lines) — exceptional
- Race detection enabled (`-race` flag in all test commands)
- Coverage profiling with `-coverprofile` and `-covermode=atomic`
- Coverage split: unit (`coverage.out`), FVT (`coverage-fvt.out`), init (`coverage-init.out`)
- Patterns: standard `testing` package, table-driven tests, `t.Parallel()` where safe

**Integration/E2E Tests** (8.0/10):
- 186 BDD scenarios in 10 `.feature` files using godog
- Feature coverage: evaluations (43), collections (64), providers (28), GPU resources (6), health (2), metrics (2), Kubernetes (4), MLflow experiments (4), evaluation jobs (32+1)
- FVT runs both embedded and against running server (`test-fvt` vs `test-fvt-server`)
- Tag-based test selection: `@cluster`, `@local_runtime`, `@mlflow`, `@negative`, `@gha-wheel-sanity`
- MCP E2E tests via shell scripts (8 test scripts: server discovery, resources, tools, prompts, autocompletion, error scenarios, E2E workflow, client-specific)
- Python server tests: unit and integration markers

**Test Infrastructure**:
- `tests/features/` — main BDD suite with test data JSON fixtures
- `tests/kubernetes/` — Kubernetes resource testing
- `tests/mlflow/` — MLflow integration with download/run/stop scripts
- `tests/mcp/` — MCP protocol testing (stdio + HTTP transport)
- `tests/postgres/` — PostgreSQL setup for local integration testing
- `tests/secrets/` — Test secret configuration

### Code Quality

**Linting** (5.0/10):
- Only `go vet` configured (via `make lint` and `make vet` — same command)
- No `.golangci.yaml` — missing errcheck, staticcheck, gosimple, gocritic, etc.
- Format check via `gofmt` + git diff enforcement on CI — good
- Python: ruff linting + formatting via pre-commit hooks
- No ESLint (no JS/TS source code — only npm for documentation tooling)

**Pre-commit Hooks** (8.0/10):
- Comprehensive `.pre-commit-config.yaml` with:
  - ruff (Python lint + format)
  - trailing-whitespace, end-of-file-fixer, check-yaml/json/toml
  - check-merge-conflict, check-added-large-files (1MB limit)
  - debug-statements detection
  - no-commit-to-branch (prevents direct push to main)
  - commitizen (commit message convention)
  - mypy type checking (Python server)
  - pytest unit tests (Python server)
  - Go unit + FVT tests
- Pre-push hook for branch protection

**Static Analysis** (6.0/10):
- Gosec security scanner — but runs with `-no-fail`
- SARIF upload to GitHub Security tab
- No CodeQL/Semgrep
- No secret detection (Gitleaks/TruffleHog)
- CodeRabbit configured (`.coderabbit.yaml`) for automated PR review

### Container Images

**Build Process** (8.0/10):
- Multi-stage Containerfile: UBI9 go-toolset builder + UBI9 minimal runtime
- Builds 4 binaries: eval-hub, eval-runtime-sidecar, eval-runtime-init, evalhub-mcp
- CGO_ENABLED=0 for static binaries
- Non-root user (UID 1000) in runtime image
- Multi-architecture support: linux/amd64, linux/arm64
- OCI labels for metadata
- `.dockerignore` configured

**Runtime Validation** (6.5/10):
- PR: Docker build + dry-run (`docker run --rm evalhub:pr-check /app/eval-hub --local --help`)
- Push: Build, push to Quay.io, then dry-run against pushed image
- No functional testing beyond help flag validation
- No health check endpoint testing in container

**Security** (3.0/10):
- No Trivy/Snyk/Grype scanning
- No SBOM generation
- No image signing/attestation
- No vulnerability thresholds configured

### Security

| Practice | Status | Details |
|----------|--------|---------|
| Gosec | Informational only | `-no-fail` flag, SARIF upload only |
| CodeQL | Not configured | No `.github/workflows/codeql.yml` |
| Dependency scanning | Dependabot only | No explicit dependency audit in CI |
| Secret detection | Not configured | No Gitleaks/TruffleHog |
| Container scanning | Not configured | No Trivy/Snyk |
| Pin actions by SHA | Yes | All GitHub Actions pinned by commit SHA |
| Non-root containers | Yes | UID 1000 in runtime image |
| Supply chain | Partial | SHA-pinned actions; no SBOM/signing |

### Agent Rules (Agentic Flow Quality)

**Status**: Present and partially comprehensive

**What exists**:
- `CLAUDE.md` — References AGENTS.md, includes CVE-fixing instructions with Go-toolset version awareness
- `AGENTS.md` — Comprehensive developer guide: build commands, testing strategy, architecture, project structure, MCP usage, config details
- `.claude/rules/evalhub-service.md` — Service-specific rule with paths filter, build/test commands, architecture patterns (ExecutionContext, routing, config, database), testing strategy with FVT tags
- `.claude/rules/evalhub-mcp-service.md` — MCP-specific rule with paths filter, build/test commands, testing strategy
- `.claude/skills/fix-fvt-test/` — Custom skill for fixing FVT tests

**Strengths**:
- Path-based rule scoping (rules only activate for relevant files)
- Architecture documentation in rules helps agents make informed decisions
- FVT tag system documented in rules
- CVE-fixing workflow documented with go-toolset version constraints

**Gaps**:
- No dedicated test-type rules (e.g., `unit-tests.md`, `fvt-tests.md`, `integration-tests.md`)
- No test creation patterns or templates in rules
- No quality gate checklists for agents
- Missing examples of good test patterns for the codebase

**Recommendation**: Generate dedicated test rules with `/test-rules-generator` for:
- Unit test patterns (table-driven, t.Parallel() guidance, mock patterns)
- FVT/BDD patterns (godog step definitions, feature file conventions)
- MCP test patterns (in-memory transport testing)

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning** — Add Trivy to both PR and push workflows. Configure severity thresholds (CRITICAL, HIGH) and fail CI on findings.

2. **Enable coverage enforcement** — Update `codecov.yml` with `status` checks to block PRs that regress coverage below threshold.

3. **Make Gosec block CI** — Remove `-no-fail` from the Gosec command or configure severity-based failure. Security findings should prevent merge.

### Priority 1 (High Value)

4. **Adopt golangci-lint** — Create `.golangci.yaml` with standard linters (errcheck, staticcheck, gosimple, gocritic, ineffassign, unused, bodyclose, nilerr) and replace `go vet` in CI.

5. **Add dedicated agent test rules** — Create `.claude/rules/unit-tests.md` and `.claude/rules/fvt-tests.md` with specific patterns, table-driven test templates, godog step definition conventions, and quality gate checklists.

6. **Add SBOM generation** — Use `anchore/sbom-action` or `aquasecurity/trivy-action` with SBOM output for supply chain transparency.

7. **Add concurrency control to CI** — Use `concurrency` groups in workflows to cancel outdated PR runs.

### Priority 2 (Nice-to-Have)

8. **Add performance/load testing** — Implement API load testing for evaluation endpoints (e.g., k6 or vegeta).

9. **Add contract testing** — Test the API contract between eval-hub REST API and MCP server systematically.

10. **Add secret detection** — Configure Gitleaks in pre-commit and CI to prevent secret leaks.

11. **Add JUnit test result artifacts** — Upload test results in JUnit XML format for PR annotations.

12. **Add CodeQL analysis** — Complement Gosec with CodeQL for broader security coverage.

## Comparison to Gold Standards

| Dimension | eval-hub | odh-dashboard | notebooks | kserve |
|-----------|----------|---------------|-----------|--------|
| Unit Tests | 8.5 (514 funcs, 1.58x ratio) | 9.0 (comprehensive Jest) | 7.0 | 9.0 (enforcement) |
| Integration/E2E | 8.0 (186 BDD scenarios) | 9.5 (Cypress + contract) | 8.0 | 9.0 |
| Build Integration | 7.0 (PR Docker + dry-run) | 8.0 (multi-mode) | 7.0 | 7.0 |
| Image Testing | 7.0 (multi-arch, dry-run) | 7.0 | 9.0 (5-layer validation) | 7.0 |
| Coverage Tracking | 7.5 (Codecov, no gate) | 9.0 (enforced) | 6.0 | 9.0 (enforced) |
| CI/CD Automation | 8.5 (multi-service, cross-platform) | 9.0 | 8.0 | 9.0 |
| Agent Rules | 7.0 (service rules, no test patterns) | 9.0 (comprehensive) | 5.0 | 5.0 |
| Security Scanning | 4.0 (Gosec -no-fail only) | 7.0 | 7.0 (Trivy) | 7.0 |
| **Overall** | **7.6** | **8.6** | **7.1** | **7.9** |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` — Main CI (quality, security, Docker)
- `.github/workflows/ci-mcp.yml` — MCP service CI
- `.github/workflows/ci-python-server.yml` — Python server CI
- `.github/workflows/commitlint.yml` — Commit message linting
- `.github/workflows/publish-python-server.yml` — Cross-platform wheel pipeline
- `.github/workflows/release-mcp.yml` — MCP binary releases
- `.github/workflows/required-reviewer-approvals.yml` — PR approval enforcement
- `.github/workflows/check-trustyai-service-operator-configmap-sync.yml` — External sync check

### Testing
- `tests/features/*.feature` — BDD scenarios (10 feature files, 186 scenarios)
- `tests/features/*_test.go` — godog step definitions
- `tests/kubernetes/` — Kubernetes integration tests
- `tests/mlflow/` — MLflow integration tests
- `tests/mcp/` — MCP protocol E2E tests (shell scripts)
- `tests/postgres/` — PostgreSQL setup
- `python-server/tests/` — Python server tests
- `.conf.go-test` / `.conf.go-integration-test` — Test output colorization

### Code Quality
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff, commitizen, mypy, go tests)
- `.coderabbit.yaml` — CodeRabbit PR review config
- `.markdownlint.json` — Markdown linting
- `codecov.yml` — Coverage tracking config (range 50-75%)

### Container Images
- `Containerfile` — Multi-stage Docker build (UBI9)
- `.dockerignore` — Docker build exclusions
- `containers/` — Additional container definitions (lighteval)

### Agent Rules
- `CLAUDE.md` — CVE fixing instructions
- `AGENTS.md` — Comprehensive developer guide
- `.claude/rules/evalhub-service.md` — API service rules with architecture docs
- `.claude/rules/evalhub-mcp-service.md` — MCP service rules
- `.claude/skills/fix-fvt-test/SKILL.md` — FVT test fixing skill
