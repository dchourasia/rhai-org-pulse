---
repository: "red-hat-data-services/fms-hf-tuning"
overall_score: 5.8
scorecard:
  - dimension: "Unit Tests"
    score: 7.0
    status: "234 test functions across 21 files with pytest; good coverage of core SFT trainer and data preprocessing"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "No dedicated integration or E2E test suites; no cluster-based GPU validation or model training smoke tests"
  - dimension: "Build Integration"
    score: 4.0
    status: "PR builds validated via Konflux Tekton pipelines but no PR-time Docker build in GitHub Actions; image.yaml only runs on main push"
  - dimension: "Image Testing"
    score: 3.0
    status: "Minimal runtime validation — only checks 'which accelerate' on NVCR image; no functional startup tests"
  - dimension: "Coverage Tracking"
    score: 5.0
    status: "Coverage workflow generates reports with genbadge but no codecov integration, no PR commenting, no enforcement thresholds"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Multi-Python matrix testing, tox-based orchestration, Konflux integration, /build /merge PR commands, automated tag sync"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory — zero AI-assisted test automation guidance"
critical_gaps:
  - title: "No integration or E2E test suite"
    impact: "Training regressions, GPU-specific failures, and multi-node issues not caught before release"
    severity: "HIGH"
    effort: "40-60 hours"
  - title: "No container image functional testing"
    impact: "Image startup failures, missing dependencies, and runtime errors discovered only in production"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No coverage enforcement or PR reporting"
    impact: "Coverage can silently regress with no guardrails; developers unaware of untested code paths"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning in CI"
    impact: "Vulnerability in dependencies or container images not detected until downstream consumption"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time image build validation in GitHub Actions"
    impact: "Dockerfile/dependency breakages only caught post-merge on main branch"
    severity: "MEDIUM"
    effort: "4-6 hours"
  - title: "Pre-commit config outdated (black 22.3.0, isort 5.11.5)"
    impact: "Potential formatting inconsistencies with newer Python syntax"
    severity: "LOW"
    effort: "1 hour"
quick_wins:
  - title: "Add Trivy scanning to PR workflow"
    effort: "1-2 hours"
    impact: "Early detection of CVEs in base images and Python dependencies"
  - title: "Integrate Codecov with coverage thresholds"
    effort: "2-3 hours"
    impact: "Automated coverage reporting on PRs with regression prevention"
  - title: "Add PR-time Docker build step to test.yaml"
    effort: "2-3 hours"
    impact: "Catch Dockerfile breakages before merge; validate both UBI9 and NVCR images"
  - title: "Create CLAUDE.md with basic test patterns"
    effort: "2-3 hours"
    impact: "Enable AI agents to generate consistent, idiomatic tests for this codebase"
  - title: "Update pre-commit hook versions"
    effort: "30 minutes"
    impact: "Ensure formatting tools support latest Python syntax features"
recommendations:
  priority_0:
    - "Add integration tests that perform actual model fine-tuning with small models and verify output quality"
    - "Implement container image functional testing — verify all entrypoints, accelerate launch, and GPU detection"
    - "Add Trivy or Snyk scanning to the PR workflow for both source and container image layers"
    - "Integrate Codecov with coverage threshold enforcement and PR status checks"
  priority_1:
    - "Create E2E test suite that validates training workflows on GPU infrastructure (periodic job)"
    - "Add PR-time Docker build validation for both Dockerfile and nvcr.Dockerfile"
    - "Create comprehensive CLAUDE.md and .claude/rules/ for test automation guidance"
    - "Add conftest.py with shared fixtures to reduce test code duplication"
  priority_2:
    - "Add performance regression testing for training throughput benchmarks"
    - "Implement multi-architecture image builds (x86_64 + ARM64)"
    - "Add SBOM generation and image signing to release pipeline"
    - "Create contract tests between fms-hf-tuning and downstream consumers (RHOAI operator)"
---

# Quality Analysis: fms-hf-tuning

## Executive Summary

**Overall Score: 5.8/10**

`fms-hf-tuning` is a Python library for fine-tuning foundation models using Hugging Face's training stack. It is a Red Hat downstream fork of `foundation-model-stack/fms-hf-tuning` with Konflux/Tekton build integration for RHOAI.

