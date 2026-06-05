---
repository: "opendatahub-io/notebooks"
overall_score: 8.4
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Solid pytest + Go test coverage for utility code; coverage tooling integrated but thresholds informational only"
  - dimension: "Integration/E2E"
    score: 8.5
    status: "Multi-layer container testing (testcontainers, Playwright, papermill), automated on PR with matrix builds"
  - dimension: "Build Integration"
    score: 9.0
    status: "PR builds both ODH and RHOAI variants; matrix-based cached builds; Konflux Tekton pipelines for production"
  - dimension: "Image Testing"
    score: 9.0
    status: "5-layer validation: Dockerfile lint, static manifest checks, container runtime tests, browser E2E, Trivy scanning"
  - dimension: "Coverage Tracking"
    score: 6.5
    status: "Codecov integration with Python + Go flags and carryforward; thresholds are informational, not enforced"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "41 workflows covering builds, security, quality, releases; concurrency control, SHA-pinned actions, matrix builds"
  - dimension: "Agent Rules"
    score: 8.5
    status: "Comprehensive AGENTS.md, test conventions in .cursor/rules, Jira conventions, skills directory; missing .claude/rules"
critical_gaps:
  - title: "Coverage thresholds are informational only"
    impact: "Coverage can silently regress — no PR gate prevents merging low-coverage changes"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No .claude/rules/ directory for Claude Code agents"
    impact: "Claude Code agents lack test creation guidance natively; must rely on .cursor/rules cross-reference"
    severity: "LOW"
    effort: "2-3 hours"
  - title: "Container integration tests are not in default PR flow"
    impact: "Container test self-test only runs when tests/containers/** changes; images built on PR are not integration-tested by default"
    severity: "MEDIUM"
    effort: "4-8 hours"
  - title: "No performance/load testing for notebook images"
    impact: "Memory/startup performance regressions in notebook images go undetected until deployment"
    severity: "LOW"
    effort: "8-16 hours"
quick_wins:
  - title: "Enforce Codecov coverage thresholds"
    effort: "1-2 hours"
    impact: "Prevent coverage regression by changing informational to required status checks"
  - title: "Mirror .cursor/rules to .claude/rules"
    effort: "1-2 hours"
    impact: "Claude Code agents get native test convention guidance without needing cross-references"
  - title: "Add container test gate on image-building PRs"
    effort: "4-6 hours"
    impact: "Catch runtime failures in built images before merge"
recommendations:
  priority_0:
    - "Change Codecov status from informational to enforced with a minimum threshold (e.g., 60%)"
    - "Run container integration tests on images built during PR CI, not just when test files change"
  priority_1:
    - "Mirror .cursor/rules/test-conventions.mdc to .claude/rules/ for native Claude Code support"
    - "Add startup-time benchmarking for notebook images to detect performance regressions"
  priority_2:
    - "Add contract tests for manifest/imagestream interfaces consumed by odh-dashboard"
    - "Implement image size tracking to alert on unexpected growth"
---

# Quality Analysis: opendatahub-io/notebooks

## Executive Summary

- **Overall Score: 8.4/10**
- **Repository Type**: Container image factory (Jupyter, Code-Server, runtime images for OpenDataHub/RHOAI)
- **Primary Languages**: Python 3.14 (main), Go (build tooling), TypeScript (browser tests)
- **Frameworks**: pytest, testcontainers, Playwright, Podman/Docker, Make, uv, Tekton/Konflux

**Key Strengths**: This is one of the most mature quality ecosystems in the opendatahub-io org. The repo has an exemplary CI/CD setup with 41 GitHub Actions workflows, a multi-layer image testing strategy, comprehensive security scanning (Trivy, Gitleaks, CodeQL, Semgrep), and excellent developer documentation including AI agent rules. The build system handles both ODH and RHOAI variants with intelligent matrix generation and cached builds.

**Critical Gaps**: Coverage thresholds are informational-only (no PR gate), container integration tests don't run by default on image-building PRs, and the comprehensive agent rules live in `.cursor/rules/` but are not mirrored to `.claude/rules/`.

