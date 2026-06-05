---
repository: "vllm-project/semantic-router"
overall_score: 8.4
scorecard:
  - dimension: "Unit Tests"
    score: 9.0
    status: "615+ test files across Go/Rust/Python/TS with strong test-to-code ratios"
  - dimension: "Integration/E2E"
    score: 9.5
    status: "81 E2E test cases, 23 profiles, K8s integration tests on PR, memory integration tests"
  - dimension: "Build Integration"
    score: 8.0
    status: "PR-time Docker builds for 8 images, Helm validation, multi-arch on merge"
  - dimension: "Image Testing"
    score: 7.0
    status: "20+ Dockerfiles, PR-time amd64 builds, multi-arch on push, but no runtime validation or Trivy"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "No codecov/coveralls integration, no coverage thresholds, no PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "33 workflows, smart path filtering, concurrency control, caching, nightly builds"
  - dimension: "Agent Rules"
    score: 9.5
    status: "Comprehensive CLAUDE.md, AGENTS.md, .cursorrules, full agent harness with skill registry"
critical_gaps:
  - title: "No coverage tracking or enforcement"
    impact: "Cannot measure test coverage trends, no way to prevent coverage regression on PRs"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container vulnerability scanning (Trivy/Snyk/Grype)"
    impact: "Vulnerabilities in base images and dependencies not detected before deployment"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No SBOM generation or image signing"
    impact: "No supply chain attestation for built container images"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "No container runtime validation in CI"
    impact: "Image startup failures not caught until deployment; builds pass but containers may not run"
    severity: "MEDIUM"
    effort: "4-8 hours"
quick_wins:
  - title: "Add codecov integration to test-and-build workflow"
    effort: "2-4 hours"
    impact: "Visibility into coverage trends, PR coverage diffs, coverage badges"
  - title: "Add Trivy container scanning to docker-publish workflow"
    effort: "1-2 hours"
    impact: "Detect CVEs in container images before merge/deploy"
  - title: "Add CodeQL analysis workflow"
    effort: "1-2 hours"
    impact: "GitHub-native SAST for Go, Python, JavaScript/TypeScript code"
  - title: "Add container startup smoke test to PR Docker builds"
    effort: "2-3 hours"
    impact: "Catch image startup failures before merge"
recommendations:
  priority_0:
    - "Add codecov/coveralls integration with Go and Rust coverage generation in CI"
    - "Add Trivy or Grype container image scanning to docker-publish workflow"
  priority_1:
    - "Add CodeQL SAST scanning for Go, Python, and JavaScript"
    - "Add container runtime smoke tests (image starts, health endpoint responds)"
    - "Add SBOM generation and cosign image signing to release workflow"
  priority_2:
    - "Add Gitleaks secret detection to pre-commit and CI"
    - "Add contract tests for API boundaries between Go router and Rust bindings"
    - "Add accessibility testing for the dashboard frontend"
---

# Quality Analysis: vllm-project/semantic-router

## Executive Summary

- **Overall Score: 8.4/10**
- **Repository Type**: Polyglot monorepo (Go router, Rust ML bindings, Python CLI/tools, TypeScript dashboard/website)
- **Framework**: Envoy ExtProc filter, Kubernetes operator, Helm chart, React dashboard
- **Key Strengths**: Exceptional CI/CD automation (33 workflows), comprehensive E2E test suite (81 test cases across 23 profiles), industry-leading agent rules and harness, strong multi-language linting, custom AST-based security scanner
- **Critical Gaps**: No coverage tracking/enforcement, no container vulnerability scanning, no SBOM/image signing
- **Agent Rules Status**: **Exemplary** — CLAUDE.md + AGENTS.md + .cursorrules + full agent harness with task matrix, skill registry, and architecture guardrails

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.0/10 | 615+ test files across Go (452), Rust (47), Python (91), TS (25); strong ratio |
| Integration/E2E | 9.5/10 | 81 E2E test cases, 23 K8s profiles, matrix-based PR testing, memory integration |
| **Build Integration** | **8.0/10** | **PR Docker builds for 8 images, Helm validation, but no Konflux simulation** |
| Image Testing | 7.0/10 | 20 Dockerfiles, PR amd64 builds, multi-arch on push, no runtime validation |
| Coverage Tracking | 3.0/10 | No codecov/coveralls, no thresholds, no PR reporting |
| CI/CD Automation | 9.5/10 | 33 workflows, smart path filtering, concurrency control, comprehensive caching |
| Agent Rules | 9.5/10 | Full agent harness: CLAUDE.md, AGENTS.md, task matrix, skill registry, governance |

