---
repository: "opendatahub-io/rhoai-mcp"
overall_score: 6.5
scorecard:
  - dimension: "Unit Tests"
    score: 7.0
    status: "Good coverage across auth, training, model_registry, and composites; gaps in connections, storage, projects, pipelines domains"
  - dimension: "Integration/E2E"
    score: 6.5
    status: "Innovative MCP eval framework with DeepEval + mock cluster; no traditional E2E or live-cluster CI tests"
  - dimension: "Build Integration"
    score: 5.0
    status: "Container builds on PR via Docker Buildx with multi-arch; no Konflux simulation or runtime validation on PR"
  - dimension: "Image Testing"
    score: 5.5
    status: "Multi-stage Containerfile with UBI9 base and healthcheck; no Trivy/Snyk scanning, no SBOM, no startup validation in CI"
  - dimension: "Coverage Tracking"
    score: 4.0
    status: "Coverage generated via pytest-cov and uploaded as artifact; no codecov integration, no threshold enforcement, no PR gating"
  - dimension: "CI/CD Automation"
    score: 7.5
    status: "Well-structured CI with lint, typecheck, multi-version test matrix, concurrency control, and uv caching"
  - dimension: "Agent Rules"
    score: 5.0
    status: "Good CLAUDE.md with TDD principles and architecture docs; no .claude/rules/ directory for test automation patterns"
critical_gaps:
  - title: "No coverage threshold enforcement or codecov integration"
    impact: "Coverage can silently regress with no PR-level feedback; team has no visibility into coverage trends"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No container security scanning (Trivy, Snyk, or CodeQL)"
    impact: "Vulnerabilities in base images and dependencies go undetected until production"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "Missing unit tests for 4 domain modules (connections, storage, projects, pipelines)"
    impact: "~1,200 lines of CRUD logic without test coverage; regressions in core functionality possible"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No secret detection or SAST in CI pipeline"
    impact: "Hardcoded credentials or insecure patterns could be merged without detection"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "Eval workflow is manual-only (workflow_dispatch + PR comment trigger)"
    impact: "MCP quality regressions not caught automatically on every PR"
    severity: "MEDIUM"
    effort: "4-8 hours"
quick_wins:
  - title: "Add codecov integration with coverage threshold"
    effort: "2-3 hours"
    impact: "Immediate visibility into coverage trends; prevent regressions with PR comments and checks"
  - title: "Add Trivy container scanning to CI workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in UBI9 base image and Python dependencies on every PR"
  - title: "Add gitleaks secret detection to CI"
    effort: "1 hour"
    impact: "Prevent accidental credential leaks in commits"
  - title: "Create .claude/rules/ with unit test patterns"
    effort: "2-3 hours"
    impact: "AI-generated tests follow project conventions (pytest-asyncio, mock_k8s patterns)"
recommendations:
  priority_0:
    - "Add codecov.yml with coverage thresholds (e.g., 70% minimum, no regression on PR)"
    - "Add Trivy container scanning as a required CI check on PRs"
    - "Write unit tests for connections, storage, projects, and pipelines domains"
  priority_1:
    - "Add CodeQL or Semgrep SAST scanning to CI pipeline"
    - "Add gitleaks pre-commit hook and CI check for secret detection"
    - "Enable eval workflow on PR push (at least for core tool changes) instead of manual-only"
    - "Create .claude/rules/ directory with test patterns for unit, integration, and eval tests"
  priority_2:
    - "Add SBOM generation (syft/cyclonedx) to container build workflow"
    - "Add image signing/attestation with cosign for release images"
    - "Add pre-commit hooks (.pre-commit-config.yaml) for local developer enforcement"
    - "Add load/performance testing for MCP server concurrent connections"
---

# Quality Analysis: rhoai-mcp

## Executive Summary

