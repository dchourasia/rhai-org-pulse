---
repository: "opendatahub-io/elyra-pipeline-editor"
overall_score: 4.3
scorecard:
  - dimension: "Unit Tests"
    score: 6.0
    status: "Solid unit test suite with Jest + Testing Library; decent coverage of core logic but some UI components untested"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "Minimal Cypress suite with only 1 trivial test scenario; no meaningful E2E coverage"
  - dimension: "Build Integration"
    score: 1.0
    status: "No Dockerfile, no container build, no PR-time build validation beyond JS compilation"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images built or tested; library distributed via npm only"
  - dimension: "Coverage Tracking"
    score: 5.0
    status: "Codecov integration exists but no thresholds enforced; no coverage gates on PRs"
  - dimension: "CI/CD Automation"
    score: 4.0
    status: "Single workflow covers lint/test/cypress but uses outdated actions (v2) and Node 12/14/15; no concurrency control"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules or AI-assisted test guidance"
critical_gaps:
  - title: "Repository appears dormant — last commit March 2024"
    impact: "No active maintenance means accumulating dependency vulnerabilities and stale CI"
    severity: "HIGH"
    effort: "Ongoing"
  - title: "Cypress E2E suite has only 1 trivial test"
    impact: "No meaningful end-to-end coverage of pipeline editor interactions"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No security scanning whatsoever"
    impact: "No Trivy, CodeQL, Snyk, or dependency scanning; known vulnerabilities in pinned deps (prismjs, trim)"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "CI uses deprecated GitHub Actions versions"
    impact: "actions/checkout@v2, actions/setup-node@v2, actions/cache@v2 are deprecated; codecov-action@v1 is EOL"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No coverage enforcement or thresholds"
    impact: "Coverage can silently regress with no gating on PRs"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "Node.js test matrix uses EOL versions (12, 14, 15)"
    impact: "Testing against unsupported runtimes provides false confidence; modern Node versions not tested"
    severity: "MEDIUM"
    effort: "1 hour"
quick_wins:
  - title: "Upgrade GitHub Actions to v4"
    effort: "1 hour"
    impact: "Fix deprecation warnings, improve caching, better security"
  - title: "Update Node.js test matrix to 18, 20, 22"
    effort: "30 minutes"
    impact: "Test against supported LTS versions"
  - title: "Add codecov.yml with coverage threshold"
    effort: "1 hour"
    impact: "Prevent silent coverage regressions"
  - title: "Add GitHub CodeQL analysis workflow"
    effort: "1-2 hours"
    impact: "Automated SAST scanning for JavaScript/TypeScript vulnerabilities"
  - title: "Add Dependabot configuration"
    effort: "30 minutes"
    impact: "Automated dependency update PRs to address known CVEs"
recommendations:
  priority_0:
    - "Determine project status — if actively used by ODH, establish maintenance cadence and update all dependencies"
    - "Add security scanning (CodeQL + Dependabot) to catch vulnerabilities in stale dependencies"
    - "Upgrade CI to use current GitHub Actions versions and Node.js LTS matrix"
  priority_1:
    - "Expand Cypress E2E suite to cover core pipeline editor interactions (drag-drop, node properties, validation)"
    - "Add coverage enforcement with codecov.yml thresholds (e.g., 70% minimum)"
    - "Add pre-commit hooks for TypeScript type checking (currently only Prettier via husky)"
  priority_2:
    - "Create agent rules (.claude/rules/) for consistent test patterns"
    - "Add accessibility testing (axe-core) for the pipeline editor UI"
    - "Consider migrating from Jest to Vitest for faster test execution"
---

# Quality Analysis: elyra-pipeline-editor

## Executive Summary
- **Overall Score: 4.3/10**
- **Repository Type**: TypeScript monorepo (React component library)
- **Primary Language**: TypeScript/React
- **Packages**: `@elyra/pipeline-editor` (UI), `@elyra/pipeline-services` (logic)
- **Framework**: React 17 + Carbon Design System + Elyra Canvas
- **Build Tool**: Microbundle (pipeline-editor), TypeScript compiler (pipeline-services)
- **Last Commit**: March 13, 2024 (15+ months dormant)
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

