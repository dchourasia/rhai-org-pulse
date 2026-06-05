---
repository: "foundation-model-stack/fms-hf-tuning"
overall_score: 5.4
scorecard:
  - dimension: "Unit Tests"
    score: 7.5
    status: "Strong unit test suite with 234 tests across 21 files, 1.05:1 test-to-source LOC ratio"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "No integration or E2E tests; GPU-dependent tests only via manual tox envs (gpu, accel)"
  - dimension: "Build Integration"
    score: 3.0
    status: "No PR-time image build or Konflux simulation; image builds only on main push"
  - dimension: "Image Testing"
    score: 3.5
    status: "Basic 'which accelerate' sanity check on main push; no PR-time image validation"
  - dimension: "Coverage Tracking"
    score: 4.5
    status: "Coverage runs on PRs via tox but no codecov upload, no thresholds, no PR reporting"
  - dimension: "CI/CD Automation"
    score: 6.5
    status: "Multi-Python matrix testing on PRs; format/lint on PRs; but no caching, no concurrency control"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules for test automation"
critical_gaps:
  - title: "No coverage threshold enforcement"
    impact: "Coverage can silently decrease without any PR gate; regressions go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time image build validation"
    impact: "Dockerfile changes merged without build testing; failures discovered only post-merge on main"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning (Trivy, CodeQL, SAST)"
    impact: "Vulnerabilities in dependencies and container images undetected; no CVE protection"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No integration or E2E test automation in CI"
    impact: "GPU-dependent training workflows not validated; regressions caught only by manual testing"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No codecov/coveralls PR reporting"
    impact: "Reviewers cannot see coverage impact of changes during review"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No agent rules for test automation"
    impact: "AI-assisted development produces inconsistent test patterns"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add codecov integration with coverage upload"
    effort: "1-2 hours"
    impact: "Immediate PR-level coverage visibility and trend tracking"
  - title: "Add Trivy container scanning to image workflow"
    effort: "1-2 hours"
    impact: "Catch CVEs in container images before deployment"
  - title: "Add concurrency control to PR workflows"
    effort: "30 minutes"
    impact: "Cancel stale CI runs, save compute, speed up feedback"
  - title: "Add pip dependency caching to test workflow"
    effort: "30 minutes"
    impact: "Faster CI runs by caching pip downloads"
  - title: "Add coverage failure threshold (e.g., 70%)"
    effort: "1 hour"
    impact: "Prevent silent coverage regressions"
recommendations:
  priority_0:
    - "Add codecov integration with PR reporting and coverage threshold enforcement"
    - "Add Trivy scanning for container images and Dependabot security alerts for Python dependencies"
    - "Add PR-time Docker image build validation for both Dockerfile and nvcr.Dockerfile"
  priority_1:
    - "Create a GPU-enabled CI runner for integration tests or use mocked GPU training paths"
    - "Add CodeQL or Semgrep SAST scanning workflow"
    - "Add concurrency control and pip caching to all PR workflows"
    - "Create agent rules (.claude/rules/) for unit test patterns and conventions"
  priority_2:
    - "Add multi-architecture image builds (amd64/arm64)"
    - "Add image signing and SBOM generation"
    - "Add pre-commit hooks enforcement in CI beyond black/isort"
    - "Add performance regression testing for training throughput"
---

# Quality Analysis: fms-hf-tuning

## Executive Summary

- **Overall Score: 5.4/10**
- **Repository Type**: Python library for fine-tuning large language models using HuggingFace Transformers
- **Primary Language**: Python (3.9-3.12)
- **Key Frameworks**: PyTorch, Transformers, TRL, PEFT, Accelerate

### Key Strengths
- Strong unit test suite with 234 test functions and excellent test-to-source ratio (1.05:1)
- Multi-Python-version matrix testing (3.9, 3.10, 3.11, 3.12) on PRs
- Pre-commit hooks for formatting (Black, isort) enforced in CI
- Pylint linting with detailed configuration
- Dependabot configured for daily pip dependency updates
- Well-structured Dockerfiles with multi-stage builds (UBI9 + NVCR variants)
- Tox-based test orchestration with clear environment separation

