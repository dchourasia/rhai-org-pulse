---
repository: "red-hat-data-services/notebooks"
overall_score: 8.7
scorecard:
  - dimension: "Unit Tests"
    score: 8.5
    status: "Comprehensive Python/Go unit tests with pytest-subtests, pyfakefs, doctests, and strict markers"
  - dimension: "Integration/E2E"
    score: 9.0
    status: "Multi-layer testing: testcontainers, Playwright browser, OpenShift cluster, papermill notebook smoke"
  - dimension: "Build Integration"
    score: 9.0
    status: "PR-time builds for ODH and RHOAI variants with Konflux simulation and hermetic prefetch"
  - dimension: "Image Testing"
    score: 9.5
    status: "5-layer validation: build, testcontainers, Makefile smoke, OpenShift, Playwright; multi-arch support"
  - dimension: "Coverage Tracking"
    score: 7.5
    status: "Codecov with Python+Go flags, branch coverage, JUnit uploads; thresholds informational only"
  - dimension: "CI/CD Automation"
    score: 9.5
    status: "43+ workflows, concurrency control, matrix builds, smart change detection, SHA-pinned actions"
  - dimension: "Agent Rules"
    score: 9.0
    status: "Comprehensive AGENTS.md, CLAUDE.md, Cursor rules, testing docs, ADRs, and .agents/skills scaffolding"
critical_gaps:
  - title: "Coverage thresholds are informational only"
    impact: "Coverage can regress silently — no enforcement gate to block PRs with declining coverage"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No SBOM generation or image signing in GHA pipeline"
    impact: "Supply chain attestation relies entirely on Konflux/Tekton; GHA-built images lack provenance"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Container tests excluded from default collection"
    impact: "Developers can merge changes that break container tests if they only run 'make test'"
    severity: "LOW"
    effort: "2-3 hours to document the gap more prominently"
quick_wins:
  - title: "Enforce coverage threshold on patch (change informational to blocking)"
    effort: "1-2 hours"
    impact: "Prevents coverage regression on new code without blocking existing uncovered areas"
  - title: "Add cosign image signing to GHA build template"
    effort: "2-3 hours"
    impact: "Supply chain provenance for all GHA-built images; complements existing Konflux signing"
  - title: "Add Syft SBOM generation to PR build pipeline"
    effort: "2-3 hours"
    impact: "Already have .syft.yaml config; just needs workflow integration"
recommendations:
  priority_0:
    - "Switch Codecov patch status from informational to enforcing with a reasonable target (e.g., 60%)"
    - "Add SBOM generation using the existing .syft.yaml configuration in the GHA build template"
  priority_1:
    - "Add cosign image signing for GHA-built images to match Konflux signing"
    - "Consider adding a required PR check that runs container tests for Dockerfile changes"
    - "Expand browser tests beyond Code-Server to cover JupyterLab UI flows"
  priority_2:
    - "Add performance benchmarking for image build times to detect build-time regressions"
    - "Consider contract tests between ImageStream annotation format and ODH Dashboard consumer"
    - "Add mutation testing (e.g., mutmut) for critical CI scripts"
---

# Quality Analysis: red-hat-data-services/notebooks

## Executive Summary

- **Overall Score: 8.7/10**
- **Key Strengths**: Exceptionally mature multi-layer testing (5 test layers), comprehensive CI/CD with 43+ workflows, industry-leading container image testing with testcontainers, strong security posture (Trivy + CodeQL + Semgrep + Gitleaks + FIPS check-payload), excellent agent rules and developer documentation
- **Critical Gaps**: Coverage enforcement is informational only (no blocking gate), no SBOM generation in GHA pipeline, no image signing outside Konflux
- **Agent Rules Status**: **Excellent** — comprehensive AGENTS.md with linked topic docs, Cursor rules for test conventions and Jira, `.agents/skills/` scaffolding, dedicated testing guide

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 8.5/10 | Comprehensive Python/Go unit tests with pytest-subtests, pyfakefs, doctests |
| Integration/E2E | 9.0/10 | Multi-layer: testcontainers, Playwright, OpenShift, papermill notebook smoke |
| **Build Integration** | **9.0/10** | **PR-time ODH + RHOAI builds with Konflux simulation and hermetic prefetch** |
| Image Testing | 9.5/10 | 5-layer validation pipeline; gold standard for container image testing |
| Coverage Tracking | 7.5/10 | Codecov integration with flags but informational-only thresholds |
| CI/CD Automation | 9.5/10 | 43+ workflows, matrix builds, concurrency control, change detection |
| Agent Rules | 9.0/10 | AGENTS.md + CLAUDE.md + Cursor rules + testing docs + ADRs |

