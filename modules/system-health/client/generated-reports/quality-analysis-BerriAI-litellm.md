---
repository: "BerriAI/litellm"
overall_score: 8.4
scorecard:
  - dimension: "Unit Tests"
    score: 9.0
    status: "Exceptional test coverage with 2,057 test files, 833K lines of test code, and 1.33:1 test-to-source ratio"
  - dimension: "Integration/E2E"
    score: 8.5
    status: "Comprehensive E2E via CircleCI with Docker-based proxy tests, Playwright UI tests, and real LLM API calls"
  - dimension: "Build Integration"
    score: 7.0
    status: "Docker image built and tested in CircleCI; UI build validated on PRs; no PR-time image validation"
  - dimension: "Image Testing"
    score: 7.5
    status: "Multi-stage Docker build with Chainguard base, cosign signing, hardened non-root variant; limited runtime validation"
  - dimension: "Coverage Tracking"
    score: 9.0
    status: "Codecov with component-level tracking, flag management, carryforward, and no-drop threshold enforcement"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "40+ workflows across GitHub Actions and CircleCI with reusable bases, concurrency control, caching, and mutation testing"
  - dimension: "Agent Rules"
    score: 7.5
    status: "Strong CLAUDE.md with testing philosophy, test organization guidance, and code quality standards; no .claude/rules/ directory"
critical_gaps:
  - title: "No pre-commit hooks"
    impact: "Developers can push code without running linters or formatters locally; issues caught only in CI"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "No container vulnerability scanning in CI"
    impact: "Container image vulnerabilities are not systematically scanned; no Trivy/Snyk/Grype integration in workflows"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time Docker image build validation"
    impact: "Image build failures discovered only post-merge in CircleCI; PRs only validate code, not containerization"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "E2E tests run post-merge only (CircleCI)"
    impact: "Integration/E2E failures discovered after merge; PRs only run unit tests"
    severity: "MEDIUM"
    effort: "8-16 hours"
quick_wins:
  - title: "Add Trivy container scanning to CI"
    effort: "2-3 hours"
    impact: "Catch CVEs in container images before they ship; straightforward GitHub Actions integration"
  - title: "Add .pre-commit-config.yaml with ruff, black, mypy"
    effort: "1-2 hours"
    impact: "Catch formatting and lint issues before commit; reduce CI feedback loops"
  - title: "Add SBOM generation to Docker build workflow"
    effort: "1-2 hours"
    impact: "Supply chain transparency; required for many compliance frameworks"
  - title: "Create .claude/rules/ directory with test automation rules"
    effort: "2-3 hours"
    impact: "Codify test patterns already documented in CLAUDE.md into structured agent rules"
recommendations:
  priority_0:
    - "Add container vulnerability scanning (Trivy/Grype) to PR and post-merge workflows"
    - "Add SBOM generation with syft/trivy to Docker build pipeline"
  priority_1:
    - "Move critical E2E tests to PR-time execution (at least smoke tests)"
    - "Add PR-time Docker image build validation step in GitHub Actions"
    - "Add pre-commit hooks for ruff, black, and mypy checks"
  priority_2:
    - "Create .claude/rules/ directory with structured test creation rules"
    - "Add multi-architecture Docker image builds (arm64)"
    - "Add API contract testing with OpenAPI schema validation on PRs"
---

# Quality Analysis: BerriAI/litellm

## Executive Summary

- **Overall Score: 8.4/10**
- **Repository Type**: Python library + proxy server (LLM gateway)
- **Primary Language**: Python (with TypeScript/React UI)
- **Framework**: FastAPI (proxy), Prisma (ORM), React (UI dashboard)
- **Key Strengths**: Exceptional test volume (2,057 test files, 833K lines), sophisticated CI/CD across GitHub Actions + CircleCI, mature Codecov integration with component tracking, mutation testing, strong agent coding guidelines (CLAUDE.md), supply-chain security guardrails
- **Critical Gaps**: No container vulnerability scanning, no pre-commit hooks, E2E tests run post-merge only, no PR-time Docker image validation
- **Agent Rules Status**: Strong CLAUDE.md with detailed testing philosophy; AGENTS.md delegates to CLAUDE.md; no `.claude/rules/` directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 9.0/10 | Exceptional: 2,057 test files, 833K LOC, 1.33:1 test-to-source ratio |
| Integration/E2E | 8.5/10 | Comprehensive CircleCI E2E with Docker proxy, Playwright UI, real API calls |
| **Build Integration** | **7.0/10** | **Docker build + test in CircleCI; UI build on PRs; no PR-time image build** |
| Image Testing | 7.5/10 | Multi-stage Chainguard build, cosign, hardened variant; no Trivy/SBOM |
| Coverage Tracking | 9.0/10 | Codecov with components, flags, carryforward, threshold enforcement |
| CI/CD Automation | 9.5/10 | 40+ workflows, reusable bases, concurrency control, mutation testing |
| Agent Rules | 7.5/10 | Excellent CLAUDE.md; missing structured .claude/rules/ |