### Critical Gaps
- **No coverage enforcement**: Coverage runs but has no thresholds or codecov upload
- **No security scanning**: Zero Trivy, CodeQL, Semgrep, or Gitleaks integration
- **No PR-time image builds**: Images only built on main push, not on PRs
- **No integration/E2E automation**: GPU tests require manual tox invocation
- **No agent rules**: No CLAUDE.md or .claude/ directory for AI-assisted development

### Agent Rules Status: **Missing**

---

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.5/10 | Strong test suite with 234 tests, 1.05:1 LOC ratio |
| Integration/E2E | 3.0/10 | No automated integration tests; GPU tests manual only |
| **Build Integration** | **3.0/10** | **No PR-time image builds or Konflux simulation** |
| Image Testing | 3.5/10 | Minimal sanity check (`which accelerate`) on main only |
| Coverage Tracking | 4.5/10 | Runs on PRs but no upload, no threshold, no reporting |
| CI/CD Automation | 6.5/10 | Multi-version matrix, lint/format on PRs; no caching |
| Agent Rules | 0.0/10 | No agent rules, no CLAUDE.md, no .claude/ directory |

---

## Critical Gaps

### 1. No Coverage Threshold Enforcement
- **Impact**: Coverage can silently decrease without any PR gate; regressions go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The `coverage.yaml` workflow runs `tox -e coverage` which generates a coverage report and badge, but there is no `--fail-under` threshold configured, no codecov/coveralls upload, and no PR comment with coverage diff. The tox coverage config omits `_version.py` and `launch_training.py` but doesn't set a minimum.
- **Fix**: Add `coverage report --fail-under=70` to tox coverage env, add codecov upload step

### 2. No PR-Time Image Build Validation
- **Impact**: Dockerfile changes merged without build testing; failures discovered only post-merge
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: The `image.yaml` workflow only runs on `push` to `main`, not on PRs. The `release-image.yaml` builds on PRs to `release` branch but not `main`. There is a `/build` PR command workflow, but it requires manual invocation via a comment — it is not automatic. Changes to Dockerfiles, dependencies, or build scripts are not validated before merge.
- **Fix**: Add Docker build step to PR workflow (build only, no push)

### 3. No Security Scanning
- **Impact**: Vulnerabilities in container images and Python dependencies go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No Trivy, Snyk, CodeQL, Semgrep, Gitleaks, or any SAST/DAST tool configured. Dependabot handles dependency version bumps but does not scan for vulnerabilities in built images. Given this is an ML training library that runs in GPU clusters with access to models and data, security scanning is critical.
- **Fix**: Add Trivy image scanning workflow, enable CodeQL for Python

### 4. No Integration/E2E Test Automation in CI
- **Impact**: GPU-dependent training workflows not validated in CI; regressions caught only by manual testing
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The tox config has `gpu` and `accel` environments for GPU tests, but these are not automated in any CI workflow. The unit tests run without GPU on standard runners, but actual training execution paths (the core purpose of this library) are not continuously tested. There is no Kind/Minikube deployment testing.
- **Fix**: Set up GPU-enabled CI runners (e.g., GitHub GPU runners) or create mocked integration tests

### 5. No Codecov/Coveralls PR Reporting
- **Impact**: Reviewers cannot see coverage impact of changes during review
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: Coverage workflow generates `coverage.xml` and a badge but does not upload to codecov or post a PR comment with the diff.
- **Fix**: Add codecov GitHub Action with token to coverage workflow

### 6. No Agent Rules for Test Automation
- **Impact**: AI-assisted development produces inconsistent test patterns and may miss project conventions
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: No `CLAUDE.md`, `AGENTS.md`, or `.claude/` directory exists. There are no documented test creation patterns, naming conventions, or quality checklists for AI agents to follow.
- **Fix**: Use `/test-rules-generator` to create rules based on existing test patterns

