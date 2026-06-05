---
repository: "opendatahub-io/opencode"
overall_score: 7.2
scorecard:
  - dimension: "Unit Tests"
    score: 8.0
    status: "378 test files across packages with Bun test runner; strong coverage in core opencode package (236 tests) and app (57 tests)"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "Playwright E2E infrastructure exists but only 1 placeholder spec; HttpApi exerciser provides API-level integration coverage"
  - dimension: "Build Integration"
    score: 6.0
    status: "Turborepo builds validated on PR; no PR-time container build or deployment testing"
  - dimension: "Image Testing"
    score: 5.0
    status: "Multi-arch container builds with multi-stage Dockerfiles and UBI base; no runtime validation, scanning, or SBOM"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "No codecov integration, no coverage thresholds, no PR coverage reporting"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "29 workflows with concurrency control, caching, cross-platform testing (Linux/Windows), Nix eval, PR standards enforcement"
  - dimension: "Agent Rules"
    score: 7.0
    status: "AGENTS.md with comprehensive style guide and testing philosophy; no .claude/ directory or test-type-specific rules"
critical_gaps:
  - title: "No code coverage tracking or enforcement"
    impact: "Cannot measure test coverage trends or enforce minimum thresholds; regressions go undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "E2E test suite is a placeholder"
    impact: "Playwright infrastructure exists but the only spec is a fixme todo; no real E2E validation runs on PRs"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No container security scanning"
    impact: "Container images published to GHCR without vulnerability scanning, SBOM generation, or image signing"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time container build validation"
    impact: "Container build failures only discovered post-merge on dev branch push"
    severity: "MEDIUM"
    effort: "4-8 hours"
  - title: "Multiple packages have zero test coverage"
    impact: "sdk (43 src/0 tests), ui (178 src/5 tests), containers, plugin, web packages lack meaningful tests"
    severity: "MEDIUM"
    effort: "20-40 hours"
quick_wins:
  - title: "Add Trivy container scanning to containers workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in base images and dependencies before publishing to GHCR"
  - title: "Add codecov integration to test workflow"
    effort: "2-4 hours"
    impact: "Track coverage trends, enforce minimums on PRs, surface coverage in PR comments"
  - title: "Add container build step to PR workflow"
    effort: "2-3 hours"
    impact: "Catch Dockerfile/Containerfile build failures before merge"
  - title: "Create .claude/rules/ directory with test-type-specific rules"
    effort: "2-3 hours"
    impact: "Improve AI-generated test quality with framework-specific patterns (Bun test, Playwright, Effect)"
recommendations:
  priority_0:
    - "Add codecov/coveralls integration with coverage thresholds and PR reporting"
    - "Implement real E2E test scenarios using existing Playwright infrastructure"
    - "Add Trivy or Snyk scanning to container image workflows"
  priority_1:
    - "Add PR-time container build validation (docker build --check or similar)"
    - "Write unit tests for under-covered packages (sdk, ui, web, plugin)"
    - "Create comprehensive .claude/rules/ with test pattern guidance for Bun test, Playwright, and Effect testing"
    - "Add SBOM generation and image signing for published container images"
  priority_2:
    - "Add pre-commit hooks for linting enforcement (currently only pre-push typecheck)"
    - "Consider adding CodeQL or Semgrep for SAST analysis"
    - "Add performance/benchmark testing for CLI startup and LLM interaction latency"
    - "Implement visual regression testing with Storybook"
---

# Quality Analysis: opendatahub-io/opencode

## Executive Summary

- **Overall Score: 7.2/10**
- **Repository Type**: TypeScript monorepo (AI-powered development tool / coding assistant)
- **Primary Language**: TypeScript (1,889 files) with Bun runtime
- **Build System**: Turborepo + Bun + Nix (cross-platform)
- **Packages**: 20 packages (opencode, app, console, core, desktop, llm, ui, sdk, etc.)
- **Agent Rules Status**: Partial — AGENTS.md present with strong style guide, but no .claude/ directory or test-type-specific rules

**Key Strengths:**
- Excellent CI/CD automation (29 workflows, cross-platform Linux/Windows, concurrency control)
- Strong unit test foundation (378 test files, 25.6% test-to-source ratio)
- Well-structured AGENTS.md with clear coding standards and testing philosophy
- Multi-architecture container builds with UBI 9 base image
- Sophisticated PR management (standards enforcement, compliance tracking, AI-powered review)

