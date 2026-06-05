---
repository: "red-hat-data-services/eval-hub"
overall_score: 8.4
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "71 test files with 24.8k lines; 1.54:1 test-to-source ratio using Go stdlib testing"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Comprehensive BDD-style FVT with godog, 10 feature files (4k lines), MCP E2E suites, Kubernetes tests"
  - dimension: "Build Integration"
    score: 7.5
    status: "PR-time Docker build + dry-run; Konflux pipeline on PR via Tekton; no Konflux simulation in GHA"
  - dimension: "Image Testing"
    score: 7.0
    status: "Multi-stage UBI9 builds, multi-arch support (amd64/arm64), dry-run validation, no Trivy/vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 8.0
    status: "Codecov integration with fail_ci_if_error, 50-75% range thresholds, coverage treemap generation"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "11 workflows covering CI, security scan, commit lint, release, cross-platform build tests, PyPI publishing"
  - dimension: "Agent Rules"
    score: 8.5
    status: "CLAUDE.md, AGENTS.md, .claude/rules with path-scoped rules, custom skill; strong agentic guidance"
critical_gaps:
  - title: "No container vulnerability scanning (Trivy/Snyk/Grype)"
    impact: "CVEs in base images or Go dependencies undetected until downstream consumption"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No SBOM generation"
    impact: "Supply chain transparency missing; required for SLSA/Sigstore compliance"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Gosec configured with -no-fail flag"
    impact: "Security findings don't block PRs; vulnerabilities can be merged"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No golangci-lint configuration"
    impact: "Limited to basic go vet; misses complexity, style, and advanced static analysis checks"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add Trivy container scanning to CI workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in base images and dependencies on every PR"
  - title: "Remove -no-fail from Gosec and add severity threshold"
    effort: "30 minutes"
    impact: "Security scan failures block merging of vulnerable code"
  - title: "Add golangci-lint with recommended linters"
    effort: "2-3 hours"
    impact: "Catch complexity, style, and correctness issues beyond go vet"
  - title: "Add Syft/Trivy SBOM generation to image build"
    effort: "1-2 hours"
    impact: "Supply chain transparency and compliance readiness"
recommendations:
  priority_0:
    - "Add Trivy/Grype container vulnerability scanning to PR workflow with severity thresholds"
    - "Remove -no-fail from Gosec or set maximum severity threshold to block critical findings"
  priority_1:
    - "Add golangci-lint with a comprehensive linter set (errcheck, gosimple, gocritic, etc.)"
    - "Generate SBOM artifacts during image builds (Syft or Trivy SBOM mode)"
    - "Add image signing/attestation for supply chain security"
  priority_2:
    - "Add CodeQL workflow for deeper semantic analysis"
    - "Consider adding contract tests for the REST API (OpenAPI-based)"
    - "Add performance/load testing for API endpoints"
---

# Quality Analysis: eval-hub

## Executive Summary

- **Overall Score: 8.4/10**
- **Repository Type**: Go service (REST API + MCP server + runtime containers) with Python wheel packaging
- **Primary Language**: Go (16k LoC), with Python server wrapper and BDD tests
- **Key Strengths**: Excellent test coverage with multi-layer testing (unit + FVT + E2E + cross-platform), strong CI/CD automation, comprehensive agent rules, Codecov integration, security scanning with Gosec + Semgrep + Gitleaks, Docker dry-run validation on PRs
- **Critical Gaps**: No container vulnerability scanning, no SBOM generation, Gosec in non-blocking mode, no golangci-lint
- **Agent Rules Status**: Present and comprehensive (CLAUDE.md, AGENTS.md, .claude/rules/, .claude/skills/)

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | 71 test files, 24.8k test lines, Go stdlib testing with t.Parallel guidance |
| Integration/E2E | 9.0/10 | Comprehensive BDD FVT (godog, 10 features, ~4k lines), MCP E2E suites, Kubernetes tests |
| Build Integration | 7.5/10 | PR Docker build + dry-run, Konflux Tekton PR pipeline, hermetic builds |
| Image Testing | 7.0/10 | Multi-stage UBI9, multi-arch (amd64/arm64/ppc64le/s390x via Konflux), dry-run on PR; no vuln scanning |
| Coverage Tracking | 8.0/10 | Codecov with fail_ci_if_error, 50-75% range, treemap visualization, multi-profile coverage |
| CI/CD Automation | 9.0/10 | 11 workflows, well-organized, pinned actions with SHAs, concurrent build matrix |
| Agent Rules | 8.5/10 | CLAUDE.md + AGENTS.md + 2 path-scoped rules + 1 custom skill |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: CVEs in UBI9 base images or Go module dependencies go undetected until downstream consumption by RHOAI
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Neither Trivy, Snyk, Grype, nor any vulnerability scanner is integrated into the CI pipeline. The Containerfile uses `registry.access.redhat.com/ubi9/ubi-minimal:latest` (community) and `Dockerfile.konflux` pins by SHA, but neither gets scanned in CI.

