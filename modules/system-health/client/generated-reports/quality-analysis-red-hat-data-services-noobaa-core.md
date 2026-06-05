---
repository: "red-hat-data-services/noobaa-core"
overall_score: 4.2
scorecard:
  - dimension: "Unit Tests"
    score: 5.5
    status: "63 unit tests using Mocha framework; coverage tooling (nyc) configured but not enforced in CI"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "Sanity tests run on PR via minikube; Ceph S3 compatibility tests; pipeline tests for system-level validation"
  - dimension: "Build Integration"
    score: 3.5
    status: "Multi-stage container builds on PR but no Konflux simulation; no image startup validation"
  - dimension: "Image Testing"
    score: 3.0
    status: "7 Dockerfiles with multi-stage builds; no runtime validation, no vulnerability scanning, no multi-arch support"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "nyc/istanbul configured locally but never run in CI; no codecov integration; no coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 4.5
    status: "7 workflows but outdated (actions/checkout@v2); no caching, no concurrency control, no parallel test execution"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules for test automation"
critical_gaps:
  - title: "No security scanning in CI/CD"
    impact: "Vulnerabilities in dependencies and container images go undetected until production"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No coverage tracking or enforcement in CI"
    impact: "Code coverage regressions go undetected; no visibility into test coverage trends"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container image vulnerability scanning"
    impact: "CentOS 8 (EOL) base image likely has known CVEs; no Trivy/Snyk scanning"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Outdated CI/CD workflow actions and base images"
    impact: "Using actions/checkout@v2 (deprecated), CentOS 8 (EOL), set-output (deprecated); security and compatibility risks"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No agent rules for AI-assisted development"
    impact: "AI agents cannot follow project-specific test patterns; inconsistent AI-generated code"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Trivy container scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Immediate visibility into container image CVEs; blocks vulnerable images from merging"
  - title: "Upgrade actions/checkout@v2 to v4 across all workflows"
    effort: "1 hour"
    impact: "Fixes deprecated set-output warnings; improves CI reliability and security"
  - title: "Add codecov integration with coverage upload"
    effort: "2-4 hours"
    impact: "PR-level coverage reporting and trend tracking; enables coverage gates"
  - title: "Add Dependabot for dependency updates"
    effort: "30 minutes"
    impact: "Automated security patches for npm dependencies"
recommendations:
  priority_0:
    - "Add container vulnerability scanning (Trivy) to all PR and build workflows"
    - "Integrate coverage reporting into CI (nyc + codecov) with minimum threshold enforcement"
    - "Migrate off CentOS 8 (EOL) base image to UBI 8/9 or similar supported base"
    - "Upgrade all GitHub Actions to current versions (checkout@v4, workflow-dispatch patterns)"
  priority_1:
    - "Add CodeQL or similar SAST scanning for JavaScript/TypeScript code"
    - "Implement pre-commit hooks for linting and secret detection"
    - "Add multi-architecture build support (amd64/arm64)"
    - "Create comprehensive agent rules (.claude/rules/) for test automation patterns"
  priority_2:
    - "Add Dependabot or Renovate for automated dependency updates"
    - "Implement SBOM generation and image signing"
    - "Add performance regression testing for S3 operations"
    - "Modernize frontend testing (currently only 2 test files)"
---

# Quality Analysis: noobaa-core

## Executive Summary

- **Overall Score: 4.2/10**
- **Repository Type**: Node.js object storage system (S3-compatible) with native C++ extensions and a frontend management console
- **Primary Languages**: JavaScript (Node.js), some C++ native code, frontend JavaScript
- **Key Strengths**: Comprehensive unit test suite with 63 unit tests, Ceph S3 compatibility testing, multi-layer container build system, sanity tests with minikube deployment
- **Critical Gaps**: No security scanning, no coverage enforcement in CI, outdated base images (CentOS 8 EOL), deprecated GitHub Actions, no agent rules
- **Agent Rules Status**: Missing - No CLAUDE.md, no .claude/ directory, no test automation guidance for AI agents

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 5.5/10 | 63 unit tests with Mocha; nyc configured locally but not in CI |
| Integration/E2E | 5.0/10 | Sanity + Ceph S3 tests on PR via minikube; pipeline tests exist |
| **Build Integration** | **3.5/10** | **Multi-stage builds on PR; no Konflux simulation; no image validation** |
| Image Testing | 3.0/10 | 7 Dockerfiles; no runtime validation, no scanning, no multi-arch |
| Coverage Tracking | 2.0/10 | nyc/istanbul in package.json but never used in CI; no codecov |
| CI/CD Automation | 4.5/10 | 7 workflows; outdated actions; no caching/concurrency/parallelism |
| Agent Rules | 0.0/10 | Completely absent |

