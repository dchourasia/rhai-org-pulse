---
repository: "opendatahub-io/mod-arch-library"
overall_score: 5.4
scorecard:
  - dimension: "Unit Tests"
    score: 4.0
    status: "21 test files across 4 packages but only 1 of 43 shared components tested; no tests in kubeflow package"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "Cypress skeleton exists in mod-arch-starter only; no integration or E2E tests for the library packages"
  - dimension: "Build Integration"
    score: 5.0
    status: "PR workflow builds all packages and runs tests; verify-dist.mjs validates output; no image build on PR"
  - dimension: "Image Testing"
    score: 2.0
    status: "Dockerfile exists in mod-arch-starter only; no image build in CI; no runtime validation"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "Jest coverage configured in CI for core and shared; no codecov integration, no thresholds, no PR gating"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Semantic-release with OIDC publishing; lint-staged + husky pre-commit; matrix testing per package; npm caching"
  - dimension: "Agent Rules"
    score: 7.0
    status: "AGENTS.md with detailed monorepo guidance; .claude/rules for Jira; .claude/skills for release and review; no test-creation rules"
critical_gaps:
  - title: "Very low component test coverage in mod-arch-shared"
    impact: "Only 1 of 43 shared UI components has a test — regressions ship undetected to all downstream consumers"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "Zero tests in mod-arch-kubeflow"
    impact: "Theme provider, hooks, and MUI-to-PatternFly mapping logic entirely untested"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No coverage enforcement or reporting"
    impact: "Coverage runs in CI but results are not uploaded, gated, or visible on PRs — regressions in coverage go unnoticed"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No security scanning (SAST, dependency, container)"
    impact: "Vulnerabilities in dependencies or source code not detected until downstream consumers scan"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No integration/E2E tests for library packages"
    impact: "Cross-package interactions (core → shared → kubeflow) not validated; breakage discovered only by downstream consumers"
    severity: "MEDIUM"
    effort: "12-20 hours"
quick_wins:
  - title: "Add Codecov integration to PR workflow"
    effort: "1-2 hours"
    impact: "Immediate visibility into coverage trends; PR-level coverage diff reporting; enable threshold enforcement"
  - title: "Add GitHub Dependabot or Renovate"
    effort: "1 hour"
    impact: "Automated dependency update PRs; security advisory tracking; reduce manual npm audit burden"
  - title: "Add CodeQL or Trivy scanning workflow"
    effort: "1-2 hours"
    impact: "Automated SAST and dependency vulnerability detection on every PR"
  - title: "Add test-creation agent rules to .claude/rules/"
    effort: "2-3 hours"
    impact: "Improve AI-generated test quality; enforce testing patterns for React components, hooks, and utilities"
recommendations:
  priority_0:
    - "Add unit tests for all shared UI components (43 components, only 1 tested)"
    - "Add unit tests for mod-arch-kubeflow (ThemeProvider, hooks, MUI mappings)"
    - "Add Codecov/Coveralls integration with coverage thresholds (e.g., 60% minimum, no decrease on PR)"
    - "Add security scanning workflow (CodeQL for SAST + npm audit or Trivy for dependencies)"
  priority_1:
    - "Add integration tests validating cross-package imports and build output"
    - "Add Dependabot/Renovate for automated dependency updates"
    - "Create .claude/rules/ test-creation rules for React component tests, hook tests, and utility tests"
    - "Add concurrency control to CI workflows to cancel stale PR runs"
  priority_2:
    - "Add visual regression testing for shared components (Chromatic or similar)"
    - "Add accessibility testing automation (axe-core integration in Jest)"
    - "Add bundle size tracking to prevent regressions in published package sizes"
    - "Add Storybook with automated visual snapshot tests for component library"
---

# Quality Analysis: mod-arch-library