## Critical Gaps

### 1. No Container Vulnerability Scanning
- **Impact**: Container images may ship with known CVEs in base images or dependencies
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Despite using security-focused Chainguard base images and having cosign for image signing, there is no Trivy, Snyk, or Grype scanning integrated into any CI workflow. The Chainguard base reduces risk but does not eliminate it.

### 2. E2E Tests Run Post-Merge Only
- **Impact**: Integration and E2E failures are discovered after code is merged into main branches
- **Severity**: MEDIUM
- **Effort**: 8-16 hours to restructure
- **Details**: All CircleCI jobs (30+ E2E/integration jobs) only run on `main` and `litellm_*` branches, not on PRs. PRs run ~15 GitHub Actions unit test workflows but no E2E validation. This means broken integrations can land.

### 3. No PR-Time Docker Image Build Validation
- **Impact**: Dockerfile changes that break the build are not caught until post-merge CircleCI
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: The GitHub Actions `test-litellm-ui-build.yml` validates UI builds on PRs, but there is no equivalent for the main Docker image build. The CircleCI `build_docker_database_image` job only runs post-merge.

### 4. No Pre-Commit Hooks
- **Impact**: Developers can push unformatted or unlinted code; issues caught only in CI
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: Despite having ruff, black, flake8, and mypy configured, there is no `.pre-commit-config.yaml`. Local development relies on developers manually running `make lint` and `make format`.

## Quick Wins

### 1. Add Trivy Container Scanning (2-3 hours)
- **Impact**: Catch CVEs in container images before release
- **Implementation**: Add a GitHub Actions workflow that builds the Docker image on PRs and scans with Trivy:
```yaml
- name: Build image
  run: docker build -t litellm:pr .
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'litellm:pr'
    severity: 'CRITICAL,HIGH'
```

### 2. Add Pre-Commit Hooks (1-2 hours)
- **Impact**: Shift-left linting and formatting to developer machines
- **Implementation**: Create `.pre-commit-config.yaml` with ruff, black, and mypy hooks

### 3. Add SBOM Generation (1-2 hours)
- **Impact**: Supply chain transparency; pairs with existing cosign signing
- **Implementation**: Add syft or trivy SBOM generation step to Docker build workflow

### 4. Create `.claude/rules/` Directory (2-3 hours)
- **Impact**: Structured agent rules for test creation; builds on existing CLAUDE.md philosophy
- **Implementation**: Extract test patterns from CLAUDE.md into individual rule files per test type

## Detailed Findings

### CI/CD Pipeline

**Strengths (Score: 9.5/10)**:

litellm has one of the most sophisticated CI/CD setups encountered. It operates across **two CI systems**:

**GitHub Actions (PR-time, ~20 workflows)**:
- 13+ unit test workflows covering: core utils, LLM providers (per-provider sharding), proxy auth, proxy DB, proxy endpoints, proxy infrastructure, proxy legacy, proxy management behavior, responses/caching/types, enterprise/routing, integrations, security, documentation
- Reusable workflow bases (`_test-unit-base.yml`, `_test-unit-services-base.yml`) with parametric test paths, worker counts, rerun limits, and timeouts
- Code quality: Ruff linting, Black formatting, Semgrep custom rules, CodeQL (Python + JS + Actions), zizmor (GH Actions security), OSSF Scorecard
- Concurrency control on all workflows (`cancel-in-progress: true`)
- Dependency caching with uv lockfile hash keys
- UI build validation on PRs
- Branch protection guards (fork dependency injection blocking, main branch source validation)
- Coverage upload to Codecov with OIDC auth on every test shard

