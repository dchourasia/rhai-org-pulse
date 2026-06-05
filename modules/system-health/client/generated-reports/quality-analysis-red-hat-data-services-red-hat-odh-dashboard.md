---
repository: "red-hat-data-services/red-hat-odh-dashboard"
overall_score: 6.8
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "167 Jest spec files with Testing Library; strong coverage of utilities and components but backend has only 3 tests for 97 source files"
  - dimension: "Integration/E2E"
    score: 8.0
    status: "72 Cypress tests (56 mocked + 16 E2E) with page object model, intercept helpers, and CI automation"
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time Docker build, no Konflux simulation, no image validation before merge"
  - dimension: "Image Testing"
    score: 3.5
    status: "Multi-stage Dockerfile exists but no runtime validation, no startup testing, no vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 7.0
    status: "Codecov integration with merged Jest+Cypress coverage, but thresholds are informational-only and target is low (50-70%)"
  - dimension: "CI/CD Automation"
    score: 6.0
    status: "Single test workflow on push/PR with caching; no concurrency control, no matrix testing, no separate security/lint jobs"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules for test creation or coding standards"
critical_gaps:
  - title: "No PR-time container build validation"
    impact: "Build failures discovered only after merge in Konflux; RHOAI vs ODH branding differences untested until production"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No security scanning (Trivy, Snyk, CodeQL)"
    impact: "Vulnerabilities in dependencies and container images not detected; no SAST for source code"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Backend has only 3 unit tests for 97 source files"
    impact: "Backend API routes, middleware, and K8s proxy logic are essentially untested"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "Coverage thresholds are informational-only"
    impact: "Coverage can drop without failing CI; no enforcement prevents regression"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI agents lack guidance for test patterns, coding standards, and project conventions"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Trivy container scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Immediate visibility into CVEs in base images and dependencies"
  - title: "Make coverage thresholds enforcing (not informational)"
    effort: "30 minutes"
    impact: "Prevent coverage regression on every PR"
  - title: "Add concurrency control to test workflow"
    effort: "15 minutes"
    impact: "Cancel stale workflow runs, save CI minutes"
  - title: "Add PR-time Docker build step"
    effort: "2-3 hours"
    impact: "Catch build failures before merge"
  - title: "Create basic CLAUDE.md with testing conventions"
    effort: "2-3 hours"
    impact: "Enable consistent AI-assisted test generation"
recommendations:
  priority_0:
    - "Add container image build validation to PR workflow (both ODH and RHOAI variants)"
    - "Integrate Trivy or Snyk for container vulnerability scanning"
    - "Add CodeQL or equivalent SAST scanning workflow"
    - "Significantly expand backend unit test coverage (currently 3%)"
  priority_1:
    - "Make Codecov thresholds enforcing with minimum 60% coverage gate"
    - "Add contract tests for backend API endpoints"
    - "Create comprehensive agent rules (.claude/rules/) for all test types"
    - "Add accessibility testing with cypress-axe (dependency already present)"
    - "Add workflow concurrency controls to prevent stale runs"
  priority_2:
    - "Add performance testing (Lighthouse CI for frontend)"
    - "Add visual regression testing"
    - "Implement pre-commit hooks for lint/format checks"
    - "Add multi-Node version matrix testing"
    - "Add SBOM generation to image builds"
---

# Quality Analysis: red-hat-data-services/red-hat-odh-dashboard

## Executive Summary