### Key Strengths
- Solid unit test foundation with Jest + React Testing Library
- Good test coverage for pipeline-services package (migration, validation, circular references)
- ESLint configuration with testing-library and jest-dom plugins
- Husky pre-commit hooks with lint-staged (Prettier formatting)
- Storybook for component development and visual testing
- Strict TypeScript configuration (strict mode, nullChecks, etc.)

### Critical Gaps
- Repository appears dormant (no commits in 15+ months)
- Cypress E2E suite has only 1 trivial test
- Zero security scanning (no CodeQL, Trivy, Dependabot)
- CI uses deprecated action versions and EOL Node.js versions
- No container image building or testing
- No coverage enforcement thresholds

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6.0/10 | Solid Jest + Testing Library suite; 22 test files across 2 packages |
| Integration/E2E | 2.0/10 | Cypress configured but only 1 trivial test scenario |
| Build Integration | 1.0/10 | No container build; only JS compilation checked on PR |
| Image Testing | 0.0/10 | N/A — library published to npm, no container images |
| Coverage Tracking | 5.0/10 | Codecov upload exists but no thresholds or PR gates |
| CI/CD Automation | 4.0/10 | Single workflow with lint/test/cypress; deprecated actions |
| Agent Rules | 0.0/10 | No agent rules, CLAUDE.md, or AI-assisted test guidance |

## Critical Gaps

### 1. Repository Appears Dormant
- **Impact**: No active maintenance means accumulating dependency vulnerabilities, stale CI, and potential incompatibility with downstream consumers
- **Severity**: HIGH
- **Evidence**: Last commit was `db22f1c` on March 13, 2024 — a Dependabot bump for `@babel/traverse`. Only 1 commit in the shallow clone history
- **Action**: Determine if this project is still actively consumed by ODH components; if so, establish maintenance cadence

### 2. Minimal E2E Test Coverage
- **Impact**: The pipeline editor's core interactions (drag-drop nodes, configure properties, validate pipelines, export) are completely untested at the integration level
- **Severity**: HIGH
- **Evidence**: `cypress/integration/no-toolbar.ts` contains a single test that visits a Storybook iframe and checks for empty pipeline text
- **Effort**: 16-24 hours for meaningful coverage
- **Action**: Add Cypress tests for: node creation, node connection, property panel interaction, validation error display, pipeline save/load

### 3. Zero Security Scanning
- **Impact**: Known vulnerabilities in pinned dependencies (`prismjs@1.25.0`, `trim@0.0.3`, `immer@9.0.7`) go undetected
- **Severity**: HIGH
- **Evidence**: No `.github/workflows/codeql.yml`, no `.trivyignore`, no `.gitleaks.toml`, no Dependabot config
- **Effort**: 2-4 hours
- **Action**: Add CodeQL workflow and `dependabot.yml`

### 4. Deprecated CI Infrastructure
- **Impact**: `actions/checkout@v2`, `actions/setup-node@v2`, `actions/cache@v2` are deprecated. `codecov/codecov-action@v1` is EOL. Node matrix tests against EOL versions (12, 14, 15)
- **Severity**: MEDIUM
- **Evidence**: `.github/workflows/build.yaml` lines 28-38
- **Effort**: 1-2 hours
- **Action**: Upgrade to `@v4` actions, update Node matrix to `[18, 20, 22]`

### 5. No Coverage Enforcement
- **Impact**: Coverage can regress silently; PRs can merge with decreased coverage
- **Severity**: MEDIUM
- **Evidence**: `codecov/codecov-action@v1` uploads coverage but there's no `codecov.yml` with `target` or `threshold` settings
- **Effort**: 1-2 hours
- **Action**: Add `codecov.yml` with `project.default.target: 70%` and `patch.default.target: 80%`

## Quick Wins

### 1. Upgrade GitHub Actions Versions (1 hour)
Replace deprecated action versions in `.github/workflows/build.yaml`:
```yaml
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
- uses: actions/cache@v4
- uses: codecov/codecov-action@v4
```

