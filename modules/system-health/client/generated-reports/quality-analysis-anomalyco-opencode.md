---
repository: "anomalyco/opencode"
overall_score: 7.4
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Extensive test suite with 439 test files across packages, strong 1:4 test-to-source ratio by file count"
  - dimension: "Integration/E2E"
    score: 7.0
    status: "Playwright E2E on Linux and Windows with CI integration, but limited scenario coverage (4 spec files)"
  - dimension: "Build Integration"
    score: 5.0
    status: "Storybook build check on PRs, Nix evaluation, but no container build validation on PRs"
  - dimension: "Image Testing"
    score: 5.5
    status: "Multi-arch Docker builds with startup validation (RUN opencode --version), but no runtime or security scanning"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "No code coverage tool integration (no codecov, coveralls, or threshold enforcement)"
  - dimension: "CI/CD Automation"
    score: 9.0
    status: "29 workflows with concurrency control, caching, JUnit reporting, multi-platform testing, AI-powered review"
  - dimension: "Agent Rules"
    score: 7.5
    status: "Comprehensive AGENTS.md with style guide and testing philosophy; .opencode/ directory with commands, skills, tools"
critical_gaps:
  - title: "No code coverage tracking or enforcement"
    impact: "Cannot measure test adequacy, no regressions caught by coverage drops, unknown dead code"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning (SAST, container scanning, dependency audit)"
    impact: "Vulnerabilities in dependencies and container images not detected until production"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Limited E2E scenario coverage"
    impact: "Only 4 Playwright spec files covering session timeline - major features like file editing, provider config, permissions untested"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "No container image security scanning"
    impact: "Base images (alpine, ubuntu:24.04) and installed packages not audited for CVEs"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add Trivy scanning to container build workflow"
    effort: "1-2 hours"
    impact: "Immediate visibility into container vulnerabilities across all 5+ Dockerfiles"
  - title: "Add codecov integration to test workflow"
    effort: "2-4 hours"
    impact: "Track coverage trends, enforce minimum thresholds on PRs"
  - title: "Add npm audit / bun audit to CI"
    effort: "1 hour"
    impact: "Catch known vulnerabilities in 90+ dependencies"
  - title: "Add CodeQL or Semgrep SAST workflow"
    effort: "2-3 hours"
    impact: "Detect code-level security issues (XSS, injection) automatically on PRs"
recommendations:
  priority_0:
    - "Add code coverage collection and enforcement - integrate codecov with minimum threshold (e.g., 60%)"
    - "Add security scanning pipeline - Trivy for containers, CodeQL/Semgrep for SAST, npm audit for dependencies"
  priority_1:
    - "Expand E2E test coverage beyond session timeline to cover provider configuration, file operations, permissions, and plugin management"
    - "Add container image runtime validation in CI - test that built containers can serve requests, not just print version"
    - "Add dependency license scanning for compliance"
  priority_2:
    - "Add performance regression testing (benchmark test suite exists but not in CI)"
    - "Add contract tests for SDK/API boundaries between packages"
    - "Add accessibility testing for web app (a11y)"
    - "Consider adding pre-commit hooks beyond pre-push typecheck"
---

# Quality Analysis: anomalyco/opencode

## Executive Summary

- **Overall Score: 7.4/10**
- **Repository Type**: TypeScript monorepo (AI-powered development tool)
- **Primary Language**: TypeScript (Bun runtime)
- **Architecture**: Monorepo with 20+ packages (CLI, web app, desktop, SDK, core, LLM, UI, enterprise)
- **Build System**: Turbo + Bun + SST (serverless)
- **Key Strengths**: Exceptional unit test coverage (~439 test files, 113K LoC), sophisticated CI/CD with 29 workflows, AI-powered code review, multi-platform testing (Linux + Windows), strong developer tooling (AGENTS.md, .opencode/ commands)
- **Critical Gaps**: No code coverage tracking, no security scanning (SAST/container/dependency), limited E2E coverage
- **Agent Rules Status**: Present and comprehensive (AGENTS.md + .opencode/ directory)

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | 439 test files, 113K test LoC, Bun test runner with JUnit output |
| Integration/E2E | 7.0/10 | Playwright E2E on Linux+Windows, but only 4 spec files |
| **Build Integration** | **5.0/10** | **Storybook + Nix eval on PRs, no container build validation** |
| Image Testing | 5.5/10 | Multi-arch Docker with startup check, no runtime/security testing |
| Coverage Tracking | 3.0/10 | No codecov, no thresholds, no PR coverage reporting |
| CI/CD Automation | 9.0/10 | 29 workflows, concurrency control, caching, AI review |
| Agent Rules | 7.5/10 | AGENTS.md with style guide + testing philosophy; .opencode/ skills |

