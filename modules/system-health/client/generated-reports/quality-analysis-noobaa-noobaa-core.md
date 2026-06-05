---
repository: "noobaa/noobaa-core"
overall_score: 5.5
scorecard:
  - dimension: "Unit Tests"
    score: 6.0
    status: "Good coverage with Mocha + Jest dual framework, but no coverage measurement"
  - dimension: "Integration/E2E"
    score: 7.0
    status: "Strong external test suites (Ceph S3, Warp, Mint) with containerized execution"
  - dimension: "Build Integration"
    score: 5.0
    status: "PR-time image builds with multi-arch, but no Konflux simulation"
  - dimension: "Image Testing"
    score: 5.0
    status: "Multi-stage builds with multi-arch support, no vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tooling, enforcement, or PR reporting whatsoever"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Comprehensive PR workflow with 10 parallel test jobs and image caching"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, .claude directory, or AI agent guidance exists"
critical_gaps:
  - title: "Zero code coverage tracking"
    impact: "No visibility into what code is tested; regressions go undetected, coverage drift is invisible"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning in CI"
    impact: "Vulnerabilities in dependencies and container images are not detected before merge or release"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No secret detection"
    impact: "Leaked credentials in code or commits are not caught automatically"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No SBOM generation or image signing"
    impact: "Supply chain security gaps; cannot audit shipped artifacts for compliance"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add nyc/c8 coverage and Codecov integration"
    effort: "4-6 hours"
    impact: "Immediate visibility into tested vs. untested code; PR-level coverage diff reporting"
  - title: "Add Trivy container scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Catch known CVEs in base images and dependencies before merge"
  - title: "Add Gitleaks secret detection"
    effort: "1-2 hours"
    impact: "Prevent credential leaks in commits automatically"
  - title: "Create basic CLAUDE.md with test patterns"
    effort: "2-3 hours"
    impact: "Improve AI-generated code and test consistency"
recommendations:
  priority_0:
    - "Implement code coverage tracking (nyc/c8 + Codecov) with PR gating"
    - "Add container vulnerability scanning (Trivy) to PR and nightly workflows"
    - "Add secret detection (Gitleaks) to PR workflow"
  priority_1:
    - "Add CodeQL or Semgrep SAST analysis to PR workflow"
    - "Generate SBOMs (Syft) and sign images (Cosign) in release workflow"
    - "Add pre-commit hooks for lint and secret detection"
    - "Consolidate dual test runners (Mocha + Jest) to a single framework"
  priority_2:
    - "Create comprehensive agent rules for test automation (.claude/rules/)"
    - "Remove legacy Travis CI and Jenkins configurations"
    - "Add Go component testing (currently 0 test files for 3 Go source files)"
    - "Add performance regression testing for S3 operations"
---

# Quality Analysis: noobaa-core

## Executive Summary

- **Overall Score: 5.5/10**
- **Repository Type**: Node.js object storage system with S3 compatibility (minor Go component)
- **Primary Language**: JavaScript (ES2022), 612 source files, ~785 total JS files
- **Key Strengths**: Comprehensive PR test suite with 10 parallel jobs, external S3 compatibility tests (Ceph, Warp, Mint), multi-architecture container builds
- **Critical Gaps**: Zero code coverage tracking, no security scanning at all (no Trivy, CodeQL, Gitleaks), no agent rules
- **Agent Rules Status**: Missing - no CLAUDE.md, AGENTS.md, or .claude directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6/10 | Good coverage with Mocha + Jest dual framework, but no coverage measurement |
| Integration/E2E | 7/10 | Strong external test suites (Ceph S3, Warp, Mint) with containerized execution |
| **Build Integration** | **5/10** | **PR-time image builds with multi-arch, but no Konflux simulation** |
| Image Testing | 5/10 | Multi-stage builds with multi-arch support, no vulnerability scanning |
| Coverage Tracking | 1/10 | No coverage tooling, enforcement, or PR reporting whatsoever |
| CI/CD Automation | 7/10 | Comprehensive PR workflow with 10 parallel test jobs and image caching |
| Agent Rules | 0/10 | No CLAUDE.md, .claude directory, or AI agent guidance exists |

## Critical Gaps

### 1. Zero Code Coverage Tracking
- **Impact**: No visibility into what code is tested; regressions go undetected, coverage drift is invisible
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No codecov, coveralls, nyc, istanbul, or c8 configuration found. Neither Mocha nor Jest test runs generate coverage reports. No PR-level coverage diff is available for reviewers.

