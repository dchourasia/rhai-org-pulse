---
repository: "opendatahub-io/openclaw"
overall_score: 8.8
scorecard:
  - dimension: "Unit Tests"
    score: 9.0
    status: "~2,740 test files with Vitest, sharded parallel execution, coverage thresholds enforced (70% lines/functions/statements, 55% branches)"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "38 E2E tests, contract tests for plugins + channels, Docker-based E2E suite, multi-platform (macOS/Windows/Android/iOS)"
  - dimension: "Build Integration"
    score: 8.5
    status: "PR-time Docker image build + smoke test, CLI startup validation, extension build validation, multi-architecture support"
  - dimension: "Image Testing"
    score: 8.5
    status: "Multi-Dockerfile builds validated in CI, install smoke tests, sandbox smoke tests, runtime CLI smoke verification"
  - dimension: "Coverage Tracking"
    score: 8.0
    status: "V8 coverage provider with enforced thresholds (70/70/55/70), lcov output, iOS coverage gate at 43%"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "Sophisticated CI with docs-scope detection, changed-scope scoping, test sharding, concurrency control, 12 workflows"
  - dimension: "Agent Rules"
    score: 9.0
    status: "Comprehensive AGENTS.md (207 lines), CLAUDE.md symlink, .agents/skills/ with 5 specialized skills, .agent/workflows"
critical_gaps:
  - title: "No container vulnerability scanning (Trivy/Snyk)"
    impact: "Security vulnerabilities in base images or dependencies not caught before deployment"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No SBOM generation"
    impact: "Cannot track software supply chain artifacts for compliance"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "CodeQL only runs on workflow_dispatch (not PRs)"
    impact: "Security vulnerabilities in code changes not caught during PR review"
    severity: "HIGH"
    effort: "1 hour"
  - title: "No external coverage reporting service (Codecov/Coveralls)"
    impact: "No PR-level coverage diff reporting; coverage only enforced locally via thresholds"
    severity: "LOW"
    effort: "2-3 hours"
quick_wins:
  - title: "Enable CodeQL on pull_request trigger"
    effort: "30 minutes"
    impact: "Catch security issues during PR review instead of only on-demand"
  - title: "Add Trivy scanning to Docker release workflow"
    effort: "1-2 hours"
    impact: "Early detection of known CVEs in container images before deployment"
  - title: "Add Codecov integration for PR coverage reporting"
    effort: "2-3 hours"
    impact: "PR-level coverage diffs and automatic coverage regression detection"
  - title: "Add SBOM generation to Docker builds"
    effort: "1 hour"
    impact: "Supply chain transparency and compliance readiness"
recommendations:
  priority_0:
    - "Enable CodeQL on pull_request events to catch security issues at PR time"
    - "Add container image vulnerability scanning (Trivy) to Docker release workflow"
  priority_1:
    - "Integrate Codecov/Coveralls for PR-level coverage reporting and diff tracking"
    - "Add SBOM generation (syft/trivy) to Docker build pipelines"
    - "Add image signing/attestation for supply chain security"
  priority_2:
    - "Add performance regression testing beyond startup memory check"
    - "Consider adding fuzz testing for parser/protocol code"
    - "Add structured test documentation for the contract testing patterns"
---

# Quality Analysis: openclaw (opendatahub-io/openclaw)

## Executive Summary

- **Overall Score: 8.8/10**
- **Repository Type**: TypeScript/Node.js application (CLI + gateway + multi-platform apps)
- **Primary Language**: TypeScript (ESM), with Swift (macOS/iOS), Kotlin (Android), Python (skills)
- **Key Strengths**: Exceptionally sophisticated CI/CD with intelligent change scoping, comprehensive multi-layer test strategy (unit + E2E + contract + Docker smoke), excellent agent rules and developer documentation
- **Critical Gaps**: No container vulnerability scanning, CodeQL not running on PRs, no SBOM generation
- **Agent Rules Status**: Excellent - comprehensive AGENTS.md with detailed coding standards, testing guidelines, and architectural boundaries

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.0/10 | ~2,740 test files, Vitest with sharding, enforced thresholds |
| Integration/E2E | 9.0/10 | 38 E2E tests, contract tests, Docker E2E, multi-platform |
| Build Integration | 8.5/10 | PR Docker build + smoke, CLI startup validation, extension builds |
| Image Testing | 8.5/10 | 6 Dockerfiles validated, install smoke, sandbox smoke, runtime verification |
| Coverage Tracking | 8.0/10 | V8 provider, 70% thresholds enforced, iOS 43% gate; no PR diff reporting |
| CI/CD Automation | 9.5/10 | 12 workflows, intelligent scoping, sharding, concurrency control |
| Agent Rules | 9.0/10 | 207-line AGENTS.md, 5 agent skills, workflow automation |

