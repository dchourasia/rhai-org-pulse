---
repository: "opendatahub-io/odh-dashboard"
overall_score: 9.1
scorecard:
  - dimension: "Unit Tests"
    score: 9.0
    status: "981 test files across Jest and Go testing; 28% test-to-code ratio with coverage enforcement"
  - dimension: "Integration/E2E"
    score: 9.5
    status: "235+ Cypress E2E tests with live cluster execution, smart tag selection, cluster failover, BFF integration, and contract testing"
  - dimension: "Build Integration"
    score: 8.0
    status: "Docker build with RHOAI/ODH modes, Tekton pipelines for Konflux, kustomize validation, but no PR-time Konflux simulation"
  - dimension: "Image Testing"
    score: 7.0
    status: "Multi-stage Dockerfile with runtime health checks, but no Trivy/Snyk scanning in PR workflow"
  - dimension: "Coverage Tracking"
    score: 8.5
    status: "Codecov integration with merged unit+Cypress coverage, 70% patch target, nyc report generation"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "26 workflows, concurrency control, turbo caching, parallel matrix tests, modular architecture quality gates"
  - dimension: "Agent Rules"
    score: 10.0
    status: "18 comprehensive rules covering all test types, 20+ skills, 3,550 lines of test guidance, contract test framework"
critical_gaps:
  - title: "No container image vulnerability scanning in CI"
    impact: "Security vulnerabilities in base images or dependencies not caught until Konflux/production scanning"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time Konflux build simulation"
    impact: "Build failures in Konflux pipelines discovered only post-merge"
    severity: "MEDIUM"
    effort: "8-12 hours"
  - title: "No SBOM generation"
    impact: "Supply chain transparency and compliance requirements not met in CI"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "2-3 hours"
    impact: "Catch container image CVEs before merge, align with notebooks gold standard"
  - title: "Add SBOM generation to Dockerfile or CI"
    effort: "1-2 hours"
    impact: "Supply chain compliance and artifact attestation"
  - title: "Enable performance regression testing for BFF endpoints"
    effort: "4-6 hours"
    impact: "Catch API latency regressions in Go BFF services before merge"
recommendations:
  priority_0:
    - "Add Trivy or Grype container scanning to the PR workflow or Tekton pipeline"
    - "Generate SBOM (syft or cdxgen) as part of the image build process"
  priority_1:
    - "Add PR-time Konflux build simulation for the main dashboard image"
    - "Enable the disabled quality gate checks (contract testing, API functional, bundle size monitoring)"
    - "Add API performance regression testing for BFF Go services"
  priority_2:
    - "Expand accessibility testing coverage beyond axe-core basics"
    - "Add chaos engineering / resilience testing for operator controller"
    - "Consider CodeQL SAST integration for TypeScript/Go code paths"
---

# Quality Analysis: odh-dashboard

## Executive Summary

- **Overall Score: 9.1/10**
- **Repository Type**: Monorepo — React/TypeScript frontend + Go BFF services + Go operator
- **Primary Languages**: TypeScript (frontend), Go (BFF, operator)
- **Framework**: React 18, PatternFly v6, Webpack Module Federation, controller-runtime

**Key Strengths**: odh-dashboard is an industry-leading example of comprehensive quality engineering. With 981 test files, multi-layer testing (unit, mock, E2E, contract), a sophisticated CI/CD pipeline with 26 workflows, and the most comprehensive agent rules seen in any repository (18 rules, 20+ skills, 3,550 lines of test guidance), this repository sets the gold standard for monorepo quality practices. The E2E infrastructure with cluster failover, smart test tag selection, BFF auto-detection, and dynamic port allocation is exceptionally well-engineered.

**Critical Gaps**: The primary gaps are in container security scanning (no Trivy/Snyk in CI) and SBOM generation. There is no PR-time Konflux build simulation, though Tekton pipelines exist for pull-request and push events. Several quality gate checks in the modular architecture workflow are still disabled (contract testing enforcement, API functional testing, bundle size monitoring).