**Critical Gaps:**
- No code coverage tracking or enforcement
- E2E test suite is a placeholder (1 fixme spec)
- No container security scanning (Trivy, Snyk, etc.)
- No PR-time container build validation
- Several packages have zero or minimal test coverage

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.0/10 | 378 test files, strong opencode package coverage (236 tests), Bun test runner with JUnit reporting |
| Integration/E2E | 5.0/10 | Playwright infrastructure exists but only placeholder spec; HttpApi exerciser provides API integration |
| **Build Integration** | **6.0/10** | **Turborepo builds on PR; no PR-time container build or deployment testing** |
| Image Testing | 5.0/10 | Multi-arch builds with UBI 9 and Alpine; no runtime validation, scanning, or SBOM |
| Coverage Tracking | 2.0/10 | No codecov integration, no thresholds, no PR coverage reporting |
| CI/CD Automation | 9.0/10 | 29 workflows with concurrency, caching, cross-platform, Nix eval, PR standards |
| Agent Rules | 7.0/10 | AGENTS.md with style guide and testing philosophy; no .claude/ rules directory |

## Critical Gaps

### 1. No Code Coverage Tracking or Enforcement
- **Impact**: Cannot measure test coverage trends or enforce minimum thresholds; coverage regressions go completely undetected
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Despite having 378 test files, there is no codecov/coveralls integration. Bun supports coverage generation (`--coverage`) but it is not configured in any workflow. No coverage thresholds exist in CI.

### 2. E2E Test Suite is a Placeholder
- **Impact**: The only Playwright spec (`packages/app/e2e/todo.spec.ts`) contains `test.fixme()` — no real E2E validation runs
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Details**: Full Playwright infrastructure exists (config, browser caching, cross-platform execution, JUnit reporting, trace/screenshot/video on failure), but the actual test content is empty. The E2E job runs on PRs but validates nothing.

### 3. No Container Security Scanning
- **Impact**: Container images are published to GHCR without vulnerability scanning, SBOM generation, or image signing
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The `containers.yml` workflow builds and pushes 5 container images (base, bun-node, rust, tauri-linux, publish) to GHCR with no security scanning step. The root `Containerfile` (UBI 9 based) also lacks scanning.

### 4. No PR-Time Container Build Validation
- **Impact**: Container build failures (Dockerfile syntax, missing dependencies, architecture issues) are only discovered post-merge when pushing to dev
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: The `containers.yml` workflow only triggers on push to dev branch. PR changes to Dockerfiles or the Containerfile are not validated until after merge.

### 5. Multiple Packages Have Zero or Minimal Test Coverage
- **Impact**: Large portions of the codebase have no test protection
- **Severity**: MEDIUM
- **Effort**: 20-40 hours
- **Package breakdown**:
  - `sdk`: 43 source files, 0 tests
  - `ui`: 178 source files, 5 tests
  - `web`: 19 source files, 0 tests
  - `plugin`: 8 source files, 0 tests
  - `containers`: 1 source file, 0 tests
  - `console`: 202 source files, 3 tests
  - `storybook`: 22 source files, 0 tests

## Quick Wins