### 2. Update Node.js Test Matrix (30 minutes)
Replace EOL versions with current LTS:
```yaml
strategy:
  matrix:
    node-version: [18, 20, 22]
```

### 3. Add Coverage Threshold (1 hour)
Create `codecov.yml`:
```yaml
coverage:
  status:
    project:
      default:
        target: 70%
    patch:
      default:
        target: 80%
```

### 4. Add CodeQL Scanning (1-2 hours)
Create `.github/workflows/codeql.yml` for automated SAST on push/PR.

### 5. Add Dependabot (30 minutes)
Create `.github/dependabot.yml` for automated dependency PRs:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Detailed Findings

### CI/CD Pipeline

**Workflow**: Single workflow `build.yaml` ("Validate") triggered on push and pull_request

**Jobs** (5 total):
1. **prepare-yarn-cache** — Installs dependencies and caches node_modules + Cypress binary
2. **lint** — Runs ESLint with `--max-warnings=0` and Prettier format check
3. **test-coverage** — Runs `jest --coverage` and uploads to Codecov
4. **test** — Matrix job testing on Node 12/14/15 (all EOL)
5. **test-integration** — Runs Cypress tests against Storybook

**Issues**:
- No concurrency control (`concurrency:` block missing) — multiple PR pushes queue up
- No workflow-level timeout
- Caching uses `actions/cache@v2` instead of built-in `setup-node` caching
- `yarn install` runs in every job despite cache (should use `--frozen-lockfile` consistently)
- Node version `"*"` for installation is non-deterministic
- No release workflow or automated publishing

### Test Coverage

**Unit Tests (22 files)**:
- **pipeline-editor** (9 test files): Tests for PipelineEditor, PalettePanel, NodeTooltip, PipelineController, SplitPanelLayout, TabbedPanelLayout, properties-panels, ThemeProvider
- **pipeline-services** (13 test files): Comprehensive migration tests (v1-v8), validation tests, circular reference detection, utility tests
- **Framework**: Jest 26 + ts-jest + React Testing Library
- **Quality**: Tests use proper testing patterns (render, screen, userEvent); good isolation with test-utils

**Integration/E2E Tests**:
- **Cypress 9.2.1** configured but with only 1 test file
- Single test: visits Storybook iframe, checks for empty pipeline message text
- No tests for: node interaction, pipeline creation, validation, property panels, drag-and-drop

**Coverage**:
- Coverage collection configured for all `.ts/.tsx` files excluding declarations, test files, and test-utils
- Reports in `lcov` and `text` format
- Uploaded to Codecov but no enforcement thresholds

**Test-to-Code Ratio**: 22 test files / ~38 source files = 0.58 (adequate for core logic, weak for UI components)

### Code Quality

**ESLint** (Strong):
- React-app base configuration
- Jest + Testing Library plugins for test quality
- Import order enforcement with alphabetical sorting
- Header/license enforcement
- `--max-warnings=0` enforcement in CI (zero tolerance)

**Prettier** (Configured):
- Empty config `{}` (uses defaults)
- CI runs `format:check` to enforce
- Husky pre-commit runs Prettier via lint-staged

**TypeScript** (Strong):
- Strict mode enabled with all strict options
- `noImplicitReturns`, `noFallthroughCasesInSwitch`, `forceConsistentCasingInFileNames`
- `isolatedModules` for compatibility

**Pre-commit Hooks**:
- Husky v3 with lint-staged
- Only runs Prettier formatting — no type checking, no linting in pre-commit

### Container Images

**Not Applicable** — This is a React component library published to npm. No Dockerfile or container build exists. The library is consumed by downstream applications (e.g., Elyra, ODH Dashboard components).

### Security

**Status: Critical Gap**

| Security Practice | Status |
|------------------|--------|
| CodeQL/SAST | Not configured |
| Dependency scanning | Not configured |
| Trivy/container scanning | N/A (no containers) |
| Secret detection | Not configured |
| Dependabot | Not configured |
| Known vulnerable deps | `prismjs@1.25.0`, `trim@0.0.3` pinned in resolutions |

