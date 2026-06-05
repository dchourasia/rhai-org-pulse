---
repository: "openclaw/openclaw"
overall_score: 9.1
scorecard:
  - dimension: "Unit Tests"
    score: 9.5
    status: "6,171 test files with Vitest; 0.66 test-to-source ratio; extensive domain coverage"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Contract tests, boundary tests, live E2E with Mantis, Docker E2E lanes, multi-OS matrix"
  - dimension: "Build Integration"
    score: 8.5
    status: "PR-time build artifacts, Docker build validation, package acceptance pipeline"
  - dimension: "Image Testing"
    score: 8.0
    status: "Multi-stage Docker builds, install smoke tests, Docker E2E, release validation"
  - dimension: "Coverage Tracking"
    score: 7.0
    status: "Vitest coverage-v8 integration, Swift codecov, no enforced PR coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "56 workflows, 2200-line main CI, preflight routing, concurrency control, Blacksmith runners"
  - dimension: "Agent Rules"
    score: 9.5
    status: "277-line AGENTS.md, comprehensive coding/testing/review/security guidelines, copilot instructions"
critical_gaps:
  - title: "No enforced coverage thresholds on PRs"
    impact: "Coverage can silently regress with no gate blocking merges"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "No container vulnerability scanning (Trivy/Snyk) in PR or release pipeline"
    impact: "Vulnerable base images or dependencies may ship undetected in Docker releases"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No SBOM generation or image signing"
    impact: "Supply chain transparency gaps; no attestation for published container images"
    severity: "MEDIUM"
    effort: "4-8 hours"
quick_wins:
  - title: "Add Trivy container scanning to Docker release workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in base images and runtime dependencies before publishing"
  - title: "Add codecov/coveralls PR integration with thresholds"
    effort: "2-4 hours"
    impact: "Prevent coverage regression with automatic PR gating"
  - title: "Add SBOM generation to Docker release pipeline"
    effort: "2-3 hours"
    impact: "Supply chain transparency and compliance readiness"
recommendations:
  priority_0:
    - "Add container image vulnerability scanning (Trivy) to PR and release workflows"
    - "Enforce minimum coverage thresholds with codecov/coveralls PR checks"
  priority_1:
    - "Add SBOM generation and image signing (cosign) to Docker release pipeline"
    - "Add multi-architecture (ARM64) Docker image builds to release workflow"
  priority_2:
    - "Add fuzz testing for parser/protocol surfaces"
    - "Formalize performance regression thresholds with automated Kova baseline enforcement"
---

# Quality Analysis: OpenClaw

## Executive Summary

- **Overall Score: 9.1/10**
- **Repository Type**: Full-stack TypeScript personal AI assistant (Node.js/Bun, React UI, macOS/iOS/Android native apps)
- **Primary Language**: TypeScript (ESM, strict mode)
- **Testing Framework**: Vitest with coverage-v8
- **Key Strengths**: Exceptional test coverage (6,171 test files), world-class CI/CD automation (56 workflows), deep security analysis (25 CodeQL configs + OpenGrep + custom QL queries), comprehensive agent rules, contract/boundary testing, live E2E via Mantis
- **Critical Gaps**: No container vulnerability scanning, no enforced coverage thresholds, no SBOM/image signing
- **Agent Rules Status**: Excellent — 277-line AGENTS.md with coding, testing, review, security, and architecture guidance

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.5/10 | 6,171 test files; Vitest; 0.66 test-to-source ratio; 160+ vitest configs for sharded execution |
| Integration/E2E | 9.0/10 | Contract tests, boundary tests, Mantis live E2E, Docker E2E lanes, multi-OS CI matrix |
| **Build Integration** | **8.5/10** | **PR build artifacts, Docker build validation, package acceptance with smoke/package/product/full profiles** |
| Image Testing | 8.0/10 | Install smoke tests, Docker E2E, release validation; missing vuln scanning and SBOM |
| Coverage Tracking | 7.0/10 | coverage-v8 integration, Swift codecov; no enforced PR thresholds |
| CI/CD Automation | 9.5/10 | 56 workflows, 2200-line CI, preflight routing, Blacksmith runners, concurrency control |
| Agent Rules | 9.5/10 | 277-line AGENTS.md, scoped AGENTS.md per subsystem, copilot instructions, Codex prompts |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: Docker images published to GHCR without CVE scanning; vulnerable base images or runtime dependencies may ship to users
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The Docker release workflow (`docker-release.yml`) builds and pushes multi-arch images but includes no Trivy, Snyk, or Grype scanning step. Base images are pinned to SHA256 digests (excellent), but no runtime CVE check occurs.