**Agent Rules Status**: Exemplary — most comprehensive seen in any repository

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.0/10 | 981 test files (Jest + Go), 28% test-to-code ratio, coverage enforcement |
| Integration/E2E | 9.5/10 | 235+ Cypress E2E, live cluster testing, contract tests, BFF integration |
| **Build Integration** | **8.0/10** | **Tekton pipelines, kustomize validation, no PR-time Konflux simulation** |
| Image Testing | 7.0/10 | Multi-stage Dockerfile, health checks, no vulnerability scanning |
| Coverage Tracking | 8.5/10 | Codecov with merged unit+Cypress, 70% patch target |
| CI/CD Automation | 9.5/10 | 26 workflows, turbo caching, matrix parallelization |
| Agent Rules | 10.0/10 | 18 rules, 20+ skills, contract test framework, comprehensive guidance |

## Critical Gaps

1. **No container image vulnerability scanning in CI**
   - Impact: Security vulnerabilities in base images (ubi9/nodejs-22) or npm dependencies not caught until downstream Konflux/production scanning
   - Severity: HIGH
   - Effort: 2-4 hours
   - The `semgrep.yaml` covers source code but not container image CVEs

2. **No PR-time Konflux build simulation**
   - Impact: Build differences between GitHub CI and Tekton/Konflux pipelines discovered only post-merge
   - Severity: MEDIUM
   - Effort: 8-12 hours
   - Tekton pipelines exist in `.tekton/` (20 pipeline definitions for PR and push) but aren't triggered from GitHub Actions

3. **No SBOM generation**
   - Impact: Supply chain transparency requirements not met; no artifact attestation
   - Severity: MEDIUM
   - Effort: 2-4 hours

4. **Disabled quality gate checks**
   - Impact: Modular architecture quality gates only enforce unit tests and E2E tests; contract testing, API functional testing, API performance testing, and bundle size monitoring are all disabled
   - Severity: MEDIUM
   - Effort: 4-8 hours per check

## Quick Wins

1. **Add Trivy scanning to PR workflow** (2-3 hours)
   - Impact: Catch container image CVEs before merge
   - Implementation: Add Trivy action after Docker build step or as a standalone job
   ```yaml
   - name: Run Trivy vulnerability scanner
     uses: aquasecurity/trivy-action@master
     with:
       image-ref: 'odh-dashboard:pr-${{ github.event.number }}'
       format: 'sarif'
       severity: 'CRITICAL,HIGH'
   ```

2. **Add SBOM generation** (1-2 hours)
   - Impact: Supply chain compliance
   - Add `syft` or `cdxgen` to CI or Dockerfile

3. **Enable contract testing quality gate** (2-3 hours)
   - Impact: Enforce contract test presence for all BFF modules
   - The contract test infrastructure already exists across 8 packages; just uncomment the quality gate check

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (26 workflows):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | push, PR | Main test pipeline: Setup → Type-Check → Lint → Unit Tests → Contract Tests → Cypress Mock Tests → Coverage combine + Codecov upload |
| `cypress-e2e-test.yml` | After `test.yml` completes on PR | Live cluster E2E with cluster failover, smart tag detection, BFF auto-start |
| `dashboard-operator-tests.yml` | push/PR (operator paths) | Go lint + build + test for operator controller |
| `modular-arch-quality-gates.yml` | PR (packages paths) | Testing maturity assessment per module |
| `validate-kustomize.yml` | push/PR (manifests paths) | Kustomize build validation for RHOAI and ODH overlays |
| `dependency-validation.yml` | PR (package-lock.json) | npm audit diff — blocks new HIGH+ vulnerabilities |
| BFF test workflows (×7) | push, PR | Separate test workflows for model-registry, gen-ai, mlflow, maas, automl, autorag, eval-hub BFFs |
| `core-bff-build.yml` | push, PR | Core BFF build and tests |
| Build workflows (×2) | push, PR | Gen AI frontend build, Gen AI BFF build |
| `agentready-weekly.yml` | weekly cron | Weekly agent readiness assessment |
| `claude-preflight.yml` | schedule | Agent preflight checks |
| Release/admin workflows | manual dispatch | Release creation, auto-merge, stale management |

**Strengths**:
- Excellent concurrency control across all workflows (`cancel-in-progress: true`)
- Turbo caching for incremental builds — significantly reduces CI time
- Module caching via composite action (`.github/actions/module-caches`)
- Dynamic test group discovery from package.json metadata
- Sophisticated E2E infrastructure with:
  - Cluster health checks (DSC condition monitoring) with automatic failover
  - Smart test tag selection (PR labels, turbo change detection, frontend area mapping)
  - Dynamic port allocation for parallel execution
  - BFF auto-detection and startup (with command injection protection)
  - Self-hosted runner disk space management
  - Emergency cleanup protocols with parallel-job safety