**Agent Rules Status**: Present and comprehensive (AGENTS.md, .cursor/rules/, .agents/skills/)

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Solid pytest + Go test coverage with subtests; coverage tooling integrated |
| Integration/E2E | 8.5/10 | Multi-layer: testcontainers, Playwright, papermill; matrix builds on PR |
| Build Integration | 9.0/10 | PR builds ODH + RHOAI variants; Konflux Tekton for production; cached builds |
| Image Testing | 9.0/10 | 5-layer validation: Hadolint, static checks, container runtime, browser, Trivy |
| Coverage Tracking | 6.5/10 | Codecov with Python + Go flags; carryforward enabled; thresholds informational |
| CI/CD Automation | 9.5/10 | 41 workflows; SHA-pinned actions; concurrency control; matrix builds |
| Agent Rules | 8.5/10 | Comprehensive AGENTS.md + test conventions; missing .claude/rules/ |

## Critical Gaps

### 1. Coverage Thresholds Are Informational Only
- **Impact**: Coverage can silently regress on any PR — no gate prevents merging code with poor test coverage
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: `.codecov.yml` sets `informational: true` on both project and patch status checks. Range is `30...70`, which is relatively low. No enforcement means any PR can merge regardless of coverage delta.
- **File**: `.codecov.yml:8-18`

### 2. Container Tests Not in Default PR Flow
- **Impact**: Images built on PR are not automatically integration-tested unless `tests/containers/**` itself changed
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: `test-containers.yaml` only triggers on changes to `tests/containers/**`, `tests/conftest.py`, or `pytest.ini`. When a Dockerfile changes, the image is built by `build-notebooks-pr.yaml` but not runtime-tested.
- **File**: `.github/workflows/test-containers.yaml:6-12`

### 3. No Claude Code Native Rules
- **Impact**: Claude Code agents must follow a cross-reference from `CLAUDE.md` → `.cursor/rules/` rather than having native `.claude/rules/` files
- **Severity**: LOW
- **Effort**: 2-3 hours
- **Details**: `CLAUDE.md` only contains two lines pointing to `.cursor/rules/test-conventions.mdc` and `.cursor/rules/jira-conventions.mdc`. No `.claude/` directory exists in the repo.

### 4. No Performance/Load Testing
- **Impact**: Memory consumption, startup time, and library loading performance regressions go undetected
- **Severity**: LOW
- **Effort**: 8-16 hours

## Quick Wins

### 1. Enforce Codecov Thresholds (1-2 hours)
Change `.codecov.yml` from informational to enforced:
```yaml
coverage:
  status:
    project:
      default:
        informational: false  # was true
        target: 60%
        threshold: 5%
    patch:
      default:
        informational: false  # was true
        target: 70%
```

### 2. Mirror Cursor Rules to Claude Rules (1-2 hours)
Copy `.cursor/rules/test-conventions.mdc` and `.cursor/rules/jira-conventions.mdc` to `.claude/rules/` and update `CLAUDE.md` to reference both locations. This gives Claude Code agents native access.

### 3. Add Container Test Trigger on Dockerfile Changes (4-6 hours)
Update `test-containers.yaml` to also trigger on Dockerfile changes:
```yaml
on:
  pull_request:
    paths:
      - 'tests/containers/**'
      - 'tests/conftest.py'
      - 'pytest.ini'
      - 'jupyter/**/Dockerfile*'
      - 'runtimes/**/Dockerfile*'
      - 'codeserver/**/Dockerfile*'
      - 'base-images/**/Dockerfile*'
```

## Detailed Findings

### CI/CD Pipeline (9.5/10)

**Workflow Inventory (41 workflows)**:

| Category | Workflows | Trigger |
|----------|-----------|---------|
| Image Builds | `build-notebooks-pr.yaml`, `build-notebooks-pr-rhel.yaml`, `build-notebooks-pr-aipcc.yaml`, `build-notebooks-push.yaml` | PR, push |
| Code Quality | `code-quality.yaml` (pytest, Go tests, linting, Hadolint, kustomize, pre-commit, SHA pinning) | PR, push |
| Security | `security.yaml` (Trivy FS), `codeql.yaml`, `gitleaks.yaml`, `semgrep.yaml` | PR, push, scheduled |
| Container Tests | `test-containers.yaml` | PR (path-filtered), push |
| Browser Tests | `test-playwright-action.yaml`, `build-browser-tests.yaml` | PR (path-filtered), push |
| Release/Deploy | `notebooks-release.yaml`, `create-release.yaml`, `update-tags.yaml` | dispatch, push |
| Maintenance | `piplock-renewal.yaml`, `renovate-self-hosted.yaml`, `stale-prs.yaml`, `purge-ghcr.yaml` | scheduled |
| Manifest Validation | `params-env.yaml`, `check-image-availability.yaml` | PR, push |