## Critical Gaps

### 1. No Security Scanning in CI/CD
- **Impact**: Vulnerabilities in npm dependencies and container images are never detected before merge or deployment
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No Trivy, Snyk, CodeQL, Semgrep, or any SAST/DAST tools configured. No Dependabot or Renovate for dependency updates. No secret detection (Gitleaks/TruffleHog).

### 2. No Coverage Tracking or Enforcement in CI
- **Impact**: Code coverage regressions go completely undetected. No visibility into test coverage trends over time.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: `nyc` and `istanbul` are listed as devDependencies and a `mocha:coverage` npm script exists, but coverage is never generated or uploaded in any CI workflow. No codecov.yml. No coverage thresholds.

### 3. EOL Base Image (CentOS 8)
- **Impact**: CentOS 8 reached end-of-life on December 31, 2021. No security patches are being issued. Likely contains numerous known CVEs.
- **Severity**: HIGH
- **Effort**: 8-16 hours (migration effort)
- **Details**: `NooBaa.Dockerfile` uses `FROM centos:8`. The Tests.Dockerfile inherits from the NooBaa image. The builder uses `FROM centos:8` as well. All downstream images inherit CVEs.

### 4. Outdated GitHub Actions and Deprecated Patterns
- **Impact**: `actions/checkout@v2` is deprecated. `set-output` is deprecated. These will eventually stop working.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: All 7 workflows use `actions/checkout@v2` (current is v4). The `manual-full-build.yaml` uses the deprecated `::set-output` syntax. No concurrency control on any workflow.

### 5. No Agent Rules for AI-Assisted Development
- **Impact**: AI coding agents cannot follow project-specific conventions for testing, linting, or code organization
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: No `CLAUDE.md`, `AGENTS.md`, or `.claude/` directory. No test creation rules, no framework-specific guidance.

## Quick Wins

### 1. Add Trivy Container Scanning (1-2 hours)
- **Impact**: Immediate CVE detection for all built images
- **Implementation**:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'noobaa'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 2. Upgrade GitHub Actions to v4 (1 hour)
- **Impact**: Fix deprecation warnings, improve security
- **Implementation**: Replace `actions/checkout@v2` with `actions/checkout@v4` in all 7 workflows. Replace `::set-output` with `$GITHUB_OUTPUT`.

### 3. Add Codecov Integration (2-4 hours)
- **Impact**: PR-level coverage visibility and trend tracking
- **Implementation**:
```yaml
- name: Run tests with coverage
  run: npm run mocha:coverage
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage/lcov.info
    fail_ci_if_error: true
```

### 4. Add Dependabot (30 minutes)
- **Impact**: Automated security patches for 200+ npm dependencies
- **Implementation**: Create `.github/dependabot.yml`:
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

**Workflows Inventory** (7 total):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `unit.yaml` | push, PR | Unit tests via `make test` (builds full container chain) |
| `postgres-unit-tests.yaml` | push, PR | Unit tests with PostgreSQL backend |
| `frontend-unit.yml` | push, PR | Frontend tests via `make fe-test` + library build verify |
| `sanity.yaml` | push, PR | Deploys minikube, builds tester image, runs sanity tests |
| `manual-full-build.yaml` | workflow_dispatch | Manual build + push to DockerHub + trigger operator build |
| `weekly-build.yaml` | cron (daily @ 23:00 UTC) | Triggers manual build on master (misnamed "weekly") |
| `next-ver-build.yaml` | cron (Monday 12:00 UTC) | Triggers manual build on 5.8 branch |

**Issues**:
- All workflows use `actions/checkout@v2` (deprecated)
- No caching strategies (npm cache, Docker layer cache)
- No concurrency control (duplicate runs on rapid pushes)
- No test parallelization
- `manual-full-build.yaml` uses deprecated `::set-output` syntax
- `weekly-build.yaml` runs daily despite being named "weekly"
- Build process is slow: every PR run builds the entire container chain (builder -> base -> noobaa -> tester)

### Test Coverage

**Unit Tests** (63 test files in `src/test/unit_tests/`):
- Framework: Mocha with `node --allow-natives-syntax`
- Coverage: nyc configured (`mocha:coverage` script) but never invoked in CI
- Test-to-code ratio: 139 test files / 467 source files = **0.30** (below recommended 0.5+)
- Tests organized via index.js requiring individual test modules
- Good coverage of: S3 operations, namespace FS, chunk operations, node management, crypto/signatures