---

## Quick Wins

### 1. Add Codecov Integration (1-2 hours)
Add codecov upload to `coverage.yaml`:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
    token: ${{ secrets.CODECOV_TOKEN }}
    fail_ci_if_error: true
```

### 2. Add Trivy Container Scanning (1-2 hours)
Add to image build workflow:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'fms-hf-tuning:latest'
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

### 3. Add Concurrency Control (30 minutes)
Add to all PR-triggered workflows:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

### 4. Add Pip Caching (30 minutes)
Add to test workflow:
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: ${{ matrix.python-version.setup }}
    cache: 'pip'
```

### 5. Add Coverage Threshold (1 hour)
Update tox coverage command:
```ini
commands =
    coverage run --source=tuning,build --module pytest tests/
    coverage report -m --fail-under=70
```

---

## Detailed Findings

### CI/CD Pipeline

**Workflows (9 total)**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yaml` | PR + push (main, release) | Unit tests with Python 3.9-3.12 matrix |
| `coverage.yaml` | PR + push (main) | Coverage report generation |
| `format.yml` | PR + push (main, release) | Black/isort formatting + pylint |
| `image.yaml` | push (main) | Build and push NVCR dev image |
| `release-image.yaml` | PR + push (release) | Build UBI9 prod image |
| `staging-image.yaml` | tags + release | Build staging NVCR image |
| `build-and-publish.yaml` | release published | PyPI package publishing |
| `labelpr.yaml` | PR events | Conventional commit label enforcement |
| `pr-command.yaml` | issue_comment | `/build` and `/merge` PR commands |

**Strengths**:
- Multi-Python-version matrix (3.9-3.12) for unit tests
- Shared `free-up-disk-space` composite action for disk management
- Conventional commit enforcement via PR labels
- `/build` command for on-demand image builds from PRs

**Weaknesses**:
- No concurrency control on any workflow — stale runs pile up
- No pip caching — every run installs from scratch
- No artifact uploads or test result summaries
- Test workflow doesn't use `free-up-disk-space` action (other workflows do)
- No required status checks documented

### Test Coverage

**Test Structure**:
- 21 test files with 234 total test functions
- 9,676 lines of test code vs 9,186 lines of source code (1.05:1 ratio)
- Framework: pytest with tox orchestration
- Test data: Rich artifact fixtures (tiny models, tokenizers, data configs)

**Test Distribution**:
| Module | Test Count | Description |
|--------|-----------|-------------|
| `test_sft_trainer.py` | 67 | Core SFT training scenarios |
| `test_data_preprocessing.py` | 38 | Data preprocessing pipelines |
| `test_tuning_trainercontroller.py` | 22 | Trainer controller logic |
| `test_acceleration_framework.py` | 17 | Acceleration framework |
| `test_config_utils.py` | 16 | Configuration utilities |
| `test_launch_script.py` | 13 | Build launch scripts |
| `test_data_handlers.py` | 9 | Data handler logic |
| `test_utils.py` (build) | 9 | Build utilities |
| `test_tokenizer_data_utils.py` | 8 | Tokenizer utilities |
| `test_embedding_resize.py` | 6 | Embedding resize logic |
| Others (11 files) | 29 | Trackers, logging, misc utils |

**Test Quality Observations**:
- Extensive parameterized tests for data formats (JSON, JSONL, Parquet, Arrow)
- Good use of tiny model artifacts for fast testing without GPU
- Tests cover multiple data configurations (single-turn, multi-turn, vision)
- Tracker tests cover Aim, MLflow, ClearML, file logging, HF resource scanner
- Missing: no mock/patch patterns for GPU operations in CPU-only CI

### Code Quality

**Linting**:
- **Pylint**: Comprehensive `.pylintrc` with `fail-under=10` (maximum strictness)
- Many pylint rules disabled (no-member, too-many-arguments, cyclic-import, etc.)
- Runs on `tuning`, `scripts/*.py`, `build/*.py`, and `tests`
- **Black**: Code formatting via pre-commit (v22.3.0 — outdated, latest is 24.x)
- **isort**: Import sorting with project-specific configuration
- No type checking (no mypy, pyright, or type stubs)
- No ruff (modern replacement for flake8 + isort + black)

**Pre-commit Hooks**:
- `.pre-commit-config.yaml` with Black and isort
- Enforced in CI via `tox -e fmt` which runs `scripts/fmt.sh`
- Missing: pylint, security checks, type checking in pre-commit

### Container Images

**Two Dockerfiles**:
1. `build/Dockerfile` — UBI9-based production image with CUDA 12.1
   - Multi-stage build (base → cuda-base → cuda-devel → python-installations → release)
   - Proper user creation (non-root)
   - Build caching with `--mount=type=cache`
   - Configurable extras via build args (AIM, MLflow, FMS acceleration, etc.)
   - Final image strips Python/dnf to reduce attack surface

2. `build/nvcr.Dockerfile` — NVCR PyTorch base for development
   - Two-stage build (builder → runtime)
   - Cleanup of caches and __pycache__ in build layer
   - NVCR image version pinned (`25.02-py3`)

**Runtime Testing**:
- Only `which accelerate` check on NVCR image (main push only)
- No startup validation, no import verification, no health checks
- No multi-architecture support (x86_64 only)
- No SBOM generation or image signing

### Security

**Current State**: Minimal
- Dependabot configured for daily pip updates (version bumps only)
- CODEOWNERS file for review enforcement
- Proper secrets handling in workflows (QUAY_USERNAME, QUAY_ROBOT_TOKEN)
- Non-root user in UBI9 Dockerfile
- Removal of CVE-prone packages (perl-Net-SSLeay key) in Dockerfile

**Missing**:
- No container image scanning (Trivy, Snyk, Grype)
- No SAST/CodeQL scanning
- No secret detection (Gitleaks, TruffleHog)
- No dependency vulnerability scanning (beyond Dependabot version bumps)
- No SBOM generation
- No image signing/attestation
- No `.trivyignore` or vulnerability exception list

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: No test type rules exist
- **Quality**: N/A — no rules to evaluate
- **Gaps**: Everything — no CLAUDE.md, no AGENTS.md, no `.claude/` directory
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering:
  - Unit test patterns (pytest conventions, fixture usage, tiny model artifacts)
  - Data test patterns (parameterized data format testing)
  - Tracker test patterns (plugin-style tracker testing)
  - Build script test patterns
  - Naming conventions and file organization

---

## Recommendations

### Priority 0 (Critical)

1. **Add codecov integration with threshold enforcement**
   - Upload coverage.xml to codecov in coverage workflow
   - Set `--fail-under=70` (or appropriate baseline)
   - Enable PR comments showing coverage diff
   - Effort: 2-4 hours

2. **Add security scanning**
   - Trivy for container images (both Dockerfile and nvcr.Dockerfile)
   - CodeQL or Semgrep for Python SAST
   - Enable Dependabot security alerts (not just version updates)
   - Effort: 2-4 hours

3. **Add PR-time image build validation**
   - Build (no push) both Dockerfile and nvcr.Dockerfile on PRs to main
   - Run basic sanity checks (import tuning, which accelerate)
   - Effort: 4-6 hours

### Priority 1 (High Value)

4. **Automate GPU/integration tests**
   - Set up GPU-enabled runners or use mocked training paths
   - Create integration tests that validate training end-to-end
   - Effort: 8-16 hours

5. **Add CI optimizations**
   - Concurrency control on all PR workflows
   - Pip caching in test and coverage workflows
   - Add `free-up-disk-space` to test workflow
   - Effort: 1-2 hours

6. **Create agent rules**
   - Generate `.claude/rules/` with test patterns from existing codebase
   - Document pytest conventions, fixture patterns, tiny model usage
   - Effort: 2-4 hours

7. **Upgrade tooling**
   - Update Black from 22.3.0 to latest
   - Consider migrating from pylint to ruff (faster, more rules)
   - Add mypy or pyright for type checking
   - Effort: 4-8 hours

### Priority 2 (Nice-to-Have)

8. **Multi-architecture image builds** — Add ARM64 support
9. **Image signing and SBOM** — sigstore/cosign + syft
10. **Performance regression testing** — Track training throughput across commits
11. **Pre-commit hook expansion** — Add pylint, security checks to pre-commit
12. **Test result reporting** — JUnit XML upload for GitHub test summaries

---

## Comparison to Gold Standards

| Dimension | fms-hf-tuning | odh-dashboard | notebooks | kserve |
|-----------|:---:|:---:|:---:|:---:|
| Unit Tests | 7.5 | 9.0 | 7.0 | 9.0 |
| Integration/E2E | 3.0 | 9.0 | 8.0 | 9.0 |
| Build Integration | 3.0 | 8.0 | 7.0 | 8.0 |
| Image Testing | 3.5 | 7.0 | 9.0 | 7.0 |
| Coverage Tracking | 4.5 | 9.0 | 5.0 | 9.0 |
| CI/CD Automation | 6.5 | 9.0 | 8.0 | 9.0 |
| Agent Rules | 0.0 | 8.0 | 3.0 | 2.0 |
| **Overall** | **5.4** | **8.7** | **7.0** | **8.2** |

### Key Differences from Gold Standards
- **odh-dashboard**: Has contract tests, multi-layer testing, comprehensive CI/CD with coverage enforcement, and well-maintained agent rules — fms-hf-tuning lacks all of these
- **notebooks**: Excels at image testing with 5-layer validation and multi-arch support — fms-hf-tuning has minimal image validation
- **kserve**: Strong coverage enforcement, multi-version testing, comprehensive E2E — fms-hf-tuning has no coverage gates

---

## File Paths Reference

### CI/CD
- `.github/workflows/test.yaml` — Unit tests (PR-triggered, multi-Python matrix)
- `.github/workflows/coverage.yaml` — Coverage generation (PR-triggered)
- `.github/workflows/format.yml` — Formatting and linting (PR-triggered)
- `.github/workflows/image.yaml` — NVCR dev image build (main push only)
- `.github/workflows/release-image.yaml` — UBI9 prod image (release branch)
- `.github/workflows/staging-image.yaml` — Staging image (tags/releases)
- `.github/workflows/pr-command.yaml` — /build and /merge PR commands
- `.github/workflows/build-and-publish.yaml` — PyPI publishing
- `.github/actions/free-up-disk-space/action.yml` — Shared disk cleanup action

### Testing
- `tests/test_sft_trainer.py` — Core SFT trainer tests (67 tests)
- `tests/data/` — Data preprocessing and handler tests
- `tests/trackers/` — Tracker plugin tests (Aim, MLflow, ClearML, etc.)
- `tests/trainercontroller/` — Trainer controller tests
- `tests/acceleration/` — Acceleration framework tests
- `tests/build/` — Build script tests
- `tests/utils/` — Utility function tests
- `tests/artifacts/` — Test fixtures (tiny models, tokenizers, data configs)

### Code Quality
- `.pylintrc` — Detailed pylint configuration (fail-under=10)
- `.pre-commit-config.yaml` — Black (22.3.0) + isort hooks
- `.isort.cfg` — Import sorting configuration
- `tox.ini` — Test orchestration (py, fmt, lint, coverage, gpu, accel)
- `pytest.ini` — Pytest configuration

### Container Images
- `build/Dockerfile` — UBI9 production image (multi-stage, CUDA 12.1)
- `build/nvcr.Dockerfile` — NVCR development image (PyTorch base)
- `build/accelerate_launch.py` — Container entrypoint
- `build/utils.py` — Build utilities

### Project Config
- `pyproject.toml` — Package metadata and dependencies
- `Makefile` — Developer shortcuts (test, fmt, lint)
- `.github/dependabot.yml` — Daily pip dependency updates
- `CODEOWNERS` — Review enforcement