### 2. No SBOM Generation
- **Impact**: Supply chain transparency is missing; SLSA/Sigstore compliance not achievable
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No Syft, Trivy SBOM, or cosign integration. For a product shipped via RHOAI, SBOM generation is increasingly a requirement.

### 3. Gosec Runs in Non-Blocking Mode
- **Impact**: Security vulnerabilities found by Gosec are uploaded to GitHub Security tab but do NOT block PRs
- **Severity**: MEDIUM
- **Effort**: 30 minutes to 1 hour
- **Details**: The `security-scan` job uses `args: '-no-fail -fmt sarif -out gosec-results.sarif ./...'`. The `-no-fail` flag means the job always succeeds regardless of findings. Results go to GitHub Security tab (good for visibility) but don't gate merges.

### 4. No golangci-lint
- **Impact**: Limited static analysis; only `go vet` runs, missing errcheck, gosimple, gocritic, ineffassign, stylecheck, etc.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: The lint target in the Makefile is just `go vet ./...`. There is no `.golangci.yml` configuration. The project would benefit from golangci-lint with a comprehensive linter set.

## Quick Wins

### 1. Add Trivy Container Scanning (1-2 hours)
Add to the `ci.yml` workflow:
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

### 2. Remove -no-fail from Gosec (30 minutes)
Change the Gosec args from:
```
args: '-no-fail -fmt sarif -out gosec-results.sarif ./...'
```
To:
```
args: '-severity high -fmt sarif -out gosec-results.sarif ./...'
```

### 3. Add golangci-lint (2-3 hours)
Create `.golangci.yml` with recommended linters and add to CI:
```yaml
- name: golangci-lint
  uses: golangci/golangci-lint-action@v6
  with:
    version: latest
```

### 4. Add SBOM Generation (1-2 hours)
Add Syft to the image build step:
```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: evalhub:pr-check
    format: spdx-json
```

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- **11 well-organized workflows** covering CI, Python server CI, MCP CI, commit linting, reviewer approvals, publishing, releases, branch sync, and configmap sync
- **All GitHub Actions pinned by SHA** (not by tag), which is a security best practice
- **Path-scoped triggering**: `ci-python-server.yml` and `ci-mcp.yml` only run when relevant paths change
- **Comprehensive build matrix**: Python wheel building covers 5 platform/arch combinations (linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64)
- **Wheel validation**: Real-runner validation on ubuntu, macOS, and Windows before PyPI publish
- **TestPyPI cleanup**: Automated cleanup of old dev releases (keeps last 20)
- **Required reviewer approvals**: Custom workflow verifies all requested reviewers have approved
- **Commit linting**: Commitizen enforced via CI and pre-commit hooks
- **Concurrency**: Tekton PR pipeline has `cancel-in-progress: "true"`

**Areas for Improvement:**
- No concurrency control on the main `ci.yml` workflow (multiple PR pushes can run simultaneously)
- No test caching beyond Go module caching
- No parallelization of unit and FVT test execution

### Test Coverage

**Unit Tests (8.5/10):**
- 71 Go test files with 24,785 lines of test code
- Test-to-source ratio: 1.54:1 (excellent - more test code than source code)
- Uses Go standard library `testing` package
- Good test organization: tests co-located with source files
- Coverage for: handlers, storage/SQL, proxy, auth, config, API types, MCP server, validation, logging
- Python server has 3 test files (unit + integration + binary path tests) with pytest
- Pre-commit hooks run both Go and Python unit tests