## Critical Gaps

1. **CodeQL only runs on workflow_dispatch**
   - Impact: Security analysis (SAST) not applied to PRs - vulnerabilities slip through review
   - Severity: **HIGH**
   - Effort: 30 minutes (add `pull_request:` trigger to `.github/workflows/codeql.yml`)

2. **No container vulnerability scanning**
   - Impact: Known CVEs in base images (node:24-bookworm, ubi9/nodejs-22) not detected before deployment
   - Severity: **MEDIUM**
   - Effort: 2-4 hours (add Trivy step to Docker release workflow)

3. **No SBOM generation or image signing**
   - Impact: Supply chain compliance gaps; no attestation of image contents
   - Severity: **MEDIUM**
   - Effort: 2-3 hours (add syft/cosign to Docker workflows)

4. **No PR-level coverage reporting service**
   - Impact: Coverage thresholds enforced only locally; no visual PR diff reporting
   - Severity: **LOW**
   - Effort: 2-3 hours (Codecov integration + upload step in CI)

## Quick Wins

1. **Enable CodeQL on PRs** (30 min)
   - Add `pull_request:` trigger to `codeql.yml`
   - Already has excellent multi-language matrix (JS/TS, Python, Java, Swift, Actions)

2. **Add Trivy container scanning** (1-2 hours)
   - Add `aquasecurity/trivy-action` step after Docker build
   - Set severity threshold (CRITICAL,HIGH)

3. **Codecov integration** (2-3 hours)
   - Upload lcov output from `pnpm test:coverage`
   - Add coverage comment to PRs

4. **SBOM generation** (1 hour)
   - Add `anchore/sbom-action` to Docker release workflow
   - Attach SBOM as build artifact

## Detailed Findings

### CI/CD Pipeline (9.5/10)

**Outstanding CI architecture.** The CI system is one of the most sophisticated I've analyzed:

**12 Workflows:**
- `ci.yml` - Main CI with intelligent scoping (docs-only detection, changed-scope detection)
- `install-smoke.yml` - Docker image build + CLI smoke testing on PRs
- `sandbox-common-smoke.yml` - Sandbox container validation
- `build-openshift-image.yml` - OpenShift/UBI9 multi-arch builds (nightly + push)
- `docker-release.yml` - Multi-arch Docker release (amd64 + arm64 native runners)
- `codeql.yml` - Multi-language SAST (JS/TS, Python, Java, Swift, Actions)
- `workflow-sanity.yml` - Actionlint + tab detection + composite action interpolation checks
- `openclaw-npm-release.yml` - npm package release
- `plugin-npm-release.yml` - Plugin npm release
- `stale.yml` - Issue/PR lifecycle management
- `labeler.yml` - Automatic labeling
- `auto-response.yml` - Auto-response

**Advanced CI Features:**
- Smart docs-only change detection to skip heavy jobs
- Granular changed-scope detection (Node, macOS, Android, Python, Windows)
- Test sharding (2 shards on Linux, 6 shards on Windows)
- Concurrency control on all workflows
- Custom GitHub Actions (4 reusable actions)
- Blacksmith runners for performance (16-vCPU, 32-vCPU)
- Cross-platform testing: Linux, macOS, Windows, Android, iOS

### Test Coverage (9.0/10)

**Exceptional multi-layer test strategy:**

**Unit Tests (~2,740 files):**
- Vitest framework with multiple configs (unit, e2e, extensions, channels, gateway, live)
- Test-to-source ratio: ~0.95:1 (2,740 test files / 2,874 source files)
- Parallel test execution via `scripts/test-parallel.mjs`
- Worker isolation with `pool: "forks"`, `unstubEnvs`, `unstubGlobals`
- Bun compatibility testing (on push to main)
- Node 22 compatibility testing

**E2E Tests (38 files):**
- Dedicated `vitest.e2e.config.ts` with process fork isolation
- CLI smoke tests (launcher, JSON output, sandbox)
- Gateway multi-instance tests
- Plugin lifecycle E2E
- Docker-based E2E suite with 8+ Docker test scripts
- Platform-specific E2E (Parallels macOS/Linux/Windows)

**Contract Tests (~20 files):**
- Plugin contracts: catalog, discovery, loader, provider, registry, runtime, shape, web-search-provider, wizard
- Channel contracts: group-policy, inbound, outbound-payload, plugin, registry, session-binding, setup, status, surface, threading
- Dedicated `pnpm test:contracts` command