### 2. No Security Scanning in CI
- **Impact**: Vulnerabilities in dependencies and container images are not detected before merge or release
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: None of the 38 GitHub Actions workflows include Trivy, Snyk, CodeQL, gosec, or Semgrep. Container images (built from CentOS Stream base) are shipped without vulnerability assessment.

### 3. No Secret Detection
- **Impact**: Leaked credentials in code or commits are not caught automatically
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Details**: No Gitleaks, TruffleHog, or other secret detection tools configured. Given the project handles cloud credentials (AWS, Azure, IBM Cloud), this is a significant risk.

### 4. No SBOM Generation or Image Signing
- **Impact**: Supply chain security gaps; cannot audit shipped artifacts for compliance
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: Release workflow publishes images to Quay.io and Docker Hub without generating SBOMs (Syft) or signing images (Cosign). No attestation chain for shipped artifacts.

### 5. Dual Test Framework Fragmentation
- **Impact**: Test standards are inconsistent; some tests use Mocha conventions, others use Jest
- **Severity**: MEDIUM
- **Effort**: 20-40 hours (long-term migration)
- **Details**: 49 `.test.js` files use Jest, while 115 `test_*.js` files use Mocha via a centralized index file. Jest runs on PR directly (`jest-unit-tests.yaml`), while Mocha tests run inside containers. This split creates confusion about test patterns and makes coverage aggregation harder.

## Quick Wins

### 1. Add nyc/c8 Coverage + Codecov Integration
- **Effort**: 4-6 hours
- **Impact**: Immediate visibility into tested vs. untested code; PR-level coverage diff reporting
- **Implementation**:
  ```yaml
  # Add to jest-unit-tests.yaml
  - name: Run Jest with Coverage
    run: |
      npm install
      npm run build
      npx jest --coverage --coverageReporters=lcov
  - name: Upload Coverage
    uses: codecov/codecov-action@v4
    with:
      files: ./coverage/lcov.info
      token: ${{ secrets.CODECOV_TOKEN }}
  ```

### 2. Add Trivy Container Scanning
- **Effort**: 1-2 hours
- **Impact**: Catch known CVEs in base images and dependencies before merge
- **Implementation**:
  ```yaml
  # Add after image build in run-pr-tests.yaml
  - name: Run Trivy vulnerability scanner
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: 'noobaa'
      format: 'sarif'
      output: 'trivy-results.sarif'
      severity: 'CRITICAL,HIGH'
  ```