**Strengths**:
- **Concurrency control**: All PR workflows use `cancel-in-progress: true` with PR-number-based groups
- **SHA-pinned actions**: All `uses:` reference SHA commits, enforced by `pinact` in CI
- **Matrix builds**: Intelligent matrix generation based on changed files (only builds affected images)
- **Cached builds**: LVM overlay mounts and container cache for faster builds
- **Multi-variant**: Same PR builds both ODH and RHOAI (Konflux) variants
- **Fork handling**: Graceful degradation for fork PRs (skips subscription builds, annotates PR)

**Custom Actions (7)**:
- `apt-install`, `free-up-disk-space`, `install-podman-action`, `playwright-test`, `provision-k8s`, `setup-uv`, `trivy-scan-action`

### Test Coverage (7.5/10 Unit, 8.5/10 Integration/E2E)

**Test File Inventory**:
- Python test files: 44 (across tests/, ntb/, ci/, codeserver/)
- Go test files: 2 (scripts/buildinputs/)
- TypeScript test files: 2 (tests/browser/)

**Test Types and Layers**:

| Layer | Tests | Framework | Trigger |
|-------|-------|-----------|---------|
| Static/Manifest | `tests/test_*.py` | pytest + subtests | `make test` on every PR |
| Unit | `tests/unit/` | pytest + pyfakefs | `make test-unit` on every PR |
| Container Integration | `tests/containers/` | pytest + testcontainers + docker | `make test-integration --image=X` |
| Browser E2E | `tests/browser/` | Playwright (TypeScript) | Path-filtered on PR |
| Notebook Smoke | `scripts/test_jupyter_with_papermill.sh` | papermill | Manual/deployed |
| Go Unit | `scripts/buildinputs/` | Go testing + gotestsum | On every PR |

**Pytest Configuration** (well-configured):
- `--strict-markers` enforced
- `--cov --cov-branch` with XML + terminal output
- `--junitxml` for CI result tracking
- Subtests for per-item assertions
- Smart collection exclusion of `tests/containers/` from default runs
- 6 registered markers: openshift, cuda, rocm, buildonlytest, manifest_validation, codeserver

**Container Test Infrastructure** (13 test files):
- Base image validation (`base_image_test.py`)
- Workbench image tests (JupyterLab, datascience, TrustyAI, Code-Server)
- Runtime tests (`runtime_test.py`)
- GPU/accelerator tests (CUDA, ROCm)
- Library loading tests
- Manifest validation tests
- params.env validation tests
- Session-scoped fixtures for expensive container operations
- Allure integration for issue tracking

### Code Quality (8.0/10)

**Linting & Analysis**:
- **Ruff**: Linter + formatter for Python (check + format, via pre-commit)
- **Pyright**: Type checker for Python 3.14 (in pre-commit)
- **golangci-lint**: For Go code (v2.12.2 in CI)
- **Hadolint**: Dockerfile linting (v2.12.0 in CI)
- **yamllint**: YAML validation with strict mode
- **JSON validation**: Custom JSON syntax checker
- **Semgrep**: Custom security rules (64KB rule file covering Go, Python, TS, YAML, generic secrets)

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- `check-added-large-files`, `check-toml`, `check-symlinks`, `check-merge-conflict`, `check-executables-have-shebangs`
- `uv-lock` (lockfile consistency)
- `ruff-check` + `ruff-format` (Python)
- `gitleaks` (secret detection)
- `pyright` (type checking)

**Code Review Automation**:
- **CodeRabbit**: AI-powered PR reviews with org-wide config inheritance
- Conventional commit title validation (imperative mood, ticket references)
- Generated code consistency check (`ci/generate_code.sh`)

### Build Integration (9.0/10)

**PR Build Validation**:
- Every PR builds affected images for both ODH and RHOAI variants
- Matrix generation analyzes changed files to determine which images need rebuilding
- Multi-platform support: linux/amd64, linux/arm64, linux/ppc64le, linux/s390x
- QEMU setup for non-native architecture cross-compilation
- Images pushed to GHCR for PR testing

**Konflux/Tekton Integration**:
- 66 Tekton pipeline YAML files in `.tekton/`
- Pull-request and push pipelines for each image variant
- Group testing pipeline for coordinated builds
- Multi-arch combined pipeline
- Separate Dockerfile.konflux.* files for production builds