## Critical Gaps

### 1. Coverage Thresholds Are Informational Only
- **Impact**: Coverage can regress silently — PRs with zero test coverage pass CI
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: `.codecov.yml` sets `informational: true` for both project and patch status. While this was appropriate during initial adoption, the test suite is now mature enough to enforce a minimum patch target.

### 2. No SBOM Generation or Image Signing in GHA Pipeline
- **Impact**: GHA-built PR images lack supply chain provenance; only Konflux-built images get attestation
- **Severity**: MEDIUM
- **Effort**: 4-6 hours
- **Details**: A `.syft.yaml` config already exists at the repo root, but it's not integrated into the build template workflow. Cosign signing is handled by Konflux but not by the GHA pipeline.

### 3. Container Tests Excluded from Default Collection
- **Impact**: `make test` skips container integration tests entirely; developers may miss container breakage
- **Severity**: LOW
- **Effort**: Already well-documented in pytest.ini comments and CONTRIBUTING.md; could add a CI warning annotation

## Quick Wins

### 1. Enforce Coverage Threshold on Patch (1-2 hours)
Change `.codecov.yml` patch status from `informational: true` to enforce a minimum target:
```yaml
coverage:
  status:
    patch:
      default:
        informational: false
        target: 60%
```

### 2. Add SBOM Generation to Build Template (2-3 hours)
The `.syft.yaml` config already exists. Add a step to the build template:
```yaml
- name: Generate SBOM
  run: |
    syft packages ${{ steps.calculated_vars.outputs.OUTPUT_IMAGE }} \
      -o spdx-json=sbom.spdx.json
```

### 3. Add Cosign Image Signing (2-3 hours)
Sign GHA-built images for supply chain integrity:
```yaml
- name: Sign image with cosign
  if: github.event_name == 'push'
  run: cosign sign --yes ${{ steps.calculated_vars.outputs.OUTPUT_IMAGE }}
```

## Detailed Findings

### CI/CD Pipeline

**Score: 9.5/10** — One of the most comprehensive CI/CD setups analyzed.

**Workflow Inventory (43+ workflows)**:
- **PR-triggered**: `build-notebooks-pr.yaml` (matrix build with change detection), `code-quality.yaml` (pytest + Go tests + linting + Hadolint + kustomize), `security.yaml` (Trivy FS), `codeql.yaml`, `semgrep.yaml`, `gitleaks.yaml`
- **Template-based builds**: `build-notebooks-TEMPLATE.yaml` reusable workflow with 5 test phases per image
- **Periodic**: CodeQL weekly scan, Gitleaks weekly, Semgrep weekly, security scan every 3 weeks
- **Branch management**: `merge-main-to-stable-fast-forward.yaml`, `sync-branches-through-pr.yml`
- **Infrastructure self-test**: `test-containers.yaml`, `test-playwright-action.yaml`, `test-build-notebooks-template.yaml`

**Strengths**:
- Smart change detection via `gen_gha_matrix_jobs.py` — only builds images affected by PR changes
- Concurrency control on all workflows with `cancel-in-progress`
- All GitHub Actions SHA-pinned with `pinact` verification
- Fork PR detection with graceful degradation (subscription builds skipped with clear messaging)
- Build caching with event-aware strategy (schedule regenerates, PR reads, push read-writes)
- Disk space management with LVM overlay and btrfs compression monitoring
- FIPS compliance check via `check-payload` on every image build
- Multi-architecture support (amd64, arm64, s390x, ppc64le) with QEMU for cross-compilation