### 2. No Enforced Coverage Thresholds
- **Impact**: Test coverage can silently regress without any PR gate
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: Coverage generation exists (`pnpm test:coverage` using `@vitest/coverage-v8`), but there is no codecov/coveralls integration for PR reporting, no minimum threshold enforcement, and no coverage diff annotations on PRs.

### 3. No SBOM Generation or Image Signing
- **Impact**: Supply chain transparency gaps for published Docker images
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: No `syft` SBOM generation, no `cosign` image signing, no attestation artifacts in the Docker release pipeline.

## Quick Wins

### 1. Add Trivy Scanning to Docker Release (1-2 hours)
- **Impact**: Catch CVEs in base images and runtime dependencies
- **Implementation**:
```yaml
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.tags.outputs.version }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
- name: Upload Trivy SARIF
  uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: 'trivy-results.sarif'
```

### 2. Add Codecov PR Integration (2-4 hours)
- **Impact**: Prevent coverage regression with automatic PR gating
- **Implementation**: Add `.codecov.yml` with project/patch thresholds and integrate codecov upload in the CI test job.

### 3. Add SBOM Generation (2-3 hours)
- **Impact**: Supply chain transparency and compliance readiness
- **Implementation**: Add `anchore/sbom-action` to Docker release workflow.

## Detailed Findings

### CI/CD Pipeline

**Score: 9.5/10** — This is one of the most sophisticated CI/CD setups in any open-source project.

**Workflow Inventory (56 total)**:
- **Main CI** (`ci.yml`): 2,200 lines, ~25 jobs including preflight routing, build artifacts, sharded checks, contract tests, multi-OS validation (Linux, macOS, Windows), Android builds
- **Security**: CodeQL (4 workflows, 25 config files), OpenGrep PR diff + full repo scans, dependency guard with autoscrub
- **Release**: Docker release (multi-arch), npm release, macOS release, plugin releases
- **E2E/Live**: Mantis scenarios (Discord, Telegram, Slack desktop smoke), Docker E2E lanes, live transport tests
- **Performance**: Kova benchmarking with smoke/diagnostic/soak/release profiles, deep CPU/heap profiling
- **Quality Gates**: Package acceptance pipeline with smoke/package/product/full profiles, install smoke tests, workflow sanity checks

**Concurrency Control**: Every workflow has proper `concurrency.group` with `cancel-in-progress` configured contextually (PRs cancel, pushes to main do not).

**Caching**: pnpm store cache via custom action, Blacksmith runners for faster builds.

**Routing**: Preflight job determines `docs_only`, `docs_changed`, and routes downstream jobs via outputs — avoiding unnecessary CI spend.

### Test Coverage

**Score: 9.5/10 (Unit), 9.0/10 (Integration/E2E)**

**Unit Tests**:
- **6,171 test files** across `src/`, `ui/`, `test/`, `extensions/`
- **9,344 source files** → 0.66 test-to-source ratio (excellent)
- **Framework**: Vitest with 160+ configuration files for sharded, domain-specific test execution
- **Test categories**: unit, unit-fast, unit-security, boundary, contracts (channel-config, channel-registry, channel-session, channel-surface, plugin), extensions, bundled, live, performance, e2e, TUI PTY
- **Fake timers**: Dedicated config for deterministic time-dependent tests