**Repository**: [opendatahub-io/mod-arch-library](https://github.com/opendatahub-io/mod-arch-library)
**Type**: TypeScript/React monorepo library (npm workspaces)
**Packages**: mod-arch-core, mod-arch-shared, mod-arch-kubeflow, mod-arch-installer
**Analysis Date**: 2026-06-03

## Executive Summary

- **Overall Score: 5.4/10**
- **Key Strengths**: Well-structured CI/CD with semantic-release and OIDC publishing; comprehensive AGENTS.md; strong ESLint configuration with accessibility rules; husky pre-commit hooks; verify-dist.mjs build validation
- **Critical Gaps**: Very low test coverage (21 tests for 163+ source files); zero tests in kubeflow package; no coverage enforcement; no security scanning; no integration tests across packages
- **Agent Rules Status**: Present and detailed for development workflow, but missing test-creation rules

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 4.0/10 | 21 test files across packages; only 1/43 shared components tested; 0 kubeflow tests |
| Integration/E2E | 2.0/10 | Cypress skeleton in starter only; no cross-package integration tests |
| **Build Integration** | **5.0/10** | **PR builds + verify-dist.mjs; no image build validation** |
| Image Testing | 2.0/10 | Dockerfile in starter only; no CI image builds; no runtime validation |
| Coverage Tracking | 3.0/10 | Jest coverage runs in CI; no upload, no thresholds, no PR reporting |
| CI/CD Automation | 7.0/10 | Semantic-release, OIDC npm publish, matrix testing, npm caching |
| Agent Rules | 7.0/10 | Comprehensive AGENTS.md; .claude/rules for Jira; no test-creation rules |

## Critical Gaps

### 1. Very Low Component Test Coverage in mod-arch-shared
- **Impact**: Only 1 of 43 shared UI components (`FieldGroupHelpLabelIcon`) has a unit test. Components like `SimpleSelect`, `TypeaheadSelect`, `Table`, `MarkdownView`, `ManageColumnsModal`, and 38 others have zero tests. These components are consumed by all downstream applications — regressions ship undetected.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Current state**: 4 test files total — 1 component test + 3 utility tests (string, time, markdown)

### 2. Zero Tests in mod-arch-kubeflow
- **Impact**: The `ThemeProvider`, `useTheme` hook, MUI-to-PatternFly token mappings, and SCSS theme system are entirely untested. Theme breakage would cascade across all Kubeflow-mode deployments.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Current state**: Jest config uses `--passWithNoTests`; 11 source files, 0 test files

### 3. No Coverage Enforcement or Reporting
- **Impact**: The CI workflow runs `npm run test:jest -- --coverage` for core and shared, but the results are not uploaded to any coverage service, not reported on PRs, and no minimum thresholds are enforced. Coverage can silently degrade over time.
- **Severity**: HIGH
- **Effort**: 2-4 hours (add codecov upload step + `.codecov.yml` config)

### 4. No Security Scanning
- **Impact**: No SAST (CodeQL, Semgrep), no dependency scanning (Dependabot, Renovate, Snyk, Trivy), no secret detection (Gitleaks). Vulnerabilities discovered only if downstream consumers run their own scans.
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 5. No Integration Tests Across Packages
- **Impact**: The monorepo builds all packages before testing, which validates compilation but not runtime cross-package interactions. A breaking change in `mod-arch-core` could affect `mod-arch-shared` and `mod-arch-kubeflow` without detection.
- **Severity**: MEDIUM
- **Effort**: 12-20 hours

## Quick Wins

### 1. Add Codecov Integration (1-2 hours)
Add coverage upload to the existing `test-coverage` job:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    flags: mod-arch-core
    directory: mod-arch-core/jest-coverage

- name: Upload coverage to Codecov (shared)
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    flags: mod-arch-shared
    directory: mod-arch-shared/jest-coverage
```

### 2. Add Dependabot Configuration (1 hour)
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
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3. Add CodeQL Scanning (1-2 hours)
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

### 4. Add Test-Creation Agent Rules (2-3 hours)
Create `.claude/rules/unit-tests.md` with patterns for:
- React component testing with Testing Library
- Custom hook testing with `renderHook`
- Utility function testing patterns
- Mock strategies for API calls and context providers

## Detailed Findings

### CI/CD Pipeline

**Workflows**: 3 total
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | PR + push to main | Lint PR title, build all packages, run lint + tests, coverage |
| `release.yml` | Push to main | Semantic-release with OIDC npm publishing |
| `publish.yml` | Manual dispatch | Manual per-package or all-packages npm publish |

**Strengths**:
- Semantic PR title enforcement (conventional commits)
- Matrix strategy testing individual packages separately
- Node 22.x with npm caching
- Semantic-release with conventional commits, OIDC trusted publishing
- `verify-dist.mjs` catches unresolved path aliases and leaked test files
- Double build verification in release workflow

**Gaps**:
- No concurrency control — stale PR workflows waste resources
- No workflow for periodic testing or nightly builds
- No build status badges in README
- Coverage job runs but results are discarded (not uploaded)
- Actions not pinned to SHAs consistently (some pinned, some `@v4`)

### Test Coverage

**Test Framework**: Jest 29 + React Testing Library + ts-jest

| Package | Source Files | Test Files | Coverage | Status |
|---------|-------------|------------|----------|--------|
| mod-arch-core | 33 | 8 | ~24% file coverage | Moderate — hooks and context tested; API utils partially |
| mod-arch-shared | 109 | 4 | ~4% file coverage | Critical gap — only 1/43 components tested |
| mod-arch-kubeflow | 11 | 0 | 0% | Critical gap — zero tests |
| mod-arch-installer | 10 | 1 (flavor template) | ~10% | Low — CLI logic untested |

**Tested areas in mod-arch-core** (good):
- `ModularArchContext` — context provider
- `useModularArchContext` — hook
- `useNamespaces`, `useNamespacePersistence`, `useNamespaceSelector` — namespace hooks
- `errorUtils` — API error handling
- `useGenericObjectState` — utility hook

**Untested areas in mod-arch-core** (gaps):
- `apiUtils.ts` — HTTP client utilities
- `k8s.ts` — Kubernetes API helpers
- `useAPIState.ts` — API state management hook
- `useSettings.tsx` — settings hook
- `useNotification.ts` — notification hook
- `useTimeBasedRefresh.ts` — refresh hook
- `BrowserStorageContext.tsx` — browser storage context
- `NotificationContext.tsx` — notification context

**mod-arch-shared** (critical gap):
- 43 React components, only `FieldGroupHelpLabelIcon` tested
- 3 utility tests: `string.spec.ts`, `time.spec.ts`, `markdown.spec.ts`
- No tests for: `SimpleSelect`, `TypeaheadSelect`, `Table/TableBase`, `MarkdownView`, `TruncatedText`, `ToolbarFilter`, `ManageColumnsModal`, `ApplicationsPage`, `NavigationBlockerModal`, and 34 more

### Code Quality

**ESLint Configuration**: Comprehensive and strict
- `eslint:recommended` + `plugin:react/recommended` + `@typescript-eslint/recommended`
- Accessibility: `plugin:jsx-a11y/recommended`
- React hooks enforcement: `react-hooks/rules-of-hooks` and `exhaustive-deps` as errors
- Import ordering enforcement
- No `console.log` (error)
- No type assertions in production code (enforced via overrides)
- Prettier integration
- Custom rules: `no-only-tests`, `no-relative-import-paths`, `prefer-template`, `object-shorthand`
- Naming conventions enforced (camelCase/PascalCase/UPPER_CASE)
- **Score**: 9/10 — one of the stronger ESLint configs observed

**Pre-commit Hooks**: Husky + lint-staged
- Runs `npx eslint --max-warnings 0` on staged `.js/.ts/.jsx/.tsx` files
- Enforced via `husky` with `prepare` script
- **Score**: 8/10 — good but could add type-checking and tests

**Static Analysis**:
- No CodeQL, Semgrep, or gosec (for starter BFF)
- No dependency scanning
- No secret detection
- **Score**: 0/10

### Container Images

**Dockerfile** (in mod-arch-starter only):
- Multi-stage build: Node 22 UI builder → Go 1.24 BFF builder → Distroless final
- Non-root user (65532:65532)
- Multi-architecture support via `TARGETOS`/`TARGETARCH`
- Good security baseline with distroless

**Gaps**:
- Dockerfile not in the library packages (expected for an npm library)
- No CI workflow builds or tests the Dockerfile
- No image scanning (Trivy, Snyk)
- No image startup validation
- No SBOM generation

### Security

- No SAST tooling (CodeQL, Semgrep)
- No dependency scanning (Dependabot, Renovate, Snyk)
- No container scanning
- No secret detection (Gitleaks)
- No `.trivyignore`, `.gitleaks.toml`, or similar configs
- npm provenance enabled on publish (good)
- OIDC trusted publishing (good)
- **Score**: 3/10 (provenance is the only security practice)

### Agent Rules (Agentic Flow Quality)

**Status**: Present — above average for the ecosystem

**CLAUDE.md**: Points to AGENTS.md (minimal, correct)

**AGENTS.md** (root): Comprehensive monorepo guide
- Repository structure with all 4 packages
- Development requirements
- Common commands
- Code style conventions (detailed)
- ESLint rules summary
- Import order conventions
- Package-specific guidelines
- Architecture overview (deployment modes, context providers)
- Testing guidelines (basic patterns)
- Contributing workflow

**AGENTS.md** (mod-arch-starter): Contract-first development flow
- Mandatory 4-stage flow: Contract → BFF Stub → Frontend → Production BFF
- Detailed project structure
- Clear enforcement rules

**.claude/rules/jira-creation.md**: Detailed Jira creation rules
- RHOAIENG project configuration
- Custom field IDs and team values
- Markdown formatting guidelines for Jira

**.claude/skills/**:
- `release-version/` — release management skill
- `review-dependabot/` — dependency review skill

**.cursor/skills/**:
- `review/` — code review skill

**Gaps**:
- No test-creation rules (no `unit-tests.md`, `component-tests.md`, `hook-tests.md`)
- No testing patterns or examples in rules
- No quality gates or checklists for test coverage
- No rules for mod-arch-kubeflow theming tests

## Recommendations

### Priority 0 (Critical)

1. **Add unit tests for shared UI components** — Start with the most complex: `SimpleSelect`, `TypeaheadSelect`, `Table/TableBase`, `ManageColumnsModal`, `MarkdownView`. These have the highest regression risk.

2. **Add unit tests for mod-arch-kubeflow** — Test `ThemeProvider`, `useTheme` hook, and MUI-to-PatternFly token mapping. A theme regression affects every Kubeflow-mode deployment.

3. **Add Codecov integration with thresholds** — Upload coverage from the existing CI job, set a minimum threshold (e.g., 60%), and require no decrease on PRs.

4. **Add security scanning** — CodeQL for SAST + Dependabot for dependency updates. Both are free for public repos and take <2 hours to set up.

### Priority 1 (High Value)

5. **Add cross-package integration tests** — Validate that `mod-arch-shared` correctly imports and renders with `mod-arch-core` context providers, and that `mod-arch-kubeflow` theme overrides apply correctly.

6. **Create test-creation agent rules** — Add `.claude/rules/unit-tests.md` with React Testing Library patterns, hook testing patterns, and mod-arch-specific mocking strategies.

7. **Add concurrency control to CI** — Cancel stale PR workflow runs:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

8. **Add Dependabot** — Automated dependency updates with grouped PRs.

### Priority 2 (Nice-to-Have)

9. **Visual regression testing** — Chromatic or Percy for shared component visual snapshots
10. **Accessibility automation** — `jest-axe` integration for automated a11y checks in component tests
11. **Bundle size tracking** — Track published package sizes to prevent bloat regressions
12. **Storybook** — Component documentation + visual testing foundation

## Comparison to Gold Standards

| Dimension | mod-arch-library | odh-dashboard | notebooks | Best Practice |
|-----------|-----------------|---------------|-----------|---------------|
| Unit Tests | 4/10 (21 tests, huge gaps) | 9/10 (comprehensive) | 7/10 (script testing) | 8+/10 |
| Integration/E2E | 2/10 (none for library) | 9/10 (Cypress + mocked) | 8/10 (5-layer) | 8+/10 |
| Build Integration | 5/10 (verify-dist) | 8/10 (multi-mode builds) | 9/10 (image validation) | 8+/10 |
| Image Testing | 2/10 (starter only) | 7/10 (deployment tests) | 9/10 (5-layer validation) | 8+/10 |
| Coverage Tracking | 3/10 (runs, not enforced) | 8/10 (codecov + thresholds) | 6/10 (basic) | 8+/10 |
| CI/CD | 7/10 (semantic-release) | 9/10 (comprehensive) | 8/10 (matrix) | 9+/10 |
| Agent Rules | 7/10 (good AGENTS.md) | 9/10 (full rules + skills) | 3/10 (minimal) | 8+/10 |
| Security | 3/10 (provenance only) | 7/10 (CodeQL + scanning) | 6/10 (Trivy) | 8+/10 |
| **Overall** | **5.4/10** | **8.5/10** | **7.0/10** | **8.5+/10** |

## File Paths Reference

### CI/CD
- `.github/workflows/test.yml` — PR and push test workflow
- `.github/workflows/release.yml` — Semantic-release workflow
- `.github/workflows/publish.yml` — Manual publish workflow
- `scripts/verify-dist.mjs` — Build output validation

### Testing
- `mod-arch-core/jest.config.js` — Core test config
- `mod-arch-shared/jest.config.js` — Shared test config
- `mod-arch-kubeflow/jest.config.js` — Kubeflow test config (passWithNoTests)
- `mod-arch-core/__tests__/` — Core test directory
- `mod-arch-shared/__tests__/` — Shared test directory

### Code Quality
- `mod-arch-core/.eslintrc.cjs` — Comprehensive ESLint config
- `mod-arch-shared/.eslintrc.cjs` — Shared ESLint config
- `mod-arch-kubeflow/.eslintrc.cjs` — Kubeflow ESLint config
- `.husky/pre-commit` — Pre-commit hook (lint-staged)

### Container Images
- `mod-arch-starter/Dockerfile` — Multi-stage build (Node + Go → Distroless)

### Agent Rules
- `CLAUDE.md` — Root Claude config (points to AGENTS.md)
- `AGENTS.md` — Comprehensive monorepo development guide
- `mod-arch-starter/AGENTS.md` — Contract-first development flow
- `.claude/rules/jira-creation.md` — Jira issue creation rules
- `.claude/skills/release-version/` — Release management skill
- `.claude/skills/review-dependabot/` — Dependency review skill

### Release
- `.releaserc.json` (in package.json `release` field) — Semantic-release config
- `scripts/release-set-version.mjs` — Version bump script