- **Overall Score: 6.5/10**
- **Repository Type**: Python MCP (Model Context Protocol) server for Red Hat OpenShift AI
- **Primary Language**: Python 3.10+ (~23K lines source, ~5K lines tests)
- **Framework**: FastMCP + Kubernetes Python client + Pydantic + pluggy
- **Key Strengths**: Well-architected plugin system, comprehensive CI with multi-version matrix, innovative DeepEval-based MCP evaluation framework, strong CLAUDE.md with TDD principles, multi-arch container builds with attestation
- **Critical Gaps**: No coverage enforcement/tracking, no security scanning, missing tests for 4 domain modules, no automated eval runs on PRs
- **Agent Rules Status**: Partial - good CLAUDE.md exists but no `.claude/rules/` directory for structured test patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.0/10 | Good coverage for auth, training, model_registry, composites; 4 domains untested |
| Integration/E2E | 6.5/10 | Innovative MCP eval framework; no traditional E2E or live-cluster CI |
| Build Integration | 5.0/10 | Docker Buildx multi-arch on PR; no Konflux simulation or runtime validation |
| Image Testing | 5.5/10 | Multi-stage UBI9 Containerfile with healthcheck; no scanning or SBOM |
| Coverage Tracking | 4.0/10 | pytest-cov generates XML; no codecov, no thresholds, no PR gating |
| CI/CD Automation | 7.5/10 | Well-structured lint + typecheck + test matrix; caching and concurrency |
| Agent Rules | 5.0/10 | Good CLAUDE.md; missing .claude/rules/ for test automation patterns |

## Critical Gaps

### 1. No Coverage Threshold Enforcement or Codecov Integration
- **Impact**: Coverage can silently regress with no PR-level feedback; team has no visibility into coverage trends
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The CI generates `coverage.xml` and uploads it as an artifact, but there is no codecov/coveralls integration, no minimum coverage threshold, and no PR check that blocks merging on coverage regression. The `pyproject.toml` has `[tool.coverage.run]` and `[tool.coverage.report]` sections but no `fail_under` setting.

### 2. No Container Security Scanning
- **Impact**: Vulnerabilities in UBI9 base image and Python dependencies go undetected until production
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: The container-build workflow builds and pushes images with attestation, but there is no Trivy, Snyk, or Grype scanning step. The image uses `registry.access.redhat.com/ubi9/python-312` which is a good base, but dependency vulnerabilities are not checked.

### 3. Missing Unit Tests for 4 Domain Modules
- **Impact**: ~1,200 lines of CRUD logic in connections, storage, projects, and pipelines domains have zero test coverage
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Details**: The `tests/domains/` directory has tests for inference, model_registry, notebooks, and prompts, but connections (371 lines), storage (311 lines), projects (638 lines), and pipelines (355 lines) have no test files at all. These are core CRUD domains handling K8s resource management.

### 4. No Secret Detection or SAST
- **Impact**: Hardcoded credentials or insecure code patterns could be merged without detection
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No gitleaks, trufflehog, CodeQL, or Semgrep configuration found. The `.env.example` and `.env.eval.example` files exist (good), but there's no automated check preventing real secrets from being committed.

### 5. Eval Workflow Not Automated on PRs
- **Impact**: MCP tool quality regressions not caught until manual trigger
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: The eval workflow (`eval.yml`) only runs on `workflow_dispatch` or when a collaborator comments `@run_evals` on a PR. This means most PRs don't get eval coverage. The framework is sophisticated (DeepEval + mock cluster + Llama Stack) but underutilized.

## Quick Wins

### 1. Add Codecov Integration (2-3 hours)
```yaml
# Add to ci.yml after coverage upload step
- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: coverage.xml
    fail_ci_if_error: true
    token: ${{ secrets.CODECOV_TOKEN }}
```
```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: 60%
    patch:
      default:
        target: 80%
```

### 2. Add Trivy Container Scanning (1-2 hours)
```yaml
# Add to container-build.yml after build step
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 3. Add Gitleaks Secret Detection (1 hour)
```yaml
# Add new job to ci.yml
secrets:
  name: Secret Detection
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    - uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4. Create .claude/rules/ Directory (2-3 hours)
Create structured agent rules for test automation patterns following the project's existing testing conventions (pytest, asyncio, mock_k8s, pydantic fixtures).

## Detailed Findings

### CI/CD Pipeline

**Strengths:**
- 3 well-organized workflows: `ci.yml`, `container-build.yml`, `eval.yml`
- CI runs on push to main + PRs with concurrency control (`cancel-in-progress: true`)
- Multi-version Python matrix (3.10, 3.11, 3.12) with `fail-fast: false`
- uv package manager with GitHub Actions cache enabled
- Container build uses Docker Buildx with GHA cache (`type=gha,mode=max`)
- Multi-architecture support (linux/amd64 + linux/arm64)
- Build attestation with `actions/attest-build-provenance@v2`
- CI status check job aggregates all required checks

**Gaps:**
- No CodeQL/SAST workflow
- No secret scanning workflow
- No container vulnerability scanning
- Eval workflow is manual-trigger only
- No dependency update automation (Dependabot/Renovate)

### Test Coverage