## Critical Gaps

### 1. No Code Coverage Tracking or Enforcement
- **Impact**: Cannot measure test adequacy; coverage regressions go unnoticed; unknown dead code accumulates
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: Despite having 439 test files, there is no coverage collection (`--coverage` flag), no codecov/coveralls integration, and no minimum threshold enforcement on PRs. Test adequacy is unmeasured.

### 2. No Security Scanning Pipeline
- **Impact**: Vulnerabilities in 90+ npm dependencies and container base images go undetected until production incidents
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: No Trivy, Snyk, or Grype for container scanning. No CodeQL, Semgrep, or gosec for SAST. No `npm audit` / `bun audit` in CI. The `.gitleaksignore` file exists (for test fixtures) indicating awareness of secret scanning, but no active gitleaks workflow was found.

### 3. Limited E2E Scenario Coverage
- **Impact**: Major user-facing features like file editing, provider configuration, plugin management, permission flows, and MCP integration have no browser-level test coverage
- **Severity**: HIGH
- **Effort**: 20-40 hours
- **Details**: Only 4 Playwright spec files exist (1 smoke, 3 regression) totaling ~1,087 lines — all focused on the session timeline view. The test infrastructure is solid (mock server, CI integration with artifacts), but scenario breadth is minimal.

### 4. No Container Image Security Scanning
- **Impact**: Base images (alpine, ubuntu:24.04) and installed system packages not audited for CVEs; 5+ Dockerfiles across packages
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

## Quick Wins