**Contract/Boundary Tests**:
- Plugin contract tests (`vitest.contracts-plugin.config.ts`)
- Channel contract tests (config, registry, session, surface)
- Extension import boundary tests
- Web provider boundary tests
- Plugin SDK package contract validation
- Transport params runtime contracts

**E2E Tests**:
- UI E2E tests (chat flow, cron filters, chat picker pagination)
- Docker E2E lanes via custom `docker-e2e-plan` action
- Mantis scenario-based live E2E (Discord, Telegram, Slack)
- Install smoke tests in Docker containers (root, non-root, various package managers)
- Live tests for gateway, image generation, push notifications

**Multi-OS Testing**: Linux (Ubuntu 24.04), macOS (Swift tests, Node compat), Windows (Blacksmith testbox)

### Code Quality

**Score: 9.0/10**

**Linting**:
- **OxLint** (`.oxlintrc.json`): Type-aware mode with unicorn, typescript, oxc plugins; strict rule set (60+ rules covering correctness, perf, suspicious patterns)
- **OxFmt**: Formatting (replaced Prettier)
- **SwiftLint** + **SwiftFormat**: For macOS/iOS code
- **ktlintCheck**: For Android/Kotlin code
- **Ruff**: For Python skills scripts

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- Basic hygiene: trailing whitespace, EOF fixer, YAML check, large file check, merge conflict detection, private key detection
- ShellCheck for shell scripts
- ActionLint for GitHub Actions
- Zizmor for GitHub Actions security audit
- Ruff for Python skills
- Python tests for skills
- pnpm audit (prod dependencies, high severity)
- OxLint (type-aware)
- OxFmt formatting check
- SwiftLint + SwiftFormat

**Static Analysis**: Comprehensive (see Security section)

### Container Images

**Score: 8.0/10**

**Build Process**:
- Multi-stage Dockerfile: workspace-deps → build → runtime (bookworm-slim)
- Base images pinned to SHA256 digests (excellent reproducibility)
- Bun binary copied from official image (no curl-fetch in build)
- Build-time plugin selection via `OPENCLAW_EXTENSIONS` arg
- Node 24 on bookworm-slim runtime

**Docker Compose**: Production-ready with security hardening (`cap_drop: NET_RAW, NET_ADMIN`, `no-new-privileges`), proper volume mounts, environment isolation

**Install Testing**:
- `install-smoke.yml`: Scheduled daily + on-demand, validates npm/pnpm/Bun install paths
- Multiple Dockerfiles for testing: sandbox, install-sh-smoke, install-sh-nonroot, install-sh-e2e, cleanup-smoke
- Package acceptance pipeline with upgrade survivor testing

**Gaps**:
- No Trivy/Snyk/Grype vulnerability scanning
- No SBOM generation (`syft`)
- No image signing (`cosign`)
- No multi-architecture builds in CI (amd64 only in release; ARM64 appears manual)

### Security

**Score: 9.5/10** — Exceptional security posture for an open-source project.

**CodeQL** (4 workflows, 25 configuration files):
- **Security-critical**: core-auth-secrets, channel-runtime-boundary, network-ssrf-boundary, mcp-process-tool-boundary, plugin-trust-boundary, actions security, Android security, macOS security
- **Quality-critical**: agent-runtime-boundary, config-boundary, gateway-runtime-boundary, memory-runtime-boundary, provider-runtime-boundary, session-diagnostics-boundary, UI control plane, web-media-runtime-boundary, plugin-sdk-package-contract, plugin-sdk-reply-runtime, network-runtime-boundary
- **Custom QL queries**: `managed-proxy-runtime-mutation.ql`, `raw-socket-callsite-classification.ql` in `openclaw-boundary/` qlpack
- Runs on PRs + push to main + daily schedule

