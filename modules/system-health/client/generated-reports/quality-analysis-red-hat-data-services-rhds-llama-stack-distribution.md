---
repository: "red-hat-data-services/rhds-llama-stack-distribution"
overall_score: 4.8
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "No unit tests exist for the two Python scripts (build.py, gen_distro_docs.py)"
  - dimension: "Integration/E2E"
    score: 7.0
    status: "Solid smoke tests and upstream integration tests with multi-provider coverage"
  - dimension: "Build Integration"
    score: 7.0
    status: "PR builds, smoke tests, and ARM64 verification; Konflux Dockerfile sync is manual"
  - dimension: "Image Testing"
    score: 6.0
    status: "Good runtime validation (health, inference, Postgres) but no vulnerability scanning"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling, thresholds, or PR reporting configured"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Well-organized workflows with concurrency, caching, nightly builds, and Slack alerts"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory (CLAUDE.md is in .gitignore)"
critical_gaps:
  - title: "No unit tests for build scripts"
    impact: "Regressions in Containerfile generation or version parsing go undetected until CI or production"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container vulnerability scanning in CI"
    impact: "CVEs in base image or pip dependencies are not caught before merge or publish"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No coverage tracking"
    impact: "Cannot measure or enforce test coverage; no visibility into quality trends"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Manual Containerfile / Dockerfile.konflux synchronization"
    impact: "Drift between community Containerfile and Konflux Dockerfile causes build failures post-merge"
    severity: "HIGH"
    effort: "6-10 hours"
  - title: "No agent rules for test automation"
    impact: "AI-assisted contributions lack guidance on testing patterns and quality standards"
    severity: "LOW"
    effort: "2-3 hours"
quick_wins:
  - title: "Add Trivy container scan to PR workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in dependencies and base image before merge"
  - title: "Add unit tests for build.py version-parsing functions"
    effort: "2-3 hours"
    impact: "Protect critical Containerfile generation logic from regressions"
  - title: "Add SBOM generation to container build"
    effort: "1-2 hours"
    impact: "Supply chain transparency and compliance readiness"
  - title: "Create CLAUDE.md with basic testing guidance"
    effort: "1 hour"
    impact: "Guide AI-assisted contributions toward repo conventions"
recommendations:
  priority_0:
    - "Add Trivy or Grype vulnerability scanning to the PR workflow for the built container image"
    - "Write unit tests for build.py (version parsing, dependency categorization, Containerfile generation)"
    - "Automate Containerfile / Dockerfile.konflux synchronization or add a CI check for drift"
  priority_1:
    - "Add pytest + coverage for Python build scripts with codecov integration"
    - "Add SBOM generation (Syft/Trivy) to the container build pipeline"
    - "Create agent rules (.claude/rules/) for test and contribution patterns"
  priority_2:
    - "Add contract tests verifying the Llama Stack API surface against the distribution config"
    - "Add performance baseline tests for container startup time"
    - "Consider adding Bandit or Semgrep for Python SAST"
---

# Quality Analysis: rhds-llama-stack-distribution

## Executive Summary

- **Overall Score: 4.8/10**
- **Repository Type**: Container image distribution / packaging project (Python, Shell, YAML)
- **Purpose**: Build and distribute a containerized Llama Stack server with multi-provider inference, evaluation, and vector store integrations for Red Hat AI / OpenDataHub
- **Key Strengths**: Excellent CI/CD automation with nightly builds, multi-arch support, comprehensive smoke testing with multi-provider inference validation, and strong pre-commit hook coverage
- **Critical Gaps**: Zero unit tests for build scripts, no container vulnerability scanning, no coverage tracking, manual Containerfile/Dockerfile.konflux synchronization
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory (CLAUDE.md is explicitly in .gitignore)

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1/10 | No unit tests for build.py or gen_distro_docs.py |
| Integration/E2E | 7/10 | Solid smoke tests + upstream pytest integration tests with multi-provider coverage |
| Build Integration | 7/10 | PR image build + ARM64 verification; Konflux Dockerfile sync is manual |
| Image Testing | 6/10 | Good runtime validation (health, inference, Postgres); no vulnerability scanning |
| Coverage Tracking | 0/10 | No coverage tooling, thresholds, or PR reporting |
| CI/CD Automation | 8/10 | Well-organized workflows with concurrency, caching, nightly builds, Slack alerts |
| Agent Rules | 0/10 | No agent rules at all; CLAUDE.md is in .gitignore |

