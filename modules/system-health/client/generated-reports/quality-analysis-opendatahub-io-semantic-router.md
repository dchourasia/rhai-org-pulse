---
repository: "opendatahub-io/semantic-router"
overall_score: 8.2
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Strong coverage with 160 test files across Go/Rust/Python/TypeScript; 35% test-to-source ratio"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Exceptional E2E framework with 53 test cases across 18 profiles; Kind-based K8s testing automated on PRs"
  - dimension: "Build Integration"
    score: 7.5
    status: "PR-time Docker builds for 6 images (amd64); multi-arch on merge; no Konflux simulation"
  - dimension: "Image Testing"
    score: 7.0
    status: "Multi-stage cross-compiled Dockerfiles with PR-time build validation; no runtime image testing or vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 4.0
    status: "Codecov only for operator subproject; no coverage tracking for core semantic-router"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "23 workflows with smart change detection, concurrency control, caching, and matrix-based parallel testing"
  - dimension: "Agent Rules"
    score: 9.0
    status: "Comprehensive AGENTS.md with layered rule system, 35+ agent docs, playbooks, ADRs, and tech-debt tracking"
critical_gaps:
  - title: "No coverage tracking for core semantic-router"
    impact: "Cannot measure or enforce test coverage for the main Go codebase (272 source files)"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container security scanning (Trivy/Snyk/CodeQL)"
    impact: "Vulnerability detection relies entirely on manual review; no automated supply chain security"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No SBOM generation or image signing"
    impact: "No software bill of materials for supply chain compliance; images are unsigned"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "No secret detection in CI"
    impact: "Committed secrets or API keys could go undetected"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Immediate vulnerability detection for all 6 container images built on PRs"
  - title: "Add codecov integration for core Go tests"
    effort: "2-3 hours"
    impact: "Coverage visibility and enforcement for 272 Go source files"
  - title: "Add Gitleaks secret detection to pre-commit"
    effort: "1 hour"
    impact: "Prevent accidental secret commits across all languages"
  - title: "Add CodeQL/SAST workflow"
    effort: "2-3 hours"
    impact: "Automated static security analysis for Go, Rust, Python, and TypeScript"
recommendations:
  priority_0:
    - "Add coverage tracking (codecov) for core semantic-router Go tests — currently only operator has it"
    - "Add container image vulnerability scanning (Trivy) to PR and nightly workflows"
  priority_1:
    - "Add SBOM generation and image signing (Cosign/Sigstore) to Docker publish pipeline"
    - "Add CodeQL or gosec SAST scanning as a PR workflow"
    - "Add secret detection (Gitleaks) to pre-commit hooks and CI"
  priority_2:
    - "Add dashboard frontend unit test coverage (currently only e2e specs)"
    - "Add Rust code coverage tracking for candle-binding/ml-binding/nlp-binding"
    - "Add contract tests between Go router and dashboard backend API"
---

# Quality Analysis: semantic-router (opendatahub-io/semantic-router)

## Executive Summary

- **Overall Score: 8.2/10**
- **Repository Type**: Multi-language monorepo (Go primary, Rust bindings, Python CLI/tools, TypeScript dashboard)
- **Framework**: LLM inference routing system with Envoy ExtProc, Kubernetes operator, Helm charts
- **Key Strengths**: Exceptional CI/CD automation (23 workflows), comprehensive E2E testing (53 test cases, 18 profiles), outstanding agent rules ecosystem
- **Critical Gaps**: No coverage tracking for core codebase, no container security scanning, no SBOM/signing
- **Agent Rules Status**: Present and comprehensive — layered system with AGENTS.md, 35+ docs, playbooks, ADRs, and tech-debt register

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Strong: 160 test files, 35% ratio, Go/Rust/Python/TS coverage |
| Integration/E2E | 9.0/10 | Exceptional: 53 test cases, 18 profiles, Kind K8s, automated on PRs |
| **Build Integration** | **7.5/10** | **PR-time Docker builds (6 images); no Konflux simulation** |
| Image Testing | 7.0/10 | Multi-stage cross-compiled builds validated on PR; no runtime/vulnerability scanning |
| Coverage Tracking | 4.0/10 | Only operator has codecov; core codebase has zero coverage tracking |
| CI/CD Automation | 9.5/10 | 23 workflows, smart change detection, concurrency, caching, matrix |
| Agent Rules | 9.0/10 | Comprehensive layered system with docs, playbooks, ADRs, guardrails |

## Critical Gaps