## Critical Gaps

### 1. No Coverage Tracking or Enforcement
- **Impact**: Cannot measure test coverage trends; no way to prevent coverage regression on PRs
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Despite having 615+ test files and excellent test infrastructure, there is no codecov.yml, no `.coveragerc`, no coverage generation flags in Make targets, and no coverage upload step in CI. Coverage data is generated locally but never tracked or enforced.

### 2. No Container Vulnerability Scanning
- **Impact**: CVEs in base images and transitive dependencies not detected before deployment
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Neither Trivy, Snyk, Grype, nor any container scanner runs in the docker-publish workflow. The custom AST security scanner (2,083 lines) covers supply chain code patterns but does not scan container images for known CVEs.

### 3. No SBOM Generation or Image Signing
- **Impact**: No supply chain attestation or provenance for built container images
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: No cosign, notation, or SBOM generation (syft/CycloneDX) found in any workflow. For a project under vllm-project, this is a notable gap.

### 4. No Container Runtime Validation
- **Impact**: Image startup failures not caught until deployment; Docker builds pass but containers may not actually run
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: PR builds validate that Docker images compile but do not start them or check health endpoints. No Testcontainers or equivalent runtime validation.

## Quick Wins

### 1. Add Codecov Integration (2-4 hours)
- **Impact**: Visibility into coverage trends, PR diffs, badges
- **Implementation**: Add `-coverprofile=coverage.txt` to Go test commands, `cargo tarpaulin` for Rust, upload via codecov action in test-and-build.yml

### 2. Add Trivy Container Scanning (1-2 hours)
- **Impact**: Detect CVEs in container images before merge/deploy
- **Implementation**: Add `aquasecurity/trivy-action@master` step after Docker build in docker-publish.yml

### 3. Add CodeQL Analysis (1-2 hours)
- **Impact**: GitHub-native SAST for Go, Python, JavaScript/TypeScript
- **Implementation**: Create `.github/workflows/codeql.yml` with standard CodeQL analysis action

### 4. Add Container Startup Smoke Test (2-3 hours)
- **Impact**: Catch image startup failures before merge
- **Implementation**: After PR Docker build, run `docker run --rm -d <image>` and verify health endpoint

## Detailed Findings

### CI/CD Pipeline

**Score: 9.5/10** — One of the most comprehensive CI/CD setups analyzed.

**Workflow Inventory (33 workflows)**:
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| test-and-build | PR, push, nightly, manual | Core test suite (Go, Rust, Helm) with Milvus/Qdrant/Redis/Valkey |
| pre-commit | PR, push | Multi-language linting (Go, Rust, Python, JS/TS, YAML, Markdown, Shell) |
| integration-test-k8s | PR, push, manual | K8s E2E with Kind, dynamic profile matrix (23 profiles) |
| integration-test-memory | PR (path-filtered) | Memory feature integration with Milvus |
| integration-test-vllm-sr-cli | PR | CLI integration tests |
| docker-publish | PR, push, dispatch | Multi-image Docker builds (8 images), multi-arch on merge |
| security-scan | PR, push | Custom AST supply chain security scanner |
| performance-test | PR (path-filtered) | Component benchmarks with baseline comparison |
| dashboard-test | PR | Dashboard lint and type check |
| operator-ci | PR, push | Operator lint, test, build |
| nightly-build | Schedule (2am UTC) | Nightly Docker + Helm publish |
| performance-nightly | Manual | Nightly performance baseline |
| helm-publish | Called | Helm chart publish to GHCR OCI |
| release | Tags | Full release pipeline |
| skill-review | PR (SKILL.md changes) | Automated skill file review |

**Strengths**:
- Smart path-based filtering via reusable `ci-changes.yml` — tests only run when relevant code changes
- Concurrency control on all workflows with `cancel-in-progress: true`
- Comprehensive caching (Rust cargo, Go modules, Node.js, models)
- Real database services in CI (Milvus, Qdrant, Redis, Valkey)
- Dynamic E2E profile matrix based on changed files
- Nightly builds for Docker images and Helm charts
- Anti-spam and issue management automation

### Test Coverage

