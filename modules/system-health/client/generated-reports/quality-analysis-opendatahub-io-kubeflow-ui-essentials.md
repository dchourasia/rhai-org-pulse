---
repository: "opendatahub-io/kubeflow-ui-essentials"
overall_score: 4.6
scorecard:
  - dimension: "Unit Tests"
    score: 4.0
    status: "13 test files for 177 source files (7% ratio); no coverage thresholds enforced"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "Cypress exists in starter template only; no E2E in library packages or CI"
  - dimension: "Build Integration"
    score: 2.0
    status: "No PR-time Docker build, no Konflux simulation, no image validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "Dockerfile present in starter only; no runtime validation or image scanning"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "CI runs coverage collection but no thresholds, no codecov, no PR reporting"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Well-structured test/release/publish workflows with semantic-release and OIDC publishing"
  - dimension: "Agent Rules"
    score: 7.0
    status: "Comprehensive AGENTS.md, CLAUDE.md, Jira rules, and kubeflow theming rules; lacks test-specific rules"
critical_gaps:
  - title: "Extremely low test coverage ratio (7% file ratio, 19% line ratio)"
    impact: "Most library code is untested — regressions silently ship to all downstream consumers"
    severity: "HIGH"
    effort: "40-80 hours"
  - title: "No coverage enforcement or thresholds"
    impact: "Coverage can decrease with every PR; no gate prevents untested code from merging"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Zero security scanning (no Trivy, CodeQL, SAST, or dependency scanning)"
    impact: "Vulnerabilities in dependencies or source code go undetected until downstream consumers are impacted"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No E2E testing in CI pipeline"
    impact: "Component integration issues, theming bugs, and context provider failures are only caught manually"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No container image build or validation on PRs"
    impact: "Dockerfile breaks discovered only when downstream projects (dashboard) attempt builds"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "mod-arch-kubeflow has zero unit tests"
    impact: "Theme context, hooks, and MUI/PatternFly token mapping logic is entirely untested"
    severity: "HIGH"
    effort: "16-24 hours"
quick_wins:
  - title: "Add codecov integration with PR coverage reporting"
    effort: "2-4 hours"
    impact: "Immediate visibility into coverage trends; prevents silent coverage regression"
  - title: "Add coverage thresholds to Jest configs (e.g. 60% minimum)"
    effort: "1-2 hours"
    impact: "Blocks PRs that reduce coverage below acceptable levels"
  - title: "Add CodeQL/Trivy scanning workflow"
    effort: "2-4 hours"
    impact: "Automated vulnerability detection for npm dependencies and source code"
  - title: "Add Dependabot configuration"
    effort: "1 hour"
    impact: "Automated dependency update PRs (currently using manual Dependabot-style bumps)"
  - title: "Create .claude/rules for unit test patterns"
    effort: "2-3 hours"
    impact: "AI-generated tests follow consistent patterns; accelerates test coverage growth"
recommendations:
  priority_0:
    - "Add coverage thresholds to Jest configs and integrate codecov for PR-level coverage reporting"
    - "Write unit tests for untested packages (mod-arch-kubeflow has 0 tests, mod-arch-shared has 4 tests for 109 source files)"
    - "Add CodeQL or Trivy security scanning GitHub workflow"
  priority_1:
    - "Create Cypress or Playwright E2E test suite for library components in integration context"
    - "Add PR-time Docker build validation for mod-arch-starter Dockerfile"
    - "Create .claude/rules/ for unit-tests.md, e2e-tests.md, and component-tests.md"
    - "Add contract tests for API utilities (apiUtils, errorUtils, k8s helpers)"
  priority_2:
    - "Add multi-architecture Docker build validation"
    - "Add performance regression testing for hook rendering (useNamespaces, useSettings)"
    - "Add accessibility testing automation (axe-core integration)"
    - "Complete the WIP docs/testing.md with concrete patterns and examples"
---

# Quality Analysis: kubeflow-ui-essentials (mod-arch-library)

## Executive Summary