**Strengths:**
- 53 test files covering 10 of 14 source domains/composites
- Test-to-code ratio: 0.61 (53 test files / 87 source files) - adequate
- Lines ratio: ~22% (5,082 test lines / 23,024 source lines)
- Comprehensive auth testing (10 test files covering OIDC, RBAC, middleware, impersonation, token review)
- Good composite testing (7 files: cluster diagnostics, meta tools, neuralnav, training)
- Model registry well-tested (8 test files: auth, benchmarks, catalog, client, discovery, models, tools)
- pytest-asyncio with auto mode for async test support
- pytest-cov configured with branch coverage

**Gaps:**
- No test files for: connections, storage, projects, pipelines domains
- No tests for: domains/quickstarts/tools.py, domains/permissions.py
- Coverage generated but not tracked or enforced
- No `fail_under` in coverage config
- No integration tests against a real K8s cluster in CI
- eval tests not part of standard CI run

### Code Quality Tools

**Strengths:**
- **Ruff**: Comprehensive lint rule set (E, W, F, I, B, C4, UP, ARG, SIM) - 9 rule categories
- **Ruff Format**: Code formatting enforced in CI
- **Mypy**: Strict type checking with `disallow_untyped_defs=true` and `pydantic.mypy` plugin
- **isort**: Import sorting via Ruff's I rules with `known-first-party` config
- All quality checks run in CI on every PR

**Gaps:**
- No pre-commit hooks (`.pre-commit-config.yaml` missing) - developers must remember to run checks locally
- No Ruff security rules enabled (S category for bandit-equivalent checks)
- Per-file ignores exist but are minimal (only mock_client.py)

### Container Image Testing

**Strengths:**
- Multi-stage Containerfile separating builder from runtime
- UBI9 base image (enterprise-grade, regularly patched by Red Hat)
- Non-root execution (USER 1001)
- HEALTHCHECK defined for HTTP transports
- `.containerignore` and `.dockerignore` present
- Kubernetes deployment manifest with security hardening:
  - `runAsNonRoot: true`
  - `readOnlyRootFilesystem: true`
  - `allowPrivilegeEscalation: false`
  - `capabilities: drop: [ALL]`
- Pinned tool versions with SHA256 verification (Helm)

**Gaps:**
- No vulnerability scanning (Trivy/Snyk/Grype) in CI
- No SBOM generation
- No image signing with cosign (attestation exists but not signing)
- No startup validation test in CI (`make test-build` exists but not in CI workflow)
- Container build on PR only builds, doesn't push or scan
- Helm pinned with checksum but oc/kubectl not checksum-verified

### Security Practices

**Strengths:**
- Build attestation via `actions/attest-build-provenance`
- Security-hardened Kubernetes deployment manifest
- OIDC authentication support with token review
- RBAC enforcement with impersonation-based multi-user support
- `RHOAI_MCP_ENABLE_DANGEROUS_OPERATIONS` guard for delete operations
- `RHOAI_MCP_READ_ONLY_MODE` for safety
- .env files in .gitignore
- Non-root container with read-only filesystem

**Gaps:**
- No CodeQL or SAST scanning
- No gitleaks or trufflehog for secret detection
- No dependency scanning (Dependabot/Renovate not configured)
- No container vulnerability scanning
- No security policy (SECURITY.md missing)

### Agent Rules (Agentic Flow Quality)

**Status**: Partial

**What exists:**
- `CLAUDE.md` at root with comprehensive project guidance
- TDD principles documented ("Write tests first", "Red-Green-Refactor")
- Architecture documentation including domain module structure
- Development commands and build instructions
- Code style guidelines (Python 3.10+, Ruff, Mypy)
- `CONTRIBUTING.md` with PR guidelines

**What's missing:**
- No `.claude/` directory
- No `.claude/rules/` with structured test patterns
- No test-type-specific rules (unit, integration, eval)
- No mock pattern guidance for AI agents (mock_k8s, K8s API mocking)
- No AGENTS.md

**Recommendation**: Generate missing rules with `/test-rules-generator` to create:
- `unit-tests.md`: pytest patterns, K8s mock fixtures, async test patterns
- `integration-tests.md`: plugin discovery, cross-domain testing patterns
- `eval-tests.md`: DeepEval scenario patterns, mock cluster setup

### MCP Evaluation Framework (Notable)

This repository has a **distinctive strength** that deserves separate mention: a purpose-built MCP evaluation framework.