- **Overall Score: 6.8/10**
- **Repository Type**: TypeScript/React web application (RHOAI Dashboard downstream fork)
- **Primary Languages**: TypeScript (frontend: React + PatternFly 6, backend: Fastify/Node.js)
- **Key Strengths**: Well-structured Cypress test suite with page object model, comprehensive frontend unit tests with Testing Library, codecov integration with merged Jest+Cypress coverage
- **Critical Gaps**: No PR-time container build validation, zero security scanning, extremely low backend test coverage (3 tests / 97 files), no agent rules
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | 167 Jest spec files covering frontend utilities and components; backend severely undertested (3/97) |
| Integration/E2E | 8.0/10 | 72 Cypress tests (56 mocked + 16 E2E) with page objects, intercepts, and CI automation |
| **Build Integration** | **3.0/10** | **No PR-time Docker build, no Konflux simulation, no image validation** |
| Image Testing | 3.5/10 | Multi-stage Dockerfile exists; no runtime validation or vulnerability scanning |
| Coverage Tracking | 7.0/10 | Codecov with merged Jest+Cypress; thresholds informational-only (50-70% range) |
| CI/CD Automation | 6.0/10 | Single test workflow with caching; lacks concurrency control and parallelization |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude/ directory, no test automation guidance |

## Critical Gaps

### 1. No PR-Time Container Build Validation
- **Impact**: Build failures are discovered only after merge in Konflux. The `Dockerfile.konflux` sets RHOAI-specific env vars (product name, logos, docs links) that differ from the base `Dockerfile`, but neither is built during CI.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Detail**: The repository has two Dockerfiles — `Dockerfile` (generic ODH) and `Dockerfile.konflux` (RHOAI-branded with pinned UBI8 base image SHA). Neither is built or validated during the PR test workflow. Build regressions (e.g., missing dependencies, build arg mismatches) are only caught downstream.

### 2. No Security Scanning
- **Impact**: No SAST (CodeQL), no container scanning (Trivy/Snyk), no dependency scanning, no secret detection. CVEs in the 60+ npm dependencies go undetected.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Detail**: The `.github/workflows/` directory contains only `test.yml`, `create-tag-release.yml`, and `pr-close-image-delete.yml`. No security-related workflows exist. No `.gitleaks.toml`, `.trivyignore`, or CodeQL configuration.

### 3. Backend Test Coverage is Near Zero
- **Impact**: The Fastify backend handles K8s API proxying, authentication, route handlers, and plugin management across 97 source files — but only 3 spec files exist (`objUtils.spec.ts`, `imageUtils.spec.ts`, `dockerRepositoryURL.spec.ts`), all utility-only tests. Zero route/handler/middleware tests.
- **Severity**: HIGH
- **Effort**: 20-40 hours

### 4. Coverage Thresholds Are Informational Only
- **Impact**: The `.codecov.yml` sets `informational: true` on both project and patch coverage, meaning coverage drops never block PRs. The project range is 50-70% with `target: auto`.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours

### 5. No Agent Rules for AI-Assisted Development
- **Impact**: Without a `CLAUDE.md` or `.claude/rules/` directory, AI agents lack guidance on testing patterns, naming conventions, mock strategies, and project-specific ESLint rules. This leads to inconsistent AI-generated code.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours

## Quick Wins

### 1. Add Trivy Scanning to PR Workflow (1-2 hours)
```yaml
# Add to .github/workflows/test.yml or new security.yml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

### 2. Make Coverage Thresholds Enforcing (30 minutes)
```yaml
# .codecov.yml - change informational to false
coverage:
  status:
    project:
      default:
        informational: false  # Changed from true
        target: 60%
        threshold: 2%
    patch:
      default:
        informational: false  # Changed from true
        target: 70%
```

### 3. Add Concurrency Control (15 minutes)
```yaml
# Add to .github/workflows/test.yml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 4. Add PR-Time Docker Build (2-3 hours)
```yaml
# New job in test.yml
  build-image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build ODH image
        run: podman build -f Dockerfile -t odh-dashboard:pr-${{ github.event.pull_request.number }} .
      - name: Build RHOAI image
        run: podman build -f Dockerfile.konflux -t rhoai-dashboard:pr-${{ github.event.pull_request.number }} .
```

### 5. Create Basic CLAUDE.md (2-3 hours)
Create a `CLAUDE.md` with project conventions, testing patterns, and ESLint rules to guide AI development. Use the `/test-rules-generator` skill to generate comprehensive rules.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (4 workflows)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | push, pull_request | Run lint, type-check, unit tests, Cypress mocked tests, upload coverage |
| `create-tag-release.yml` | workflow_dispatch | Retag images on Quay for ODH releases |
| `pr-close-image-delete.yml` | pull_request (closed) | Delete PR preview images from Quay |
| `authorized-tag-creators.txt` | N/A | Allowlist for tag creation |