The `resolutions` field in `package.json` pins `prismjs@1.25.0` and `trim@0.0.3` — these appear to be security fixes but are now themselves outdated.

### Agent Rules (Agentic Flow Quality)

**Status**: Missing
- No `CLAUDE.md` or `AGENTS.md` in repository root
- No `.claude/` directory
- No `.claude/rules/` for test creation patterns
- No `.claude/skills/` for custom skills
- No testing documentation beyond inline code comments

**Recommendation**: Generate agent rules with `/test-rules-generator` to establish:
- Unit test patterns for React components (Testing Library conventions)
- Jest configuration and mock patterns
- Cypress E2E test templates for pipeline editor interactions
- Coverage expectations and test organization

## Recommendations

### Priority 0 (Critical)
1. **Assess project lifecycle status** — Determine if `elyra-pipeline-editor` is still actively consumed. If yes, assign a maintainer and establish monthly maintenance cadence
2. **Add security scanning** — CodeQL workflow + Dependabot for npm and GitHub Actions
3. **Upgrade CI infrastructure** — Actions v4, Node LTS matrix, fix codecov action

### Priority 1 (High Value)
1. **Expand Cypress E2E suite** — Add tests for pipeline creation, node connection, property editing, validation display, error handling
2. **Add coverage enforcement** — `codecov.yml` with project (70%) and patch (80%) targets
3. **Add TypeScript type checking to CI** — Run `tsc --noEmit` as a separate CI step (currently only runs during `build`)
4. **Upgrade dependencies** — React 17→18, Jest 26→29, Cypress 9→13, TypeScript 4.1→5.x

### Priority 2 (Nice-to-Have)
1. **Create agent rules** — `.claude/rules/` with unit-tests.md, e2e-tests.md, react-components.md
2. **Add accessibility testing** — `@axe-core/react` or `jest-axe` for a11y validation
3. **Add Storybook visual regression** — Chromatic or Percy for visual snapshot testing
4. **Migrate to Vitest** — Faster test execution, native ESM support
5. **Add concurrency control** — `concurrency: { group: ..., cancel-in-progress: true }` to CI workflow

## Comparison to Gold Standards

| Practice | elyra-pipeline-editor | odh-dashboard | notebooks | kserve |
|----------|----------------------|---------------|-----------|--------|
| Unit Tests | Jest + RTL (22 files) | Jest + RTL (500+ files) | pytest | Go testing |
| E2E Tests | Cypress (1 test) | Cypress (comprehensive) | Robot Framework | Kind + pytest |
| Coverage Tracking | Codecov (no thresholds) | Codecov (enforced) | Per-notebook | Codecov (enforced) |
| Security Scanning | None | CodeQL + Snyk | Trivy | CodeQL + Trivy |
| CI Actions Version | v2 (deprecated) | v4 (current) | v4 (current) | v4 (current) |
| Pre-commit | Prettier only | Prettier + lint + type check | Various | golangci-lint |
| Agent Rules | None | Comprehensive | None | None |
| Dependency Management | Manual | Dependabot | Dependabot | Dependabot |
| Container Testing | N/A | E2E with Kind | 5-layer validation | envtest + Kind |
| Release Automation | None | Automated | Automated | Automated |

## File Paths Reference

| File | Purpose |
|------|---------|
| `.github/workflows/build.yaml` | Single CI workflow (lint, test, coverage, cypress) |
| `package.json` | Root monorepo config with husky/lint-staged |
| `jest.config.js` | Root Jest config (projects mode) |
| `jest.config.base.js` | Shared Jest preset (ts-jest, node env) |
| `.eslintrc.js` | ESLint with react-app, jest, testing-library plugins |
| `.prettierrc` | Prettier config (empty/defaults) |
| `tsconfig.base.json` | Shared TypeScript strict config |
| `cypress.json` | Cypress config pointing to Storybook (localhost:6006) |
| `cypress/integration/no-toolbar.ts` | Single E2E test |
| `lerna.json` | Lerna monorepo config (yarn workspaces) |
| `packages/pipeline-editor/` | React component library (UI) |
| `packages/pipeline-services/` | Pipeline logic (migration, validation) |
