---
repository: "opendatahub-io/opendatahub.io"
overall_score: 1.8
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist anywhere in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E test infrastructure"
  - dimension: "Build Integration"
    score: 2.0
    status: "PR workflow runs gatsby build only — no type checking, no linting"
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfile, no container image pipeline"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tool configured, no codecov/coveralls integration"
  - dimension: "CI/CD Automation"
    score: 4.0
    status: "Three basic workflows: PR build check, two deploy pipelines (duplicated)"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules"
critical_gaps:
  - title: "Zero test coverage — no tests of any kind"
    impact: "Any code change can silently break the site with no automated detection"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No linting or static analysis in CI"
    impact: "Code quality regressions, inconsistent patterns, and potential bugs go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Duplicate deploy workflows (deploy-site.yml and gatsby.yml)"
    impact: "Confusing CI config, potential race conditions on deploy, wasted compute"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No security scanning (SAST, dependency, secret detection)"
    impact: "Vulnerable dependencies and leaked secrets are not caught"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No type checking in CI"
    impact: "TypeScript errors can be merged without detection despite tsconfig having strict mode"
    severity: "HIGH"
    effort: "30 minutes"
  - title: "No Dependabot or Renovate for dependency updates"
    impact: "Dependencies become stale and accumulate vulnerabilities over time"
    severity: "MEDIUM"
    effort: "1 hour"
quick_wins:
  - title: "Add TypeScript type checking to PR workflow"
    effort: "30 minutes"
    impact: "Catches type errors before merge — the typecheck script already exists in package.json"
  - title: "Add ESLint with React/TypeScript config"
    effort: "2-3 hours"
    impact: "Catches bugs, enforces consistency across 34 TSX and 8 TS source files"
  - title: "Add Dependabot configuration"
    effort: "30 minutes"
    impact: "Automated dependency update PRs keep npm packages current and secure"
  - title: "Consolidate duplicate deploy workflows"
    effort: "1-2 hours"
    impact: "Eliminates confusion and potential double-deploys"
  - title: "Add basic Cypress or Playwright smoke tests"
    effort: "4-6 hours"
    impact: "Validates that key pages render correctly on every PR"
recommendations:
  priority_0:
    - "Add TypeScript type checking (npm run typecheck) to the PR workflow immediately"
    - "Install and configure ESLint with typescript-eslint and eslint-plugin-react, add to CI"
    - "Add at least smoke-level E2E tests (Cypress or Playwright) to verify page rendering"
  priority_1:
    - "Add dependency scanning via Dependabot or Renovate"
    - "Add GitHub CodeQL or Snyk for security scanning"
    - "Consolidate the two overlapping deploy workflows into one"
    - "Add component-level unit tests with Jest and React Testing Library"
  priority_2:
    - "Add accessibility testing (axe-core) for key pages"
    - "Add Lighthouse CI for performance regression detection"
    - "Create CLAUDE.md and .claude/rules/ for agent-assisted development"
    - "Add pre-commit hooks with Husky for local quality gates"
---

# Quality Analysis: opendatahub.io

## Executive Summary

- **Overall Score: 1.8/10**
- **Repository Type**: Static website (Gatsby 5 + React + TypeScript + PatternFly)
- **Primary Language**: TypeScript/TSX (42 source files)
- **Key Strengths**: TypeScript strict mode enabled, Prettier configured, basic PR build check exists
- **Critical Gaps**: Zero tests of any kind, no linting in CI, no security scanning, duplicate deploy workflows
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

This is a marketing/documentation website for the Open Data Hub project. While the codebase is relatively small (42 TypeScript/TSX files, ~249 total files including content), it has **no quality infrastructure** beyond a Prettier config and a TypeScript strict-mode tsconfig. The PR workflow only runs `npm run build` — it does not type-check, lint, or test. There are zero test files in the entire repository.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist anywhere in the repository |
| Integration/E2E | 0/10 | No integration or E2E test infrastructure |
| **Build Integration** | **2/10** | **PR workflow runs gatsby build only — no type checking, no linting** |
| Image Testing | 0/10 | No Dockerfile, no container image pipeline (N/A for static site) |
| Coverage Tracking | 0/10 | No coverage tool configured |
| CI/CD Automation | 4/10 | Three basic workflows, two are duplicated deploy configs |
| Agent Rules | 0/10 | No CLAUDE.md, no .claude/ directory, no agent rules |

## Critical Gaps

### 1. Zero Test Coverage — No Tests of Any Kind
- **Impact**: Any code change (component refactors, Gatsby config changes, styling updates) can silently break the site with no automated detection
- **Severity**: HIGH
- **Effort**: 16-24 hours for initial test suite
- **Details**: `find` for `*.test.*`, `*.spec.*`, `*_test.*` returned 0 results. No `test/`, `tests/`, `__tests__/`, `e2e/`, or `integration/` directories exist. No testing framework (Jest, Vitest, Cypress, Playwright) is installed.