**Strengths**:
- Good node_modules caching strategy (repo, backend, frontend cached separately)
- Includes Cypress cache for faster test runs
- Uploads coverage to Codecov on every push/PR
- Uploads Cypress results as artifacts for debugging

**Weaknesses**:
- No concurrency control — stale runs not cancelled
- Single Node version matrix (18.x only)
- No separate lint/type-check/unit/e2e jobs — all sequential in one job
- No Docker build in PR pipeline
- No security scanning workflows
- No periodic/nightly test runs

### Test Coverage

**Frontend Unit Tests (167 spec files)**:
- **Framework**: Jest 28 + @testing-library/react + @testing-library/jest-dom
- **Pattern**: Colocated tests in `__tests__/` directories next to source files
- **Coverage**: Jest coverage generated to `jest-coverage/` directory
- **Strengths**: Good coverage of utilities (`valueUnits`, `useFetchState`, `useValidation`, etc.) and component rendering
- **Key directories covered**: `utilities/`, `pages/projects/`, `concepts/`, `api/`, `components/`

**Frontend Cypress Tests (72 test files)**:
- **Framework**: Cypress 13 with page object model
- **Mocked tests (56)**: Run against a static build with intercepted API calls using `cy.interceptK8s()` and `cy.interceptOdh()` custom commands
- **E2E tests (16)**: Run against real cluster (storage classes, settings, learning resources, data science projects/pipelines, navigation)
- **Page objects (74)**: Well-organized page object files for consistent test interactions
- **Reporting**: Mochawesome + JUnit reporters for CI/CD integration
- **Coverage**: Istanbul-based coverage merged with Jest coverage

**Backend Tests (3 spec files)**:
- **Framework**: Jest with ts-jest preset
- **Coverage**: Only utility functions tested (`objUtils`, `imageUtils`, `dockerRepositoryURL`)
- **Gap**: Zero tests for Fastify routes, plugins, middleware, K8s proxy, WebSocket handlers

**Test-to-Code Ratio**:
- Frontend: 167 test files / 1,422 source files = 11.7% file ratio
- Frontend lines: ~26,000 test lines / ~103,000 source lines = 25% line ratio
- Cypress: ~36,000 lines across all test infrastructure
- Backend: 3 test files / 97 source files = 3.1% file ratio

### Code Quality

**ESLint Configuration** — Comprehensive and strict:
- Extended configs: `eslint:recommended`, `plugin:jsx-a11y/recommended`, `plugin:react/recommended`, `plugin:@typescript-eslint/recommended`, `plugin:prettier/recommended`
- 30+ custom rules enforced including `no-console`, `eqeqeq`, `prefer-destructuring`, `no-param-reassign`
- TypeScript strict: `@typescript-eslint/no-unnecessary-condition`, `@typescript-eslint/explicit-module-boundary-types`, `@typescript-eslint/no-base-to-string`
- Accessibility: `jsx-a11y` plugin with anchor and autofocus rules
- Import ordering enforced
- `no-only-tests/no-only-tests` prevents `.only()` from reaching CI
- Product name hardcoding prevented via restricted-syntax rules
- `--max-warnings 0` in CI — zero warnings allowed

**Prettier**: Configured with consistent settings (single quotes, trailing commas, 100 char width)

**TypeScript**: Strict type checking via `tsc --noEmit` in test pipeline

**Weaknesses**:
- No pre-commit hooks (`.pre-commit-config.yaml` absent)
- No EditorConfig enforcement beyond basic `.editorconfig`
- "Goal" ESLint config (`.eslintrc.goal.js`) suggests aspirational rules not yet enforced

### Container Images