**Tekton/Konflux Pipelines**: 20 pipeline definitions in `.tekton/` covering:
- Main dashboard: pull-request + push
- Dashboard operator: pull-request + push
- 8 modular architecture modules: pull-request + push each

### Test Coverage

**Unit Tests (Jest)**:
- 981 test files across frontend, backend, and packages
- Test-to-code ratio: 990 test files / 3,475 source files = **28.5%**
- Framework: Jest with TypeScript support
- Coverage generation: `test-unit-coverage` script produces `jest-coverage/`
- Organized under `__tests__/` directories with `*.spec.ts(x)` naming

**Cypress Mock Tests**:
- Extensive mocked Cypress test suite run on every PR
- Dynamic test group discovery from `packages/cypress/cypress/tests/mocked/`
- Package-level Cypress tests via `cypress.mocked` in `package.json`
- Coverage collection via Istanbul/nyc
- Parallelized via matrix strategy based on test group discovery

**Cypress E2E Tests** (235+ `.cy.ts` files):
- Runs against live OpenShift clusters
- Cluster failover: primary (`dash-e2e-int`) → secondary (`dash-e2e`)
- Smart test selection:
  - Default: `@ci-dashboard-regression-tags` (always runs)
  - PR labels: `test:*` pattern → Cypress grep tags
  - Auto-detected: Turbo change detection + frontend area mapping via `.github/frontend-ci-tags.json`
  - Package `e2eCiTags` in `package.json` for self-service opt-in
- BFF auto-detection and startup with port/command allowlisting
- Non-admin test mode support (`@NonAdmin` tag uses TEST_USER_3 credentials)
- Accessibility testing: `axe-core` integration via `cypress/support/commands/axe.ts`

**Contract Tests**:
- Full contract test framework in `packages/contract-tests/`
- 8 packages with contract tests: model-registry, mlflow, gen-ai, eval-hub, autorag, automl, agent-ops, core-bff
- Schema validation against OpenAPI specs
- HTML report generation for results
- Runs as part of main `test.yml` workflow with Go 1.25 + uv for Python dependencies

**Go Operator Tests** (5 test files):
- CRD type tests (`dashboard_types_test.go`)
- Controller reconciler tests (`dashboard_reconciler_test.go`)
- Controller action tests (`actions_test.go`)
- Support utility tests (`support_test.go`)
- Webhook validation tests (`dashboard_webhook_test.go`)

**Go BFF Tests** (184 test files):
- Extensive test coverage across all BFF packages
- Repository-level tests, handler tests, integration tests
- Kubernetes client integration tests (token, namespace registry, factory)
- Run via dedicated per-package CI workflows

### Code Quality

**Linting**:
- ESLint: Shared config (`@odh-dashboard/eslint-config`) with recommended React/TypeScript rules
- ESLint goal config (`frontend/.eslintrc.goal.js`) — progressive tightening
- golangci-lint v2 with standard linters enabled for operator (govet with most checks enabled)
- Prettier: `.prettierrc` for consistent formatting
- TypeScript: Strict type checking via `turbo` across all packages

**Pre-commit Hooks**:
- Husky pre-commit hook with `lint-staged`
- Module Federation port validation on staged `package.json` changes
- Helpful error messages with auto-fix instructions
- Skip/force override mechanisms (`SKIP_LINT_HOOK`, `FORCE_LINT_HOOK`)

**Static Analysis**:
- Semgrep: Comprehensive unified rules (`semgrep.yaml`) covering:
  - Go (Kubernetes controllers/operators)
  - TypeScript/JavaScript (React frontends)
  - YAML (Kubernetes manifests, GitHub Actions)
  - Generic secrets detection across all file types
- Gitleaks: `.gitleaks.toml` with test file exclusions
- npm audit: Dependency validation workflow with diff-based analysis (only blocks NEW advisories)

### Container Images

**Dockerfile Analysis**:
- Multi-stage build (builder → runtime)
- Base image: `registry.access.redhat.com/ubi9/nodejs-22:latest`
- Build modes: ODH (default) and RHOAI (via `BUILD_MODE` arg)
- Production dependency optimization: Custom `prepare-production-manifest.js` script
- FIPS compliance: esbuild binary removal post-build
- Runtime: Minimal with `curl-minimal` for health probes
- Non-root user execution (USER 1001:0)
- Proper labels for OpenShift integration