### 2. No Linting or Static Analysis in CI
- **Impact**: Code quality issues, unused imports, accessibility problems, and React anti-patterns are not caught
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No ESLint config exists. No `.eslintrc*` file. The `package.json` has no lint script. Prettier is configured but not enforced in CI (no `prettier --check` step).

### 3. No Type Checking in CI
- **Impact**: TypeScript compilation errors can be merged to main despite `strict: true` in tsconfig
- **Severity**: HIGH
- **Effort**: 30 minutes
- **Details**: A `typecheck` script (`tsc --noEmit`) exists in `package.json` but is NOT called in the PR workflow. The PR workflow only runs `npm ci && npm run build`. Gatsby's build may not catch all type errors.

### 4. Duplicate Deploy Workflows
- **Impact**: Confusing configuration, potential race conditions, wasted GitHub Actions minutes
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: Two workflows deploy to GitHub Pages:
  - `deploy-site.yml`: Triggered on push to main + daily cron, deploys via `JamesIves/github-pages-deploy-action@v4`
  - `gatsby.yml`: Triggered on push to main, deploys via `actions/deploy-pages@v4`
  - Both build and deploy on every push to main — this is redundant and confusing

### 5. No Security Scanning
- **Impact**: Vulnerable npm dependencies and potential secrets in code are not detected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No CodeQL, Trivy, Snyk, Dependabot, Renovate, or Gitleaks integration. No `.gitleaks.toml`, `.trivyignore`, or security-related workflow files.

### 6. No Dependency Management Automation
- **Impact**: npm dependencies become stale and accumulate known vulnerabilities
- **Severity**: MEDIUM
- **Effort**: 1 hour
- **Details**: No `dependabot.yml` or Renovate config. Dependencies like `gatsby@^5.8.1` and `react@^18.2.0` may have known issues.

## Quick Wins

### 1. Add TypeScript Type Checking to PR Workflow (30 minutes)
The `typecheck` script already exists. Just add it to `.github/workflows/pull-request.yml`:
```yaml
name: Test Build
on: pull_request
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run typecheck
      - run: npm run build
```

### 2. Add ESLint with TypeScript/React Config (2-3 hours)
Install and configure ESLint:
```bash
npm install --save-dev eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-plugin-react eslint-plugin-react-hooks
```
Add `"lint": "eslint src --ext .ts,.tsx"` to scripts and add it to the CI workflow.

### 3. Add Dependabot Configuration (30 minutes)
Create `.github/dependabot.yml`:
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

### 4. Consolidate Deploy Workflows (1-2 hours)
Remove one of the two deploy workflows. The `gatsby.yml` workflow is more modern (uses `actions/deploy-pages@v4` and `actions/upload-pages-artifact@v3`), so consider removing `deploy-site.yml` and adding the daily cron trigger to `gatsby.yml`.

### 5. Add Prettier Check to CI (30 minutes)
Add `"prettier:check": "prettier --check src/"` to scripts and add to PR workflow.

## Detailed Findings

### CI/CD Pipeline