### 1. Add Trivy Scanning to Container Build Workflow
- **Effort**: 1-2 hours
- **Impact**: Immediate visibility into container vulnerabilities
- **Implementation**: Add `aquasecurity/trivy-action` step after `docker build` in `containers.yml`:
```yaml
- name: Scan container image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/opencode:${{ env.TAG }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 2. Add Codecov Integration to Test Workflow
- **Effort**: 2-4 hours
- **Impact**: Track coverage trends, enforce minimum thresholds
- **Implementation**: Add `--coverage` flag to Bun test commands and upload via `codecov/codecov-action`. Create `.codecov.yml` with thresholds.

### 3. Add npm/Dependency Audit to CI
- **Effort**: 1 hour
- **Impact**: Catch known CVEs in 90+ dependencies automatically
- **Implementation**: Add `bun audit` step to PR workflow or create a dedicated security workflow.

### 4. Add CodeQL SAST Workflow
- **Effort**: 2-3 hours
- **Impact**: Detect code-level security issues (XSS, injection, prototype pollution) automatically
- **Implementation**: Add `.github/workflows/codeql.yml` with JavaScript/TypeScript analysis.

## Detailed Findings

### CI/CD Pipeline

**Score: 9.0/10** - Exceptional automation

The repository has **29 GitHub Actions workflows** — one of the most comprehensive CI/CD setups observed:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | PR, push(dev) | Unit tests (Linux + Windows) + E2E (Playwright) |
| `typecheck.yml` | PR, push(dev) | TypeScript type checking via `bun typecheck` |
| `nix-eval.yml` | PR, push(dev) | Nix flake evaluation (4 systems) |
| `storybook.yml` | PR, push(dev) | Storybook build validation |
| `pr-standards.yml` | PR (opened/edited) | Conventional commit title + issue link enforcement |
| `compliance-close.yml` | Schedule (30m) | Auto-close non-compliant PRs after 2h |
| `review.yml` | Issue comment (/review) | AI-powered code review via opencode |
| `opencode.yml` | Issue comment (/oc) | AI assistant on PRs |
| `containers.yml` | Push(dev), paths | Multi-arch container builds (GHCR) |
| `publish.yml` | Push(dev/ci/beta) | Full release pipeline (CLI + npm + Docker + GitHub Action + VSCode extension) |
| `deploy.yml` | Push(dev/production) | SST deployment to AWS |
| `duplicate-issues.yml` | Issues | Automated duplicate detection |
| `pr-management.yml` | PR events | PR lifecycle management |
| `triage.yml` | Issues | Automated issue triage |
| `stats.yml` | Push(dev) | Repository statistics |

**Strengths:**
- Concurrency control with intelligent grouping (dev branch preserves all runs, PRs cancel stale)
- Turbo cache for fast rebuilds
- Playwright browser caching
- JUnit report publishing with `mikepenz/action-junit-report`
- Artifact upload for test results
- Cross-platform testing (Linux + Windows)
- SHA-pinned actions with version comments
- AI-powered code review enforcing the project's own style guide

**Minor Gaps:**
- No dedicated security scanning workflow
- No coverage reporting in CI
- Container builds only on `dev` push, not validated on PRs

### Test Coverage

**Score: 8.5/10 (Unit) / 7.0/10 (E2E)**

#### Unit Tests — Excellent

- **439 test files** across the monorepo
- **113,357 lines of test code** against ~339,442 lines of source (33% test-to-source ratio by LoC)
- **Test-to-source file ratio**: 439:1,748 (~1:4)
- **Framework**: Bun test runner (built-in)
- **Output**: JUnit XML reports for CI visibility
- **Cross-platform**: Tests run on both Linux and Windows

**Coverage by Package:**
| Package | Test Files | Key Areas |
|---------|-----------|-----------|
| `packages/opencode` | ~200+ | CLI, TUI, ACP, server, session, tools, plugins, MCP, LSP, PTY |
| `packages/app` | ~60+ | Components, context, pages, utils, addons, i18n |
| `packages/core` | ~40+ | Config, filesystem, git, models, plugins (30+ providers), npm |
| `packages/llm` | ~20+ | Provider adapters, caching, routing, schema, streaming |
| `packages/ui` | ~6 | Component rendering tests |
| `packages/enterprise` | 2 | Share and storage |
| `packages/desktop` | 2 | Shell env and HTML rendering |
| `packages/console` | 4 | Provider usage, rate limiter, dates |

**Notable Testing Patterns:**
- HTTP recorder for replay-based provider tests (`packages/http-recorder`)
- Mock server for E2E tests (`packages/app/e2e/utils/mock-server.ts`)
- `.tsx` test files for SolidJS component testing with happy-dom
- HttpAPI exerciser gate tests (coverage, auth, and effect modes)
- Benchmark test suite (`bench:test`) and profiler (`profile:test`) scripts

#### E2E Tests — Growing

- **Framework**: Playwright (Chromium only)
- **Spec files**: 4 (1 smoke, 3 regression)
- **Total E2E LoC**: ~1,087
- **CI**: Runs on Linux + Windows with 30-min timeout, 2 retries on CI
- **Artifacts**: JUnit reports, test results, Playwright HTML reports
- **Infrastructure**: Dev server auto-start, mock server utility

**E2E Gap**: Only session timeline is tested. Missing coverage for:
- Provider configuration flows
- File editing/viewing
- Plugin management
- Permission dialogs
- MCP server connections
- Desktop-specific features

### Code Quality

**Score: 7.5/10**

- **Linter**: OxLint (`oxlint` v1.60.0) — modern, fast Rust-based linter
  - Type-aware mode enabled
  - `suspicious` category active
  - Reasonable rule customizations (Effect.gen/SolidJS compatibility)
  - No-floating-promises and no-misused-spread warnings enabled
- **Formatter**: Prettier (semi: false, printWidth: 120)
- **Editor Config**: Consistent (UTF-8, LF, 2-space indent)
- **Pre-push Hook**: Husky pre-push runs Bun version check + typecheck
- **Type Checking**: `tsgo` (TypeScript Go compiler, native-preview) for speed
- **No Pre-commit Hook**: Only pre-push; lint/format not enforced before commit

**Gap**: No lint step in CI workflows (oxlint runs locally via `bun lint` but isn't enforced in GitHub Actions).

### Container Images

**Score: 5.5/10**

**5 Dockerfiles found:**
| Path | Base Image | Purpose |
|------|-----------|---------|
| `packages/opencode/Dockerfile` | `alpine` | CLI distribution (multi-arch: amd64+arm64) |
| `packages/containers/base/Dockerfile` | `ubuntu:24.04` | CI base image |
| `packages/containers/bun-node/Dockerfile` | (extends base) | CI with Bun+Node |
| `packages/containers/publish/Dockerfile` | (extends base) | Release pipeline |
| `packages/containers/rust/Dockerfile` | (extends base) | Rust build environment |
| `packages/containers/tauri-linux/Dockerfile` | (extends base) | Desktop builds |

**Strengths:**
- Multi-architecture support (amd64 + arm64) for CLI image
- Multi-stage builds
- Startup validation: `RUN opencode --version`
- GHCR publishing with proper auth
- Docker Buildx + QEMU for cross-compilation

**Gaps:**
- No security scanning (Trivy, Snyk, Grype)
- No SBOM generation
- No image signing/attestation
- No runtime functional testing (only `--version` check)
- Container builds not validated on PRs (only on `dev` push)

### Security Practices

**Score: 4.0/10**

- **Secret Detection**: `.gitleaksignore` file exists (suppresses test fixtures) — indicates awareness but no active gitleaks workflow
- **No SAST**: No CodeQL, Semgrep, or gosec workflows
- **No Container Scanning**: No Trivy, Snyk, or Grype integration
- **No Dependency Audit**: No `npm audit`, `bun audit`, or Dependabot/Renovate
- **SHA-pinned Actions**: Actions use full commit SHAs with version comments — excellent supply chain practice
- **PR Compliance**: Automated checks enforce PR template adherence with 2-hour grace period before auto-close

### Agent Rules (Agentic Flow Quality)

**Score: 7.5/10**

- **Status**: Present and comprehensive
- **AGENTS.md**: Detailed document covering:
  - Conventional commit conventions
  - Style guide (destructuring, imports, variables, control flow)
  - Schema definitions (Drizzle)
  - Testing philosophy ("avoid mocks, test actual implementation")
  - Type checking instructions
- **.opencode/ Directory**: Rich configuration including:
  - `agent/`: Duplicate PR detection, triage agents
  - `command/`: 8 custom commands (ai-deps, changelog, commit, issues, learn, rmslop, spellcheck, translate)
  - `glossary/`: i18n translation glossaries (18 languages)
  - `skills/`: Effect pattern skill
  - `tool/`: Custom GitHub PR search and triage tools
  - `plugins/`: TUI smoke testing plugin
  - `themes/`: Custom theme support
  - `opencode.jsonc`: Project configuration

**Strengths:**
- Testing philosophy explicitly stated ("avoid mocks")
- Test-from-package-dir guard (`do-not-run-tests-from-root`)
- Style guide covers real patterns with good/bad examples
- Custom tooling for AI-assisted development

**Gaps:**
- No explicit test creation rules (no `.claude/rules/unit-tests.md` equivalent)
- No E2E test writing guidelines
- No testing checklist or quality gates
- AGENTS.md focuses on style rather than test patterns

## Recommendations

### Priority 0 (Critical)

1. **Add code coverage collection and enforcement**
   - Integrate `codecov` with Bun's `--coverage` flag
   - Set minimum threshold (suggest 60% initially, raise to 70%)
   - Add PR coverage comments showing delta
   - Effort: 4-6 hours

2. **Add security scanning pipeline**
   - Container scanning: Add Trivy to `containers.yml`
   - SAST: Add CodeQL workflow for JavaScript/TypeScript
   - Dependency audit: Add `bun audit` to PR workflow
   - Secret scanning: Add gitleaks workflow
   - Effort: 4-8 hours total

### Priority 1 (High Value)

3. **Expand E2E test coverage**
   - Add spec files for provider configuration, file operations, permissions, plugin management
   - Target 15-20 spec files covering major user flows
   - Effort: 20-40 hours

4. **Add lint enforcement in CI**
   - Add `bun lint` (oxlint) step to PR workflow
   - Currently only runs locally; CI enforcement ensures consistency
   - Effort: 1 hour

5. **Validate container builds on PRs**
   - Add Docker build step to PR workflow (build but don't push)
   - Catch Dockerfile issues before merge
   - Effort: 2-3 hours

### Priority 2 (Nice-to-Have)

6. **Add performance regression testing to CI**
   - Benchmark infrastructure exists (`bench:test`, `perf/` directory)
   - Run benchmarks in CI and track trends
   - Effort: 4-8 hours

7. **Add contract tests for SDK/API boundaries**
   - SDK clients should validate against server API schemas
   - HTTP recorder pattern is already in place — extend to contract testing
   - Effort: 8-16 hours

8. **Add accessibility testing**
   - Use `axe-playwright` plugin for a11y checks in E2E tests
   - Effort: 4-6 hours

9. **Add pre-commit hook for lint/format**
   - Currently only pre-push runs typecheck
   - Catch lint/format issues earlier in workflow
   - Effort: 1 hour

## Comparison to Gold Standards

| Dimension | opencode | odh-dashboard | notebooks | kserve |
|-----------|----------|---------------|-----------|--------|
| Unit Tests | 8.5 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 7.0 | 9.0 | 8.0 | 9.5 |
| Build Integration | 5.0 | 8.0 | 7.0 | 7.0 |
| Image Testing | 5.5 | 7.0 | 9.5 | 6.0 |
| Coverage Tracking | 3.0 | 8.0 | 5.0 | 9.0 |
| CI/CD Automation | 9.0 | 8.5 | 8.0 | 8.5 |
| Agent Rules | 7.5 | 8.5 | 3.0 | 2.0 |
| **Overall** | **7.4** | **8.6** | **7.4** | **8.1** |

**Key Differentiators:**
- opencode excels in CI/CD automation (29 workflows, AI-powered review) and agent rules
- Major gaps vs gold standards are in coverage tracking and security scanning
- E2E infrastructure is solid but scenario coverage lags behind odh-dashboard

## File Paths Reference

### CI/CD Workflows
- `.github/workflows/test.yml` - Unit + E2E test orchestration
- `.github/workflows/typecheck.yml` - TypeScript type checking
- `.github/workflows/nix-eval.yml` - Nix flake evaluation
- `.github/workflows/storybook.yml` - Storybook build check
- `.github/workflows/pr-standards.yml` - PR title + issue enforcement
- `.github/workflows/compliance-close.yml` - Auto-close non-compliant PRs
- `.github/workflows/review.yml` - AI-powered code review
- `.github/workflows/containers.yml` - Container image builds
- `.github/workflows/publish.yml` - Full release pipeline
- `.github/workflows/deploy.yml` - SST deployment

### Testing
- `packages/opencode/test/` - Core CLI test suite (~200+ files)
- `packages/app/src/**/*.test.ts` - App component tests (~60+ files)
- `packages/app/e2e/` - Playwright E2E tests (4 specs)
- `packages/core/test/` - Core library tests (~40+ files)
- `packages/llm/test/` - LLM provider tests (~20+ files)
- `packages/app/playwright.config.ts` - Playwright configuration

### Code Quality
- `.oxlintrc.json` - OxLint configuration (type-aware)
- `.editorconfig` - Editor settings
- `.husky/pre-push` - Pre-push hook (version + typecheck)
- `turbo.json` - Turbo task configuration

### Container Images
- `packages/opencode/Dockerfile` - CLI distribution image
- `packages/containers/*/Dockerfile` - CI/build environment images

### Agent Rules
- `AGENTS.md` - Style guide and testing philosophy
- `.opencode/` - Commands, skills, tools, agents, glossaries

### Configuration
- `package.json` - Root workspace configuration
- `tsconfig.json` - TypeScript configuration
- `sst.config.ts` - SST (serverless) configuration
- `flake.nix` - Nix flake for reproducible builds