**CircleCI (Post-merge, ~30 jobs)**:
- Docker image build and multi-scenario testing
- Proxy E2E tests with real Postgres, Redis, and LLM API calls
- Playwright UI E2E tests
- Multi-instance proxy tests
- Pass-through endpoint tests
- Helm chart testing with Kind clusters
- Windows compatibility testing
- Python version matrix (3.10, 3.13, v2 migration resolver)
- Comprehensive coverage aggregation across all jobs

**Special features**:
- **Mutation testing** (`mutation-test.yml`): Manual workflow using mutmut with `mutate_only_covered_lines` optimization, targeting proxy management endpoints
- **Performance benchmarks** (`codspeed.yml`): CodSpeed integration for PR and push performance regression detection
- **Schema sync checks**: Validate Prisma schema consistency
- **Model map validation**: Ensure model pricing data is correct
- **Supply-chain hardening**: SHA-pinned actions, fork dependency guards, no `curl | bash` policy

**Gaps**:
- E2E tests only run post-merge (CircleCI doesn't trigger on PRs)
- No Docker image build validation on PRs
- No Trivy/Snyk container scanning anywhere

### Test Coverage

**Strengths (Score: 9.0/10)**:

The test infrastructure is exceptional in volume and organization:

- **2,057 test files** with **833,326 lines** of test code
- **1,917 source files** with **627,697 lines** of production code
- **Test-to-source ratio**: 1.33:1 (tests significantly exceed source volume)
- **Test organization**: `tests/test_litellm/` mirrors `litellm/` directory structure (documented in readme)
- **Testing frameworks**: pytest with pytest-asyncio, pytest-xdist (parallel), pytest-rerunfailures, pytest-cov, pytest-recording (VCR cassettes), pytest-mock, respx/responses/requests-mock for HTTP mocking
- **Test categories**: Unit tests, proxy behavior tests, integration tests, E2E tests, load tests, benchmarks, proxy security tests, Windows tests, documentation validation tests, code coverage analysis tests
- **Mutation testing**: mutmut configured for proxy management endpoints with `>90% kill rate` target stated in CLAUDE.md
- **Dependency injection**: CLAUDE.md explicitly discourages monkeypatching, prefers DI for testability

**Coverage Tracking (Score: 9.0/10)**:
- Codecov integration with OIDC authentication
- Component-level coverage: Router, LLMs, Caching, litellm_logging, Proxy_Authentication, Enterprise
- Flag management with carryforward for re-runs
- `target: auto` with `threshold: 0%` — coverage must not drop on project or patch
- PR comment layout includes header, diff, flags, and components
- Coverage generated per-shard with pytest-cov, uploaded per-workflow flag

### Code Quality

**Strengths (Score: 8.5/10)**:

- **Ruff**: Configured with `line-length = 120`, `E501`, `PLR0915`, `T20` rules enabled; per-file overrides for complex modules
- **Black**: Code formatting with `isort` profile
- **Flake8**: Backup linter with extensive ignore list (for compatibility with Black)
- **MyPy**: Type checking with Pydantic plugin (`plugins = "pydantic.mypy"`)
- **Pyright**: Additional type checking (with pragmatic exclusions for complex types)
- **Semgrep**: Custom rules for security (no `.claude/` directory committed) and reliability (unbounded asyncio queues)
- **CodeQL**: Multi-language scanning (Python, JavaScript/TypeScript, Actions) on push and PRs, plus daily scheduled scans
- **zizmor**: GitHub Actions security analysis
- **OSSF Scorecard**: Supply-chain security scoring
- **GitGuardian**: Secret detection with extensive false-positive suppression

**Gaps**:
- No `.pre-commit-config.yaml` — all quality checks are CI-only
- Flake8 configuration has extremely broad ignore list (nearly every rule ignored)
- No dead code detection tools (vulture, etc.)

### Container Images

**Strengths (Score: 7.5/10)**:

- **Base image**: Chainguard wolfi-base with SHA256 pinning (security-focused, minimal attack surface)
- **Multi-stage builds**: Builder and runtime stages with proper layer caching
- **UV for dependency management**: Reproducible installs with `uv sync --frozen`
- **Non-root variant**: `Dockerfile.non_root` for hardened deployments
- **Hardened docker-compose**: `docker-compose.hardened.yml` with read-only filesystem, `cap_drop: ALL`, `no-new-privileges`, proxy enforcement via Squid
- **Image signing**: cosign public key present (`cosign.pub`) for image verification
- **Prisma binary isolation**: Only Prisma cache directories copied, not full build cache (avoids CVE from setuptools wheel)

**Gaps**:
- No Trivy/Snyk/Grype container scanning in any CI pipeline
- No SBOM generation (syft/trivy)
- No multi-architecture builds (only amd64)
- No PR-time Docker build validation
- Runtime stage includes npm for a one-time dependency fix — potential attack surface

### Security

**Strengths (Score: 8.5/10)**:

- **CodeQL**: Multi-language SAST on PRs, pushes, and daily schedule
- **Semgrep**: Custom security rules (no .claude directory, unbounded memory)
- **GitGuardian**: Secret detection with `version: 2` config and SHA-based false-positive suppression
- **zizmor**: GitHub Actions security analysis (workflow injection, artifact poisoning)
- **OSSF Scorecard**: Supply-chain security scoring with SARIF upload
- **Fork dependency guard**: Blocks fork PRs from modifying `uv.lock` or adding new dependencies
- **Main branch guard**: Only `litellm_internal_staging` or `litellm_hotfix_*` branches can target `main`
- **SHA-pinned actions**: All GitHub Actions use full SHA pins (e.g., `actions/checkout@08eba0b27...`)
- **CI supply-chain policy**: CLAUDE.md mandates SHA verification for all downloaded binaries; no `curl | bash`
- **Bug bounty program**: P0-P2 classification with $500-$3,000 bounties
- **cosign image signing**: Public key available for verification
- **Image attestation awareness**: Chainguard base images with built-in provenance

**Gaps**:
- No container image vulnerability scanning
- No dependency vulnerability scanning (Dependabot/Renovate not visible)
- No SBOM generation

### Agent Rules (Agentic Flow Quality)

**Status**: Present (CLAUDE.md + AGENTS.md) | **Score: 7.5/10**

**Strengths**:
- **CLAUDE.md**: 76 lines of highly opinionated, practical coding guidelines covering:
  - Testing philosophy: "meaningful tests" with `>90% mutation testing kill rate` goal
  - Test organization: `tests/test_litellm/` mirrors `litellm/` convention
  - Anti-patterns: No monkeypatching, prefer dependency injection
  - Proof-of-fix: Requires real `curl` commands against live proxy, not just pytest screenshots
  - Code quality priorities: correct > secure > performant > readable > maintainable > modern
  - Comment policy: No comments unless absolutely necessary (DRY rationale)
  - Supply-chain safety: SHA verification for all CI downloads
- **AGENTS.md**: Points to CLAUDE.md (single source of truth)
- **GEMINI.md**: Points to CLAUDE.md (cross-agent consistency)
- **Semgrep rule**: Prevents `.claude/` directory from being committed

**Gaps**:
- No `.claude/` directory or `.claude/rules/` with structured per-test-type rules
- No specific agent rules for unit vs integration vs E2E test creation patterns
- No agent skills for test generation or quality validation
- CLAUDE.md guidelines are excellent but monolithic — not structured for agent tool consumption

## Recommendations

### Priority 0 (Critical)
1. **Add container vulnerability scanning** — Integrate Trivy or Grype into GitHub Actions for PR-time and post-merge scanning. Given the Chainguard base, focus on application-layer dependencies
2. **Add SBOM generation** — Pair with existing cosign signing for complete supply-chain attestation. Use `syft` or `trivy sbom` in the Docker build pipeline

### Priority 1 (High Value)
3. **Move smoke E2E tests to PR-time** — Select 3-5 critical CircleCI E2E scenarios and replicate as GitHub Actions workflows that run on PRs. Focus on proxy startup, basic API passthrough, and auth
4. **Add PR-time Docker image build** — Create a GitHub Actions workflow that builds the Docker image on PRs without pushing, catching Dockerfile regressions early
5. **Add pre-commit hooks** — Create `.pre-commit-config.yaml` with ruff, black, mypy, and the existing semgrep rules

### Priority 2 (Nice-to-Have)
6. **Create `.claude/rules/` directory** — Extract CLAUDE.md testing guidance into structured rules: `unit-tests.md`, `integration-tests.md`, `e2e-tests.md`, `proxy-tests.md`
7. **Add multi-architecture Docker builds** — Support arm64 alongside amd64 for Apple Silicon development and ARM cloud instances
8. **Add API contract testing** — Validate OpenAPI schema consistency between documentation and actual proxy endpoints on PRs
9. **Add dependency vulnerability scanning** — Integrate Dependabot or Renovate for automated dependency update PRs

## Comparison to Gold Standards

| Practice | litellm | odh-dashboard | notebooks | kserve |
|----------|---------|---------------|-----------|--------|
| Unit Test Coverage | Exceptional (1.33:1) | Strong | Moderate | Strong |
| Integration/E2E | Post-merge only | PR-time | PR-time | PR-time |
| Container Scanning | None | Trivy | Trivy | Trivy |
| Coverage Enforcement | Codecov (auto, 0%) | Codecov (thresholds) | Basic | Codecov |
| Pre-commit Hooks | None | Yes | No | Yes |
| Mutation Testing | Yes (mutmut) | No | No | No |
| Performance Testing | CodSpeed | No | No | No |
| Agent Rules | Strong CLAUDE.md | Comprehensive .claude/rules | None | None |
| Supply-chain Security | Excellent (SHA-pin, cosign, fork guards) | Good | Basic | Good |
| Multi-arch Images | No | Yes | Yes | Yes |
| SBOM | No | No | No | No |

## File Paths Reference

### CI/CD
- `.github/workflows/` — 40+ GitHub Actions workflows
- `.github/workflows/_test-unit-base.yml` — Reusable test base (parameterized)
- `.github/workflows/_test-unit-services-base.yml` — Reusable test base with Postgres
- `.circleci/config.yml` — 2,729-line CircleCI config with 30+ jobs
- `Makefile` — Local development targets (lint, format, test shards)

### Testing
- `tests/test_litellm/` — Primary unit tests (mirrors `litellm/` structure)
- `tests/proxy_unit_tests/` — Legacy proxy unit tests
- `tests/proxy_security_tests/` — Security-focused tests
- `tests/proxy_behavior/` — Management endpoint behavior pinning
- `tests/multi_instance_e2e_tests/` — Multi-instance proxy E2E
- `tests/benchmarks/` — Performance benchmarks (CodSpeed)
- `tests/load_tests/` — Load testing (Locust)
- `ui/litellm-dashboard/e2e_tests/` — Playwright UI E2E

### Code Quality
- `ruff.toml` — Ruff linter configuration
- `.flake8` — Flake8 configuration (backup)
- `pyproject.toml` — MyPy, pytest, coverage, mutmut, isort config
- `pyrightconfig.json` — Pyright type checker config
- `.semgrep/rules/` — Custom Semgrep rules (security + reliability)

### Container Images
- `Dockerfile` — Main multi-stage Docker build (Chainguard)
- `docker/Dockerfile.non_root` — Hardened non-root variant
- `docker/Dockerfile.database` — Database variant
- `docker-compose.yml` — Development composition
- `docker-compose.hardened.yml` — Security-hardened composition
- `cosign.pub` — Image signing public key

### Coverage
- `codecov.yaml` — Codecov config with components, flags, thresholds
- `pyproject.toml [tool.coverage.run]` — pytest-cov source config

### Security
- `.github/workflows/codeql.yml` — CodeQL multi-language scanning
- `.github/workflows/zizmor.yml` — GH Actions security analysis
- `.github/workflows/scorecard.yml` — OSSF Scorecard
- `.github/workflows/guard-fork-dependencies.yml` — Fork supply-chain guard
- `.github/workflows/guard-main-branch.yml` — Branch protection guard
- `.gitguardian.yaml` — Secret detection configuration
- `security.md` — Security policy and bug bounty program
- `cosign.pub` — Image attestation public key

### Agent Rules
- `CLAUDE.md` — Comprehensive coding and testing guidelines (76 lines)
- `AGENTS.md` — Delegates to CLAUDE.md
- `GEMINI.md` — Delegates to CLAUDE.md
- `.semgrep/rules/security/no-claude-directory.yml` — Prevents .claude/ from being committed