### 3. Add Gitleaks Secret Detection
- **Effort**: 1-2 hours
- **Impact**: Prevent credential leaks in commits automatically
- **Implementation**:
  ```yaml
  # New workflow: .github/workflows/gitleaks.yaml
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
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

### 4. Create Basic CLAUDE.md
- **Effort**: 2-3 hours
- **Impact**: Improve AI-generated code and test consistency
- **Implementation**: Document test patterns for both Mocha (index-based) and Jest (.test.js) styles, ESLint conventions, and container-based test execution requirements.

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (38 files)**:

| Category | Workflows | Trigger |
|----------|-----------|---------|
| **PR Tests** | `run-pr-tests.yaml` (orchestrator), `jest-unit-tests.yaml`, `Validate-package-lock.yaml` | `pull_request` |
| **PR Builds** | `build-arm64-image.yaml`, `build-ppc64le-image.yaml` | `push, pull_request` |
| **Nightly** | `nightly-tests.yaml`, `test-aws-sdk-clients.yaml`, `nightly-rpm-build-and-install-test.yaml`, `nightly-rpm-master-build.yaml` | `schedule, workflow_dispatch` |
| **IBM Infra** | `ibm-nightly-vm-provision.yaml`, `ibm-nightly-vm-cleanup.yaml`, `ibm-daily-leftover-cleanup.yaml` + dispatchers | `schedule, workflow_dispatch` |
| **Build** | `manual-full-build.yaml`, `manual-build-rpm.yaml`, `weekly-build.yaml`, `current-ver-build.yaml`, `next-ver-build.yaml` | `workflow_dispatch, push` |
| **Release** | `releaser.yaml` | `workflow_dispatch` |
| **Shared** | `sanity.yaml`, `sanity-ssl.yaml`, `postgres-unit-tests.yaml`, `nc_unit.yml`, `ceph-s3-tests.yaml`, `ceph-nsfs-s3-tests.yaml`, `warp-tests.yaml`, `warp-nc-tests.yaml`, `mint-tests.yaml`, `mint-nc-tests.yaml` | `workflow_call` |
| **Housekeeping** | `stale.yml` | `schedule` |
| **RPM** | `rpm-build-base.yaml`, `rpm-build-and-upload-flow.yaml`, `rpm-build-and-install-test-base.yaml`, `manual-rpm-build-and-install-test.yaml` | Various |

**Strengths**:
- Comprehensive PR test matrix: sanity, sanity-ssl, postgres unit, NC unit, ceph-s3, ceph-nsfs-s3, warp, warp-nc, mint, mint-nc (10 parallel jobs)
- Good concurrency control (`cancel-in-progress: true` on most workflows)
- Smart image caching: pulls base/builder images from quay.io before rebuilding, with date-based tag lookup going back 20 days
- Conditional base image rebuild based on changed files (package.json, Dockerfile, .nvmrc, fs_napi.cpp)
- Artifact passing between jobs via `upload-artifact`/`download-artifact`

**Gaps**:
- Legacy CI configurations still present (`.travis.yml`, `.jenkins/`) - creates confusion
- No workflow reuse across the non-shared workflows (some duplication in build steps)
- No test result caching or test impact analysis
- Nightly tests are `workflow_dispatch` only - not actually scheduled (despite the name)

### Test Coverage

**Test Architecture**:
- **Dual framework**: Mocha (legacy, majority) + Jest (newer, growing)
- **Total test files**: 219 JavaScript test files
- **Unit tests**: 90 files in `src/test/unit_tests/`
- **Integration tests**: 58 files in `src/test/integration_tests/`
- **System tests**: 11 files in `src/test/system_tests/`
- **External S3 compatibility**: Ceph S3, Warp, Mint, Hadoop S3A
- **Test-to-source ratio**: 219 test files / 612 source files = 0.36

**Test Organization**:
```
src/test/
├── unit_tests/          # 90 files - utilities, API, IAM, NSFS, native, NC
│   ├── api/             # S3, IAM validation
│   ├── internal/        # Core components (chunk, file, replication)
│   ├── nc/              # Non-containerized (lifecycle, config, master keys)
│   ├── nsfs/            # NSFS filesystem testing
│   ├── native/          # Native code (fs_napi)
│   ├── tls/             # TLS configuration
│   └── util_functions/  # Utility function tests
├── integration_tests/   # 58 files - DB, API, NSFS, NC CLI
│   ├── api/             # S3, IAM, STS
│   ├── db/              # Store tests (md_store, nodes_store)
│   ├── internal/        # Map client, agent blocks
│   ├── nc/cli/          # CLI tests (bucket, account, connection)
│   └── nsfs/            # Concurrency tests
├── system_tests/        # 11 files - Full system sanity
├── external_tests/      # S3 compatibility suites
│   ├── ceph_s3_tests/   # Ceph S3 compatibility
│   ├── warp/            # Warp performance tests
│   ├── mint/            # MinIO Mint compatibility
│   └── hadoop_s3a_tests/ # Hadoop S3A tests
├── pipeline/            # Pipeline tests (namespace cache, quota)
└── framework/           # Test infrastructure
```

**Mocha Test Execution**:
Tests are organized via index files (`src/test/utils/index/index.js`) that `require()` individual test files. This is an older pattern - it means all tests must be maintained in index files, and forgetting to add a test to the index means it won't run.

**Jest Test Execution**:
49 `.test.js` files run via `npx jest` directly. These follow modern patterns and don't need manual index management.

**Coverage Status**: None. No coverage tooling is configured for either Mocha or Jest.

### Code Quality

**ESLint Configuration** (`.eslintrc.js`):
- **Approach**: Extends `eslint:all` and selectively overrides - very comprehensive
- **Plugins**: `@stylistic/js` for style, `header` for copyright enforcement
- **Notable rules**:
  - Copyright header enforcement: `header/header` (error)
  - Complexity limit: 35 (should be ~10)
  - Max file length: 2000 lines
  - Max function length: 400 lines
  - Max parameters: 7
  - Max statements per function: 60
  - Line length: 140 chars
- **Quality**: Strong ESLint config, but thresholds are very permissive (complexity 35, function length 400 lines)

**Code Review**: CodeRabbit AI configured (`.coderabbit.yaml`) with auto-review on `master` branch, "chill" profile. Good - provides automated review.

**Missing**:
- No pre-commit hooks (`.pre-commit-config.yaml` absent)
- No static analysis tools (CodeQL, Semgrep)
- No TypeScript strict mode (only 1 `.ts` file, project is mostly JavaScript)
- No dependency auditing in CI

### Container Images

**Dockerfile Inventory** (8 files):
| File | Purpose |
|------|---------|
| `Base.Dockerfile` | Base image with npm deps and native code |
| `builder.Dockerfile` | Build environment |
| `NooBaa.Dockerfile` | Production image (multi-stage from CentOS Stream) |
| `Tests.Dockerfile` | Tester image for CI |
| `RPM.Dockerfile` | RPM package build |
| `SSLPostgres.Dockerfile` | SSL Postgres for integration tests |
| `dev.Dockerfile` | Development environment |
| `AWSClient.Dockerfile` | AWS SDK client testing |

**Strengths**:
- Multi-stage builds (builder → base → production)
- Multi-architecture support (amd64, arm64, ppc64le) built on every PR
- Tester image pattern - tests execute in consistent container environment
- Smart conditional rebuild based on changed files
- RPM build and install test validates packaging

**Gaps**:
- No vulnerability scanning on any built images
- No SBOM generation
- No image signing/attestation
- Base image is `quay.io/centos/centos:stream9` - not minimal (could use UBI minimal)
- `.dockerignore` is minimal (only 3 entries)

### Security

**Current State**: No security tooling exists in the repository.

| Tool Category | Status | Gap |
|---------------|--------|-----|
| Container Scanning (Trivy/Snyk) | Missing | Images shipped without CVE assessment |
| SAST (CodeQL/Semgrep) | Missing | No static analysis for code vulnerabilities |
| Secret Detection (Gitleaks) | Missing | Cloud credentials at risk of leaking |
| Dependency Scanning | Missing | npm audit not run in CI |
| SBOM Generation (Syft) | Missing | No supply chain transparency |
| Image Signing (Cosign) | Missing | No artifact integrity verification |
| DAST | Missing | No dynamic testing of S3 endpoints |

This is the most critical gap in the repository's quality posture. Given that noobaa-core handles cloud storage credentials (AWS, Azure, IBM Cloud), manages object storage with S3 API compatibility, and publishes container images to public registries, the absence of any security scanning is a significant risk.

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None - no CLAUDE.md, AGENTS.md, or `.claude/` directory
- **Quality**: N/A
- **Gaps**:
  - No test creation guidelines for AI agents
  - No documentation of the dual Mocha/Jest pattern
  - No guidance on container-based vs. direct test execution
  - No coding standards beyond ESLint configuration
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` to cover:
  - Unit test patterns (Jest `.test.js` format preferred for new tests)
  - Integration test patterns (with Postgres, NC mode)
  - The Mocha index file requirement for legacy tests
  - Container-based test execution requirements
  - S3 compatibility test patterns (Ceph, Warp, Mint)