**Coverage:**
- V8 coverage provider with lcov reporter
- Enforced thresholds: 70% lines, 70% functions, 55% branches, 70% statements
- iOS coverage gate at 43% (xcresult + xccov)
- Swift code coverage enabled in test builds

### Code Quality (9.0/10)

**Comprehensive linting and formatting:**

**Linting/Formatting:**
- Oxlint (type-aware) with plugins: unicorn, typescript, oxc
- Oxfmt for formatting with import sorting
- SwiftLint + SwiftFormat for Swift code
- ShellCheck for shell scripts (error severity)
- Actionlint for GitHub workflow validation
- Zizmor for GitHub Actions security audit
- Ruff for Python skills scripts
- jscpd for code duplication detection
- Knip for dead code detection
- Markdownlint for documentation

**Pre-commit Hooks (13 hooks):**
- trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-merge-conflict
- detect-private-key, detect-secrets (Yelp, with exclusion baseline)
- shellcheck, actionlint, zizmor
- ruff (Python), oxlint, oxfmt
- pnpm-audit-prod, swiftlint, swiftformat, skills python tests

**Security:**
- detect-secrets with comprehensive baseline and exclusion patterns
- zizmor for GitHub Actions security
- pnpm audit --prod --audit-level=high
- Private key detection
- CODEOWNERS enforcement for security-critical paths

**Architectural Boundary Guards (14+ custom lint scripts):**
- Plugin/extension import boundaries
- Plugin-SDK subpath export validation
- Channel-agnostic boundary checks
- Web search provider boundaries
- Webhook auth body order validation
- Extension relative import validation

### Container Images (8.5/10)

**Strong multi-image build pipeline:**

**Dockerfiles (6):**
- `Dockerfile` - Main multi-stage build with variant support (default/slim), extension build-args
- `Dockerfile.openshift` - UBI9 multi-stage build for OpenShift deployment
- `Dockerfile.sandbox` - Sandbox runtime container
- `Dockerfile.sandbox-common` - Shared sandbox base
- `Dockerfile.sandbox-browser` - Browser sandbox
- `scripts/` - Additional smoke test Dockerfiles (install, non-root, e2e, QR import)

**Build Validation:**
- PR-time Docker builds via `install-smoke.yml`
- CLI startup smoke in Docker containers
- Extension dependency validation in containers
- Plugin discovery validation in containers
- Non-root user validation
- Sandbox setup script validation

**Multi-Architecture:**
- Native amd64 + arm64 builds (no QEMU emulation)
- Multi-platform manifest creation
- OpenShift builds also multi-arch

**Gaps:**
- No Trivy/Snyk vulnerability scanning
- No SBOM generation
- No image signing/attestation (cosign)
- Pinned digests for base images (good), but no automated digest update

### Security (7.5/10)

**Good foundations, some gaps:**

**Strengths:**
- CodeQL multi-language analysis (5 languages)
- detect-secrets with comprehensive exclusion patterns
- pnpm audit for dependency vulnerabilities
- Private key detection in pre-commit
- zizmor for GitHub Actions security
- CODEOWNERS for security-critical paths
- Docker image digest pinning

**Gaps:**
- CodeQL only on `workflow_dispatch` (not triggered on PRs)
- No container image vulnerability scanning
- No SBOM generation
- No dependency review action on PRs
- No image signing/attestation

### Agent Rules (9.0/10)

**Excellent agent guidance:**

**AGENTS.md / CLAUDE.md (207 lines):**
- Comprehensive project structure documentation
- Module organization and import boundaries
- Detailed coding style and naming conventions
- Build/test/development commands
- Documentation standards (Mintlify)
- Operational guides (VM ops)
- Security considerations (CODEOWNERS)

**Agent Skills (.agents/skills/):**
- `openclaw-ghsa-maintainer` - GHSA maintenance
- `openclaw-parallels-smoke` - Parallels smoke testing
- `openclaw-pr-maintainer` - PR maintenance
- `openclaw-release-maintainer` - Release management
- `parallels-discord-roundtrip` - Discord roundtrip testing

**Agent Workflows (.agent/workflows/):**
- `update_clawdbot.md` - Bot update automation

**Skills Directory (skills/):**
- skill-creator (with Python tests)
- openai-image-gen (with tests)
- model-usage (with tests)
- Python skills tested in CI via pytest

**Gaps:**
- No explicit `.claude/rules/` directory with test-type-specific rules
- Test automation guidance embedded in AGENTS.md rather than structured rule files
- No explicit test creation templates or checklists

## Recommendations

### Priority 0 (Critical)

1. **Enable CodeQL on pull_request events**
   - Currently only `workflow_dispatch` - PR changes go unscanned
   - Simple fix: add `pull_request:` trigger
   ```yaml
   on:
     pull_request:
     workflow_dispatch:
   ```