**Integration/FVT Tests (9.0/10):**
- BDD-style testing with **godog** (Go Cucumber framework)
- 10 feature files with ~4,000 lines of Gherkin scenarios
- Feature coverage: evaluations, providers, collections, health, metrics, GPU resources, Kubernetes resources, MLflow experiments
- Well-organized tagging system: `@cluster`, `@local_runtime`, `@mlflow`, `@negative`, `@gha-wheel-sanity`
- FVT runs against actual HTTP server (start-service → test → stop-service)
- Coverage collection during FVT via `-coverprofile` and `GOCOVERDIR`
- JUnit XML report generation for CI integration
- HTML FVT report generation with cucumber-html-reporter

**E2E Tests:**
- MCP E2E test suite with 4 shell-script parts: stdio transport, HTTP transport, error scenarios, e2e workflow
- VS Code/Cursor MCP integration tests (8 test suites covering server discovery, resources, tools, prompts, autocompletion, error scenarios, e2e workflow, client-specific)
- Cross-platform build tests (9 make targets): build-all, binary-info, binary-naming, version, no-runtime-deps, container-build, container-http, checksums, formula-syntax
- Homebrew formula integration tests (install, test, uninstall)
- Kubernetes-specific feature tests in separate `tests/kubernetes/` directory

**Test Data:**
- Rich test data directory with JSON fixtures for providers, collections, evaluations, GPU configs
- YAML test data for GPU provider configurations
- Jsonnet test data for template testing

### Code Quality

**Linting:**
- Go: `go vet` only (no golangci-lint)
- Python: Ruff configured in pyproject.toml (E, W, F, I, B, C4, UP rules)
- API docs: Redocly CLI for OpenAPI linting and validation
- Markdown: `.markdownlint.json` configured

**Pre-commit Hooks (Strong):**
- Ruff linting and formatting for Python
- Standard hooks: trailing-whitespace, end-of-file-fixer, check-yaml, check-json, check-toml, check-merge-conflict, check-added-large-files (1MB limit), debug-statements
- No-commit-to-main protection (pre-push)
- Commitizen for conventional commit messages
- mypy type checking for python-server
- pytest unit tests for Python
- Go unit + FVT tests

**Static Analysis:**
- **Gosec**: Security scanning (but non-blocking with `-no-fail`)
- **Semgrep**: Comprehensive unified ruleset (v3.0.0) covering Go, Python, TypeScript, YAML, and generic secrets detection
- **Gitleaks**: Secret detection with well-configured allowlists for test fixtures

**Formatting:**
- `go fmt` enforced in CI with `git diff --exit-code` check
- Ruff formatting for Python via pre-commit
- Conventional commits enforced via Commitizen

### Container Images

**Build Process (Good):**
- Multi-stage builds using UBI9 base images (`go-toolset:1.26` builder, `ubi-minimal` runtime)
- Separate `Containerfile` (community) and `Dockerfile.konflux` (RHOAI/FIPS with `GOEXPERIMENT=strictfipsruntime`)
- Konflux Dockerfile pins base images by SHA digest (good for reproducibility)
- Non-root user (UID 1000) in runtime image
- OCI labels for image metadata
- Multi-architecture support: amd64/arm64 in GHA, plus ppc64le/s390x via Konflux
- `.dockerignore` configured to exclude unnecessary files

**Runtime Validation:**
- Docker dry-run on PRs: `docker run --rm evalhub:pr-check /app/eval-hub --local --help`
- Docker dry-run on push: pulls by digest and runs help command
- Container HTTP test: starts container, sends MCP initialize request, verifies response
- Cross-platform binary validation: file type, architecture, static linking, naming convention

**Gaps:**
- No vulnerability scanning (Trivy, Snyk, Grype)
- No SBOM generation
- No image signing or attestation
- No Testcontainers or similar for structured container testing

### Security