## Critical Gaps

### 1. No Unit Tests for Build Scripts
- **Impact**: Regressions in Containerfile generation, version parsing (`is_version_tag`, `is_install_from_source`, `get_llama_stack_install`), or dependency categorization go undetected until CI builds fail or production images are broken
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: `distribution/build.py` (347 lines) contains complex version parsing, dependency categorization, and template rendering logic with zero test coverage. `scripts/gen_distro_docs.py` (280 lines) has similar untested parsing logic.

### 2. No Container Vulnerability Scanning
- **Impact**: CVEs in the UBI9 base image, pip dependencies (60+ packages including torch, numpy, scipy, transformers), or transitive dependencies are not caught before merge or publish
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The image installs 60+ pip packages including large ML frameworks. No Trivy, Snyk, Grype, or similar scanner runs in the GitHub Actions pipeline. The Konflux pipeline may handle some scanning, but the community CI does not.

### 3. Manual Containerfile / Dockerfile.konflux Synchronization
- **Impact**: `Containerfile` (community/ODH) and `Dockerfile.konflux` (RHOAI) are maintained separately. Mergify posts a reminder comment when `Containerfile.in` changes, but synchronization is manual and error-prone.
- **Severity**: HIGH
- **Effort**: 6-10 hours
- **Details**: `Containerfile` is auto-generated from `Containerfile.in` by `build.py`. `Dockerfile.konflux` is a separate file using a different base image and build process (wheel releases, RPM checks, selftest). A CI check to detect drift or an automated sync mechanism would prevent silent divergence.

### 4. No Coverage Tracking
- **Impact**: Cannot measure, trend, or enforce test coverage. No visibility into whether new code includes tests.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours

### 5. No Agent Rules
- **Impact**: AI-assisted contributions have no guidance on testing patterns, code conventions, or quality standards
- **Severity**: LOW
- **Effort**: 2-3 hours
- **Note**: `CLAUDE.md` is explicitly listed in `.gitignore`, suggesting a deliberate choice or that developers use local-only agent configuration

## Quick Wins

### 1. Add Trivy Container Scanning to PR Workflow (1-2 hours)
```yaml
# Add after the "Build image" step in redhat-distro-container.yml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: '${{ env.IMAGE_NAME }}:${{ github.sha }}'
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
    ignore-unfixed: true
```

### 2. Add Unit Tests for build.py (2-3 hours)
```python
# tests/test_build.py
import pytest
from distribution.build import is_version_tag, is_install_from_source, get_llama_stack_install

class TestVersionParsing:
    def test_version_tag_with_rhai_suffix(self):
        assert is_version_tag("v0.5.0+rhai0") is True

    def test_version_tag_without_prefix(self):
        assert is_version_tag("0.5.0") is True

    def test_branch_name_main(self):
        assert is_version_tag("main") is False

    def test_branch_name_release(self):
        assert is_version_tag("release-0.5.x") is False

    def test_install_from_source_rhai(self):
        assert is_install_from_source("v0.5.0+rhai0") is True

    def test_install_from_source_version_tag(self):
        assert is_install_from_source("0.5.0") is False

    def test_install_from_source_branch(self):
        assert is_install_from_source("main") is True
```

### 3. Add SBOM Generation (1-2 hours)
```yaml
# Add after Trivy scan
- name: Generate SBOM
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: '${{ env.IMAGE_NAME }}:${{ github.sha }}'
    format: 'cyclonedx'
    output: 'sbom.json'
- name: Upload SBOM
  uses: actions/upload-artifact@v4
  with:
    name: sbom-${{ github.sha }}
    path: sbom.json
```