**OpenGrep/Semgrep**:
- PR-scoped diff scanning with high-precision rules
- Full repository scan (manual dispatch)
- Custom OpenGrep rules in `security/opengrep/rules/`
- Pinned OpenGrep install script by commit SHA (supply chain hardened)

**Dependency Security**:
- Dependabot with daily interval, grouped updates, npm registry auth
- Dependency guard workflow with autoscrub (auto-removes lockfile changes from untrusted PRs)
- `pnpm audit --production` in pre-commit hooks
- Package trusted sources allowlist (`.github/package-trusted-sources.json`)

**GitHub Actions Security**:
- Zizmor audit in pre-commit hooks and CI
- ActionLint validation
- Pin-by-SHA for critical actions (`actions/checkout`, `docker/login-action`, etc.)
- `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` environment variable
- `pull_request_target` with trusted base checkout pattern in dependency-guard

**Secret Detection**: `detect-private-key` pre-commit hook; Gitleaks-style patterns in CodeQL

### Agent Rules (Agentic Flow Quality)

**Score: 9.5/10** — Among the most comprehensive agent rules in any open-source project.

**AGENTS.md** (277 lines):
- **Status**: Present and extensive; CLAUDE.md is a symlink to AGENTS.md
- **Coverage**: Coding standards, test practices, review policy, security, architecture, CI/CD, GitHub PR workflow, dependency handling, migration/refactor patterns, performance/caching
- **Scoped Rules**: Subsystem-specific AGENTS.md files in `extensions/`, `src/`, `packages/`, `test/`, `docs/`, `ui/`, `scripts/`
- **Copilot Integration**: `.github/instructions/copilot.instructions.md`
- **Codex Prompts**: `.github/codex/prompts/` with specialized agent prompts

**Key Strengths**:
- Explicit test philosophy: "Tests prove behavior/regressions, not every internal branch"
- Code quality philosophy: "Lean code is a goal. No internal shims, aliases, legacy names"
- Dependency inspection mandate: "direct dependency inspection is mandatory when feasible"
- ClawSweeper review policy with structured findings, evidence maps, and best-fix judgments
- Architecture rules: plugin boundaries, SDK contracts, state management (SQLite-first)
- Pre-land validation: mandatory `$autoreview` before landing

**Gaps**: None significant. The agent rules are exceptionally thorough.

### Performance Testing

**Score: 8.0/10**

- **Kova Benchmarks**: Dedicated performance benchmarking tool with smoke/diagnostic/soak/release profiles
- **Daily Schedule**: Runs `cron: "11 5 * * *"`
- **Deep Profiling**: Optional CPU/heap/trace artifacts
- **Live Provider Testing**: OpenAI GPT-5.5 agent-turn lanes
- **Regression Detection**: `fail_on_regression` option (not enabled by default)
- **Gap**: No automated baseline enforcement; regression detection is opt-in

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning**: Integrate Trivy in the Docker release workflow to scan images before pushing to GHCR. This is the single most impactful gap for a project that publishes Docker images.

2. **Enforce coverage thresholds**: Add codecov/coveralls with minimum project coverage (e.g., 70%) and patch coverage (e.g., 80%) requirements on PRs. The infrastructure exists (`@vitest/coverage-v8`); just needs the reporting/gating layer.

### Priority 1 (High Value)

3. **Add SBOM generation and image signing**: Use `anchore/sbom-action` for SBOM and `sigstore/cosign-installer` for image signing in the Docker release pipeline. This is increasingly expected for security-conscious projects.

4. **Enable multi-arch Docker builds**: Add ARM64 builds to the release pipeline for Apple Silicon and ARM-based cloud deployments.

5. **Make performance regression detection mandatory**: Change Kova `fail_on_regression` to `true` for scheduled runs and publish regression alerts.

### Priority 2 (Nice-to-Have)