**System Tests** (12 files in `src/test/system_tests/`):
- Ceph S3 compatibility test suite (pinned to specific commit)
- Sanity build test
- Cloud pools, bucket access, blob API, authentication tests
- Run via framework that deploys to Kubernetes (minikube in CI)

**Pipeline Tests** (11 files in `src/test/pipeline/`):
- System configuration, account management, quota, namespace cache, dataset tests
- Resource-constrained (400m CPU, 400Mi memory per test)
- Run via Kubernetes job framework

**QA Tests** (9 files in `src/test/qa/`):
- Load testing, capacity, data availability, data resiliency
- Agent matrix testing, rebuild replicas
- Not run in CI (manual execution)

**Frontend Tests** (2 files in `frontend/src/tests/`):
- Only `test-restore-session.js` and `index.js`
- Minimal frontend test coverage for a full management console

### Code Quality

**ESLint**:
- Extends `eslint:all` (aggressive base) with many rules turned off
- Good: copyright header enforcement, complexity limits (35), max line length (140), max lines per function (400)
- Weak: Many modern JS best practices disabled (`no-var: off`, `prefer-const: off`, `prefer-template: off`, `prefer-destructuring: off`)
- Uses `eslint-plugin-header` for copyright verification

**TSLint** (deprecated):
- Still using TSLint instead of ESLint for TypeScript
- TSLint has been deprecated since 2019
- Many rules disabled

**TypeScript**:
- `tsconfig.json` enables `checkJs` and `allowJs` (type-checking JS files)
- `noEmit: true` - used only for type checking, not compilation
- Targets ES2020

**Pre-commit Hooks**: None configured
**Static Analysis**: None (no CodeQL, gosec, Semgrep)
**Secret Detection**: None (no Gitleaks, TruffleHog)

### Container Images

**Dockerfile Architecture** (7 Dockerfiles):
1. `builder.Dockerfile` - Build environment with build tools
2. `Base.Dockerfile` - Base image with runtime dependencies (FROM builder)
3. `NooBaa.Dockerfile` - Main production image (FROM centos:8, multi-stage)
4. `Tests.Dockerfile` - Test image with MongoDB, dev tools (FROM noobaa)
5. `FrontendLib.Dockerfile` - Frontend library build verification
6. `dev.Dockerfile` - Developer tools image
7. `Attributes.Dockerfile` - Unknown purpose

**Issues**:
- Base image: `centos:8` (EOL since Dec 2021)
- No multi-architecture support (x86_64 only)
- No vulnerability scanning (no Trivy, Snyk, Grype)
- No SBOM generation
- No image signing/attestation
- No runtime validation tests
- No `.trivyignore` for managing known CVEs
- Test image installs MongoDB 3.6.3 (EOL since April 2021)

### Security

**Current State**: No security tooling configured whatsoever.

| Security Practice | Status |
|-------------------|--------|
| Container scanning (Trivy/Snyk) | Not configured |
| SAST (CodeQL/Semgrep) | Not configured |
| Dependency scanning (Dependabot) | Not configured |
| Secret detection (Gitleaks) | Not configured |
| SBOM generation | Not configured |
| Image signing | Not configured |
| Supply chain security | Not configured |

### Agent Rules (Agentic Flow Quality)

- **Status**: Completely missing
- **Coverage**: No test type rules exist
- **Quality**: N/A
- **Gaps**: No CLAUDE.md, no AGENTS.md, no `.claude/` directory, no `.claude/rules/`, no `.claude/skills/`
- **Recommendation**: Generate comprehensive rules with `/test-rules-generator` covering:
  - Unit test patterns (Mocha, nyc, Node.js testing conventions)
  - S3 compatibility test patterns
  - Container build testing
  - Kubernetes deployment testing

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning** - Integrate Trivy into all PR workflows and the manual build workflow. CentOS 8 EOL base image likely has dozens of critical CVEs.

2. **Migrate off CentOS 8** - Switch to UBI 8/9 or a supported base image. CentOS 8 has been EOL since Dec 2021. This is a security liability.

3. **Integrate coverage reporting into CI** - The `mocha:coverage` script already exists. Add it to the unit test workflow and upload to codecov. Set a minimum coverage threshold (start at current level, ratchet up).

4. **Upgrade all GitHub Actions** - Move from `actions/checkout@v2` to `v4`. Replace deprecated `::set-output` with `$GITHUB_OUTPUT`. Add concurrency groups to prevent duplicate workflow runs.