**Dockerfiles**:
- `Dockerfile` — Multi-stage build (builder + runtime) using `ubi8/nodejs-18:latest`. Builds both frontend and backend, serves via Fastify.
- `Dockerfile.konflux` — Same structure but with pinned UBI8 SHA digest and RHOAI-specific env vars (product name, logo, docs/support links)
- `scripts/ci/Dockerfile` — Fedora-based Cypress CI image with Chrome, NVM, oc CLI for running E2E tests

**Strengths**:
- Multi-stage builds reduce final image size
- `--omit=dev --omit=optional` in runtime stage
- Proper USER/group permissions (1001:0)
- Clear labels for image metadata
- `.dockerignore` present

**Weaknesses**:
- No runtime validation (image startup test)
- No vulnerability scanning
- No SBOM generation
- No multi-architecture build in CI (Makefile has `docker-buildx` target but not automated)
- No image signing or attestation
- `Dockerfile` uses `:latest` tag (unpinned base image)

### Security

- **SAST**: None (no CodeQL, Semgrep, or gosec)
- **Container Scanning**: None (no Trivy, Snyk, or Grype)
- **Dependency Scanning**: None (no `npm audit` in CI, no Dependabot/Renovate config)
- **Secret Detection**: None (no Gitleaks, TruffleHog)
- **SBOM**: None
- **Image Signing**: None

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No rules exist
- **Quality**: N/A
- **Gaps**:
  - No `CLAUDE.md` or `AGENTS.md` in repository root
  - No `.claude/` directory
  - No test creation rules for unit tests, Cypress tests, or component tests
  - No coding standards documentation for AI agents
  - No mock pattern documentation
  - No project architecture guidance for AI tools
- **Recommendation**: Generate comprehensive rules using `/test-rules-generator` for:
  - Unit test patterns (Jest + Testing Library)
  - Cypress test patterns (page objects, custom commands)
  - Mock data creation (interceptK8s, interceptOdh)
  - ESLint rule adherence
  - TypeScript conventions

## Recommendations

### Priority 0 (Critical)

1. **Add container image build validation to PR workflow** — Build both `Dockerfile` and `Dockerfile.konflux` on PRs to catch build regressions before merge. Include image startup validation (`podman run --rm -d && curl health endpoint`).

2. **Integrate Trivy for container vulnerability scanning** — Add filesystem scan on every PR and container image scan on builds. Set `exit-code: 1` for CRITICAL/HIGH findings.

3. **Add CodeQL SAST scanning** — Enable `github/codeql-action` for JavaScript/TypeScript to detect security vulnerabilities in source code.

4. **Dramatically expand backend test coverage** — The backend handles K8s API proxying, authentication, and data transformation with zero route-level tests. Prioritize:
   - Route handler tests with Fastify `.inject()`
   - K8s proxy middleware tests
   - Authentication/authorization flow tests
   - Error handling tests

### Priority 1 (High Value)

5. **Make Codecov thresholds enforcing** — Change `informational: true` to `informational: false` with minimum 60% project and 70% patch targets.

6. **Add contract tests for backend API** — The frontend Cypress tests use `cy.interceptK8s()` to mock K8s responses. These mocks should be validated against actual K8s API schemas to prevent mock drift.

7. **Create comprehensive agent rules** — Generate `.claude/rules/` with rules for:
   - `unit-tests.md` — Jest + Testing Library patterns
   - `cypress-tests.md` — Page objects, custom commands, mocked vs E2E
   - `coding-standards.md` — ESLint rules, TypeScript conventions
   - `component-tests.md` — React component test patterns with PatternFly

8. **Add accessibility testing with cypress-axe** — The `cypress-axe` dependency is already installed but appears underutilized. Add `cy.injectAxe()` and `cy.checkA11y()` to E2E tests.

9. **Add workflow concurrency controls** — Prevent stale CI runs from consuming resources.

### Priority 2 (Nice-to-Have)

10. **Add Lighthouse CI for frontend performance** — Track performance metrics, accessibility scores, and best practices on each PR.

