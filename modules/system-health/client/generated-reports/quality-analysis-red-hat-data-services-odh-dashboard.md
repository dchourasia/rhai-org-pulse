---
repository: "red-hat-data-services/odh-dashboard"
overall_score: 8.7
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "753 unit/spec test files across frontend, backend, and packages using Jest; strong test-to-code ratio"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "235 Cypress tests spanning 25+ mocked areas and 21 E2E areas; contract tests across 9 modules; cluster failover E2E"
  - dimension: "Build Integration"
    score: 7.5
    status: "Kustomize validation, modular architecture quality gates, BFF build verification; no PR-time Konflux simulation"
  - dimension: "Image Testing"
    score: 6.5
    status: "11 Dockerfiles including Konflux variants; multi-stage builds; no runtime validation or startup testing in CI"
  - dimension: "Coverage Tracking"
    score: 8.0
    status: "Codecov integration with merged unit+Cypress coverage; informational mode with 70% patch target; no hard enforcement"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "26 workflows with concurrency control, caching, matrix strategies, Tekton pipelines, Turbo-based parallelism"
  - dimension: "Agent Rules"
    score: 9.5
    status: "19 comprehensive agent rules covering all test types, architecture, security, conventions; 20 custom skills; AgentReady weekly"
critical_gaps:
  - title: "No PR-time Konflux build simulation"
    impact: "Build issues in Konflux Dockerfiles discovered only after merge; divergence between Dockerfile and Dockerfile.konflux"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No container image runtime validation"
    impact: "Image startup failures, missing environment variables, or broken Node.js entrypoints not caught until deployment"
    severity: "HIGH"
    effort: "6-8 hours"
  - title: "No security scanning in GitHub workflows"
    impact: "Vulnerabilities in dependencies or code not detected at PR time; relies entirely on Konflux/external scanning"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Coverage enforcement is informational only"
    impact: "Coverage can regress without blocking PRs; 70% patch target is advisory"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add Trivy container scanning to PR workflow"
    effort: "2-3 hours"
    impact: "Early detection of CVEs in base images and dependencies before merge"
  - title: "Enable Semgrep scanning in CI"
    effort: "1-2 hours"
    impact: "Semgrep rules exist (semgrep.yaml) but no CI workflow runs them; immediate SAST coverage"
  - title: "Switch Codecov from informational to blocking"
    effort: "30 minutes"
    impact: "Prevent coverage regressions by enforcing the 70% patch target"
  - title: "Add Gitleaks scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Gitleaks config exists (.gitleaks.toml) but no CI workflow runs it; detect secrets in PRs"
recommendations:
  priority_0:
    - "Add PR-time Konflux Dockerfile build validation — build Dockerfile.konflux in CI to catch build divergence early"
    - "Add container image runtime validation — build and start the image in CI, verify health endpoint responds"
  priority_1:
    - "Enable existing Semgrep and Gitleaks configs in CI workflows — the rules are already authored, just not wired into automation"
    - "Add Trivy or Snyk scanning to the PR workflow for container image vulnerability detection"
    - "Switch Codecov enforcement from informational to required status check"
  priority_2:
    - "Add performance regression testing for dashboard page load times"
    - "Enable the disabled modular architecture quality gate checks (mock tests, contract testing, API functional/perf, bundle size)"
    - "Add multi-architecture image build testing (currently single-arch only in CI)"
---

# Quality Analysis: odh-dashboard

## Executive Summary

- **Overall Score: 8.7/10**
- **Repository Type**: TypeScript/React monorepo with Go BFF services and Go operator
- **Primary Languages**: TypeScript (frontend/backend), Go (BFF services, operator)
- **Framework**: React 18 + PatternFly v6 + Module Federation + Turbo monorepo

### Key Strengths
- **Multi-layer testing**: Unit (Jest), Cypress mock, Cypress E2E (live cluster), contract tests — one of the most comprehensive test pyramids in the OpenShift AI ecosystem
- **Contract testing**: 9 modules with contract test suites validating frontend-BFF API boundaries
- **Agent rules excellence**: 19 detailed agent rules + 20 custom skills + weekly AgentReady assessment — industry-leading AI-assisted development infrastructure
- **CI/CD sophistication**: 26 GitHub workflows + Tekton pipelines with concurrency control, aggressive caching, matrix parallelization, and smart test selection

### Critical Gaps
- No PR-time Konflux build simulation — Dockerfile.konflux divergence caught post-merge
- No container image runtime validation in CI
- Security scanning tools (Semgrep, Gitleaks) are configured but not wired into CI workflows
- Coverage enforcement is informational (advisory, not blocking)