2. **Add container vulnerability scanning**
   - Add Trivy scanning to Docker release workflow
   ```yaml
   - name: Run Trivy vulnerability scanner
     uses: aquasecurity/trivy-action@master
     with:
       image-ref: ${{ steps.tags.outputs.value }}
       severity: 'CRITICAL,HIGH'
       exit-code: '1'
   ```

### Priority 1 (High Value)

3. **Integrate Codecov for PR coverage reporting**
   - Upload lcov from `test:coverage` to Codecov
   - Get coverage diff comments on PRs
   - Set coverage regression threshold

4. **Add SBOM generation to Docker builds**
   - Use `anchore/sbom-action` or `aquasecurity/trivy-action` with SBOM output
   - Attach as build artifact

5. **Add dependency review action on PRs**
   - `actions/dependency-review-action` catches vulnerable new dependencies

### Priority 2 (Nice-to-Have)

6. **Add structured agent test rules**
   - Create `.claude/rules/` with explicit test-type rules
   - Add templates for unit, e2e, contract tests

7. **Performance regression testing**
   - Expand beyond `test:startup:memory` and `test:perf:budget`
   - Add API latency benchmarks

8. **Fuzz testing for protocol/parser code**
   - Apply fuzzing to gateway protocol parsing

## Comparison to Gold Standards

| Feature | openclaw | odh-dashboard | notebooks | kserve |
|---------|----------|---------------|-----------|--------|
| Unit Tests | Vitest + sharding | Jest + RTL | pytest | Go testing |
| Contract Tests | Plugin + Channel | API contracts | N/A | N/A |
| E2E Tests | Vitest + Docker | Cypress | N/A | envtest |
| Coverage Thresholds | 70/70/55/70 | Enforced | N/A | ~80% |
| Coverage Service | Local only | Codecov | N/A | Codecov |
| Container Scanning | None | None | Trivy | N/A |
| SBOM | None | None | Present | N/A |
| Pre-commit | 13 hooks | Limited | N/A | golangci-lint |
| Multi-arch | amd64 + arm64 | amd64 | Multi-arch | amd64 |
| Agent Rules | 207-line AGENTS.md + skills | Comprehensive | None | None |
| CI Sophistication | Exceptional (scoping, sharding) | Good | Basic | Good |

## File Paths Reference

### CI/CD
- `.github/workflows/ci.yml` - Main CI (34KB, highly sophisticated)
- `.github/workflows/install-smoke.yml` - Docker install smoke tests
- `.github/workflows/sandbox-common-smoke.yml` - Sandbox validation
- `.github/workflows/build-openshift-image.yml` - OpenShift multi-arch builds
- `.github/workflows/docker-release.yml` - Docker release pipeline
- `.github/workflows/codeql.yml` - CodeQL SAST (dispatch-only)
- `.github/workflows/workflow-sanity.yml` - Actionlint + sanity checks

### Testing
- `vitest.config.ts` - Base test config with coverage thresholds
- `vitest.unit.config.ts` - Unit test config
- `vitest.e2e.config.ts` - E2E test config
- `vitest.extensions.config.ts` - Extension test config
- `vitest.channels.config.ts` - Channel test config
- `vitest.gateway.config.ts` - Gateway test config
- `vitest.live.config.ts` - Live integration tests
- `src/plugins/contracts/` - Plugin contract tests (10 files)
- `src/channels/plugins/contracts/` - Channel contract tests (10+ files)
- `scripts/test-parallel.mjs` - Parallel test runner

### Code Quality
- `.oxlintrc.json` - Oxlint config (type-aware, 3 plugins)
- `.oxfmtrc.jsonc` - Oxfmt formatter config
- `.pre-commit-config.yaml` - 13 pre-commit hooks
- `.detect-secrets.cfg` - Secret detection exclusions
- `.secrets.baseline` - Secret detection baseline
- `.jscpd.json` - Code duplication config
- `knip.config.ts` - Dead code detection
- `zizmor.yml` - GitHub Actions security audit config

### Container Images
- `Dockerfile` - Main multi-stage build (default/slim variants)
- `Dockerfile.openshift` - UBI9 OpenShift build
- `Dockerfile.sandbox` / `Dockerfile.sandbox-common` / `Dockerfile.sandbox-browser`
- `docker-compose.yml` - Development compose

### Agent Rules
- `AGENTS.md` - Comprehensive agent guidelines (207 lines)
- `CLAUDE.md` - Symlink to AGENTS.md
- `.agents/skills/` - 5 specialized agent skills
- `.agent/workflows/` - Agent workflow automation
- `skills/` - Python skills with tests