**Strengths:**
- **Gosec**: SAST scanner for Go with SARIF output to GitHub Security tab
- **Semgrep**: Comprehensive rule set covering secrets, injection, crypto, path traversal, SSRF, and more across multiple languages
- **Gitleaks**: Secret detection with thoughtful allowlist configuration for test fixtures
- **SHA-pinned actions**: All GitHub Actions are pinned by SHA, preventing supply chain attacks via tag manipulation
- **FIPS compliance**: Konflux build uses `GOEXPERIMENT=strictfipsruntime` with CGO_ENABLED=1
- **Hermetic builds**: Konflux pipeline configured with `hermetic: true`
- **Non-root container**: Runtime image runs as UID 1000

**Gaps:**
- Gosec in non-blocking mode (`-no-fail`)
- No dependency scanning (Dependabot/Renovate configuration not visible in repo root)
- No CodeQL workflow
- No container vulnerability scanning

### Agent Rules (Agentic Flow Quality)

**Status**: Present and comprehensive

**Coverage:**
- `CLAUDE.md` (root): CVE fixing instructions, Go version guidelines, npm dependency guidance
- `AGENTS.md` (root): Full project documentation including build commands, testing, architecture, MCP server, configuration, coding conventions
- `.claude/rules/evalhub-service.md`: Path-scoped rule for the API service with ExecutionContext pattern, config system, routing, metrics, testing strategy
- `.claude/rules/evalhub-mcp-service.md`: Path-scoped rule for the MCP service with build/test commands and unit test patterns
- `.claude/skills/fix-fvt-test/SKILL.md`: Custom skill for FVT test fixing

**Quality:**
- Rules are path-scoped using frontmatter (`paths:` field), so they activate only for relevant files
- Comprehensive architecture documentation in AGENTS.md
- Testing strategy clearly documented with tag system and parallel test guidance
- Convention enforcement: `make fmt lint` before commits, conventional commits
- Go version policy explicitly documented (never downgrade go.mod)

**Gaps:**
- No rules for container testing patterns
- No rules for security testing (how to handle Gosec/Semgrep findings)
- No rules for coverage requirements or thresholds

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning** - Integrate Trivy or Grype into the PR workflow to scan the built Docker image. Configure severity thresholds (CRITICAL/HIGH) to block merges. This is the most impactful missing piece for a product shipping via RHOAI.

2. **Make Gosec findings block PRs** - Remove the `-no-fail` flag or configure a severity threshold. Currently, security vulnerabilities can be merged without any CI gate.

### Priority 1 (High Value)

3. **Add golangci-lint** - Replace bare `go vet` with golangci-lint configured with recommended linters (errcheck, gosimple, gocritic, ineffassign, stylecheck, revive, etc.). This catches a much broader class of issues.

4. **Generate SBOM artifacts** - Add Syft or Trivy SBOM generation to the image build pipeline. For RHOAI products, this is increasingly required for compliance.

5. **Add image signing** - Integrate cosign for image signing and attestation to support supply chain verification.

### Priority 2 (Nice-to-Have)

6. **Add CodeQL workflow** - For deeper semantic analysis beyond what Gosec provides, particularly for Go and Python code.

7. **Add concurrency control to ci.yml** - Prevent redundant CI runs on rapid PR pushes:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

8. **Add contract tests for REST API** - Use the OpenAPI spec (`docs/src/openapi.yaml`) to generate contract tests that validate the API implementation matches the spec.

9. **Add performance testing** - Consider adding k6 or similar load testing for the API endpoints, especially the evaluation job creation path.

## Comparison to Gold Standards