**Score: 9.0/10** — Excellent breadth and depth across all languages.

**Test Inventory**:
| Language | Source Files | Test Files | Source Lines | Test Lines | Test-to-Code Ratio |
|----------|-------------|------------|--------------|------------|---------------------|
| Go | 927 | 452 | 213,433 | 140,691 | 0.66 |
| Rust | 108 | 47 | 50,566 | 17,083 | 0.34 |
| Python | 288 | 91 | 98,171 | 26,699 | 0.27 |
| TypeScript | — | 25 | — | — | — |
| **Total** | **1,323+** | **615+** | **362,170+** | **184,473+** | **0.51** |

**Testing Framework**:
- **Go**: Standard `testing` package with testify assertions
- **Rust**: Built-in `#[test]` framework with criterion benchmarks
- **Python**: pytest with custom test harnesses
- **TypeScript**: ESLint + TypeScript type checking (no unit test framework detected for dashboard)

**E2E Test Infrastructure**:
- 81 E2E test cases in `e2e/testcases/`
- 23 test profiles covering: Kubernetes, Dashboard, Istio, Agent Gateway, AIBrix, AuthZ-RBAC, Dynamic Config, LLM-D, ML Model Selection, Multi-Endpoint, Multimodal Routing, Production Stack, RAG, Response API, Router Replay, Routing Strategies, Streaming, Vectorstore Registry
- Kind cluster-based testing with full Helm deployment
- Profile-aware change detection — only affected profiles run on PR
- 30,685 lines of E2E test code

**Operator Tests**:
- 7 test files covering controller, webhook, CRD validation, OpenShift integration
- `envtest`-based controller tests

**Benchmark Infrastructure**:
- Performance test suite in `perf/` and `bench/`
- PR-time performance regression testing with baseline comparison
- PR commenting with benchmark results

### Code Quality

**Score: 9.0/10** — Comprehensive multi-language linting with strong enforcement.

**Linting Configuration**:
- **Go**: golangci-lint v2.5.0 with 14+ linters enabled (bodyclose, gosec, staticcheck, revive, errorlint, etc.), 170-line config with thoughtful exclusions
- **Rust**: rustfmt + cargo check (no clippy in pre-commit, only fmt)
- **Python**: Black formatter (no ruff, mypy, or flake8 active)
- **TypeScript/JavaScript**: ESLint configured for website and dashboard
- **YAML**: yaml-lint via Make target
- **Markdown**: markdownlint with custom rules
- **Shell**: ShellCheck for .sh files

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- 11 hooks covering all languages: trailing whitespace, end-of-file, large file check, go fmt, shellcheck, golang-lint, markdown-lint, yaml-lint, JS/TS lint, cargo fmt, cargo check, Black, supply chain security scan, agent changed-files lint
- Custom supply chain security scan hook using tree-sitter AST analysis
- Agent-aware lint gate for changed files

**Static Analysis**:
- Custom AST-based security scanner (2,083 lines) using tree-sitter for Python, Go, JavaScript, TypeScript, Rust
- Three-layer architecture: AST diff extractor, pattern matcher, anomaly scorer
- gosec integrated via golangci-lint
- No CodeQL or Semgrep

### Container Images

**Score: 7.0/10** — Good build infrastructure but gaps in scanning and validation.

**Dockerfile Inventory** (20 Dockerfiles):
- Core: `tools/docker/Dockerfile` (main router), `Dockerfile.extproc`, `Dockerfile.extproc-rocm`
- Dashboard: `dashboard/Dockerfile`, `dashboard/backend/Dockerfile`
- Operator: `deploy/operator/Dockerfile`, `deploy/operator/bundle/Dockerfile`
- ML Bindings: `onnx-binding/Dockerfile.fa-test`, `onnx-binding/Dockerfile.rocm`, `openvino-binding/Dockerfile`
- Tools: `tools/mock-vllm/Dockerfile`, `tools/docker/Dockerfile.precommit`
- Testing: `e2e/testing/anthropic-shim/Dockerfile`, `e2e/testing/llm-katan/Dockerfile`
- Other: `src/vllm-sr/Dockerfile`, `src/vllm-sr/Dockerfile.rocm`, `src/fleet-sim/Dockerfile`

**Build Process**:
- PR builds: amd64-only for 8 images (fast feedback, ~60 min timeout)
- Merge builds: Multi-arch (amd64 + arm64) for 6 images with cross-compilation
- GHA cache for layer reuse
- Build parameter matrix for different image variants
- ROCm variant support (AMD GPU)