- **Overall Score: 4.6/10**
- **Repository Type**: TypeScript/React monorepo — npm-published UI library for micro-frontend architectures
- **Key Strengths**: Well-structured CI/CD with semantic-release, comprehensive agent rules (AGENTS.md + CLAUDE.md), strong ESLint configuration with Prettier, Husky pre-commit hooks, OIDC-based npm publishing
- **Critical Gaps**: Very low test coverage (13 test files / 177 source files), no security scanning, no E2E testing in CI, no coverage enforcement, no container image testing
- **Agent Rules Status**: Present and well-developed for code style, Jira workflows, and theming guidelines; **missing test automation rules**

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 4.0/10 | 13 test files for 177 source files (7%); 1,937 test LOC vs 10,373 source LOC (19%) |
| Integration/E2E | 2.0/10 | Cypress only in starter template; not run in CI; no library-level E2E |
| **Build Integration** | **2.0/10** | **No PR-time Docker build; no Konflux simulation; no image validation** |
| Image Testing | 1.0/10 | Dockerfile in starter only; no runtime validation, scanning, or SBOM |
| Coverage Tracking | 3.0/10 | CI runs `--coverage` but no thresholds, no codecov, no PR gates |
| CI/CD Automation | 7.0/10 | 3 workflows (test/release/publish); semantic-release; OIDC publishing; matrix testing |
| Agent Rules | 7.0/10 | Comprehensive AGENTS.md; .claude/rules for Jira and theming; missing test rules |

## Critical Gaps

### 1. Extremely Low Test Coverage (Severity: HIGH)
- **Impact**: Most library code ships to downstream consumers (odh-dashboard, kubeflow modules) untested
- **Details**:
  - `mod-arch-core`: 33 source files, 8 test files (24% file ratio)
  - `mod-arch-shared`: 109 source files, 4 test files (4% file ratio)
  - `mod-arch-kubeflow`: 11 source files, **0 test files** (0%)
  - `mod-arch-installer`: 24 source files, 1 test file (4%)
- **Effort**: 40-80 hours to reach 60% coverage across packages
- **Risk**: As an npm-published library, untested APIs can break multiple downstream applications simultaneously

### 2. No Coverage Enforcement (Severity: HIGH)
- **Impact**: Coverage can silently decrease with every merged PR
- **Details**: Jest configs define `coverageDirectory` and `collectCoverageFrom` but **no `coverageThreshold`**. CI runs coverage collection for core and shared packages but results aren't reported or gated.
- **Effort**: 4-6 hours (add thresholds + codecov integration)

### 3. Zero Security Scanning (Severity: HIGH)
- **Impact**: Vulnerabilities in 1000+ transitive npm dependencies go undetected
- **Details**: No CodeQL, Trivy, Snyk, Gitleaks, or any SAST/DAST tool configured. No Dependabot configuration despite numerous manual dependency bump PRs visible in git history.
- **Effort**: 4-8 hours

### 4. No E2E Testing in CI (Severity: HIGH)
- **Impact**: Integration between context providers, hooks, and components across packages is never validated automatically
- **Details**: Cypress exists in `mod-arch-starter/frontend` with a single NavBar test, but it's not part of the library CI workflow. No component-level E2E for the published packages.
- **Effort**: 16-24 hours

### 5. mod-arch-kubeflow Package Has Zero Tests (Severity: HIGH)
- **Impact**: Theme context provider, MUI/PatternFly token mapping, SCSS architecture — all untested
- **Details**: This package has 11 source files with complex theming logic, including MUI-to-PatternFly design token mapping and theme context switching. Zero test coverage.
- **Effort**: 16-24 hours

### 6. No Container Image Testing (Severity: MEDIUM)
- **Impact**: Dockerfile in `mod-arch-starter` is never built or validated on PRs
- **Details**: Multi-stage Dockerfile (Node + Go BFF + distroless) exists but is never exercised in CI. Build failures only discovered downstream.
- **Effort**: 8-12 hours

## Quick Wins

### 1. Add Coverage Thresholds to Jest Configs (1-2 hours)
Add to both `mod-arch-core/jest.config.js` and `mod-arch-shared/jest.config.js`:
```javascript
coverageThreshold: {
  global: {
    branches: 50,
    functions: 50,
    lines: 60,
    statements: 60,
  },
},
```

### 2. Add Codecov Integration (2-4 hours)
Add to `.github/workflows/test.yml` test-coverage job:
```yaml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v5
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        flags: mod-arch-core
        directory: mod-arch-core/jest-coverage
```

### 3. Add CodeQL Security Scanning (2-4 hours)
Create `.github/workflows/codeql.yml`:
```yaml
name: CodeQL
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript
      - uses: github/codeql-action/analyze@v3
```

### 4. Add Dependabot Configuration (1 hour)
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      dev-dependencies:
        dependency-type: "development"