### Agent Rules Status: **Exemplary**
19 rules covering architecture, BFF, contract tests, Cypress E2E/mock, unit tests, security, operator patterns, conventions, CSS/PatternFly, modular architecture, module federation, onboarding, pull requests, React, Jira, testing standards, and third-party theming. Plus 20 custom skills for development workflows.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | 753 test files, Jest framework, strong coverage across all workspace packages |
| Integration/E2E | 9.0/10 | 235 Cypress files, 25 mocked areas, 21 E2E areas, contract tests in 9 modules |
| **Build Integration** | **7.5/10** | **Kustomize validation, modular quality gates; no Konflux simulation** |
| Image Testing | 6.5/10 | 11 Dockerfiles with multi-stage builds; no runtime validation or startup checks |
| Coverage Tracking | 8.0/10 | Codecov with merged unit+Cypress coverage; informational mode only |
| CI/CD Automation | 9.5/10 | 26 workflows, Tekton, concurrency control, caching, matrix strategies |
| Agent Rules | 9.5/10 | 19 rules, 20 skills, AgentReady weekly assessment, comprehensive guidance |

## Critical Gaps

### 1. No PR-Time Konflux Build Simulation
- **Impact**: `Dockerfile` and `Dockerfile.konflux` can diverge (different base image pinning, different env vars, different build steps). Build failures in Konflux discovered only post-merge.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Evidence**: `Dockerfile` uses `ARG BASE_IMAGE` with build mode switching; `Dockerfile.konflux` hardcodes RHOAI env vars and pins a specific `ubi9/nodejs-22` digest. These can drift apart.

### 2. No Container Image Runtime Validation
- **Impact**: Node.js server startup failures, missing assets, broken module federation configs not caught until deployment to a cluster
- **Severity**: HIGH
- **Effort**: 6-8 hours
- **Evidence**: No workflow step builds and starts the container image to verify health. 11 Dockerfiles × 0 runtime tests = significant risk surface.

### 3. Security Scanning Not Wired Into CI
- **Impact**: `semgrep.yaml` has comprehensive rules (generic secrets, TypeScript, Go, YAML, Kubernetes patterns) and `.gitleaks.toml` has allowlists configured — but neither is run in any GitHub workflow. Vulnerabilities detected only post-merge by external tools.
- **Severity**: MEDIUM
- **Effort**: 4-6 hours (combined)
- **Evidence**: `grep -rl "trivy\|snyk\|codeql\|semgrep\|gitleaks\|gosec" .github/workflows/` returns empty. The `semgrep.yaml` is a detailed 3.0.0 template covering 5 languages.

### 4. Coverage Enforcement is Informational
- **Impact**: The `.codecov.yml` sets `informational: true` for both project and patch status — coverage regressions don't block PRs
- **Severity**: MEDIUM
- **Effort**: 30 minutes to toggle
- **Evidence**: `.codecov.yml` lines: `informational: true` under both `project.default` and `patch.default`

## Quick Wins

### 1. Enable Semgrep in CI (1-2 hours)
The `semgrep.yaml` file already exists with comprehensive rules. Add a workflow:
```yaml
name: Semgrep
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: semgrep/semgrep-action@v1
        with:
          config: semgrep.yaml
```

### 2. Enable Gitleaks in CI (1-2 hours)
`.gitleaks.toml` is already configured with test file allowlists:
```yaml
name: Gitleaks
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

### 3. Switch Codecov to Blocking (30 minutes)
Change `.codecov.yml`:
```yaml
status:
  patch:
    default:
      informational: false  # was: true
      target: 70%
```

### 4. Add Trivy Scanning (2-3 hours)
```yaml
- name: Build image
  run: docker build -t dashboard:test .
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: dashboard:test
    severity: HIGH,CRITICAL