### 1. No Coverage Tracking for Core Semantic Router
- **Impact**: 272 Go source files with 126 test files but no way to measure, track, or enforce coverage
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The operator subproject (`deploy/operator/`) has Codecov integration with `coverprofile` and upload, but the core `src/semantic-router/` codebase — which is the heart of the project — has no coverage generation in `make test` and no codecov upload in the `test-and-build.yml` workflow
- **Fix**: Add `-coverprofile=coverage.out -covermode=atomic` to the Go test command and add `codecov/codecov-action@v4` step

### 2. No Container Security Scanning
- **Impact**: 15+ Dockerfiles produce images with no automated vulnerability scanning; security issues discovered only at deployment time
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No Trivy, Snyk, Grype, or any CVE scanner in any workflow. The Docker publish workflow builds and pushes without scanning. No `.trivyignore` exists.
- **Fix**: Add Trivy scan step after image build in `docker-publish.yml` PR job

### 3. No SBOM Generation or Image Signing
- **Impact**: No software bill of materials for compliance; images pushed to GHCR are unsigned
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: Multi-arch images are published to GHCR but without provenance attestation, SBOM, or Cosign signatures

### 4. No Secret Detection in CI
- **Impact**: API keys, tokens, or credentials could be committed without detection
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No Gitleaks, TruffleHog, or similar tool in pre-commit hooks or CI workflows

## Quick Wins

### 1. Add Trivy Scanning to PR Workflow (1-2 hours)
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.tags.outputs.tags }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 2. Add Codecov for Core Tests (2-3 hours)
Add to `test-and-build.yml` after the test step:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: src/semantic-router/coverage.out
    flags: core
    name: semantic-router-coverage
```

### 3. Add Gitleaks to Pre-commit (1 hour)
Add to `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
    - id: gitleaks
```

### 4. Add CodeQL Workflow (2-3 hours)
Create `.github/workflows/codeql.yml` with Go, Python, and JavaScript analysis.

## Detailed Findings

### CI/CD Pipeline

**Outstanding CI/CD infrastructure with 23 workflows:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test-and-build.yml` | PR + push + nightly | Core unit tests with Milvus + Redis |
| `pre-commit.yml` | PR + push | Linting, formatting, agent fast gate |
| `integration-test-k8s.yml` | PR + push | 14-profile Kind-based E2E tests |
| `integration-test-helm.yml` | PR + push | Helm lint + template validation |
| `integration-test-memory.yml` | PR (path-filtered) | Memory features with Milvus |
| `integration-test-vllm-sr-cli.yml` | PR | CLI integration tests |
| `dashboard-test.yml` | PR (dashboard changes) | Dashboard lint + type check + build |
| `operator-ci.yml` | PR (operator changes) | Operator lint + test + coverage |
| `performance-test.yml` | PR (perf-related paths) | Benchmarks with PR commenting |
| `performance-nightly.yml` | Nightly | Full performance regression suite |
| `docker-publish.yml` | PR + push | 6 images: amd64 on PR, multi-arch on push |
| `docker-release.yml` | Release | Release image publishing |
| `helm-publish.yml` | Push | Helm chart publishing |

**Strengths:**
- Smart change detection (`ci-changes.yml` reusable workflow) — tests only run when relevant files change
- Concurrency control on all workflows with `cancel-in-progress: true`
- Comprehensive caching (Rust, Go, Node, pre-commit, models)
- Matrix strategy for E2E profiles with `fail-fast: false`
- Test artifacts and reports uploaded on failure
- Performance benchmarks with PR commenting

**Gaps:**
- No security scanning workflows (CodeQL, Trivy, Gitleaks)
- No dependency update automation (Renovate/Dependabot)

### Test Coverage

**Unit Tests (8.5/10)**
- **160 total test files** across the codebase
- Core Go router: 126 test files for 272 source files (46% file ratio)
- Operator: 5 test files with coverage tracking
- Dashboard backend: 8 test files (Go handlers)
- Dashboard frontend: 1 unit test + 10 Playwright e2e specs
- Rust bindings: test support in candle-binding, onnx-binding
- Testing framework: Go standard `testing` + `testify`
- Build tags for integration tests (`integration`, `milvus`)

**Integration/E2E Tests (9.0/10)**
- **Custom E2E framework** (`e2e/`) with Go-based test runner
- **53 test case files** covering:
  - AI Gateway, AIBrix, Istio, LLM-D, Dynamo integration
  - Routing strategies, model selection, MCP classification
  - RAG, vector store, streaming, rate limiting
  - PII detection, jailbreak detection, hallucination
  - Response API, auth/RBAC, multi-replica health
  - Performance throughput, resource utilization
- **18 E2E profiles** with dedicated Kubernetes manifests
- Kind cluster provisioning automated in CI
- Profile-specific change detection — only affected profiles test on PR
- CLI integration tests (Python-based)
- Memory integration tests with Docker Compose (Milvus + llm-katan)