**Gaps**:
- No Trivy/Snyk/Grype vulnerability scanning
- No SBOM generation
- No image signing (cosign)
- No container startup/health validation after build

### Security

**Score: 7.5/10** — Unique custom scanner but missing standard tools.

**Strengths**:
- Custom AST-based supply chain security scanner using tree-sitter (multi-language: Python, Go, JS, TS, Rust)
- Runs on PRs and pushes with diff-aware scanning
- Security scan allowlist for known-good domains
- gosec integrated via golangci-lint
- Dedicated security scan workflow with PR commenting

**Gaps**:
- No CodeQL / GitHub Advanced Security
- No Gitleaks or TruffleHog for secret detection
- No container image vulnerability scanning
- No dependency scanning (Dependabot, Renovate)
- No SBOM/SLSA attestation

### Agent Rules (Agentic Flow Quality)

**Score: 9.5/10** — Industry-leading agent infrastructure.

**Status**: Exemplary — one of the most comprehensive agent setups in the open-source ecosystem.

**Files Present**:
- `CLAUDE.md` — Detailed repository overview, dev workflow, architecture rules, validation commands, commit trajectory guidelines
- `AGENTS.md` — Full agent entrypoint with environment matrix, non-negotiable rules, canonical commands, rule layers
- `.cursorrules` — IDE-specific agent guidance mirroring AGENTS.md
- `.github/copilot-instructions.md` — GitHub Copilot-specific instructions
- `.opencode.yaml` — OpenCode configuration
- `.agents/skills/harness/SKILL.md` — Agent harness discovery bridge

**Agent Harness Infrastructure** (under `tools/agent/` and `docs/agent/`):
- `repo-manifest.yaml` — Repository structure definition
- `task-matrix.yaml` — Task routing and classification
- `skill-registry.yaml` — Skill discovery and registration
- `structure-rules.yaml` — Architecture enforcement rules
- `maintainer-policy.yaml` — Maintainer workflow policies
- `e2e-profile-map.yaml` — E2E test profile mapping
- `agent.mk` — Make targets for agent operations
- Full documentation suite: architecture guardrails, change surfaces, environments, governance, feature-complete checklist, repo map, module boundaries, tech debt register

**Unique Features**:
- `make agent-report` — Automated context routing for agents based on changed files
- `make agent-pr-gate` — Full local PR baseline reproduction
- `make agent-feature-gate` — Feature-specific validation
- Architecture scorecard ratchet
- Execution plans with indexed history
- Skill review CI workflow for SKILL.md changes

**Assessment**: This repository sets a gold standard for agent-assisted development. The layered rule system (entry → architecture → testing → executable contract → maintainer ops) is more comprehensive than any repository previously analyzed.

## Recommendations

### Priority 0 (Critical)

1. **Add codecov/coveralls integration with coverage generation**
   - Add `-coverprofile=coverage.txt -covermode=atomic` to Go test commands
   - Add `cargo tarpaulin` or `cargo llvm-cov` for Rust coverage
   - Add codecov action to test-and-build.yml
   - Set minimum coverage thresholds (e.g., 60% for new code)
   - Effort: 4-6 hours

2. **Add container vulnerability scanning**
   - Integrate `aquasecurity/trivy-action` in docker-publish.yml after image build
   - Configure severity thresholds (fail on HIGH/CRITICAL)
   - Add `.trivyignore` for known acceptable vulnerabilities
   - Effort: 2-4 hours

### Priority 1 (High Value)

3. **Add CodeQL SAST scanning**
   - Create `.github/workflows/codeql.yml` for Go, Python, JavaScript
   - Enable GitHub Advanced Security features
   - Effort: 1-2 hours

4. **Add container runtime smoke tests**
   - After PR Docker builds, start each image and verify it responds on health endpoint
   - Can use `docker run --rm -d` with timeout + curl check
   - Effort: 2-3 hours

5. **Add SBOM and image signing to release workflow**
   - Use `anchore/sbom-action` for SBOM generation
   - Use `sigstore/cosign-installer` for image signing
   - Attach attestations to release artifacts
   - Effort: 4-6 hours

### Priority 2 (Nice-to-Have)