## Recommendations

### Priority 0 (Critical)

1. **Implement code coverage tracking**
   - Add `c8` or `nyc` to Mocha test runs, enable `--coverage` for Jest
   - Integrate Codecov with PR comments and gating
   - Start with baseline measurement, then set minimum threshold (e.g., 50%)
   - Effort: 4-6 hours

2. **Add container vulnerability scanning (Trivy)**
   - Scan the built `noobaa` image in PR workflow
   - Set `severity: CRITICAL,HIGH` to fail on serious CVEs
   - Add `.trivyignore` for accepted risks
   - Effort: 1-2 hours

3. **Add secret detection (Gitleaks)**
   - Add to PR workflow with full history scan
   - Configure exceptions via `.gitleaks.toml` for test fixtures
   - Effort: 1-2 hours

### Priority 1 (High Value)

4. **Add CodeQL SAST analysis**
   - Enable for JavaScript (primary language)
   - Run on PR and weekly schedule
   - Effort: 2-3 hours

5. **Add SBOM generation and image signing to release workflow**
   - Use Syft for SBOM, Cosign for signing
   - Attach SBOMs as release artifacts
   - Effort: 4-6 hours

6. **Add pre-commit hooks**
   - ESLint, secret detection, package-lock validation
   - Use `.pre-commit-config.yaml` with husky or lint-staged
   - Effort: 2-3 hours

7. **Consolidate test frameworks**
   - Migrate Mocha tests to Jest over time
   - New tests should use Jest `.test.js` pattern exclusively
   - Remove index file dependency for new tests
   - Effort: 20-40 hours (phased)

### Priority 2 (Nice-to-Have)

8. **Create comprehensive CLAUDE.md and agent rules**
   - Document test patterns, architecture, contribution guidelines
   - Add `.claude/rules/` for unit, integration, and E2E test creation
   - Effort: 2-3 hours