```

### 5. Create Agent Rules for Test Patterns (2-3 hours)
Create `.claude/rules/unit-tests.md` with patterns for:
- React hook testing with `renderHook`
- Component testing with React Testing Library
- Context provider testing
- API utility mocking patterns

## Detailed Findings

### CI/CD Pipeline

**Workflows (3 total)**:
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | PR + push to main | Lint PR title, build all, lint, test, coverage, per-package matrix test |
| `release.yml` | Push to main | Semantic release → OIDC npm publish (all 4 packages) |
| `publish.yml` | Manual dispatch | Manual version-specific publish with package selection |

**Strengths**:
- Semantic PR title enforcement (conventional commits)
- Matrix testing per package (core, shared, kubeflow)
- npm cache via `setup-node`
- OIDC-based npm trusted publishing (no long-lived tokens)
- `verify-dist.mjs` script validates build output before publish
- Build → test → verify → publish pipeline

**Gaps**:
- No concurrency control on test workflow (duplicate runs on PR + push)
- No caching of `npm ci` beyond node modules
- Coverage job runs separately but doesn't upload or gate
- No E2E or integration test step

### Test Coverage

**Framework**: Jest with ts-jest, React Testing Library, jsdom environment

**Per-Package Breakdown**:
| Package | Source Files | Test Files | File Ratio | Status |
|---------|-------------|------------|------------|--------|
| mod-arch-core | 33 | 8 | 24% | Partial — hooks and context tested, API utilities gaps |
| mod-arch-shared | 109 | 4 | 4% | Critical — 105 untested components and utilities |
| mod-arch-kubeflow | 11 | 0 | 0% | Critical — entire theming package untested |
| mod-arch-installer | 24 | 1 | 4% | Critical — CLI installer barely tested |
| **Total** | **177** | **13** | **7%** | **Critical** |

**Line counts**: 1,937 lines of test code vs 10,373 lines of source code (19% ratio)

**Test scripts per package**:
- All packages run: lint → unit tests → type-check (`run-s test:lint test:unit test:type-check`)
- Jest passes with `--passWithNoTests` for shared and kubeflow (masking zero-test state)
- Installer uses custom `test-flavor.mjs` script

### Code Quality

**ESLint Configuration**: Strong
- TypeScript parser with project references
- Plugins: `@typescript-eslint`, `react-hooks`, `import`, `no-only-tests`, `no-relative-import-paths`, `prettier`
- Extends: `eslint:recommended`, `jsx-a11y/recommended`, `react/recommended`, `@typescript-eslint/recommended`, `prettier`
- `--max-warnings 0` enforced in CI
- Import ordering rules configured

**Pre-commit Hooks**: Present
- Husky configured with `npx lint-staged`
- lint-staged runs ESLint on `mod-arch-*/**/*.{js,ts,jsx,tsx}`
- Enforces `--max-warnings 0`

**Prettier**: Configured per package (core, shared, starter)

**TypeScript**: Strict enough — `noEmit` type checking in test pipeline, separate `tsconfig.build.json` for builds

### Container Images

**Dockerfile** (mod-arch-starter only):
- Multi-stage: Node 22 (UI build) → Go 1.24.3 (BFF build) → distroless (runtime)
- `TARGETOS`/`TARGETARCH` support for multi-arch
- Non-root user (65532:65532)
- Distroless base image

**Gaps**:
- Not built or tested in CI
- No image startup validation
- No vulnerability scanning (Trivy, Snyk)
- No SBOM generation
- No image signing/attestation
- Only present in starter template, not the library packages themselves

### Security

**Current State**: No security scanning whatsoever
- No CodeQL/SAST
- No Trivy/Snyk for container scanning
- No dependency scanning (no Dependabot config despite manual bumps)
- No secret detection (Gitleaks, TruffleHog)
- No npm audit in CI
- OIDC publishing is a security positive (no long-lived npm tokens)

### Agent Rules (Agentic Flow Quality)

**Status**: Present — above average for agent guidance
- **CLAUDE.md**: Points to AGENTS.md
- **AGENTS.md**: Comprehensive monorepo guide with structure, commands, conventions, testing patterns, component guidelines
- **.claude/rules/jira-creation.md**: Detailed Jira issue creation rules (Bug/Story/Task/Epic workflows, severity guidelines, field mappings)
- **.claude/skills/**: release-version and review-dependabot skills
- **mod-arch-kubeflow/.claude/rules/**: 3 rules for PatternFly tokens, SCSS architecture, and workflow

**Coverage Assessment**:
| Rule Category | Status | Notes |
|---------------|--------|-------|
| Code Style | Present | ESLint rules, naming conventions, import order |
| Jira Workflow | Present | Comprehensive Bug/Story/Task/Epic templates |
| Theming | Present | PatternFly tokens, SCSS architecture, MUI integration |
| Unit Tests | **Missing** | No rules for test patterns, mocking strategies, coverage expectations |
| E2E Tests | **Missing** | No Cypress/Playwright guidance for agents |
| Component Tests | **Missing** | No React Testing Library patterns documented as rules |
| API Tests | **Missing** | No contract test or API utility test rules |

**Recommendation**: Generate test-specific rules with `/test-rules-generator` to fill the gap — particularly for React hook testing, component rendering, and context provider testing patterns used in this codebase.

## Recommendations

### Priority 0 (Critical)
1. **Add coverage thresholds and codecov integration** — prevent silent coverage regression, make coverage visible on PRs
2. **Write unit tests for mod-arch-kubeflow** (0% → 60%) — theme context, hook behavior, token mapping
3. **Write unit tests for mod-arch-shared** (4% → 40%) — UI components, utility functions
4. **Add CodeQL security scanning** — catch vulnerabilities in source and dependencies
5. **Add npm audit to CI** — quick dependency vulnerability check

### Priority 1 (High Value)
1. **Create E2E test suite** — Cypress or Playwright testing components in realistic provider hierarchy
2. **Add PR-time Docker build** for `mod-arch-starter/Dockerfile` — validate multi-stage build doesn't break
3. **Create `.claude/rules/` for test automation** — unit-tests.md, component-tests.md, e2e-tests.md
4. **Add Dependabot** — automate dependency update PRs
5. **Add concurrency control** to test workflow — avoid duplicate runs

### Priority 2 (Nice-to-Have)
1. **Add Trivy container scanning** for starter Dockerfile
2. **Performance testing** for hooks (useNamespaces renders, useGenericObjectState equality checks)
3. **Accessibility testing** (axe-core) integration in component tests
4. **Complete docs/testing.md** — currently a WIP placeholder with no concrete content
5. **Add SBOM generation** for npm packages and container images
6. **Add image signing** (cosign/sigstore) for published npm packages

## Comparison to Gold Standards

| Dimension | kubeflow-ui-essentials | odh-dashboard | notebooks | Gold Standard |
|-----------|----------------------|---------------|-----------|---------------|
| Unit Test Coverage | ~7% file ratio | >80% | N/A | >70% with thresholds |
| E2E Tests | Cypress in starter only | Cypress (mocked + real) | N/A | Multi-layer (mocked + live) |
| Coverage Enforcement | None | Codecov + thresholds | N/A | PR gates + trend tracking |
| Security Scanning | None | CodeQL + Trivy | Trivy | CodeQL + Trivy + Dependabot |
| Image Testing | None | N/A | 5-layer validation | Build + startup + functional |
| CI/CD Quality | Good (semantic-release) | Excellent | Good | Matrix + caching + concurrency |
| Agent Rules | Strong (style/Jira/theming) | Strong (comprehensive) | None | Test rules + code rules + workflow |
| Pre-commit Hooks | Husky + lint-staged | Husky + lint-staged | N/A | Lint + format + type-check |
| Contract Tests | None | Yes | N/A | API boundary tests |

## File Paths Reference

### CI/CD
- `.github/workflows/test.yml` — PR testing (lint, build, test, coverage, matrix)
- `.github/workflows/release.yml` — Semantic release + OIDC npm publish
- `.github/workflows/publish.yml` — Manual version publish

### Testing
- `mod-arch-core/__tests__/` — Core hook and context tests
- `mod-arch-core/api/__tests__/` — API utility tests
- `mod-arch-shared/__tests__/` — Shared component tests
- `mod-arch-shared/utilities/__tests__/` — Utility tests
- `mod-arch-starter/frontend/src/__tests__/cypress/` — Cypress tests (starter only)
- `mod-arch-core/jest.config.js` — Core Jest configuration
- `mod-arch-shared/jest.config.js` — Shared Jest configuration

### Code Quality
- `mod-arch-core/.eslintrc.cjs` — Core ESLint config
- `mod-arch-shared/.eslintrc.cjs` — Shared ESLint config
- `.husky/pre-commit` — Pre-commit hook (lint-staged)
- `.releaserc.json` — Semantic release configuration

### Container Images
- `mod-arch-starter/Dockerfile` — Multi-stage Node + Go + distroless

### Agent Rules
- `CLAUDE.md` — Points to AGENTS.md
- `AGENTS.md` — Comprehensive monorepo development guide
- `.claude/rules/jira-creation.md` — Jira issue templates and workflows
- `.claude/skills/release-version/SKILL.md` — Release version skill
- `.claude/skills/review-dependabot/SKILL.md` — Dependabot review skill
- `mod-arch-kubeflow/AGENTS.md` — Kubeflow theming agent rules
- `mod-arch-kubeflow/.claude/rules/` — PatternFly tokens, SCSS architecture, workflow