### Priority 1 (High Value)

5. **Add CodeQL SAST scanning** - Enable CodeQL for JavaScript analysis. This catches security vulnerabilities, code quality issues, and common bugs.

6. **Add pre-commit hooks** - Configure `.pre-commit-config.yaml` with ESLint, secret detection, and commit message formatting.

7. **Add multi-architecture build support** - Support both amd64 and arm64 using Docker buildx. Critical for customers running on ARM-based infrastructure.

8. **Create agent rules** - Generate `.claude/rules/` with test patterns for Mocha unit tests, S3 compatibility tests, and Kubernetes deployment tests.

9. **Modernize TSLint to ESLint** - TSLint has been deprecated since 2019. Migrate TypeScript linting to ESLint with `@typescript-eslint/parser`.

### Priority 2 (Nice-to-Have)

10. **Add Dependabot** - Automated dependency updates for npm packages and GitHub Actions.

11. **Implement SBOM generation** - Add Syft or similar SBOM tool to the build pipeline.

12. **Add performance regression testing** - Benchmark S3 operations (GET, PUT, LIST) and track regressions.

13. **Improve frontend test coverage** - Only 2 frontend test files for an entire management console. Add unit tests for frontend components.

14. **Add Docker layer caching in CI** - Speed up CI builds by caching Docker layers between runs.

## Comparison to Gold Standards

| Practice | noobaa-core | odh-dashboard | notebooks | kserve |
|----------|-------------|---------------|-----------|--------|
| Unit test framework | Mocha | Jest + Cypress | pytest | Go testing |
| Coverage enforcement | None | PR gates | Per-image | Codecov thresholds |
| Container scanning | None | Trivy | Trivy + Snyk | Trivy |
| SAST | None | CodeQL | CodeQL | CodeQL |
| Pre-commit hooks | None | Husky + lint-staged | pre-commit | pre-commit |
| Multi-arch builds | None | N/A | Yes (5-layer) | Yes |
| Dependency scanning | None | Dependabot | Dependabot | Renovate |
| Agent rules | None | Comprehensive | Partial | None |
| CI caching | None | npm cache | pip cache | Go module cache |
| Concurrency control | None | Yes | Yes | Yes |
| Secret detection | None | Gitleaks | Gitleaks | Gitleaks |
| SBOM generation | None | No | No | Syft |

## File Paths Reference

### CI/CD
- `.github/workflows/unit.yaml` - Unit test workflow
- `.github/workflows/postgres-unit-tests.yaml` - Postgres unit tests
- `.github/workflows/frontend-unit.yml` - Frontend tests
- `.github/workflows/sanity.yaml` - Sanity build + minikube deploy
- `.github/workflows/manual-full-build.yaml` - Manual image build
- `.github/workflows/weekly-build.yaml` - Scheduled builds
- `.github/workflows/next-ver-build.yaml` - Next version build
- `Makefile` - Build targets (builder, base, tester, noobaa, test)

### Testing
- `src/test/unit_tests/` - 63 unit test files (Mocha)
- `src/test/system_tests/` - 12 system-level tests
- `src/test/pipeline/` - 11 pipeline integration tests
- `src/test/qa/` - 9 QA/load tests (manual)
- `src/test/framework/` - Test execution framework
- `src/test/web/` - Web UI tests (Selenium)
- `frontend/src/tests/` - 2 frontend test files

### Code Quality
- `.eslintrc.js` - ESLint config (extends eslint:all)
- `.eslintignore` - ESLint ignore patterns
- `tsconfig.json` - TypeScript config (checkJs enabled)
- `tslint.json` - TSLint config (deprecated tool)

### Container Images
- `src/deploy/NVA_build/NooBaa.Dockerfile` - Production image
- `src/deploy/NVA_build/Base.Dockerfile` - Base image
- `src/deploy/NVA_build/builder.Dockerfile` - Build tools
- `src/deploy/NVA_build/Tests.Dockerfile` - Test image
- `src/deploy/NVA_build/FrontendLib.Dockerfile` - FE library build
- `src/deploy/NVA_build/dev.Dockerfile` - Dev tools
- `.dockerignore` - Docker ignore rules

### Infrastructure
- `.travis/deploy_minikube.sh` - Minikube deployment for CI
- `src/test/framework/run_test_job.sh` - K8s test job runner
- `src/test/system_tests/ceph_s3_tests_deploy.sh` - Ceph S3 test setup