6. **Add fuzz testing for parsers/protocol handlers**: The gateway protocol, plugin SDK, and channel adapters handle untrusted input — fuzzing would complement the existing CodeQL/OpenGrep analysis.

7. **Add license compliance scanning**: No license scanning detected; useful for a project with many dependencies.

8. **Container runtime validation**: While install smoke tests exist, add explicit container startup health checks (`HEALTHCHECK` in Dockerfile) and validate them in CI.

## Comparison to Gold Standards

| Dimension | OpenClaw | odh-dashboard | notebooks | kserve |
|-----------|----------|---------------|-----------|--------|
| Unit Tests | 9.5 (6,171 files) | 8.5 | 6.0 | 8.0 |
| Contract Tests | 9.0 (boundary+SDK) | 8.0 | N/A | 7.0 |
| E2E Tests | 9.0 (Mantis live) | 8.5 | 7.0 | 9.0 |
| Coverage Tracking | 7.0 (no thresholds) | 8.0 | 5.0 | 8.0 |
| CI/CD | 9.5 (56 workflows) | 8.0 | 7.0 | 8.5 |
| Image Testing | 8.0 (no vuln scan) | 7.0 | 9.0 | 7.0 |
| Security | 9.5 (CodeQL+OpenGrep) | 6.0 | 5.0 | 7.0 |
| Agent Rules | 9.5 (277-line AGENTS.md) | 7.0 | 3.0 | 2.0 |
| Performance | 8.0 (Kova) | 5.0 | N/A | 6.0 |
| **Overall** | **9.1** | **7.3** | **6.0** | **7.3** |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` — Main CI (2,200 lines, 25 jobs)
- `.github/workflows/codeql.yml` — CodeQL security scans
- `.github/workflows/codeql-critical-quality.yml` — CodeQL quality scans
- `.github/workflows/opengrep-precise.yml` — PR-scoped OpenGrep scanning
- `.github/workflows/dependency-guard.yml` — Dependency security guard
- `.github/workflows/docker-release.yml` — Docker image release
- `.github/workflows/install-smoke.yml` — Installation smoke tests
- `.github/workflows/package-acceptance.yml` — Package acceptance pipeline
- `.github/workflows/openclaw-performance.yml` — Kova performance benchmarks
- `.github/workflows/mantis-scenario.yml` — Live E2E scenarios

### Testing
- `test/vitest/` — 160+ Vitest configuration files (sharded, domain-specific)
- `test/vitest/vitest.boundary.config.ts` — Boundary tests
- `test/vitest/vitest.contracts-*.config.ts` — Contract test suites
- `test/vitest/vitest.e2e.config.ts` — E2E test config
- `test/vitest/vitest.unit-security.config.ts` — Security-focused unit tests
- `vitest.config.ts` — Root Vitest configuration

### Code Quality
- `.oxlintrc.json` — OxLint configuration (60+ rules)
- `.pre-commit-config.yaml` — Pre-commit hooks (13 hooks)
- `.github/actionlint.yaml` — ActionLint configuration
- `.github/zizmor.yml` — GitHub Actions security audit config

### Security
- `.github/codeql/` — 25 CodeQL configuration files
- `.github/codeql/openclaw-boundary/` — Custom CodeQL queries
- `security/opengrep/` — Custom OpenGrep/Semgrep rules
- `.semgrepignore` — OpenGrep exclusions
- `.github/package-trusted-sources.json` — Trusted dependency sources

### Container
- `Dockerfile` — Multi-stage production Dockerfile
- `docker-compose.yml` — Production deployment config
- `scripts/docker/` — Docker testing infrastructure
- `scripts/e2e/Dockerfile` — E2E test Dockerfile

### Agent Rules
- `AGENTS.md` — Root agent rules (277 lines)
- `CLAUDE.md` — Symlink to AGENTS.md
- `.github/instructions/copilot.instructions.md` — Copilot-specific instructions
- `.github/codex/prompts/` — Codex agent prompts