**Multi-architecture Support**:
- Makefile target `docker-buildx` for `linux/s390x,linux/amd64,linux/ppc64le`

**Gaps**:
- No Trivy/Snyk/Grype scanning in CI workflows
- No SBOM generation (syft, cdxgen)
- No image signing/attestation in GitHub Actions (may be handled by Konflux)

### Security

**Implemented**:
- Semgrep security rules (hardcoded secrets, CWE-798 detection)
- Gitleaks for secret scanning
- npm audit with differential analysis (new vulnerabilities only)
- BFF command injection protection (allowlisted commands and directories)
- Agent rule for security review (`.claude/rules/security.md`)
- Non-root container execution
- Audit bypass tracking with labeled PRs and artifact upload

**Gaps**:
- No CodeQL/SAST integration for TypeScript or Go code
- No container image scanning (Trivy/Snyk)
- No dependency-level CVE tracking beyond npm audit

### Agent Rules (Agentic Flow Quality)

**Status**: Exemplary — the most comprehensive agent rules implementation observed

**Rules** (18 files, 3,550+ lines of test guidance):
| Rule | Lines | Coverage |
|------|-------|----------|
| `testing-standards.md` | 69 | Cross-cutting test type selection guide |
| `unit-tests.md` | 610 | Jest patterns, hooks, components, mocking |
| `cypress-mock.md` | 1,206 | Mock test patterns, intercepts, page objects |
| `cypress-e2e.md` | 668 | Live cluster testing, tagging, prerequisites |
| `contract-tests.md` | 997 | BFF API validation, schema matching |
| `bff-go.md` | — | Go BFF patterns and conventions |
| `architecture.md` | — | Monorepo structure and boundaries |
| `conventions.md` | — | TypeScript/React coding standards |
| `css-patternfly.md` | — | PatternFly v6 styling conventions |
| `modular-architecture.md` | — | Module Federation, plugin system |
| `module-federation.md` | — | Module exposure/consumption patterns |
| `module-onboarding.md` | — | New module creation guide |
| `operator-controller.md` | — | Go controller-runtime patterns |
| `pull-requests.md` | — | PR template and guidelines |
| `react.md` | — | React component/hook conventions |
| `security.md` | — | Auth, secrets, input validation |
| `jira-creation.md` | — | Jira issue formatting |
| `third-party-theming.md` | — | External library theming |

**Skills** (20+ custom skills):
- Development workflow (`dev-workflow`)
- Code review (`coderabbit-autofix`, `coderabbit-code-review`, `coderabbit-review`)
- RBAC review (`rbac-review`)
- Style review (`style-review`)
- Preflight checks (`preflight`)
- Jira integration (6 skills: triage, validate-area, validate-description, validate-issue-type, validate-priority, evaluate-blockers)
- Documentation (3 skills: create, create-package, update)
- Upstream sync (2 skills: sync, sync-status)
- Evaluation review (`jira-eval-review`)

**Quality Assessment**:
- All test types are covered with dedicated rules
- Rules are actionable with specific patterns, examples, and checklists
- Framework-specific (Jest, Cypress, Go testing)
- Cross-cutting testing standards guide for test type selection
- Contract test guidelines specific to BFF API validation
- Weekly agent readiness assessment via CI (`agentready-weekly.yml`)

**Recommendation**: This repository's agent rules serve as the gold standard. Other repositories should model their rules after this implementation.

## Recommendations

### Priority 0 (Critical)

1. **Add container image vulnerability scanning** (2-4 hours)
   - Add Trivy or Grype scanning to the main PR workflow or as a Tekton task
   - Configure severity thresholds (block on CRITICAL, warn on HIGH)
   - This is the most significant security gap

2. **Generate SBOM for built images** (1-2 hours)
   - Add syft or cdxgen to the Docker build or CI pipeline
   - Attach SBOM as a build artifact for supply chain compliance

### Priority 1 (High Value)

3. **Add PR-time Konflux build simulation** (8-12 hours)
   - Create a CI job that simulates the Tekton pipeline locally
   - Catch build differences between GitHub Actions and Konflux before merge
   - Alternatively, integrate Tekton-as-Code to trigger Konflux pipelines from PRs