**Workflows Found**: 3

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pull-request.yml` | PR | Runs `npm ci && npm run build` only |
| `deploy-site.yml` | Push to main, daily cron | Build + deploy via JamesIves action |
| `gatsby.yml` | Push to main, manual | Build + deploy via GitHub Pages actions |

**Issues**:
- PR workflow is minimal — only verifies the build compiles
- No type checking, linting, testing, or formatting validation on PRs
- Two deploy workflows are redundant (both trigger on push to main)
- `deploy-site.yml` uses outdated `actions/checkout@v3` while `gatsby.yml` uses `v4`
- `gatsby.yml` has proper concurrency control and caching; `deploy-site.yml` does not
- No workflow for dependency updates, security scanning, or performance checks

**Positives**:
- `gatsby.yml` uses `actions/cache@v4` for Gatsby build cache
- `gatsby.yml` has `concurrency.cancel-in-progress: false` for safe deploys
- Daily cron in `deploy-site.yml` picks up external doc changes from `gatsby-source-git`

### Test Coverage

**Status**: No tests exist.

- 0 test files found (searched for `*.test.*`, `*.spec.*`, `*_test.*`)
- 0 test directories found (searched for `test/`, `tests/`, `__tests__/`, `e2e/`, `integration/`)
- No testing framework in `devDependencies` (no Jest, Vitest, Cypress, Playwright, Testing Library)
- No test script in `package.json`
- Test-to-code ratio: 0:42 (0 test files to 42 source files)

### Code Quality

**Prettier**: Configured (`.prettierrc` with import ordering), but not enforced in CI. `.prettierignore` excludes content directories.

**TypeScript**: `tsconfig.json` has `strict: true`, `noImplicitReturns`, `noImplicitThis` — good strictness settings. But `noImplicitAny: false` weakens the strict config. The `typecheck` script exists but is not used in CI.

**ESLint**: Not configured. No `.eslintrc*` file exists.

**Pre-commit hooks**: Not configured. No Husky, lint-staged, or `.pre-commit-config.yaml`.

### Container Images

**N/A** — This is a static Gatsby site deployed to GitHub Pages. No Dockerfile or container image pipeline exists. This is appropriate for the project type.

### Security

**Status**: No security tooling.

- No CodeQL workflow
- No Trivy/Snyk scanning
- No Gitleaks/TruffleHog for secret detection
- No Dependabot or Renovate
- No npm audit in CI
- Google Analytics tracking ID (`G-9KEMPL6SJ3`) is hardcoded in `gatsby-config.ts` — this is public-facing and acceptable, but other secrets could leak without scanning

### Agent Rules (Agentic Flow Quality)

**Status**: Missing

- No `CLAUDE.md` or `AGENTS.md` in root
- No `.claude/` directory
- No `.claude/rules/` for test creation rules
- No `.claude/skills/` for custom skills
- `CONTRIBUTING.md` exists but is minimal (only setup instructions, no quality standards)

**Gap**: AI agents working on this repository have no guidance for:
- Testing patterns and frameworks to use
- Code style beyond Prettier config
- Component patterns (PatternFly usage)
- Content structure requirements
- PR requirements and review standards

## Recommendations

### Priority 0 (Critical — Do First)

1. **Add TypeScript type checking to PR workflow** — 30 minutes. The script exists; just call it.
2. **Install and configure ESLint** — 2-3 hours. Add `@typescript-eslint`, React plugins, and enforce in CI.
3. **Consolidate duplicate deploy workflows** — 1-2 hours. Keep `gatsby.yml`, retire `deploy-site.yml`.

### Priority 1 (High Value)

4. **Add basic E2E smoke tests** — 4-6 hours. Use Playwright to verify key pages (home, blog, docs, community) render without errors.
5. **Add Dependabot** — 30 minutes. Automate npm and GitHub Actions dependency updates.
6. **Add `npm audit` to CI** — 30 minutes. Catch known vulnerabilities in dependencies.
7. **Add component unit tests** — 8-12 hours. Use Jest + React Testing Library for shared components (Navbar, Footer, ContentCard, Layout).

### Priority 2 (Nice-to-Have)

8. **Add Lighthouse CI** — 2-3 hours. Track performance, accessibility, SEO scores per PR.
9. **Add accessibility testing (axe-core)** — 2-3 hours. Integrate with E2E tests.
10. **Create CLAUDE.md and agent rules** — 2-3 hours. Guide AI agents on testing patterns, Gatsby conventions, PatternFly usage.
11. **Add pre-commit hooks** — 1-2 hours. Use Husky + lint-staged for local enforcement.
12. **Add Prettier check to CI** — 30 minutes. Enforce formatting consistency.

## Comparison to Gold Standards

| Dimension | opendatahub.io | odh-dashboard | notebooks | Best Practice |
|-----------|---------------|---------------|-----------|---------------|
| Unit Tests | None | Jest + RTL, high coverage | N/A | Framework-specific tests |
| Integration/E2E | None | Cypress, multi-layer | Testcontainers | Automated in CI |
| Build Integration | Build-only PR | Full lint+test+build | Multi-stage | Lint, type-check, test, build |
| Coverage Tracking | None | Codecov with thresholds | N/A | Codecov/Coveralls + gates |
| CI/CD | 3 basic workflows | Comprehensive, well-organized | Multi-arch builds | Concurrency, caching, matrix |
| Security | None | CodeQL, Snyk | Trivy | SAST + dependency + secret scan |
| Agent Rules | None | Comprehensive .claude/ | N/A | CLAUDE.md + .claude/rules/ |
| Pre-commit | None | Husky + lint-staged | N/A | Pre-commit hooks |
| Dependency Mgmt | None | Dependabot | Dependabot | Automated updates |

## File Paths Reference

| File | Purpose |
|------|---------|
| `package.json` | Dependencies, scripts (build, typecheck, prettier) |
| `tsconfig.json` | TypeScript config with strict mode |
| `.prettierrc` | Prettier config with import ordering |
| `.prettierignore` | Prettier exclusions |
| `gatsby-config.ts` | Gatsby plugins, site config, external doc sourcing |
| `gatsby-node.ts` | Gatsby build-time page generation |
| `.github/workflows/pull-request.yml` | PR build validation (minimal) |
| `.github/workflows/gatsby.yml` | Deploy to GitHub Pages (modern) |
| `.github/workflows/deploy-site.yml` | Deploy to GitHub Pages (legacy, overlapping) |
| `CONTRIBUTING.md` | Minimal contribution guide |
| `src/` | All source code (42 TS/TSX files, 2 SCSS, 8 CSS) |
| `src/components/` | React components (shared + page-specific) |
| `src/pages/` | Gatsby page components |
| `src/templates/` | Gatsby page templates |
| `src/content/` | Blog posts, docs, images |