9. **Remove legacy CI configurations**
   - `.travis.yml` appears unused (GHA handles everything)
   - `.jenkins/` directory may be unused
   - Effort: 1 hour

10. **Add Go component testing**
    - 3 Go source files in `go/` with 0 test files
    - Add basic unit tests for the Go utilities
    - Effort: 2-4 hours

11. **Tighten ESLint thresholds**
    - Reduce complexity from 35 to ~15
    - Reduce max-lines-per-function from 400 to ~100
    - Reduce max-statements from 60 to ~30
    - Effort: 8-16 hours (phased, with codemod)

12. **Add npm audit to CI**
    - Run `npm audit --audit-level=high` in PR workflow
    - Effort: 30 minutes

## Comparison to Gold Standards

| Capability | noobaa-core | odh-dashboard | notebooks | kserve |
|------------|-------------|---------------|-----------|--------|
| Unit Test Framework | Mocha + Jest (dual) | Jest | pytest | Go testing |
| Integration Tests | Container-based | Cypress + API | Image validation | envtest |
| E2E Tests | S3 compat suites | Cypress E2E | Multi-layer | KServe E2E |
| Coverage Tracking | **None** | Codecov enforced | Present | Codecov enforced |
| Coverage Gating | **None** | PR thresholds | Basic | PR thresholds |
| Container Scanning | **None** | Trivy | Trivy | Trivy |
| SAST | **None** | CodeQL | Limited | CodeQL |
| Secret Detection | **None** | Gitleaks | Gitleaks | Gitleaks |
| Pre-commit Hooks | **None** | Husky + lint-staged | pre-commit | pre-commit |
| SBOM/Signing | **None** | Cosign + Syft | Cosign | Cosign + Syft |
| Agent Rules | **None** | Comprehensive | Basic | Partial |
| Multi-arch Builds | arm64, ppc64le | amd64 | Multi-arch | Multi-arch |
| CI Concurrency | cancel-in-progress | cancel-in-progress | cancel-in-progress | cancel-in-progress |
| Test Parallelism | 10 parallel jobs | Sharded | Matrix | Parallel |

**Key Takeaways**:
- noobaa-core excels at S3 compatibility testing and multi-architecture builds
- The biggest gaps vs. gold standards are in coverage tracking, security scanning, and agent rules
- The test suite is functionally rich (219 test files, external compatibility suites) but lacks measurement and enforcement

## File Paths Reference

### CI/CD
- `.github/workflows/run-pr-tests.yaml` - Main PR orchestrator
- `.github/workflows/jest-unit-tests.yaml` - Jest unit tests (PR)
- `.github/workflows/Validate-package-lock.yaml` - Package lock validation (PR)
- `.github/workflows/build-arm64-image.yaml` - ARM64 build (PR)
- `.github/workflows/build-ppc64le-image.yaml` - PPC64LE build (PR)
- `.github/workflows/nightly-tests.yaml` - Nightly test dispatch
- `.github/workflows/releaser.yaml` - Release workflow

### Testing
- `src/test/unit_tests/` - 90 unit test files
- `src/test/integration_tests/` - 58 integration test files
- `src/test/system_tests/` - 11 system test files
- `src/test/external_tests/` - Ceph, Warp, Mint, Hadoop S3A
- `src/test/utils/index/index.js` - Mocha test index (entry point)
- `src/test/framework/` - Test infrastructure

### Code Quality
- `.eslintrc.js` - Comprehensive ESLint config (extends eslint:all)
- `.eslintignore` - ESLint ignore list
- `.coderabbit.yaml` - CodeRabbit AI review config
- `tslint.json` - TSLint config (likely unused/legacy)

### Container Images
- `src/deploy/NVA_build/Base.Dockerfile` - Base image
- `src/deploy/NVA_build/NooBaa.Dockerfile` - Production image
- `src/deploy/NVA_build/Tests.Dockerfile` - Test image
- `src/deploy/NVA_build/builder.Dockerfile` - Builder image
- `src/deploy/RPM_build/RPM.Dockerfile` - RPM build

### Build
- `Makefile` - Build and test targets (extensive: test-postgres, test-cephs3, test-warp, test-mint, etc.)
- `package.json` - npm scripts (test, lint, mocha, jest)
- `binding.gyp` - Native code build config

### Legacy CI (candidates for removal)
- `.travis.yml` - Travis CI config
- `.jenkins/` - Jenkins pipeline configs