4. **Enable disabled quality gate checks** (4-8 hours each)
   - Contract testing gate: Infrastructure exists, just needs enforcement
   - API functional testing: Requires common testing framework for modular architecture
   - Bundle size monitoring: Important for Module Federation performance

5. **Add API performance regression testing for BFF services** (4-6 hours)
   - The Go BFF services (7+ packages) lack performance benchmarks
   - Add Go benchmarks or k6/vegeta load testing to catch latency regressions

### Priority 2 (Nice-to-Have)

6. **Expand accessibility testing** (4-6 hours)
   - axe-core is integrated but coverage could be expanded
   - Add automated a11y checks to Cypress mock tests

7. **Add CodeQL SAST scanning** (2-4 hours)
   - Complement Semgrep with CodeQL for deeper TypeScript/Go analysis
   - GitHub-native integration, free for open source

8. **Add chaos engineering for operator** (8-16 hours)
   - Test controller reconciliation under failure conditions
   - Validate webhook behavior with invalid/corrupt input

## Comparison to Gold Standards

| Dimension | odh-dashboard | notebooks (gold std) | kserve (gold std) | Kubernetes best practices |
|-----------|:------------:|:-------------------:|:-----------------:|:------------------------:|
| Unit Tests | 9.0 | 7.0 | 8.0 | 8.0 |
| Integration/E2E | 9.5 | 8.0 | 9.0 | 8.0 |
| Build Integration | 8.0 | 7.0 | 7.0 | 8.0 |
| Image Testing | 7.0 | 9.0 | 7.0 | 8.0 |
| Coverage Tracking | 8.5 | 6.0 | 9.0 | 8.0 |
| CI/CD Automation | 9.5 | 8.0 | 8.0 | 8.0 |
| Agent Rules | **10.0** | 4.0 | 3.0 | N/A |
| Container Scanning | ❌ | ✅ Trivy 5-layer | ❌ | ✅ Expected |
| SBOM | ❌ | ✅ | ❌ | ✅ Expected |
| Contract Tests | ✅ 8 packages | ❌ | ❌ | ❌ |
| Accessibility | ✅ axe-core | N/A | N/A | N/A |
| Pre-commit | ✅ Husky | ❌ | ❌ | ✅ Expected |

**odh-dashboard IS the gold standard** for:
- Agent rules and agentic workflow quality
- Multi-layer testing (unit → mock → E2E → contract)
- CI/CD sophistication and automation
- Monorepo quality practices with modular architecture quality gates

**Areas where others lead**:
- **notebooks**: Container image testing (5-layer validation, Trivy scanning, SBOM)
- **kserve**: Coverage enforcement thresholds

## File Paths Reference

### CI/CD
- `.github/workflows/test.yml` — Main test pipeline (unit, lint, type-check, contract, Cypress mock)
- `.github/workflows/cypress-e2e-test.yml` — Live cluster E2E with failover
- `.github/workflows/dashboard-operator-tests.yml` — Go operator CI
- `.github/workflows/modular-arch-quality-gates.yml` — Module quality assessment
- `.github/workflows/validate-kustomize.yml` — Manifest validation
- `.github/workflows/dependency-validation.yml` — npm audit diff
- `.github/workflows/*-bff-tests.yml` — Per-package BFF test workflows (×7)
- `.tekton/` — 20 Tekton pipeline definitions

### Testing
- `packages/cypress/cypress/tests/mocked/` — Cypress mock tests
- `packages/cypress/cypress/tests/e2e/` — Cypress E2E tests
- `packages/*/contract-tests/` — Contract test suites (8 packages)
- `dashboard-operator/internal/controller/*_test.go` — Operator tests
- `packages/*/bff/**/*_test.go` — BFF Go tests (184 files)

### Code Quality
- `.eslintrc.js` — Root ESLint config (shared)
- `dashboard-operator/.golangci.yml` — Go linter (v2, standard)
- `.prettierrc` — Formatting
- `.husky/pre-commit` — Pre-commit hook with lint-staged
- `semgrep.yaml` — Unified security rules
- `.gitleaks.toml` — Secret scanning config
- `.codecov.yml` — Coverage config (70% patch target)

### Agent Rules
- `.claude/rules/` — 18 rule files (3,550+ lines)
- `.claude/skills/` — 20+ custom skills
- `CLAUDE.md` / `AGENTS.md` — Agent guidance documents
- `.agentready-config.yaml` — Agent readiness config