**Performance Tests**
- Dedicated benchmark suite in `perf/` with Go benchmarks
- Configurable SLO thresholds in `perf/config/thresholds.yaml`
- Regression detection with percentage-based thresholds
- PR-time benchmarks with result commenting
- Nightly full performance suite

### Code Quality

**Linting (Strong)**
- `golangci-lint v2.5.0` with 12 linters enabled:
  - `bodyclose`, `copyloopvar`, `depguard`, `errorlint`, `gocritic`
  - `gosec` (security), `importas`, `misspell`, `revive`, `staticcheck`
  - `testifylint`, `unconvert`
- Formatters: `gofumpt` + `gci` (import grouping)
- ESLint for dashboard frontend and website
- Rust: `clippy` + `rustfmt` via pre-commit
- Python: `black` formatter
- Markdown: `markdownlint`
- YAML: `yamllint`
- Shell: `shellcheck`
- Codespell: spelling checker

**Pre-commit Hooks (Strong)**
- `.pre-commit-config.yaml` with hooks for Go, Rust, Python, JS/TS, Markdown, YAML, Shell
- Enforced in CI via `make precommit-check`
- Agent fast gate (`make agent-fast-gate`) validates changed files against structural rules

**Static Analysis**
- `gosec` enabled in golangci-lint (with reasonable exclusions for dev/test)
- No standalone SAST tool (CodeQL, Semgrep)
- No dependency vulnerability scanning

### Container Images

**Build Process (7.0/10)**
- 15+ Dockerfiles for various components
- Multi-stage cross-compilation for amd64/arm64 (extproc, dashboard, vllm-sr, llm-katan)
- ROCm variants for AMD GPU support (extproc-rocm, vllm-sr-rocm)
- PR-time builds: 6 images built on amd64 only (fast feedback)
- Push/merge builds: full multi-arch with manifest merge
- GHA build cache (`type=gha`) for layer reuse
- Docker Buildx with QEMU for arm64

**Gaps:**
- No runtime validation of built images
- No Trivy/Snyk vulnerability scanning
- No SBOM generation
- No image signing (Cosign/Sigstore)
- No image startup testing in CI

### Security

**Current State (Weak)**
- `gosec` linter enabled (basic Go security checks)
- PII detection and jailbreak detection as application features (not CI security)
- No CodeQL or SAST workflow
- No container vulnerability scanning
- No dependency scanning (Dependabot/Renovate/Snyk)
- No secret detection (Gitleaks/TruffleHog)
- No SBOM or supply chain attestation
- GHCR images are pushed unsigned

### Agent Rules (Agentic Flow Quality)

**Status: Present and Comprehensive (9.0/10)**

This is one of the most thorough agent rule systems observed across repositories:

- **`AGENTS.md`** at root: structured entry point with read-first order, supported environments, non-negotiable rules, canonical commands, and rule layer index
- **35+ agent documentation files** in `docs/agent/`:
  - Architecture guardrails, module boundaries, governance
  - Testing strategy, feature-complete checklist
  - Repo map, change surfaces, environments
  - Context management, glossary
  - 4 playbooks (e2e-selection, go-router, rust-bindings, vllm-sr-cli-docker)
  - 3 ADRs (architecture decision records)
  - 11 tech-debt entries with structured index
  - 3 execution plans
- **Executable rule layer** in `tools/agent/`:
  - `repo-manifest.yaml` — repository structure and ownership
  - `task-matrix.yaml` — task routing and validation rules
  - `skill-registry.yaml` — agent skill definitions
  - `structure-rules.yaml` — structural validation rules
  - `e2e-profile-map.yaml` — E2E profile ownership mapping
  - `context-map.yaml` — context boundaries
- **Agent-specific Makefile targets** (`tools/make/agent.mk`):
  - `agent-bootstrap`, `agent-validate`, `agent-scorecard`
  - `agent-lint`, `agent-ci-gate`, `agent-feature-gate`
  - `agent-e2e-affected`, `agent-report`
- **Local `AGENTS.md` files** in hotspot directories for sub-tree rules
- **Agent fast gate** enforced in CI pre-commit workflow

**Gaps:**
- No `.claude/rules/` directory with test-type-specific rules (unit-tests.md, e2e-tests.md)
- Agent rules are documentation-oriented; could benefit from machine-readable test pattern templates

## Recommendations

### Priority 0 (Critical)

1. **Add coverage tracking for core semantic-router** — Currently the most impactful gap. Add `-coverprofile` to `make test-semantic-router` and upload to Codecov in `test-and-build.yml`. Set initial threshold at current baseline, then ratchet up.

2. **Add container vulnerability scanning** — Add Trivy to `docker-publish.yml` PR builds. Block on CRITICAL/HIGH findings. This is a standard security practice for any project publishing container images.