6. **Add Gitleaks secret detection**
   - Add to pre-commit hooks and CI workflow
   - Configure `.gitleaks.toml` with repo-specific allowlists
   - Effort: 1-2 hours

7. **Enable Rust clippy in pre-commit and CI**
   - Currently only cargo fmt and cargo check; clippy would catch more bugs
   - Effort: 1 hour

8. **Add Python type checking (mypy or pyright)**
   - Currently only Black formatting; no type safety enforcement
   - Effort: 2-4 hours

9. **Add Dependabot or Renovate for dependency updates**
   - Automated dependency update PRs for Go, Rust, Python, Node.js
   - Effort: 1-2 hours

10. **Add dashboard frontend unit tests**
    - 25 TS test files exist but appear to be mostly linting; add Jest/Vitest unit tests
    - Effort: 8-16 hours

## Comparison to Gold Standards

| Dimension | semantic-router | odh-dashboard | notebooks | kserve | Best Practice |
|-----------|----------------|---------------|-----------|--------|---------------|
| Unit Tests | 9.0 (615+ files) | 9.0 | 7.0 | 8.0 | 9.0+ |
| Integration/E2E | 9.5 (81 cases, 23 profiles) | 8.0 | 7.0 | 9.0 | 9.0+ |
| Build Integration | 8.0 (PR Docker builds) | 8.0 | 9.0 | 7.0 | 9.0+ |
| Image Testing | 7.0 (build only) | 7.0 | 9.0 (5-layer) | 6.0 | 9.0+ |
| Coverage Tracking | **3.0** (none) | 8.0 | 5.0 | 8.0 | 9.0+ |
| CI/CD Automation | 9.5 (33 workflows) | 8.0 | 8.0 | 8.0 | 9.0+ |
| Agent Rules | **9.5** (full harness) | 7.0 | 3.0 | 2.0 | 9.0+ |
| Security Scanning | 7.5 (custom AST) | 7.0 | 6.0 | 7.0 | 9.0+ |
| **Overall** | **8.4** | 7.8 | 6.8 | 7.0 | 9.0+ |

**Key Differentiators**:
- semantic-router excels in CI/CD automation, E2E breadth, and agent rules — areas where most repos score 2-7
- The custom AST-based security scanner is unique; most repos rely solely on off-the-shelf tools
- The agent harness (CLAUDE.md + AGENTS.md + task matrix + skill registry) is the most comprehensive seen
- The main gap is coverage tracking — an unusual omission given the mature test infrastructure
- Container security scanning is the other notable gap vs. industry best practices

## File Paths Reference

### CI/CD Workflows
- `.github/workflows/test-and-build.yml` — Core test suite
- `.github/workflows/pre-commit.yml` — Multi-language linting
- `.github/workflows/integration-test-k8s.yml` — K8s E2E tests
- `.github/workflows/integration-test-memory.yml` — Memory integration
- `.github/workflows/docker-publish.yml` — Docker image builds
- `.github/workflows/security-scan.yml` — AST security scanning
- `.github/workflows/performance-test.yml` — Performance benchmarks
- `.github/workflows/operator-ci.yml` — Operator CI
- `.github/workflows/dashboard-test.yml` — Dashboard tests
- `.github/workflows/nightly-build.yml` — Nightly builds

### Testing Infrastructure
- `e2e/testcases/` — 81 E2E test cases
- `e2e/profiles/` — 23 E2E test profiles
- `bench/` — Benchmark suite
- `perf/` — Performance tests
- `deploy/operator/controllers/*_test.go` — Operator tests

### Code Quality
- `tools/linter/go/.golangci.yml` — Go linter config (170 lines, 14+ linters)
- `.pre-commit-config.yaml` — 11 pre-commit hooks
- `tools/security/ast_security_scanner.py` — Custom AST security scanner (2,083 lines)

### Agent Rules
- `CLAUDE.md` — Claude Code instructions
- `AGENTS.md` — Agent entrypoint
- `.cursorrules` — Cursor IDE rules
- `.github/copilot-instructions.md` — Copilot instructions
- `tools/agent/` — Agent harness (manifests, scripts, skills)
- `docs/agent/` — Agent documentation (20+ files)

### Container Images
- `tools/docker/Dockerfile*` — Main router images
- `dashboard/Dockerfile` — Dashboard image
- `deploy/operator/Dockerfile` — Operator image
- 20 Dockerfiles total across the monorepo