| Dimension | eval-hub | odh-dashboard (Gold) | notebooks (Gold) | kserve (Gold) |
|-----------|----------|---------------------|-------------------|---------------|
| Unit Tests | 8.5 - Strong Go stdlib tests, good test-to-code ratio | 9 - Multi-framework, snapshot tests | 7 - Image-focused testing | 9 - envtest, extensive mocks |
| Integration/E2E | 9.0 - godog BDD, MCP E2E, K8s tests | 9 - Cypress E2E, contract tests | 8 - Multi-layer image validation | 9 - Multi-version KServe testing |
| Build Integration | 7.5 - PR Docker build+dry-run, Konflux pipeline | 8 - Module Federation validation | 7 - Image build validation | 7 - Operator integration |
| Image Testing | 7.0 - Dry-run, multi-arch, no vuln scan | 7 - Basic image validation | 10 - 5-layer validation, Trivy | 8 - Multi-version images |
| Coverage Tracking | 8.0 - Codecov, fail_ci_if_error, treemap | 9 - Coverage enforcement + trends | 6 - Basic coverage | 9 - Threshold enforcement |
| CI/CD Automation | 9.0 - 11 workflows, SHA-pinned, matrix builds | 9 - Comprehensive pipeline | 8 - Image-centric CI | 9 - Well-organized workflows |
| Agent Rules | 8.5 - CLAUDE.md, AGENTS.md, path-scoped rules | 9 - Comprehensive multi-layer rules | 3 - Minimal | 2 - None |
| **Security** | **6.5** - Gosec (non-blocking), Semgrep, Gitleaks | **8** - CodeQL, scanning | **8** - Trivy, SBOM | **8** - CodeQL, scanning |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - Main CI (tests, lint, coverage, docs, Docker build, security scan)
- `.github/workflows/ci-python-server.yml` - Python server CI (path-scoped)
- `.github/workflows/ci-mcp.yml` - MCP server CI (path-scoped)
- `.github/workflows/commitlint.yml` - Conventional commit enforcement
- `.github/workflows/required-reviewer-approvals.yml` - Reviewer approval verification
- `.github/workflows/publish-python-server.yml` - PyPI wheel build/publish pipeline
- `.github/workflows/release-mcp.yml` - MCP GitHub Release on tag push
- `.github/workflows/check-trustyai-service-operator-configmap-sync.yml` - ConfigMap sync check
- `.github/workflows/sync-branch-incubation.yaml` - Branch sync
- `.github/workflows/sync-branch-stable.yaml` - Branch sync
- `.tekton/odh-eval-hub-pull-request.yaml` - Konflux PR pipeline

### Testing
- `tests/features/*.feature` - 10 BDD feature files (godog)
- `tests/features/*_test.go` - FVT step definitions and suite
- `tests/kubernetes/` - Kubernetes-specific FVT tests
- `tests/mlflow/` - MLflow integration tests
- `tests/mcp/scripts/` - MCP E2E test scripts (4 parts)
- `tests/mcp/vscode/test-scripts/` - VS Code/Cursor MCP integration tests (8 suites)
- `python-server/tests/` - Python server tests (3 files)
- `internal/**/*_test.go` - Unit tests co-located with source

### Code Quality
- `.pre-commit-config.yaml` - Pre-commit hooks (Ruff, mypy, commitizen, Go tests)
- `semgrep.yaml` - Unified Semgrep security rules (v3.0.0)
- `.gitleaks.toml` - Secret detection configuration
- `python-server/pyproject.toml` - Ruff linting config for Python
- `.markdownlint.json` - Markdown linting
- `.cz.toml` - Commitizen config

### Container Images
- `Containerfile` - Community multi-stage build (UBI9, multi-arch)
- `Dockerfile.konflux` - RHOAI/FIPS build (SHA-pinned bases, strictfipsruntime)
- `.dockerignore` - Build context exclusions

### Coverage
- `codecov.yml` - Codecov configuration (50-75% range thresholds)

### Security
- `semgrep.yaml` - Comprehensive security rules
- `.gitleaks.toml` - Secret detection config
- `.gitleaksignore` - Secret detection allowlist

### Agent Rules
- `CLAUDE.md` - Root-level agent instructions (CVE fixing)
- `AGENTS.md` - Comprehensive project documentation for AI agents
- `.claude/rules/evalhub-service.md` - API service rules (path-scoped)
- `.claude/rules/evalhub-mcp-service.md` - MCP service rules (path-scoped)
- `.claude/skills/fix-fvt-test/SKILL.md` - Custom FVT test fixing skill

### API Documentation
- `docs/src/openapi.yaml` - OpenAPI 3.1.0 source specification
- `redocly.yaml` - Redocly CLI configuration