**Key Strengths:**
- Solid unit test suite with 234 test functions across 21 files covering the core SFT trainer, data processing, trackers, and utility modules
- Multi-Python version testing (3.9-3.12) via tox matrix in CI
- Konflux/Tekton pipeline integration for PR and push builds with SBOM generation
- Useful PR command system (`/build`, `/merge`) for manual image builds and merges
- Automated upstream tag synchronization with hourly monitoring

**Critical Gaps:**
- No integration or E2E tests — there is no test that actually runs a fine-tuning job end-to-end
- Container image testing is trivial (only `which accelerate` check)
- No security scanning (Trivy, Snyk, CodeQL) in any workflow
- Coverage is generated but has no enforcement, thresholds, or PR reporting
- Zero agent rules for AI-assisted development

**Agent Rules Status:** Missing — No CLAUDE.md, AGENTS.md, or .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.0/10 | 234 test functions, pytest framework, multi-version matrix |
| Integration/E2E | 2.0/10 | No dedicated integration or E2E suites exist |
| **Build Integration** | **4.0/10** | **Konflux pipelines present but no PR-time GitHub Actions image build** |
| Image Testing | 3.0/10 | Only validates `which accelerate` on NVCR image |
| Coverage Tracking | 5.0/10 | Coverage generation with genbadge, but no enforcement or PR reporting |
| CI/CD Automation | 7.0/10 | Well-structured tox+GHA+Konflux pipeline with PR commands |
| Agent Rules | 0.0/10 | No AI development guidance whatsoever |

## Critical Gaps

### 1. No Integration or E2E Test Suite
- **Impact:** Training regressions, GPU-specific failures, and multi-node issues are not caught before release. The test suite runs only CPU-based unit tests.
- **Severity:** HIGH
- **Effort:** 40-60 hours
- **Details:** All 234 test functions are unit tests that run on CPU. There are `tox -e gpu` and `tox -e accel` environments defined, but these are not automated in CI and require GPU hardware. No test actually performs a full fine-tuning run and validates the output model.

### 2. No Container Image Functional Testing
- **Impact:** Image startup failures, missing dependencies, and runtime errors are only discovered in production deployment.
- **Severity:** HIGH
- **Effort:** 8-12 hours
- **Details:** The `image.yaml` workflow (runs on main push only) builds the NVCR image and performs exactly one check: `docker run --rm --entrypoint which "$IMAGE_NAME" accelerate`. This doesn't validate that the training entrypoint (`accelerate_launch.py`) can start, that Python imports succeed, or that configuration files are correctly placed.