**Manifest Validation**:
- Kustomize build verification in CI
- params.env SHA validation (both ODH and RHOAI)
- Image availability checking
- Digest updater automation

### Container Image Testing (9.0/10)

**5-Layer Validation Strategy**:

1. **Dockerfile Lint** (Hadolint) — Catches anti-patterns at build definition time
2. **Static Manifest Checks** — Validates params.env, kustomize overlays, JSON/YAML syntax
3. **Container Runtime Tests** (testcontainers) — Image startup, exec, library availability, HTTP readiness
4. **Browser E2E** (Playwright) — Full UI testing of JupyterLab and Code-Server in container
5. **Security Scanning** (Trivy) — Vulnerability detection on filesystem and built images

**Image Build Process**:
- 46 Dockerfiles (28 base + 18 Konflux variants)
- Multi-stage builds (not image inheritance)
- Platform-specific variants (CPU, CUDA, ROCm)
- SBOM generation via Syft (with smart exclusions for monorepo cross-contamination)
- `.dockerignore` for build context optimization

### Security Practices (9.0/10)

| Tool | Scope | Trigger | SARIF Upload |
|------|-------|---------|-------------|
| **Trivy** (v0.70.0) | Filesystem scan (deps) + image scan | PR, push, scheduled | Yes |
| **CodeQL** | Python + Go SAST | PR, push, weekly | Yes |
| **Gitleaks** (v8.30.1) | Secret detection in git history | PR, push, weekly | Yes |
| **Semgrep** | Custom rules (secrets, CWE-798, injection) | PR, push, weekly | Yes |

**Strengths**:
- Four independent security scanners with overlapping coverage
- SARIF upload to GitHub Security tab for all scanners
- Custom Semgrep rules (3.0.0 template) covering multi-language patterns
- Gitleaks with sensible allowlists for test data and fixture files
- Trivy configured with custom file patterns for non-standard requirements files
- Weekly scheduled scans for all security tools
- Syft SBOM with monorepo-aware exclusions

**Secret Management**:
- `git-crypt` for encrypted subscription secrets
- GitHub Actions secrets for registry auth
- `.gitleaksignore` for known false positives
- Pre-commit hook for local secret detection

### Agent Rules (8.5/10)