### 4. Create CLAUDE.md (1 hour)
Remove `CLAUDE.md` from `.gitignore` and create a basic agent configuration file with testing guidance, coding conventions, and contribution patterns.

## Detailed Findings

### CI/CD Pipeline

**Workflows (4 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `redhat-distro-container.yml` | PR, push, dispatch, cron(6AM UTC) | Build, test, publish container images |
| `pre-commit.yml` | PR, push | Run pre-commit hooks and verify no diffs |
| `semantic-pr.yml` | PR (target) | Enforce conventional commit PR titles |
| `stale_bot.yml` | cron(daily) | Auto-close stale issues and PRs |

**Strengths:**
- All workflows use concurrency control with `cancel-in-progress: true`
- GHA Docker build cache (`type=gha`) for fast rebuilds
- Nightly schedule tests `main` branch of upstream llama-stack
- `workflow_dispatch` allows custom builds from arbitrary commit SHA
- Smart publish gate: only pushes images when `distribution/` actually changed
- Slack notifications on success (image published) and failure
- Log collection and artifact upload for debugging
- All GH Actions pinned to commit SHAs (supply chain security)
- Dependabot for GH Actions (weekly) and Python dependencies (security-only)
- Renovate for Konflux-specific dependency updates

**Areas for improvement:**
- No security scanning step in the pipeline
- No SBOM generation
- No image signing/attestation (in GH Actions; Konflux may handle this)

### Test Coverage

**Test Files (3 shell scripts):**

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `tests/smoke.sh` | Smoke | 233 | Container startup, health check, model listing, inference, Postgres validation |
| `tests/run_integration_tests.sh` | Integration | 130 | Runs upstream llama-stack pytest suite against the built container |
| `tests/test_utils.sh` | Utility | 11 | Common test helpers |

**Smoke Test Coverage:**
- ✅ Container startup and health check (60s timeout with retry)
- ✅ Model registration verification (vLLM, Vertex AI, OpenAI, sentence-transformers)
- ✅ OpenAI-compatible inference testing per model
- ✅ PostgreSQL table creation verification
- ✅ PostgreSQL data population verification
- ✅ Conditional provider testing (skips when credentials unavailable)
- ✅ Failure tracking with detailed reporting

**Integration Test Coverage:**
- ✅ Clones upstream llama-stack at matching version
- ✅ Runs `pytest` against `tests/integration/inference/`
- ✅ Multi-model testing (vLLM, Vertex AI, OpenAI)
- ⚠️ Several tests explicitly skipped with TODOs (structured output, tool calling, MCP)
- ⚠️ Relies entirely on upstream test suite — no distribution-specific integration tests

**Missing Test Coverage:**
- ❌ No unit tests for `build.py` (version parsing, dependency categorization, Containerfile generation)
- ❌ No unit tests for `gen_distro_docs.py` (version extraction, table generation)
- ❌ No tests for `entrypoint.sh` logic (config resolution, OTEL wrapping)
- ❌ No tests for `notify.sh` (Slack notification formatting)
- ❌ No contract tests for the config.yaml provider configuration

### Code Quality

**Pre-commit Configuration (Excellent):**
- **17 hooks** across 4 repositories + 2 local hooks
- `pre-commit/pre-commit-hooks`: merge conflict, trailing whitespace, large files, end-of-file, no-commit-to-branch, YAML, private key detection, requirements-txt-fixer, mixed line endings, shebangs, JSON, symlinks, TOML
- `ruff-pre-commit`: Python linting (`--fix`) and formatting
- `actionlint`: GitHub Actions workflow validation
- `shellcheck`: Shell script linting
- **Local hooks**: `pkg-gen` (auto-generate Containerfile) and `doc-gen` (auto-generate distribution docs)

**PR Quality Gates:**
- ✅ Semantic PR titles enforced
- ✅ Pre-commit checks in CI with diff verification
- ✅ CODEOWNERS for docs, CI, and tests
- ✅ PR template with test plan section
- ✅ Mergify auto-merge with 2 approvals required
- ✅ Dependency PRs auto-merge with 1 approval
- ✅ Stale bot for issue/PR hygiene

**Missing:**
- ❌ No Python type checking (mypy, pyright)
- ❌ No SAST tools (CodeQL, Semgrep, Bandit)
- ❌ No secret scanning beyond pre-commit (no Gitleaks in CI)

### Container Images

**Build Process:**
- ✅ Auto-generated Containerfile from `Containerfile.in` template via `build.py`
- ✅ UBI9 base image (Red Hat certified): `registry.access.redhat.com/ubi9/python-312`
- ✅ Multi-architecture: AMD64 (build + test) and ARM64 (build verification)
- ✅ Separate Konflux build path: `Dockerfile.konflux` with RHOAI-specific base image, wheel releases, RPM checks, and selftest
- ✅ Deterministic builds with pinned dependencies
- ⚠️ Some dependency versions are loose (e.g., `fastapi`, `httpx` without version pins)

**Konflux Integration:**
- ✅ Tekton PipelineRuns for PR and push events
- ✅ Central pipeline reference (`odh-konflux-central`)
- ✅ Path filtering (only triggers on `distribution/` changes)
- ✅ Renovate configuration for Konflux-specific updates
- ⚠️ `Dockerfile.konflux` and `Containerfile` are maintained separately — manual sync needed

**Runtime Testing:**
- ✅ Health check endpoint validation
- ✅ Multi-provider model inference testing
- ✅ Database integration testing (PostgreSQL table creation + data population)
- ❌ No vulnerability scanning
- ❌ No SBOM generation
- ❌ No image signing or attestation

### Security

| Practice | Status | Details |
|----------|--------|---------|
| Dependency scanning | ✅ Partial | Dependabot (security-only for Python), Renovate for Konflux |
| GH Actions pinning | ✅ | All actions pinned to commit SHAs |
| Secret detection | ✅ Partial | `detect-private-key` in pre-commit; no Gitleaks in CI |
| Container scanning | ❌ | No Trivy, Snyk, or Grype in CI |
| SAST | ❌ | No CodeQL, Semgrep, or Bandit |
| SBOM | ❌ | No SBOM generation |
| Image signing | ❌ | No Cosign/Sigstore in GH Actions (Konflux may handle) |
| Supply chain | ✅ Partial | SHA-pinned actions, but no SLSA provenance |

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: All test type rules missing; no contribution guidance for AI agents
- **Notable**: `CLAUDE.md` is listed in `.gitignore`, suggesting the team either uses local-only agent configs or has deliberately excluded agent rules from the repo
- **Recommendation**: Remove `CLAUDE.md` from `.gitignore` and generate test rules with `/test-rules-generator` to guide AI-assisted contributions

## Recommendations

### Priority 0 (Critical)

1. **Add container vulnerability scanning to PR workflow**
   - Add Trivy or Grype scan step after image build
   - Set exit-code=1 for CRITICAL/HIGH severities
   - This is the highest-ROI security improvement

2. **Write unit tests for build.py**
   - Test `is_version_tag()`, `is_install_from_source()`, `get_llama_stack_install()`
   - Test `get_dependencies()` output parsing and categorization
   - Test `generate_containerfile()` template rendering
   - Add pytest + coverage configuration

3. **Automate Containerfile / Dockerfile.konflux drift detection**
   - Add a CI check that compares key aspects (base packages, entrypoint, config) between the two build paths
   - Or create a shared template system that generates both files

### Priority 1 (High Value)

4. **Add pytest + coverage for Python scripts**
   - Create `pyproject.toml` or `setup.cfg` with test configuration
   - Add codecov integration with coverage threshold (e.g., 80%)
   - Add coverage reporting to PRs

5. **Add SBOM generation**
   - Use Syft or Trivy to generate CycloneDX SBOM
   - Attach as build artifact and/or embed in image labels

6. **Create agent rules**
   - Remove `CLAUDE.md` from `.gitignore`
   - Create `.claude/rules/` with test and contribution patterns
   - Use `/test-rules-generator` to generate test rules for shell and Python

7. **Add unit tests for gen_distro_docs.py**
   - Test `extract_llama_stack_version()` with various Containerfile formats
   - Test `gen_distro_table()` provider table generation
   - Test `load_external_providers_info()` config parsing

### Priority 2 (Nice-to-Have)

8. **Add Python SAST (Bandit or Semgrep)**
   - Scan build.py and gen_distro_docs.py for security issues
   - Add as pre-commit hook or CI step

9. **Add contract tests for config.yaml**
   - Validate provider configuration schema
   - Test that all required environment variables are documented
   - Verify provider module versions match installed packages

10. **Add container startup time benchmarking**
    - Track image startup time across builds
    - Alert on significant regressions (the image has 60+ pip packages)

11. **Add tests for entrypoint.sh**
    - Test config resolution logic (RUN_CONFIG_PATH, DISTRO_NAME, default)
    - Test OTEL instrumentation wrapping

## Comparison to Gold Standards

| Dimension | rhds-llama-stack | odh-dashboard | notebooks | kserve |
|-----------|-----------------|---------------|-----------|--------|
| Unit Tests | 1/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 7/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 7/10 | 8/10 | 8/10 | 7/10 |
| Image Testing | 6/10 | 8/10 | 10/10 | 7/10 |
| Coverage Tracking | 0/10 | 9/10 | 6/10 | 9/10 |
| CI/CD Automation | 8/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **4.8/10** | **8.7/10** | **7.3/10** | **7.7/10** |

**Key takeaway**: The repository excels at CI/CD automation and runtime testing but falls significantly behind gold standards in unit testing, coverage tracking, and security scanning. The gap is partly explained by the repo's nature as a distribution/packaging project (fewer code files to test), but the build scripts contain enough complex logic to warrant unit tests.

## File Paths Reference

### CI/CD
- `.github/workflows/redhat-distro-container.yml` — Main build/test/publish pipeline
- `.github/workflows/pre-commit.yml` — Pre-commit checks
- `.github/workflows/semantic-pr.yml` — PR title validation
- `.github/workflows/stale_bot.yml` — Stale issue/PR cleanup
- `.github/actions/setup-vllm/action.yml` — vLLM setup composite action
- `.github/actions/setup-postgres/action.yml` — PostgreSQL setup composite action
- `.github/actions/notify-slack/notify.sh` — Slack notification script
- `.tekton/odh-llama-stack-core-pull-request.yaml` — Konflux PR pipeline
- `.tekton/odh-llama-stack-core-push.yaml` — Konflux push pipeline

### Testing
- `tests/smoke.sh` — Container smoke test (startup, inference, Postgres)
- `tests/run_integration_tests.sh` — Upstream integration test runner
- `tests/test_utils.sh` — Common test utilities

### Build & Configuration
- `distribution/build.py` — Containerfile generator (347 lines)
- `distribution/Containerfile.in` — Containerfile template
- `distribution/Containerfile` — Auto-generated Containerfile
- `distribution/config.yaml` — Llama Stack distribution configuration (348 lines)
- `distribution/entrypoint.sh` — Container entrypoint script
- `Dockerfile.konflux` — Konflux/RHOAI Dockerfile
- `konflux/cpu-ubi9.conf` — Konflux build arguments
- `scripts/gen_distro_docs.py` — Distribution docs generator (280 lines)

### Code Quality
- `.pre-commit-config.yaml` — 17 hooks (Ruff, actionlint, shellcheck, custom)
- `.github/mergify.yml` — Auto-merge rules with quality gates
- `.github/dependabot.yml` — Dependency updates (GH Actions + Python security)
- `.github/CODEOWNERS` — Code ownership for docs, CI, and tests
- `.github/PULL_REQUEST_TEMPLATE.md` — PR template with test plan section
- `renovate.json` / `.github/renovate.json` — Renovate configuration for Konflux