```

## Detailed Findings

### CI/CD Pipeline

**Workflows (26 total)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| test.yml | push, PR | Main test suite: setup, type-check, lint, unit tests, contract tests, Cypress mock tests, coverage merge + Codecov upload |
| cypress-e2e-test.yml | After test.yml on PRs | Live cluster E2E with failover (primary: dash-e2e-int, secondary: dash-e2e), smart test selection via PR labels and Turbo change detection |
| dashboard-operator-tests.yml | push/PR (operator paths) | Go operator lint, build, test with coverage |
| core-bff-build.yml | push/PR (core-bff paths) | Core BFF Go lint, build, test |
| automl-bff-tests.yml | push/PR | AutoML BFF tests |
| autorag-bff-tests.yml | push/PR | AutoRAG BFF tests |
| eval-hub-bff-tests.yml | push/PR | EvalHub BFF tests |
| gen-ai-bff-build.yml | push/PR | Gen AI BFF build + test |
| gen-ai-frontend-build.yml | push/PR | Gen AI frontend test + build |
| maas-bff-tests.yml | push/PR | MaaS BFF tests |
| mlflow-bff-tests.yml | push/PR | MLflow BFF tests |
| model-registry-bff-tests.yml | push/PR | Model Registry BFF tests |
| model-registry-frontend-tests.yml | push/PR | Model Registry frontend tests |
| eval-hub-frontend-tests.yml | push/PR | EvalHub frontend tests |
| modular-arch-quality-gates.yml | PR (packages/**) | Per-module testing maturity assessment |
| validate-kustomize.yml | push/PR (manifests/**) | RHOAI and ODH Kustomize build validation |
| dependency-validation.yml | PR (package-lock.json) | npm audit diff: blocks PRs that introduce new HIGH advisories |
| agentready-weekly.yml | Weekly schedule | AgentReady assessment, creates issue if score < 75% |
| dependabot-auto-merge.yml | Dependabot PRs | Auto-merge minor/patch updates |
| stale.yml | Daily schedule | Mark stale issues/PRs |
| audit-bypass-notice.yml | PR label | Notification when audit bypass label is applied |
| release-*.yml | workflow_dispatch | Release automation |
| pr-image-expiry.yml | workflow_dispatch | PR image cleanup |

**Strengths**:
- Concurrency control on all major workflows (`cancel-in-progress: true`)
- Aggressive caching: npm modules, Turbo cache, Cypress build cache
- Matrix strategy for Cypress tests (auto-discovered test groups)
- Smart test selection in E2E: PR labels, Turbo change detection, frontend area mapping
- Cluster failover for E2E tests (primary/secondary cluster health checks)
- Path-based triggering to avoid unnecessary runs

**Tekton Pipelines**: 21 pipeline definitions in `.tekton/` for Konflux integration covering:
- Main dashboard (pull-request, push)
- Dashboard operator (pull-request, push)
- Modular architecture packages: MaaS, agent-ops, AutoML, AutoRAG, EvalHub, GenAI, MLflow, Model Registry
- Combined modular architecture pipeline

### Test Coverage

**Test-to-Code Ratio Analysis**:

| Component | Source Files | Test Files | Ratio | Framework |
|-----------|-------------|------------|-------|-----------|
| Frontend | 1,803 TS/TSX | 310 spec/test | 1:5.8 | Jest |
| Backend | 99 TS | 6 spec/test | 1:16.5 | Jest |
| Packages | — | 437 spec/test | — | Jest |
| Cypress (mocked) | — | ~200 cy.ts | — | Cypress |
| Cypress (E2E) | — | ~35 cy.ts | — | Cypress |
| Go (operator) | ~200 .go | 223 _test.go | 1:0.9 | Go testing |
| Contract Tests | — | 24 files | — | Custom + schema validation |

**Notable**:
- Backend test coverage is low (6 test files for 99 source files)
- Go operator has excellent test coverage (nearly 1:1 test-to-code ratio)
- Contract tests cover 9 separate modules: model-registry, mlflow, gen-ai, eval-hub, autorag, automl, agent-ops, core-bff, plus shared utilities
- Coverage merge combines Jest unit + Cypress instrumented coverage into single Codecov report

### Code Quality

**Linting**:
- **ESLint**: Shared config via `@odh-dashboard/eslint-config` package with React TypeScript preset
- **Prettier**: Configured (single quotes, trailing commas, 100 char width)
- **golangci-lint v2.1.0**: Standard linters enabled for operator and BFF services
- **Turbo**: Monorepo task runner for parallel lint/type-check/test across all packages

**Pre-commit Hooks**:
- **Husky**: Pre-commit hook runs `lint-staged` on all staged files
- Module federation port validation on `package.json` changes
- Skip/force override with environment variables
- Helpful error messages with fix instructions

**Static Analysis**:
- `semgrep.yaml`: Comprehensive rule set covering Go, Python, TypeScript, YAML, generic secrets — **NOT wired into CI**
- `.gitleaks.toml`: Secret detection config with test file allowlists — **NOT wired into CI**
- No CodeQL, Trivy, or Snyk integration in GitHub workflows

### Container Images

**Dockerfiles (11 total)**:
- `Dockerfile`: Multi-stage build with ODH/RHOAI build mode switching
- `Dockerfile.konflux`: RHOAI-specific with pinned base image digest
- `Dockerfile.konflux.*`: 9 variant Dockerfiles for modular architecture packages (agent-ops, automl, autorag, eval-hub, genai, maas, mlflow, modelregistry, sealights)

**Build Practices**:
- Multi-stage builds (builder → runtime)
- UBI9 Node.js 22 base image
- Production dependency pruning via custom `prepare-production-manifest.js`
- FIPS compliance: explicit removal of esbuild Go binaries
- Sealights instrumentation variant for code coverage in deployed environments

**Gaps**:
- No image startup validation in CI
- No multi-architecture build testing
- No container scanning workflow
- Potential Dockerfile/Dockerfile.konflux drift (different base image strategies)

### Security

**Configured but not automated**:
- `semgrep.yaml`: 30+ rules across 5 languages (comprehensive template v3.0.0)
- `.gitleaks.toml`: Secret detection with smart allowlists for test fixtures
- `.gitleaksignore`: Known false positive suppression

**Automated**:
- `dependency-validation.yml`: npm audit diff on PR — blocks PRs introducing new HIGH/CRITICAL advisories
- `audit-bypass-notice.yml`: Tracks when teams bypass audit with `ok-to-skip-audit` label
- Sealights integration for runtime code coverage analysis

**Missing**:
- No Trivy/Snyk container scanning in CI
- No CodeQL/SAST workflow
- Semgrep and Gitleaks rules not executed in any workflow

### Agent Rules (Agentic Flow Quality)

**Status**: Exemplary — best-in-class across the ecosystem

**Coverage** (19 rules):
| Rule | Description |
|------|-------------|
| `architecture.md` | Monorepo package boundaries and BFF structure |
| `bff-go.md` | BFF API patterns and Go conventions |
| `contract-tests.md` | Contract test guidelines with BFF API validation |
| `conventions.md` | TypeScript, React, PatternFly coding conventions |
| `css-patternfly.md` | CSS and PatternFly v6 styling rules |
| `cypress-e2e.md` | E2E test creation for live cluster testing |
| `cypress-mock.md` | Mock test creation for isolated component testing |
| `jira-creation.md` | Jira issue creation with RHOAIENG project formatting |
| `modular-architecture.md` | Module Federation and plugin/extension system |
| `module-federation.md` | Module exposure and consumption patterns |
| `module-onboarding.md` | New module/package creation guide |
| `operator-controller.md` | Go operator/controller-runtime patterns |
| `pull-requests.md` | PR creation guidelines with template usage |
| `react.md` | React component/hook/page conventions |
| `security.md` | Auth, secrets, input validation, K8s API reviews |
| `testing-standards.md` | Cross-cutting test type selection guidance |
| `third-party-theming.md` | External library theming with PF tokens |
| `unit-tests.md` | Jest unit test guidelines for utilities/hooks/components |

**Skills (20)**:
- Development workflows: `dev-workflow`, `preflight`, `upstream-sync`, `upstream-sync-status`
- Code review: `coderabbit-autofix`, `coderabbit-code-review`, `coderabbit-review`, `style-review`, `rbac-review`
- Documentation: `docs-create`, `docs-create-package`, `docs-update`
- Jira: `jira-assign-scrum-team`, `jira-eval-review`, `jira-evaluate-blockers`, `jira-triage`, `jira-validate-area-label`, `jira-validate-description`, `jira-validate-issue-type`, `jira-validate-priority-severity`

**Quality Assurance**:
- Weekly AgentReady assessment with automatic issue creation on score regression
- `AGENTS.md` with comprehensive monorepo overview, technology table, and command reference
- `CLAUDE.md` for additional agent context
- `BOOKMARKS.md` indexing key documentation areas

## Recommendations

### Priority 0 (Critical)

1. **Add PR-time Konflux Dockerfile build validation**
   - Build `Dockerfile.konflux` in a CI workflow step to catch build divergence
   - Compare build outputs between `Dockerfile` and `Dockerfile.konflux`
   - Effort: 8-12 hours

2. **Add container image runtime validation**
   - Build image → start container → verify health endpoint → check for startup errors
   - Cover at least the main `Dockerfile.konflux` and 2-3 modular variants
   - Effort: 6-8 hours

### Priority 1 (High Value)

3. **Wire Semgrep into CI**
   - `semgrep.yaml` already has comprehensive rules — just add the workflow
   - Effort: 1-2 hours

4. **Wire Gitleaks into CI**
   - `.gitleaks.toml` already configured — just add the workflow
   - Effort: 1-2 hours

5. **Add Trivy container scanning**
   - Scan built images for CVEs before merge
   - Effort: 2-3 hours

6. **Switch Codecov to blocking mode**
   - Change `informational: true` to `false` for patch coverage
   - Effort: 30 minutes

7. **Increase backend test coverage**
   - 6 test files for 99 source files is significantly below the frontend ratio
   - Effort: 20-30 hours (incremental)

### Priority 2 (Nice-to-Have)

8. **Enable disabled modular architecture quality gate checks**
   - Mock tests, contract testing, API functional/performance, bundle size monitoring are all defined but disabled
   - Effort: Variable per check

9. **Add performance regression testing**
   - Dashboard page load time benchmarks (Lighthouse CI or similar)
   - Effort: 8-12 hours

10. **Add multi-architecture image build testing**
    - Verify ARM64 builds alongside AMD64
    - Effort: 4-6 hours

## Comparison to Gold Standards

| Dimension | odh-dashboard | Gold Standard (odh-dashboard itself IS the gold standard for many) | Notes |
|-----------|--------------|-------------------------------------------------------------------|-------|
| Unit Tests | 8.5 | 9.0 (kserve: coverage enforcement) | Backend test coverage gap |
| Integration/E2E | 9.0 | 9.0 (odh-dashboard) | Contract tests + E2E with cluster failover is best-in-class |
| Build Integration | 7.5 | 9.0 (notebooks: 5-layer validation) | Missing Konflux simulation |
| Image Testing | 6.5 | 9.0 (notebooks: runtime validation) | No startup/runtime checks |
| Coverage Tracking | 8.0 | 9.0 (kserve: enforced thresholds) | Informational only |
| CI/CD Automation | 9.5 | 9.5 (odh-dashboard) | Exemplary workflow organization |
| Agent Rules | 9.5 | 9.5 (odh-dashboard) | Sets the standard for the ecosystem |

**odh-dashboard IS the gold standard** for agent rules, CI/CD organization, and multi-layer testing strategy. The gaps are concentrated in container image lifecycle (build simulation, runtime validation, security scanning) — areas where the `notebooks` repository excels.

## File Paths Reference

### CI/CD
- `.github/workflows/test.yml` — Main test suite (lint, type-check, unit, Cypress mock, contract, coverage)
- `.github/workflows/cypress-e2e-test.yml` — Live cluster E2E with failover
- `.github/workflows/modular-arch-quality-gates.yml` — Per-module testing maturity
- `.github/workflows/validate-kustomize.yml` — Kustomize manifest validation
- `.github/workflows/dependency-validation.yml` — npm audit diff
- `.github/workflows/dashboard-operator-tests.yml` — Go operator tests
- `.github/workflows/*-bff-*.yml` — BFF service test workflows (7 total)
- `.tekton/` — 21 Tekton pipeline definitions

### Testing
- `frontend/src/` — 310 Jest test files
- `backend/src/` — 6 Jest test files
- `packages/*/` — 437 Jest test files across feature packages
- `packages/cypress/cypress/tests/mocked/` — 25 mocked test areas
- `packages/cypress/cypress/tests/e2e/` — 21 E2E test areas
- `packages/*/contract-tests/` — Contract tests in 9 modules
- `dashboard-operator/` — 223 Go test files

### Code Quality
- `.eslintrc.js` — Root ESLint config (shared config package)
- `.prettierrc` — Prettier config
- `semgrep.yaml` — Comprehensive Semgrep rules (NOT in CI)
- `.gitleaks.toml` — Gitleaks config (NOT in CI)
- `.husky/pre-commit` — lint-staged + port validation
- `dashboard-operator/.golangci.yml` — Go linter config

### Container Images
- `Dockerfile` — Main build with ODH/RHOAI mode switching
- `Dockerfile.konflux` — RHOAI Konflux build with pinned digest
- `Dockerfile.konflux.*` — 9 modular architecture variants
- `.codecov.yml` — Coverage config (informational mode)

### Agent Rules
- `CLAUDE.md` — Root agent context
- `AGENTS.md` — Comprehensive monorepo guide
- `.claude/rules/` — 19 detailed rules
- `.claude/skills/` — 20 custom skills
- `.github/workflows/agentready-weekly.yml` — Weekly AgentReady assessment