### Priority 1 (High Value)

3. **Add CodeQL/SAST workflow** — Create a dedicated security scanning workflow for Go, Python, and TypeScript. GitHub CodeQL is free for public repos and catches real vulnerabilities.

4. **Add SBOM generation and image signing** — Add `syft` for SBOM and `cosign` for image signing to the Docker publish pipeline. Important for supply chain security compliance.

5. **Add secret detection** — Add Gitleaks to both pre-commit hooks and CI. Trivial effort with high security value.

6. **Add Dependabot or Renovate** — Automate dependency updates for Go, Rust, Python, and npm. Currently no automated dependency management.

### Priority 2 (Nice-to-Have)

7. **Dashboard frontend unit test coverage** — Currently only has Playwright e2e specs and 1 unit test. Add Vitest/Jest unit tests for React components.

8. **Rust code coverage** — Add `cargo-tarpaulin` or `llvm-cov` for candle-binding, ml-binding, nlp-binding, and upload to Codecov.

9. **Contract tests** — Add contract tests between Go router gRPC/HTTP API and dashboard backend API consumers.

10. **Add `.claude/rules/` test pattern templates** — Supplement the excellent agent docs with machine-readable test creation rules for each test type.

## Comparison to Gold Standards

| Dimension | semantic-router | odh-dashboard | notebooks | kserve |
|-----------|----------------|---------------|-----------|--------|
| Unit Tests | 8.5 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 9.0 | 9.0 | 8.0 | 9.5 |
| Build Integration | 7.5 | 8.0 | 9.0 | 7.0 |
| Image Testing | 7.0 | 7.0 | 9.5 | 6.0 |
| Coverage Tracking | 4.0 | 8.0 | 5.0 | 9.0 |
| CI/CD Automation | 9.5 | 9.0 | 8.0 | 8.5 |
| Agent Rules | 9.0 | 8.0 | 3.0 | 2.0 |
| **Overall** | **8.2** | **8.4** | **7.5** | **7.6** |

**Notable strengths vs. gold standards:**
- CI/CD automation is best-in-class (23 workflows with smart change detection)
- Agent rules system is the most comprehensive observed
- E2E framework is exceptionally well-designed (53 test cases, 18 profiles, profile-specific change detection)
- Performance testing with SLO thresholds is ahead of most projects

**Notable gaps vs. gold standards:**
- Coverage tracking is significantly behind odh-dashboard and kserve
- Security scanning is absent (all gold standards have at least Trivy or CodeQL)
- No SBOM/signing (notebooks and kserve have this)

## File Paths Reference

### CI/CD Workflows (23 total)
- `.github/workflows/test-and-build.yml` — Core unit tests
- `.github/workflows/pre-commit.yml` — Linting and formatting
- `.github/workflows/integration-test-k8s.yml` — K8s E2E (18 profiles)
- `.github/workflows/integration-test-helm.yml` — Helm validation
- `.github/workflows/integration-test-memory.yml` — Memory integration
- `.github/workflows/docker-publish.yml` — Container image builds
- `.github/workflows/performance-test.yml` — PR benchmarks
- `.github/workflows/operator-ci.yml` — Operator tests + coverage
- `.github/workflows/dashboard-test.yml` — Dashboard checks

### Test Infrastructure
- `src/semantic-router/pkg/` — 126 Go unit test files
- `e2e/testcases/` — 53 E2E test cases
- `e2e/profiles/` — 18 E2E profiles
- `perf/benchmarks/` — Performance benchmarks
- `perf/config/thresholds.yaml` — SLO thresholds
- `dashboard/frontend/e2e/` — 10 Playwright specs
- `dashboard/backend/handlers/` — 8 Go handler tests

### Code Quality
- `tools/linter/go/.golangci.yml` — 12 Go linters
- `.pre-commit-config.yaml` — Multi-language hooks
- `website/eslint.config.mjs` — Website ESLint
- `dashboard/frontend/eslint.config.js` — Dashboard ESLint

### Container Images (15+ Dockerfiles)
- `tools/docker/Dockerfile.extproc` — Main ExtProc image (cross-compiled)
- `tools/docker/Dockerfile.extproc-rocm` — AMD ROCm variant
- `src/vllm-sr/Dockerfile` — vLLM-SR Python image
- `dashboard/backend/Dockerfile` — Dashboard backend
- `e2e/testing/llm-katan/Dockerfile` — Test mock LLM

### Agent Rules
- `AGENTS.md` — Root agent entry point
- `docs/agent/` — 35+ agent documentation files
- `tools/agent/` — Executable rule layer (YAML configs)
- `tools/make/agent.mk` — Agent Makefile targets