### 3. No Coverage Enforcement
- **Impact:** Coverage can silently regress with no guardrails. No PR-level visibility into coverage changes.
- **Severity:** HIGH
- **Effort:** 4-6 hours
- **Details:** The `coverage.yaml` workflow runs `tox -e coverage` which generates XML and a badge with `genbadge`, but the badge is not uploaded/published anywhere. There is no Codecov/Coveralls integration, no minimum coverage threshold, and no PR commenting. Coverage runs only on main branch pushes, not on PRs (despite being configured for PRs, it generates the badge locally and doesn't report).

### 4. No Security Scanning
- **Impact:** Known CVEs in dependencies or base images go undetected until downstream consumers flag them.
- **Severity:** HIGH
- **Effort:** 2-4 hours
- **Details:** No Trivy, Snyk, CodeQL, or any other security scanner is configured. No `.gitleaks.toml`, no `.trivyignore`, no dependency scanning. The Konflux pipeline includes some built-in scanning (via `clair-scan` and `sast-snyk-check` tasks), but the GitHub Actions workflows have zero security checks.

### 5. No PR-Time Image Build in GitHub Actions
- **Impact:** Dockerfile or dependency breakages are only caught after merge to main.
- **Severity:** MEDIUM
- **Effort:** 4-6 hours
- **Details:** `image.yaml` runs on `push` to main only. `release-image.yaml` runs on push/PR to the `release` branch. There is no GitHub Actions workflow that builds the Docker image on PR to `main`. The Konflux Tekton pipeline does build on PR, providing some coverage, but the faster GitHub Actions feedback loop is missing.

## Quick Wins

### 1. Add Trivy Scanning to PR Workflow (1-2 hours)
Add a Trivy container scan step to the test or format workflow:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

### 2. Integrate Codecov (2-3 hours)
Update `coverage.yaml` to upload results and enforce thresholds:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
    token: ${{ secrets.CODECOV_TOKEN }}
```
Add `.codecov.yml`:
```yaml
coverage:
  status:
    project:
      default:
        target: auto
        threshold: 2%
    patch:
      default:
        target: 80%
```

### 3. Add PR-Time Docker Build (2-3 hours)
Add a build-only job to `test.yaml` or create a new workflow:
```yaml
- name: Build Docker image (validation only)
  run: |
    docker build --target release -t fms-hf-tuning:test -f build/Dockerfile .
```

### 4. Create CLAUDE.md (2-3 hours)
Add agent rules documenting:
- Test patterns (pytest, fixtures, parametrize)
- Test data management (use `tests/artifacts/testdata/`)
- Mocking patterns (patch for logging, config utils)
- Test naming conventions

### 5. Update Pre-commit Hooks (30 minutes)
Current versions are outdated:
- `black`: 22.3.0 → latest (24.x)
- `isort`: 5.11.5 → latest (6.x or 5.13)

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (11 workflows):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yaml` | PR + push (main, release) | Unit tests via tox, Python 3.9-3.12 matrix |
| `coverage.yaml` | PR + push (main) | Coverage report generation |
| `format.yml` | PR + push (main, release) | Black/isort formatting + pylint |
| `image.yaml` | push (main) | Build & push NVCR dev image to Quay |
| `release-image.yaml` | PR + push (release) | Build & push UBI9 prod image |
| `staging-image.yaml` | tags + release | Build & push staging NVCR image |
| `build-and-publish.yaml` | release published | Build wheel & publish to PyPI |
| `labelpr.yaml` | PR events | Auto-label PRs by conventional commit type |
| `pr-command.yaml` | issue comment | `/build` and `/merge` commands |
| `monitor-tags.yaml` | cron (hourly) | Sync upstream tags to downstream |
| `push-upstream-tag.yaml` | workflow_dispatch | Push upstream tag with Tekton files |

**Strengths:**
- Multi-Python version matrix testing (3.9, 3.10, 3.11, 3.12)
- tox-based test orchestration enables local reproducibility
- Conventional commit enforcement via `labelpr.yaml`
- `/build` command allows on-demand image builds from PR comments
- Automated upstream tag synchronization prevents drift

**Weaknesses:**
- No concurrency control on any workflow (duplicate runs possible)
- No pip caching in any workflow (slower CI)
- No test parallelization
- `image.yaml` only runs on main push, not on PRs
- No dependency caching via `actions/cache`

### Test Coverage

**Test Structure:**
- **Total test functions:** 234
- **Total test files:** 21 (plus 4 helper/fixture files)
- **Source files:** 48
- **Test-to-code ratio:** ~1.1:1 (9,854 test LOC / 8,997 source LOC)
- **Framework:** pytest with parametrize, skipIf markers

**Test Distribution:**

| Module | Test Functions | Files |
|--------|---------------|-------|
| `test_sft_trainer.py` | 67 | 1 (2,835 lines — monolithic) |
| `data/` | 47 | 2 |
| `trainercontroller/` | 22 | 1 |
| `acceleration/` | 21 | 2 |
| `build/` | 22 | 2 |
| `utils/` | 44 | 7 |
| `trackers/` | 11 | 6 |

**Observations:**
- `test_sft_trainer.py` is a 2,835-line monolithic test file — hard to navigate and maintain
- Good use of `pytest.mark.skipif` for conditional testing (49 markers in sft_trainer)
- Extensive test data fixtures in `tests/artifacts/testdata/` with multiple formats (JSON, JSONL, Parquet, Arrow)
- No `conftest.py` — shared fixtures and configuration are missing
- Mocking is used in 7 files, primarily for logging and config utilities
- No parametrize-driven property testing or fuzzing

**Coverage Status:**
- `tox -e coverage` runs `coverage run` with `--source=tuning,build` and `--omit=*/_version.py,*/launch_training.py`
- Generates XML report and badge via `genbadge`
- No threshold enforcement or CI integration

### Code Quality

**Linting & Formatting:**
- **Pylint:** Configured via `tox -e lint` — runs across `tuning`, `scripts/*.py`, `build/*.py`, `tests`
- **Black:** v22.3.0 (outdated — current stable is 24.x)
- **isort:** v5.11.5 (outdated)
- **Pre-commit:** Configured with black and isort only
- **No ruff, mypy, or type checking** — significant gap for a Python library

**Missing Tools:**
- No type checking (mypy, pyright, or pytype)
- No ruff (modern, fast linter/formatter that replaces black + isort + flake8)
- No bandit or safety for Python security scanning
- Pylint version capped at 3.1.0 — may miss newer checks

### Container Images

**Dockerfiles:**
- `build/Dockerfile` — UBI9-based multi-stage build (base → cuda-base → cuda-devel → python-installations → release)
- `build/nvcr.Dockerfile` — NVIDIA NGC Container Registry-based (builder → runner)

**Strengths:**
- Multi-stage builds with clean separation of concerns
- Non-root user execution (`tuning` user, UID 1000)
- Build arg configurability (enable/disable optional features like AIM, MLflow, FMS acceleration)
- Cache mounts for pip installations
- Security hardening: removes `subscription-manager`, strips python from release base

**Weaknesses:**
- No HEALTHCHECK instruction
- No `.dockerignore` file (sends entire repo context including tests, docs, git)
- x86_64 only — no multi-architecture support
- No image signing or attestation in GitHub Actions
- SBOM generation only via Konflux pipeline, not GitHub Actions

### Security

**Current State: No security scanning in GitHub Actions.**

- No Trivy, Snyk, or Grype container scanning
- No CodeQL or Semgrep SAST
- No `gitleaks` or `truffleHog` for secret detection
- No `pip-audit` or `safety` for Python dependency scanning
- No `.trivyignore` or security scanning configuration

**Konflux Coverage:**
The Tekton pipelines include built-in security tasks (`clair-scan`, `sast-snyk-check`), providing some baseline scanning in the Konflux build system. However, this feedback comes later in the development cycle than GitHub Actions PR checks.

### Agent Rules (Agentic Flow Quality)

**Status:** Missing
- No `CLAUDE.md` or `AGENTS.md` in repository root
- No `.claude/` directory
- No `.claude/rules/` test creation rules
- No `.claude/skills/` custom skills
- No testing documentation beyond inline docstrings

**Coverage:** Zero — no test types have AI development rules

**Quality:** N/A

**Gaps:**
- No guidance for AI agents on test creation patterns
- No examples of expected test structure or fixtures
- No quality gates or checklists for AI-generated code
- No documentation of testing philosophy or conventions

**Recommendation:** Generate comprehensive agent rules with `/test-rules-generator` covering:
- Unit test patterns (pytest, fixtures, parametrize, skipif for GPU)
- Test data management (use `tests/artifacts/testdata/` directory)
- Mocking patterns (logging, config utils, external services)
- Naming conventions (test_<module>_<scenario>)
- GPU test environment setup (tox -e gpu, CUDA_VISIBLE_DEVICES)

## Recommendations

### Priority 0 (Critical)

1. **Add integration tests for model fine-tuning** — Create tests that run a small model (e.g., `Maykeye/TinyLlama`) through the full SFT pipeline and validate output model weights, loss convergence, and checkpoint saving.

2. **Implement container image functional testing** — After building, run the image and verify:
   - Python imports succeed (`python -c "from tuning import sft_trainer"`)
   - Entrypoint script is executable and parseable
   - Accelerate configuration is valid
   - All required files are present (`/app/accelerate_launch.py`, defaults YAML)

3. **Add security scanning** — Add Trivy for container scanning and `pip-audit` for dependency scanning to the PR workflow.

4. **Enforce coverage thresholds** — Integrate Codecov with project and patch coverage targets, and block PRs that drop coverage below threshold.

### Priority 1 (High Value)

5. **Create E2E test pipeline** — Periodic GPU-based CI job that validates:
   - LoRA fine-tuning with PEFT
   - FSDP multi-GPU training
   - Checkpoint save/resume
   - Inference with tuned model

6. **Add PR-time Docker build validation** — Build both Dockerfile and nvcr.Dockerfile on PRs to catch dependency/packaging issues early.

7. **Create CLAUDE.md and agent rules** — Document test patterns, fixtures, and conventions for AI-assisted development.

8. **Add conftest.py** — Create shared fixtures for model initialization, temp directories, and test data loading to reduce duplication across test files.

9. **Add type checking** — Introduce mypy or pyright with gradual strictness to catch type errors early.

### Priority 2 (Nice-to-Have)

10. **Add training throughput benchmarks** — Track tokens/sec regression across releases with standardized model and dataset configurations.

11. **Multi-architecture image support** — Add ARM64 builds for broader deployment compatibility.

12. **Add SBOM and image signing** — Add cosign signing and SBOM generation to GitHub Actions release workflows (already present in Konflux).

13. **Contract tests with downstream** — Define API contracts between fms-hf-tuning and RHOAI operator for training job specification, checkpoint format, and model output structure.

14. **Break up monolithic test file** — Refactor `test_sft_trainer.py` (2,835 lines, 67 tests) into domain-specific test files.

## Comparison to Gold Standards

| Dimension | fms-hf-tuning | odh-dashboard | notebooks | kserve |
|-----------|--------------|---------------|-----------|--------|
| Unit Tests | 7/10 (234 tests, pytest) | 9/10 (Jest, comprehensive) | 7/10 (pytest) | 9/10 (Go testing) |
| Integration/E2E | 2/10 (none) | 9/10 (Cypress E2E) | 6/10 (image validation) | 9/10 (envtest + E2E) |
| Build Integration | 4/10 (Konflux only) | 7/10 (PR builds) | 8/10 (image matrix) | 8/10 (PR builds) |
| Image Testing | 3/10 (`which` check) | 7/10 (startup tests) | 9/10 (5-layer validation) | 7/10 (kind deploy) |
| Coverage | 5/10 (generated only) | 9/10 (Codecov enforced) | 5/10 (basic) | 9/10 (enforced thresholds) |
| CI/CD | 7/10 (tox + matrix) | 9/10 (comprehensive) | 8/10 (matrix builds) | 9/10 (Prow + GHA) |
| Agent Rules | 0/10 (none) | 8/10 (comprehensive) | 2/10 (minimal) | 3/10 (basic) |
| Security | 2/10 (Konflux only) | 7/10 (Trivy + CodeQL) | 6/10 (image scan) | 8/10 (SAST + container) |

## File Paths Reference

### CI/CD
- `.github/workflows/test.yaml` — Unit tests (PR + push, Python 3.9-3.12)
- `.github/workflows/coverage.yaml` — Coverage reporting
- `.github/workflows/format.yml` — Formatting + linting
- `.github/workflows/image.yaml` — NVCR dev image (main push)
- `.github/workflows/release-image.yaml` — UBI9 prod image (release branch)
- `.github/workflows/staging-image.yaml` — Staging image (tags/releases)
- `.github/workflows/build-and-publish.yaml` — PyPI publishing
- `.github/workflows/pr-command.yaml` — `/build` and `/merge` PR commands
- `.github/workflows/monitor-tags.yaml` — Upstream tag sync (hourly cron)
- `.tekton/fms-hf-tuning-pull-request.yaml` — Konflux PR pipeline
- `.tekton/fms-hf-tuning-push.yaml` — Konflux push pipeline

### Testing
- `tests/test_sft_trainer.py` — Main SFT trainer tests (67 functions)
- `tests/data/` — Data preprocessing and handler tests
- `tests/trackers/` — Tracker integration tests
- `tests/trainercontroller/` — Trainer controller tests
- `tests/acceleration/` — FMS acceleration framework tests
- `tests/build/` — Build utility and launch script tests
- `tests/utils/` — Utility function tests
- `tests/artifacts/` — Test fixtures, data, and model references

### Code Quality
- `.pre-commit-config.yaml` — Black (22.3.0) + isort (5.11.5)
- `tox.ini` — Test environments (py, fmt, lint, coverage, gpu, accel)
- `pytest.ini` — pytest configuration
- `Makefile` — Make targets (test, fmt, lint)

### Container Images
- `build/Dockerfile` — UBI9 multi-stage production image
- `build/nvcr.Dockerfile` — NVIDIA NGC-based development image

### Package
- `pyproject.toml` — Package configuration, dependencies, optional extras
- `CODEOWNERS` — 5 maintainers