**Strengths**:
- **AGENTS.md** (131 lines): Comprehensive entry point with linked docs table, common commands, conduct rules, boundaries, operational notes
- **CLAUDE.md**: Cross-references .cursor/rules for test and Jira conventions
- **.cursor/rules/test-conventions.mdc** (294 lines): Excellent test creation guide covering all test types, fixture chains, markers, patterns, DO/DON'T lists, and implementation checklists
- **.cursor/rules/jira-conventions.mdc**: Jira integration patterns
- **.agents/skills/**: Skills directory with README (AgentSkills.io convention)
- **ARCHITECTURE.md**: Authoritative system map
- **CONTRIBUTING.md**: Development workflow and local testing gotchas
- **docs/agents/testing.md**: Test catalog for agents
- **.github/AGENTS.md**: GitHub Actions-specific agent guidance
- **tests/browser/AGENTS.md**: Playwright-specific agent guidance
- **.coderabbit.yaml**: AI code review configuration

**Gaps**:
- No `.claude/` directory — CLAUDE.md is minimal (2 lines)
- Test conventions in `.cursor/rules/` format, not `.claude/rules/`
- No `.agents/skills/` actual skills implemented (only README)

### Documentation (9.0/10)

Outstanding documentation ecosystem:
- **28 doc files** covering CI, Konflux, FIPS, CVE remediation, developer guides, architecture decisions (ADR)
- ADR directory linked from `.adr-dir`
- Topic-specific agent docs distributed across subdirectories
- AI coding assistant configuration guide (`docs/ai-coding-assistant-project-config.md`)

## Recommendations

### Priority 0 (Critical)
1. **Enforce Codecov coverage thresholds** — Change `informational: true` to `false` in `.codecov.yml` with a minimum project target (e.g., 60%) and patch target (e.g., 70%). This prevents silent coverage regression.
2. **Run container integration tests on image-building PRs** — Add Dockerfile path triggers to `test-containers.yaml` or create a post-build test step in `build-notebooks-TEMPLATE.yaml` that runs basic container smoke tests on freshly built images.

### Priority 1 (High Value)
3. **Mirror .cursor/rules to .claude/rules** — Create `.claude/rules/` directory and symlink or copy `test-conventions.mdc` and `jira-conventions.mdc`. Update `CLAUDE.md` to reference both.
4. **Add startup-time benchmarking** — Track image startup time and memory consumption in CI to detect performance regressions early.
5. **Implement actual agent skills** — The `.agents/skills/` directory has only a README. Create skills for common tasks (CVE fix, dependency update, image testing).

### Priority 2 (Nice-to-Have)
6. **Add contract tests for manifest interfaces** — Validate that manifest format consumed by odh-dashboard remains compatible.
7. **Image size tracking** — Add image size reporting to PR comments to alert on unexpected growth.
8. **Chaos/resilience testing** — Test notebook image behavior under resource constraints.

## Comparison to Gold Standards

| Dimension | notebooks | odh-dashboard | kserve | Best Practice |
|-----------|-----------|---------------|--------|---------------|
| Unit Tests | 7.5 | 9.0 | 9.0 | Coverage enforcement |
| Integration/E2E | 8.5 | 9.0 | 8.5 | Contract tests |
| Build Integration | 9.0 | 7.0 | 7.5 | Multi-variant PR builds |
| Image Testing | 9.0 | 6.0 | 6.5 | 5-layer validation |
| Coverage Tracking | 6.5 | 8.0 | 9.0 | Enforced thresholds |
| CI/CD Automation | 9.5 | 9.0 | 8.5 | Matrix + caching |
| Agent Rules | 8.5 | 8.0 | 3.0 | Comprehensive guides |
| Security | 9.0 | 7.0 | 7.0 | 4-scanner coverage |
| Documentation | 9.0 | 8.0 | 7.0 | ADR + agent docs |

**notebooks is the gold standard for**: Image testing strategy, build integration (multi-variant PR builds), security scanning coverage, CI/CD automation maturity, and AI agent documentation.

**notebooks trails in**: Coverage enforcement (informational-only), unit test depth (utility code focus), and Claude Code native integration (relies on .cursor/).

## File Paths Reference

### CI/CD
- `.github/workflows/` — 41 workflow files
- `.github/actions/` — 7 custom composite actions
- `.tekton/` — 66 Tekton pipeline definitions
- `Makefile` — Build and test orchestration
- `ci/` — CI scripts and cached build tools

### Testing
- `tests/test_*.py` — Static/manifest tests
- `tests/unit/` — Unit tests
- `tests/containers/` — Container integration tests (13 test files)
- `tests/browser/` — Playwright browser tests
- `scripts/test_jupyter_with_papermill.sh` — Notebook smoke tests
- `scripts/buildinputs/*_test.go` — Go unit tests
- `pytest.ini` — pytest configuration
- `tests/conftest.py` — Root conftest with collection exclusions

### Code Quality
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff, pyright, gitleaks, uv-lock)
- `semgrep.yaml` — Custom Semgrep security rules
- `ci/hadolint-config.yaml` — Dockerfile linting config
- `ci/yamllint-config.yaml` — YAML linting config

### Container Images
- `jupyter/` — Jupyter workbench Dockerfiles
- `runtimes/` — Runtime image Dockerfiles
- `codeserver/` — Code-Server Dockerfiles
- `base-images/` — Base image Dockerfiles
- `manifests/` — Kustomize manifests and params.env

### Coverage & Security
- `.codecov.yml` — Codecov configuration
- `trivy.yaml` — Trivy scan configuration
- `.gitleaks.toml` — Gitleaks configuration
- `.syft.yaml` — SBOM generation config
- `.github/workflows/codeql.yaml` — CodeQL SAST
- `.github/workflows/security.yaml` — Trivy FS scan
- `.github/workflows/gitleaks.yaml` — Secret detection
- `.github/workflows/semgrep.yaml` — Custom security rules

### Agent Rules
- `AGENTS.md` — Primary AI agent entry point
- `CLAUDE.md` — Claude Code cross-references
- `.cursor/rules/test-conventions.mdc` — Test creation conventions (294 lines)
- `.cursor/rules/jira-conventions.mdc` — Jira conventions
- `.agents/skills/` — Agent Skills directory
- `.github/AGENTS.md` — GitHub Actions agent guidance
- `tests/browser/AGENTS.md` — Playwright agent guidance
- `docs/agents/testing.md` — Test catalog for agents