**Architecture:**
- DeepEval-based evaluation with configurable LLM judges (Google Vertex, OpenAI, Anthropic)
- Mock Kubernetes cluster for deterministic testing
- Llama Stack integration for inference
- Docker Compose orchestration of 3 services (rhoai-mcp, llama-stack, lightspeed-stack)
- 5 evaluation scenarios: cluster exploration, model deployment, tool discovery, training workflow, troubleshooting
- Historical result tracking with JSONL recording
- Trend analysis and comparison reporting
- PR comment integration for eval results

**Gaps in the eval framework:**
- Not automated on PRs (only manual trigger)
- Requires external LLM API keys
- No baseline/threshold enforcement for eval scores
- Limited to mock cluster (live cluster tests exist but separate)

## Recommendations

### Priority 0 (Critical)

1. **Add codecov integration with coverage thresholds** - Prevent silent coverage regression. Set project target at 60%, patch target at 80%. Upload coverage from Python 3.12 job.

2. **Add Trivy container scanning to CI** - Scan built images for CVEs. Block on CRITICAL/HIGH findings. Generate SARIF for GitHub Security tab.

3. **Write unit tests for untested domains** - connections (84+86+201=371 lines), storage (67+85+159=311 lines), projects (213+112+101+212=638 lines), pipelines (83+118+139+15=355 lines). Follow existing patterns in training and model_registry tests.

### Priority 1 (High Value)

4. **Add CodeQL or Semgrep SAST scanning** - Python CodeQL catches injection, XSS, and insecure deserialization patterns.

5. **Add gitleaks secret detection** - Both as pre-commit hook and CI check. Simple to add, prevents credential leaks.

6. **Automate eval runs on PR** - At minimum, run evals when files in `src/rhoai_mcp/domains/` change. Could use a lightweight mock-only eval subset.

7. **Create .claude/rules/ for test patterns** - Document pytest conventions, K8s mock patterns, async test setup, and eval scenario structure.

### Priority 2 (Nice-to-Have)

8. **Add SBOM generation** - Use syft or cyclonedx-python to generate SBOM during container build. Required for supply chain compliance.

9. **Add cosign image signing** - Sign release images for verification in deployment pipelines.

10. **Add pre-commit hooks** - Enforce ruff, mypy, and gitleaks locally before push.

11. **Add Dependabot/Renovate** - Automate dependency updates for both Python packages and GitHub Actions.

12. **Add load testing** - The MCP server handles concurrent connections; test under load with tools like locust or k6.

## Comparison to Gold Standards

| Dimension | rhoai-mcp | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 7.0 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 6.5 | 9.0 | 8.0 | 9.0 |
| Build Integration | 5.0 | 8.0 | 7.0 | 7.0 |
| Image Testing | 5.5 | 7.0 | 9.0 | 7.0 |
| Coverage Tracking | 4.0 | 8.0 | 6.0 | 9.0 |
| CI/CD Automation | 7.5 | 9.0 | 8.0 | 9.0 |
| Agent Rules | 5.0 | 8.0 | 3.0 | 3.0 |
| **Overall** | **6.5** | **8.5** | **7.0** | **8.0** |

**Key differentiator**: rhoai-mcp has a unique MCP evaluation framework that is ahead of most repositories in the ecosystem. If automated and enforced, this could become a gold standard for MCP server testing.

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - Main CI: lint, typecheck, test matrix
- `.github/workflows/container-build.yml` - Container build + push + attestation
- `.github/workflows/eval.yml` - MCP evaluation (manual trigger)
- `Makefile` - Development and container management targets

### Testing
- `tests/` - Unit and integration tests (53 test files)
- `tests/conftest.py` - Shared fixtures (K8s mocks, sample resources)
- `tests/integration/` - Plugin discovery integration tests
- `tests/auth/` - Authentication and RBAC tests (10 files)
- `tests/domains/` - Domain-specific tests
- `tests/composites/` - Composite tool tests
- `evals/` - DeepEval MCP evaluation framework
- `evals/scenarios/` - 5 evaluation scenarios

### Code Quality
- `pyproject.toml` - Ruff, mypy, pytest, coverage configuration
- `CLAUDE.md` - Agent development guidelines

### Container
- `Containerfile` - Multi-stage UBI9-based build
- `.containerignore` / `.dockerignore` - Build context exclusions
- `docker-compose.eval.yml` - Eval stack orchestration
- `deploy/kubernetes/deployment.yaml` - K8s deployment manifests

### Source
- `src/rhoai_mcp/` - Main package (87 source files, ~23K lines)
- `src/rhoai_mcp/domains/` - 10 domain modules
- `src/rhoai_mcp/composites/` - 4 composite modules
- `src/rhoai_mcp/auth/` - Authentication subsystem