### 1. Add Trivy Container Scanning (1-2 hours)
Add Trivy vulnerability scanning to the containers workflow:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: ${{ env.REGISTRY }}/build/${{ matrix.image }}:${{ env.TAG }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 2. Add Codecov Integration (2-4 hours)
Enable coverage collection in the test workflow:
```yaml
- name: Run unit tests with coverage
  run: bun turbo test:ci -- --coverage --coverageReporter=lcov

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: packages/*/coverage/lcov.info
    fail_ci_if_error: false
```

### 3. Add Container Build to PR Workflow (2-3 hours)
Add a build-only step (no push) to the PR trigger:
```yaml
on:
  pull_request:
    paths:
      - 'Containerfile'
      - 'packages/containers/**'
      - 'packages/opencode/Dockerfile'
```

### 4. Create .claude/rules/ for Test Patterns (2-3 hours)
Create test-type-specific rules to guide AI-assisted test generation:
- `unit-tests.md` — Bun test patterns, Effect testing with `testEffect`, fixture usage
- `e2e-tests.md` — Playwright patterns, selectors, assertions
- `integration-tests.md` — HttpApi exerciser patterns

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (29 workflows):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | PR, push to dev | Unit tests (Linux/Windows) + E2E (Linux/Windows) |
| `typecheck.yml` | PR to dev, push | TypeScript type checking via `bun typecheck` |
| `nix-eval.yml` | PR to dev, push | Nix flake evaluation across 4 platforms |
| `storybook.yml` | PR to dev (path-filtered) | Storybook build validation |
| `containers.yml` | Push to dev (path-filtered) | Multi-arch container builds → GHCR |
| `publish.yml` | Push to dev/ci/beta, manual | Full release pipeline (CLI, desktop, VS Code) |
| `deploy.yml` | Push to dev/production | SST deployment (Cloudflare, PlanetScale) |
| `pr-standards.yml` | PR opened/edited/synced | Automated PR compliance checking |
| `compliance-close.yml` | Cron (every 30 min) | Auto-close non-compliant PRs after 2 hours |
| `review.yml` | Issue comment `/review` | AI-powered code review (OpenCode + GPT-5.5) |
| `opencode.yml` | Issue/PR comment `/oc` | AI-powered issue handling |
| `generate.yml` | Push to dev | Auto-generate code and commit |
| `nix-hashes.yml` | Push to dev | Nix hash management |
| `docs-*.yml` | Push to dev | Documentation sync and updates |
| `close-issues.yml` | Various | Automated issue management |
| `close-prs.yml` | Various | Automated PR management |

**Strengths:**
- Sophisticated concurrency control (separate groups for dev vs PR)
- Turborepo caching in CI
- Cross-platform testing (Linux + Windows) for both unit and E2E
- Automated PR compliance enforcement with 2-hour window
- AI-powered code review workflow
- Pinned action versions with SHA hashes (security best practice)

**Gaps:**
- No dedicated security scanning workflow (CodeQL, Semgrep, etc.)
- Container builds only on push, not on PR
- No performance/benchmark testing workflow

### Test Coverage

**Unit Testing:**
- **Framework**: Bun's built-in test runner (`bun:test`)
- **Total test files**: 378
- **Test-to-source ratio**: 25.6% (378 test files / 1,453 source files)
- **JUnit reporting**: Configured via `--reporter=junit`
- **Cross-platform**: Tests run on both Linux and Windows

**Per-package coverage:**

| Package | Test Files | Source Files | Ratio | Notes |
|---------|-----------|-------------|-------|-------|
| opencode | 236 | 518 | 45.6% | Core package, best covered |
| app | 57 | 183 | 31.1% | UI app with unit + E2E setup |
| core | 47 | 111 | 42.3% | Well-tested core library |
| llm | 25 | 57 | 43.9% | LLM abstraction layer |
| ui | 5 | 178 | 2.8% | Very low coverage |
| console | 3 | 202 | 1.5% | Minimal coverage |
| desktop | 2 | 49 | 4.1% | Minimal coverage |
| enterprise | 2 | 15 | 13.3% | Low coverage |
| sdk | 0 | 43 | 0% | No tests |
| web | 0 | 19 | 0% | No tests |
| plugin | 0 | 8 | 0% | No tests |

**E2E Testing:**
- **Framework**: Playwright (Chromium only)
- **Test files**: 1 (placeholder — `test.fixme()`)
- **Configuration**: Well-configured with retries (2 on CI), trace on first retry, screenshot on failure, video on failure retain
- **Infrastructure**: Full setup with browser caching, JUnit reporting, artifact upload
- **Gap**: Infrastructure is excellent but content is empty

**Integration Testing:**
- **HttpApi Exerciser**: Custom API-level integration testing (`test:httpapi` script)
  - Coverage mode: validates API endpoint coverage
  - Auth mode: validates authentication behavior
  - Effect mode: validates Effect-based API patterns
  - Fails on missing or skipped endpoints (`--fail-on-missing --fail-on-skip`)

**Testing Philosophy (from AGENTS.md):**
- "Avoid mocks as much as possible"
- "Test actual implementation, do not duplicate logic into tests"
- Tests use Effect framework patterns (`testEffect`, `Layer.mergeAll`)

### Code Quality

**Linting:**
- **OxLint**: Configured (`.oxlintrc.json`) with type-aware checking
  - Suspicious category: warn level
  - TypeScript-specific rules: `no-floating-promises`, `no-misused-spread`
  - Sensible suppressions for Effect/SolidJS patterns
  - Run via `bun run lint` → `oxlint`
- **No ESLint**: Migrated to OxLint (faster, Rust-based)

**Git Hooks:**
- **Husky**: Configured with pre-push hook
  - Pre-push: Bun version check + `bun typecheck`
  - No pre-commit hooks (linting not enforced before commit)

**TypeScript:**
- Extends `@tsconfig/bun/tsconfig.json`
- Typecheck via `bun typecheck` (never `tsc` directly)
- Enforced on pre-push and in CI

**Static Analysis:**
- No CodeQL or SAST integration
- No Semgrep rules
- Gitleaks configured (baseline file found for test false positives)
- No dependency vulnerability scanning (Dependabot, Renovate, etc.)

### Container Images

**Dockerfiles/Containerfiles:**

1. **Root `Containerfile`** (UBI 9 based — Red Hat ecosystem)
   - Multi-stage build (builder + runtime)
   - UBI 9 minimal runtime image
   - SHA256 checksum validation for all binary downloads
   - Multi-architecture support (x86_64, aarch64)
   - Non-root user (UID 1001)
   - `opencode --version` validation in build
   - Includes Python 3.12, uv, git, ripgrep in runtime

2. **`packages/opencode/Dockerfile`** (Alpine based — public distribution)
   - Multi-arch via build args (`build-amd64`, `build-arm64`)
   - Minimal Alpine image
   - `opencode --version` validation

3. **`packages/containers/`** (5 build images)
   - base, bun-node, rust, tauri-linux, publish
   - Multi-platform builds (linux/amd64, linux/arm64)
   - Published to GHCR via Buildx

**Strengths:**
- Multi-architecture support throughout
- SHA256 verification for downloaded binaries
- Non-root container execution
- Multi-stage builds for smaller images
- Version validation in build (smoke test)

**Gaps:**
- No Trivy/Snyk/Grype vulnerability scanning
- No SBOM generation (Syft, etc.)
- No image signing (Cosign, Notary)
- No container runtime testing beyond `--version`
- No `.dockerignore` analysis (potential for large context)
- Containers only built on push to dev, not on PR

### Security

**Strengths:**
- Comprehensive `SECURITY.md` with clear threat model
- Pinned GitHub Action versions with SHA hashes
- Gitleaks baseline for false positive management
- Non-root container execution
- SHA256 verification for binary downloads
- PR compliance enforcement (auto-close after 2 hours)

**Gaps:**
- No CodeQL/SAST scanning workflow
- No Dependabot/Renovate for dependency updates
- No container vulnerability scanning
- No secret scanning in CI (only Gitleaks baseline)
- No SBOM generation or supply chain attestation

### Agent Rules (Agentic Flow Quality)

**Status**: Partial — AGENTS.md present, no .claude/ directory

**AGENTS.md Coverage:**
- SDK regeneration instructions
- Parallel tool usage directive
- Default branch specification (`dev`)
- Comprehensive style guide:
  - Variable naming, destructuring, control flow
  - Effect framework patterns
  - Drizzle schema conventions
  - Function organization
- Testing philosophy: "Avoid mocks", "Test actual implementation"
- TypeScript checking instructions

**Gaps:**
- No `.claude/` directory or `.claude/rules/`
- No test-type-specific rules (unit test patterns, E2E patterns, integration patterns)
- No examples of Bun test patterns or Effect testing patterns
- No Playwright-specific testing guidance
- No coverage expectations or quality gates defined
- Style guide is in AGENTS.md but could be more granular in rules

**Recommendation**: Generate comprehensive `.claude/rules/` with `/test-rules-generator` covering:
- Bun test patterns and fixtures
- Effect testing with `testEffect` and Layer composition
- Playwright E2E patterns
- HttpApi exerciser patterns

## Recommendations

### Priority 0 (Critical)

1. **Add codecov integration with coverage thresholds**
   - Enable Bun coverage generation (`--coverage --coverageReporter=lcov`)
   - Integrate codecov/coveralls for PR reporting
   - Set minimum coverage threshold (start at current baseline, increase over time)
   - Effort: 4-6 hours

2. **Implement real E2E test scenarios**
   - Replace `todo.spec.ts` with actual test scenarios
   - Cover core user flows: session creation, message sending, tool execution
   - Use existing Playwright infrastructure (already configured with retries, traces, etc.)
   - Effort: 16-24 hours

3. **Add container vulnerability scanning**
   - Add Trivy scanning to `containers.yml` workflow
   - Scan root `Containerfile` builds
   - Set severity thresholds (CRITICAL, HIGH)
   - Upload SARIF results to GitHub Security tab
   - Effort: 2-4 hours

### Priority 1 (High Value)

4. **Add PR-time container build validation**
   - Trigger container builds on PRs that modify Dockerfiles/Containerfile
   - Build-only (no push) to validate syntax and dependencies
   - Effort: 4-8 hours

5. **Write tests for under-covered packages**
   - Focus on `ui` (178 src / 5 tests), `console` (202 src / 3 tests), `sdk` (43 src / 0 tests)
   - Start with exported API surface and critical paths
   - Effort: 20-40 hours

6. **Create .claude/rules/ directory**
   - Add test-type-specific rules for AI-assisted test generation
   - Cover Bun test, Playwright, Effect testing, HttpApi patterns
   - Include examples from existing tests
   - Effort: 2-3 hours

7. **Add SBOM generation and image signing**
   - Generate SBOMs with Syft for published images
   - Sign images with Cosign
   - Publish attestations
   - Effort: 4-6 hours

### Priority 2 (Nice-to-Have)

8. **Add pre-commit hooks**
   - Currently only pre-push typecheck; add pre-commit linting with OxLint
   - Prevents lint violations from reaching CI
   - Effort: 1-2 hours

9. **Add CodeQL or Semgrep for SAST**
   - Enable code scanning for common vulnerability patterns
   - JavaScript/TypeScript security rules
   - Effort: 2-4 hours

10. **Add performance/benchmark testing**
    - CLI startup time benchmarks
    - LLM interaction latency tracking
    - Memory usage regression testing
    - Effort: 8-12 hours

11. **Implement visual regression testing**
    - Use Storybook (already configured) with Chromatic or similar
    - Catch UI regressions automatically
    - Effort: 4-6 hours

12. **Add Dependabot or Renovate**
    - Automated dependency update PRs
    - Security update notifications
    - Effort: 1-2 hours

## Comparison to Gold Standards

| Dimension | opencode | odh-dashboard | notebooks | kserve |
|-----------|----------|---------------|-----------|--------|
| Unit Tests | 8/10 (378 files, Bun test) | 9/10 (Jest, extensive) | 6/10 (Python pytest) | 9/10 (Go testing, envtest) |
| Integration/E2E | 5/10 (placeholder E2E) | 9/10 (Cypress, contract tests) | 7/10 (Image validation) | 8/10 (envtest, multi-version) |
| Build Integration | 6/10 (Turbo on PR) | 7/10 (Webpack, Module Fed) | 8/10 (Image pipeline) | 7/10 (Controller builds) |
| Image Testing | 5/10 (Multi-arch, no scan) | 6/10 (Containerfile builds) | 9/10 (5-layer validation) | 7/10 (E2E image tests) |
| Coverage Tracking | 2/10 (None) | 8/10 (Codecov enforced) | 5/10 (Basic tracking) | 9/10 (Enforced thresholds) |
| CI/CD Automation | 9/10 (29 workflows) | 9/10 (Comprehensive) | 8/10 (Periodic + PR) | 8/10 (Multi-version) |
| Agent Rules | 7/10 (AGENTS.md) | 8/10 (CLAUDE.md + rules) | 3/10 (Minimal) | 4/10 (Minimal) |

## File Paths Reference

### CI/CD
- `.github/workflows/test.yml` — Unit + E2E test pipeline
- `.github/workflows/typecheck.yml` — TypeScript type checking
- `.github/workflows/containers.yml` — Container image builds
- `.github/workflows/publish.yml` — Full release pipeline
- `.github/workflows/deploy.yml` — SST deployment
- `.github/workflows/nix-eval.yml` — Nix flake evaluation
- `.github/workflows/pr-standards.yml` — PR compliance
- `.github/workflows/review.yml` — AI-powered code review
- `.github/workflows/compliance-close.yml` — Auto-close non-compliant

### Testing
- `packages/opencode/test/` — Core unit tests (236 files)
- `packages/app/e2e/` — Playwright E2E (placeholder)
- `packages/app/src/**/*.test.ts` — App unit tests (57 files)
- `packages/core/test/` — Core library tests (47 files)
- `packages/llm/test/` — LLM tests (25 files)
- `turbo.json` — Turborepo test task configuration

### Code Quality
- `.oxlintrc.json` — OxLint configuration
- `.husky/pre-push` — Bun version check + typecheck
- `tsconfig.json` — TypeScript configuration

### Container Images
- `Containerfile` — UBI 9 multi-stage build
- `packages/opencode/Dockerfile` — Alpine production image
- `packages/containers/` — Build container images (5 images)
- `packages/containers/script/build.ts` — Container build orchestration

### Agent Rules
- `AGENTS.md` — Style guide, testing philosophy, coding standards
- `SECURITY.md` — Threat model and security policy