11. **Add visual regression testing** — Consider Percy or Chromatic for catching unintended UI changes.

12. **Implement pre-commit hooks** — Add `.pre-commit-config.yaml` with ESLint, Prettier, and type-check hooks to catch issues before push.

13. **Add multi-Node version matrix** — Test against Node 18.x and 20.x (CI Docker image already uses Node 20).

14. **Add SBOM generation** — Use `syft` or `trivy sbom` to generate Software Bill of Materials for container images.

15. **Add dependency update automation** — Configure Dependabot or Renovate for automated dependency PR creation.

## Comparison to Gold Standards

| Dimension | red-hat-odh-dashboard | odh-dashboard (upstream) | notebooks | Best Practice |
|-----------|----------------------|-------------------------|-----------|--------------|
| Unit Tests | 167 spec files (Jest) | 800+ spec files | N/A | Full coverage of utilities + components |
| Integration/E2E | 72 Cypress (56 mocked + 16 E2E) | 200+ Cypress | Image validation | Comprehensive scenarios + real cluster |
| Build Integration | No PR build | PR builds + image validation | Multi-arch builds | Konflux simulation on PR |
| Image Testing | None | Basic startup test | 5-layer validation | Startup + functional + security scan |
| Coverage Tracking | Codecov (informational) | Codecov (enforcing) | N/A | ≥80% with enforcement |
| CI/CD Automation | 1 workflow, sequential | Multi-workflow, parallel | Multi-workflow | Parallel jobs, concurrency control |
| Security Scanning | None | CodeQL + Trivy | Trivy | SAST + container + dependency scan |
| Agent Rules | None | Comprehensive | None | Full .claude/rules/ with all test types |
| Accessibility | cypress-axe (installed) | cypress-axe (active) | N/A | Automated a11y checks on every PR |

**Key Insight**: This is the downstream RHOAI fork of odh-dashboard. The upstream repository (`opendatahub-io/odh-dashboard`) has significantly more mature quality practices. This downstream fork retains the test infrastructure but has not kept pace with CI/CD improvements, suggesting an opportunity to adopt upstream quality practices.

## File Paths Reference

### CI/CD
- `.github/workflows/test.yml` — Main test workflow (push + PR)
- `.github/workflows/create-tag-release.yml` — Manual tag/release workflow
- `.github/workflows/pr-close-image-delete.yml` — Cleanup PR images from Quay
- `Makefile` — Build, push, deploy targets

### Testing
- `frontend/jest.config.js` — Jest configuration
- `frontend/src/__tests__/cypress/cypress.config.ts` — Cypress configuration
- `frontend/src/__tests__/cypress/cypress/tests/mocked/` — 56 mocked Cypress tests
- `frontend/src/__tests__/cypress/cypress/tests/e2e/` — 16 E2E Cypress tests
- `frontend/src/__tests__/cypress/cypress/pages/` — 74 page object files
- `frontend/src/__tests__/cypress/cypress/support/` — Custom commands and setup
- `frontend/src/__mocks__/` — 103 mock data files
- `backend/jest.config.js` — Backend Jest configuration
- `backend/src/__tests__/` — 3 backend spec files

### Code Quality
- `frontend/.eslintrc` — Comprehensive ESLint configuration
- `frontend/.eslintrc.goal.js` — Aspirational "goal" ESLint config
- `.prettierrc` — Prettier configuration
- `.editorconfig` — Editor configuration

### Container Images
- `Dockerfile` — ODH dashboard image (multi-stage, UBI8/Node 18)
- `Dockerfile.konflux` — RHOAI-branded image (pinned UBI8 SHA)
- `scripts/ci/Dockerfile` — Cypress CI runner image (Fedora 40)
- `.dockerignore` — Docker build exclusions

### Coverage
- `.codecov.yml` — Codecov configuration (informational thresholds)

### Manifests
- `manifests/odh/` — ODH deployment overlays
- `manifests/rhoai/` — RHOAI deployment overlays
- `manifests/common/` — Shared manifests
- `install/deploy.sh` — Deployment script