**Minor gaps**:
- Some CI checks (yamllint, hadolint, gotestsum) are inline in workflows rather than Makefile targets (tracked in #3174)

### Test Coverage

**Score: 8.5/10 (Unit), 9.0/10 (Integration/E2E)**

**Test File Counts**:
- Python test files: 44
- Python source files: 66
- Go test files: 2 (of 4 Go source files)
- TypeScript test specs: 2 (Playwright)
- Test-to-code ratio: ~0.67 (good)

**Test Types**:
1. **Static/Manifest tests** (`tests/test_*.py`): Validate Dockerfiles, pylock files, renovate config, manifest consistency
2. **Unit tests** (`tests/unit/`): Test CI scripts, lockfile generators, index URL resolution, renovate validation
3. **Container integration tests** (`tests/containers/`): Testcontainers-based image validation — startup, library imports, GPU loading, base image checks, params_env validation, manifest validation
4. **Browser E2E tests** (`tests/browser/`): Playwright tests for Code-Server UI
5. **Notebook smoke tests** (`scripts/test_jupyter_with_papermill.sh`): Papermill execution of test notebooks
6. **Go tests** (`scripts/buildinputs/`): Tests for Dockerfile dependency parser
7. **K8s deployment tests**: Pod lifecycle tests on Kind cluster with OpenShift markers

**Testing Frameworks**:
- pytest with `--strict-markers`, `--cov`, `--cov-branch`, JUnit XML output
- pytest-subtests for granular per-item assertions
- allure-pytest for issue tracking and step decoration
- testcontainers for container lifecycle management
- pyfakefs for filesystem mocking
- Playwright for browser automation
- papermill for notebook execution
- gotestsum for Go test reporting

**Coverage Configuration**:
- Python: source paths `ntb/`, `ci/`, `scripts/` with branch coverage
- Go: `coverage-go.out` with atomic mode
- Both uploaded to Codecov with separate flags
- JUnit XML results uploaded to Codecov test analytics

### Code Quality

**Score: 9.0/10** — Exceptionally thorough.

**Linting & Formatting**:
- **Ruff**: 25+ rule categories enabled (B, C4, COM, E, W, F, FA, G, I, ISC, N, PERF, PGH, PIE, PL, S, etc.) with granular per-file ignores. Python 3.14 target.
- **Pyright**: `basic` type checking mode with `reportMissingImports: error`, `reportUnboundVariable: error`
- **golangci-lint**: v2.12.2 for Go code
- **Hadolint**: Dockerfile linting with custom config
- **yamllint**: Strict YAML validation
- **JSON validation**: Custom script for JSON syntax

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- check-added-large-files, check-toml, check-symlinks, check-merge-conflict, check-executables-have-shebangs
- `uv-lock` — lockfile integrity check
- ruff-check + ruff-format for Python
- Gitleaks for secret detection
- Pyright type checking

**Static Analysis**:
- CodeQL for Python and Go (PR + push + weekly schedule)
- Semgrep with custom rules (1873-line `semgrep.yaml`)
- GitHub Actions SHA pinning verified by pinact
- CodeRabbit automated PR review with custom title conventions

### Build Integration

**Score: 9.0/10** — Excellent PR-time build validation.

**PR Build Validation**:
- Builds both ODH and RHOAI variants on PRs
- Change detection only builds affected images (matrix generation)
- Hermetic prefetch with `cachi2` for Konflux-style builds
- Multi-stage build validation across cpu, cuda, rocm variants
- Fork PR detection with clear messaging about skipped subscription builds

**Image Testing in CI** (per-image in build template):
1. `make <target>` — Build the image
2. Testcontainers pytest — Container integration tests
3. `make test-<notebook>` — Makefile-driven K8s deployment test
4. OpenShift pytest — Tests requiring OpenShift cluster (on Kind)
5. Playwright — Browser tests (Code-Server images)
6. Trivy scan — Vulnerability scanning (on label or schedule)
7. check-payload — FIPS compliance validation

### Container Image Testing

**Score: 9.5/10** — Gold standard for container image testing in the ODH ecosystem.

**5-Layer Validation**:
1. **Build validation**: Multi-stage Dockerfile build with build-args per variant
2. **Container integration (testcontainers)**: Library imports, CLI tool presence, env vars, startup
3. **K8s deployment**: Pod deployment on Kind, readiness probes, papermill notebook execution
4. **OpenShift-specific**: Tests marked `@openshift` for real cluster validation
5. **Browser tests**: Playwright UI tests for Code-Server

**Per-Image Test Notebooks**: Each image variant ships a `test/test_notebook.ipynb` executed via papermill

**Multi-Architecture**: Builds on amd64, arm64, s390x, ppc64le with QEMU

**Security Scanning**:
- Trivy configured with custom file patterns for Python requirements
- Scans both FS and container image modes
- SARIF output uploaded to GitHub Security tab
- Severity filter: MEDIUM, HIGH, CRITICAL
- Per-repo OS package scanning config (RHEL vs CentOS Stream)

### Security

**Score: 9.0/10** — Comprehensive multi-tool security posture.

| Tool | Scope | Trigger |
|------|-------|---------|
| Trivy | Filesystem vulnerabilities | PR + push + schedule |
| Trivy (image) | Container image vulnerabilities | PR (label) + schedule |
| CodeQL | SAST for Python and Go | PR + push + weekly |
| Semgrep | Custom rules (secrets, patterns) | PR + push + weekly |
| Gitleaks | Secret detection (pre-commit + CI) | PR + push + weekly |
| check-payload | FIPS compliance | Every image build |
| Quay scan | Weekly vulnerability reports | Scheduled (every 3 weeks) |
| CodeRabbit | Automated PR review | Every PR |
| pinact | GitHub Actions SHA verification | Every PR |
| Supply-chain hardening | `exclude-newer = "3 days"` in uv config | Every lock resolution |

**Notable**: The `pyproject.toml` sets `exclude-newer = "3 days"` for supply chain hardening — only resolves package versions published 3+ days ago, reducing risk from compromised packages.

### Agent Rules (Agentic Flow Quality)

**Score: 9.0/10** — Among the best in the ecosystem.

**Present**:
- `AGENTS.md` (134 lines): Comprehensive entry point with topic routing table, baseline tools, repo model, ODH/RHOAI build explanation, common commands, agent conduct rules, boundaries, operational notes
- `CLAUDE.md` (4 lines): Points to Cursor rules for detailed conventions
- `.cursor/rules/test-conventions.mdc` (293 lines): Exhaustive test creation guide with patterns for every test type, markers, fixtures, testcontainers lifecycle, allure integration, assertions, DO/DON'T lists, implementation checklist
- `.cursor/rules/jira-conventions.mdc`: Jira integration patterns
- `docs/agents/testing.md` (135 lines): Full test catalog with types, CI parity, framework reference, troubleshooting
- `.github/AGENTS.md`: GitHub Actions editing guide
- `tests/browser/AGENTS.md`: Playwright test editing guide
- `.agents/skills/`: Skills directory (scaffolded, README.md present)
- Architecture Decision Records in `docs/architecture/decisions/` (12 ADRs)
- `.coderabbit.yaml`: Automated review with PR title validation rules

**Gaps**:
- `.agents/skills/` is scaffolded but has no actual skills yet
- No `.claude/rules/` directory (uses `.cursor/rules/` instead — different tool ecosystem)
- Could add agent rules for Dockerfile modification patterns and Konflux pipeline changes

## Recommendations

### Priority 0 (Critical)
1. **Enforce Codecov patch coverage threshold** — Switch from `informational: true` to a blocking 60% patch target. The test infrastructure is mature enough to support this.
2. **Add SBOM generation** — The `.syft.yaml` config exists; integrate Syft into the build template workflow.

### Priority 1 (High Value)
1. **Add cosign image signing** to GHA-built images to match Konflux attestation
2. **Create a required status check** for container tests when Dockerfiles change — currently `make test` skips them
3. **Expand Playwright browser tests** to cover JupyterLab UI (currently only Code-Server)
4. **Port .cursor/rules/ to .claude/rules/** for Claude Code compatibility (or symlink)

### Priority 2 (Nice-to-Have)
1. **Add image build time benchmarking** to detect build performance regressions
2. **Contract testing** between ImageStream annotation format and ODH Dashboard consumer
3. **Mutation testing** (mutmut) for critical CI scripts in `ci/` and `ntb/`
4. **Populate `.agents/skills/`** with reusable skills for image build, CVE fix, lockfile refresh

## Comparison to Gold Standards

| Dimension | notebooks (this) | odh-dashboard | kserve | Industry Best |
|-----------|------------------|---------------|--------|---------------|
| Unit Tests | 8.5 | 8.0 | 8.0 | 9.0 |
| Integration/E2E | 9.0 | 9.0 | 8.5 | 9.0 |
| Build Integration | 9.0 | 7.0 | 6.0 | 9.0 |
| Image Testing | **9.5** | 6.0 | 7.0 | 9.0 |
| Coverage Tracking | 7.5 | 8.0 | 8.5 | 9.0 |
| CI/CD Automation | **9.5** | 8.5 | 8.0 | 9.0 |
| Agent Rules | **9.0** | 7.0 | 3.0 | 8.0 |
| Security | **9.0** | 7.0 | 7.0 | 9.0 |
| **Overall** | **8.7** | 7.5 | 7.0 | 9.0 |

**This repository IS the gold standard** for container image testing in the ODH ecosystem. Its 5-layer testing pipeline, multi-architecture builds, FIPS compliance checks, and comprehensive agent documentation set the bar for other projects to follow.

## File Paths Reference

### CI/CD
- `.github/workflows/build-notebooks-pr.yaml` — PR build trigger with change detection
- `.github/workflows/build-notebooks-TEMPLATE.yaml` — Reusable build template (5 test phases)
- `.github/workflows/code-quality.yaml` — Linting, tests, coverage upload
- `.github/workflows/security.yaml` — Trivy filesystem scan
- `.github/workflows/codeql.yaml` — CodeQL SAST
- `.github/workflows/semgrep.yaml` — Semgrep scan
- `.github/workflows/gitleaks.yaml` — Secret detection
- `.github/workflows/test-containers.yaml` — Container test self-tests
- `.tekton/` — 85 Tekton/Konflux pipeline definitions

### Testing
- `tests/test_*.py` — Static/manifest tests
- `tests/unit/` — Python unit tests
- `tests/containers/` — Container integration tests (testcontainers)
- `tests/browser/tests/*.spec.ts` — Playwright browser tests
- `scripts/buildinputs/*_test.go` — Go tests
- `jupyter/*/test/test_notebook.ipynb` — Per-image notebook smoke tests
- `pytest.ini` — Test configuration with strict markers and coverage

### Code Quality
- `pyproject.toml` — Ruff + Pyright + coverage configuration
- `.pre-commit-config.yaml` — Pre-commit hooks (ruff, gitleaks, pyright, uv-lock)
- `.coderabbit.yaml` — Automated PR review rules
- `ci/yamllint-config.yaml` — YAML linting config
- `ci/hadolint-config.yaml` — Dockerfile linting config

### Container Images
- `jupyter/*/Dockerfile.*` — JupyterLab image definitions
- `runtimes/*/Dockerfile.*` — Pipeline runtime image definitions
- `codeserver/*/Dockerfile.*` — Code-Server image definitions
- `base-images/*/Dockerfile.*` — GPU base image definitions

### Security
- `trivy.yaml` — Trivy scan configuration
- `semgrep.yaml` — Semgrep rules (1873 lines)
- `.gitleaks.toml` — Gitleaks configuration
- `.syft.yaml` — SBOM generation config (not yet integrated)
- `.codecov.yml` — Coverage reporting config

### Agent Rules
- `AGENTS.md` — Primary AI agent guide
- `CLAUDE.md` — Claude Code entry point
- `.cursor/rules/test-conventions.mdc` — Test creation conventions
- `.cursor/rules/jira-conventions.mdc` — Jira integration patterns
- `docs/agents/testing.md` — Full test catalog
- `.github/AGENTS.md` — GitHub Actions guide
- `tests/browser/AGENTS.md` — Playwright test guide
- `docs/architecture/decisions/` — 12 Architecture Decision Records
