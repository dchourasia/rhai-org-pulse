---
repository: "red-hat-data-services/red-hat-ai-examples"
overall_score: 4.2
scorecard:
  - dimension: "Unit Tests"
    score: 6.0
    status: "Good validation tests for notebook structure/syntax; limited code-level unit tests for Python utilities"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Structural validation only; no notebook execution or runtime integration testing"
  - dimension: "Build Integration"
    score: 1.0
    status: "No container images, no Konflux integration, no build-time validation"
  - dimension: "Image Testing"
    score: 1.0
    status: "No Dockerfiles or container image testing; examples are not containerized"
  - dimension: "Coverage Tracking"
    score: 3.0
    status: "pytest-cov configured locally but no CI enforcement, no codecov integration, no thresholds"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Solid code quality workflows with Ruff, markdown linting, and triple secret scanning; lacks coverage enforcement and concurrency control"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules for test automation"
critical_gaps:
  - title: "No notebook execution testing"
    impact: "Notebooks may have broken code, missing imports, or runtime errors undetected until manual execution"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No coverage enforcement in CI"
    impact: "Test coverage cannot regress without detection; no PR coverage gates"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Missing example.yaml in 8 of 9 examples"
    impact: "Metadata validation tests skip for most examples; structured discovery is incomplete"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No SAST/CodeQL integration"
    impact: "Python code vulnerabilities not detected at PR time; only secret scanning exists"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "No container image testing"
    impact: "Examples cannot be validated in containerized environments matching RHOAI deployment"
    severity: "MEDIUM"
    effort: "16-24 hours"
quick_wins:
  - title: "Add codecov integration with coverage thresholds"
    effort: "2-3 hours"
    impact: "Enforce minimum coverage and prevent regressions on every PR"
  - title: "Add concurrency control to CI workflows"
    effort: "30 minutes"
    impact: "Cancel stale workflow runs on new pushes to save CI resources"
  - title: "Create example.yaml for all 8 missing examples"
    effort: "4-6 hours"
    impact: "Enable metadata validation for all examples; improve discoverability"
  - title: "Add CodeQL/Semgrep workflow for Python SAST"
    effort: "1-2 hours"
    impact: "Catch security vulnerabilities in Python code at PR time"
  - title: "Create basic CLAUDE.md with testing guidance"
    effort: "2-3 hours"
    impact: "Guide AI agents to follow project testing patterns and conventions"
recommendations:
  priority_0:
    - "Add notebook execution smoke tests using papermill or nbconvert to validate notebooks run without errors"
    - "Enforce coverage thresholds in CI with codecov integration and PR status checks"
    - "Create example.yaml metadata files for all 8 examples missing them"
  priority_1:
    - "Add CodeQL or Semgrep SAST scanning for Python security vulnerabilities"
    - "Create agent rules (.claude/rules/) for test creation patterns and notebook standards"
    - "Add smoke tests for more examples beyond knowledge-tuning (model-serve-flow, fine-tuning, ray)"
  priority_2:
    - "Create containerized testing environment matching RHOAI workbench images"
    - "Add dependency vulnerability scanning (Dependabot or Renovate)"
    - "Add notebook output regression testing for examples with keep_output cells"
---

# Quality Analysis: red-hat-ai-examples

## Executive Summary

- **Overall Score: 4.2/10**
- **Repository Type**: Python/Jupyter notebook examples repository for AI/ML on Red Hat platforms
- **Primary Languages**: Python (38 files), Jupyter Notebooks (39 files)
- **Testing Framework**: pytest with pytest-cov, pytest-xdist
- **Key Strengths**: Excellent pre-commit hooks with triple secret scanning, well-configured Ruff linting, thorough notebook structure validation, strong contributing documentation
- **Critical Gaps**: No notebook execution testing, no coverage enforcement in CI, most examples missing metadata files, no container testing, no agent rules
- **Agent Rules Status**: Missing

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6.0/10 | Good structural validation; limited code-level unit tests |
| Integration/E2E | 3.0/10 | Structure-only; no runtime execution testing |
| **Build Integration** | **1.0/10** | **No containers, no build validation** |
| Image Testing | 1.0/10 | No Dockerfiles or container testing |
| Coverage Tracking | 3.0/10 | Configured locally, not enforced in CI |
| CI/CD Automation | 7.0/10 | Strong quality/security, lacks coverage gates |
| Agent Rules | 0.0/10 | No agent rules exist |

## Critical Gaps

### 1. No Notebook Execution Testing
- **Impact**: Notebooks may have broken code, missing imports, or runtime errors that go undetected until manual execution. For an examples repository, this is the most critical gap — broken examples damage credibility.
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Current State**: Tests validate notebook JSON structure, cell types, and Python syntax via AST parsing, but never actually execute any notebook cells.
- **Fix**: Use `papermill` or `nbconvert --execute` to run notebooks in CI with mocked/minimal environments. Start with a subset of lightweight notebooks that don't require GPU/cluster access.

### 2. No Coverage Enforcement in CI
- **Impact**: Test coverage can silently regress. No PR gates prevent merging uncovered code.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Current State**: `pytest-cov` is in test dependencies and `[tool.coverage.*]` is configured in `pyproject.toml`, but CI workflows don't run coverage or upload results.
- **Fix**: Add `--cov` flags to pytest commands in `notebook-tests.yml`, upload to codecov, and set minimum threshold.

### 3. Missing example.yaml in 8 of 9 Examples
- **Impact**: The metadata validation tests (`test_example_metadata.py`) skip for most examples. The structured example discovery and schema validation system is ineffective.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Current State**: Only `examples/ray/data/rag/ray-data-pipeline/example.yaml` exists. Missing from: `automl`, `autorag`, `domain_customization_kfp_pipeline`, `fine-tuning`, `knowledge-tuning`, `llmcompressor`, `model-serve-flow`, `trainer`.
- **Fix**: Create `example.yaml` for each example directory following the schema in `docs/METADATA_SCHEMA.md`.

### 4. No SAST/CodeQL Integration
- **Impact**: Python code security vulnerabilities not caught at PR time. Only secret scanning (Gitleaks/Talisman/detect-secrets) exists.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Fix**: Add a CodeQL or Semgrep workflow targeting Python.

### 5. No Container/Image Testing
- **Impact**: Examples cannot be validated in environments matching RHOAI workbench images. Dependency compatibility issues may only surface during actual deployment.
- **Severity**: MEDIUM
- **Effort**: 16-24 hours
- **Fix**: Create a minimal container image based on RHOAI workbench base image and run notebook validation inside it.

## Quick Wins

### 1. Add Codecov Integration (2-3 hours)
Add coverage collection and reporting to the notebook-tests workflow:
```yaml
- name: Run validation tests
  run: |
    pytest tests/validation/ -v --tb=short \
      --cov=tests --cov-report=xml \
      --junit-xml=validation-results.xml

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
    fail_ci_if_error: true
```

### 2. Add Concurrency Control (30 minutes)
Add to both workflows to cancel stale runs:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 3. Create Missing example.yaml Files (4-6 hours)
Use the existing `examples/ray/data/rag/ray-data-pipeline/example.yaml` as a template. Each example needs at minimum: `title`, `description`, `status`, and `components.rhoai`.

### 4. Add CodeQL Python Scanning (1-2 hours)
```yaml
name: CodeQL
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
```

### 5. Create Basic CLAUDE.md (2-3 hours)
Add agent rules for test creation patterns, notebook standards, and pre-commit requirements.

## Detailed Findings

### CI/CD Pipeline

**Workflows Inventory**:
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `code-quality.yml` | PR + push to main + dispatch | Ruff linting/formatting, markdownlint, Gitleaks, Talisman |
| `notebook-tests.yml` | PR + push to main + dispatch | Validation tests + smoke tests with JUnit XML + step summary |

**Strengths**:
- Both workflows trigger on PRs, push to main, and manual dispatch
- Ruff version pinned (`0.14.4`) for consistency with pre-commit
- Test results uploaded as artifacts with 7-day retention
- GitHub step summary generated for test results
- Python pip caching enabled in notebook-tests workflow

**Gaps**:
- No concurrency control — stale runs waste resources
- No coverage collection or reporting in CI
- `continue-on-error: true` on test steps means failures may not block PRs effectively (though "Check test results" step partially addresses this)
- No matrix testing for multiple Python versions
- No dependency caching in code-quality workflow

### Test Coverage

**Test Infrastructure** (2,139 lines across 9 test files):

| Test Category | Files | Lines | What It Validates |
|--------------|-------|-------|-------------------|
| Notebook Structure | `test_notebook_structure.py` | 108 | JSON validity, nbformat schema, cell types, error detection |
| Notebook Content | `test_notebook_content.py` | 94 | Cleared execution counts, no stored outputs, no empty cells |
| Notebook Syntax | `test_notebook_syntax.py` | 185 | Import parseability, Python AST validity, shell command handling |
| Notebook Metadata | `test_notebook_metadata.py` | 171 | Kernelspec consistency, no env-specific metadata, required sections |
| Example Structure | `test_example_structure.py` | 344 | Required files, naming conventions, env var documentation |
| Example Metadata | `test_example_metadata.py` | 310 | YAML validity, required fields, schema validation, predefined values |
| PyProject Validation | `test_pyproject_toml.py` | 215 | TOML validity, required sections, dependency versions, venv build |
| Smoke Tests | `test_smoke.py` | 301 | Knowledge-tuning structure, imports, env vars, documentation |
| Utility Tests | `test_knowledge_utils.py` | 265 | Unit tests for knowledge_utils.py with mocked transformers |

**Strengths**:
- Parameterized discovery — validation tests auto-discover all notebooks and examples
- Well-structured conftest with session-scoped fixtures
- Test markers defined (`smoke`, `validation`, `slow`, `integration`)
- Mock strategy for heavy dependencies (transformers)
- Data contract validation in utility tests
- Comprehensive notebook structure/content/syntax checks

**Gaps**:
- Only 1 of 9 examples has smoke tests (knowledge-tuning)
- No notebook execution tests — validates syntax but never runs code
- No test-to-code ratio tracking
- Coverage configured in `pyproject.toml` but not used in CI
- `continue-on-error: true` weakens test gate enforcement

### Code Quality

**Linting**: Ruff (v0.14.4) with rules: `E` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear), `W` (warnings), `UP` (pyupgrade). Well-configured with sensible ignores and unfixable rules.

**Formatting**: Ruff format with Black-compatible settings (double quotes, 88-char lines, preview mode).

**Markdown**: markdownlint-cli with custom config (`.markdownlint.json`) — sensible rule adjustments.

**Pre-commit Hooks** (11+ hooks across 7 repos):
| Hook | Purpose |
|------|---------|
| `nbstripout` | Strip notebook outputs before commit |
| `ruff` (linter) | Python linting with auto-fix |
| `ruff-format` | Python formatting |
| `markdownlint` | Markdown quality |
| `gitleaks` | Secret scanning |
| `talisman-commit` | Secret scanning (additional) |
| `detect-secrets` | Secret scanning (with baseline) |
| `trailing-whitespace` | File hygiene |
| `end-of-file-fixer` | File hygiene |
| `check-yaml` | YAML validity |
| `check-added-large-files` | Prevent large files (>1MB) |
| `check-merge-conflict` | Prevent conflict markers |
| `detect-private-key` | Key detection |

**Assessment**: 9/10 — Exceptional pre-commit setup. Triple-layer secret scanning (Gitleaks + Talisman + detect-secrets) is gold-standard. nbstripout prevents notebook output pollution. Only missing static type checking (mypy/pyright).

### Container Images

- No Dockerfiles or Containerfiles exist in the repository
- No container build process
- No multi-architecture support
- No vulnerability scanning for container images
- No SBOM generation

**Context**: As an examples repository, containerization is less critical than for production services. However, testing examples inside RHOAI workbench-compatible containers would significantly improve confidence that examples work in the target environment.

### Security

**Strengths**:
- Triple secret scanning: Gitleaks (v8.29.0), Talisman (v1.37.0), detect-secrets (v1.5.0)
- `.gitleaks.toml` with sensible allowlist for base64 image data and hashes
- `.talismanrc` with per-file checksum allowlist
- `.secrets.baseline` for detect-secrets audit trail
- `detect-private-key` pre-commit hook
- `check-added-large-files` (1MB max) prevents accidental binary commits

**Gaps**:
- No SAST (CodeQL, Semgrep, Bandit)
- No dependency vulnerability scanning (Dependabot, Renovate, Safety)
- No Trivy/Snyk for package audit
- Talisman runs with `continue-on-error: true` in CI — failures are not blocking

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: All test types lack agent rules. No guidance for AI-generated tests, notebook standards, or pre-commit requirements.
- **Recommendation**: Generate rules with `/test-rules-generator` covering:
  - Validation test patterns (parameterized notebook discovery)
  - Smoke test patterns (per-example structure validation)
  - Utility function test patterns (with mocking strategies)
  - Notebook content standards (nbstripout compatibility, metadata requirements)

## Recommendations

### Priority 0 (Critical)

1. **Add notebook execution smoke tests** — Use `papermill` or `nbconvert --execute` to validate that notebooks run without errors in a minimal environment. Start with notebooks that don't require GPU/cluster:
   ```bash
   pip install papermill
   papermill notebook.ipynb output.ipynb --no-progress-bar
   ```

2. **Enforce coverage in CI** — Add `--cov` to pytest commands, upload to codecov, set minimum threshold (e.g., 60% for test code).

3. **Create example.yaml for all examples** — Only 1 of 9 examples has metadata. This undermines the metadata validation system.

### Priority 1 (High Value)

4. **Add SAST scanning** — CodeQL or Semgrep workflow for Python security analysis.

5. **Create agent rules** — `.claude/rules/` with patterns for validation tests, smoke tests, and utility function tests. Include mock patterns for heavy ML dependencies.

6. **Expand smoke tests** — Add `tests/examples/` directories for `model-serve-flow`, `fine-tuning`, and `ray` examples following the knowledge-tuning pattern.

7. **Fix continue-on-error weaknesses** — Talisman runs with `continue-on-error: true` in CI; consider making it blocking or adding a summary gate.

### Priority 2 (Nice-to-Have)

8. **Containerized testing** — Test notebooks inside RHOAI-compatible container images.

9. **Dependency vulnerability scanning** — Dependabot or Renovate for automated dependency updates and security alerts.

10. **Add mypy/pyright** — Static type checking for Python utility code.

11. **Matrix testing** — Test against Python 3.11 and 3.12 in CI.

12. **Notebook output regression testing** — For cells marked with `keep_output`, validate output doesn't regress.

## Comparison to Gold Standards

| Dimension | red-hat-ai-examples | odh-dashboard | notebooks | Best Practice |
|-----------|-------------------|---------------|-----------|---------------|
| Unit Tests | Validation + 1 smoke suite | Multi-layer with contracts | Image-level validation | Per-component unit + integration |
| Integration/E2E | None (structural only) | Cypress E2E | Multi-image E2E | Automated E2E on PR |
| Coverage | Configured, not enforced | Codecov with thresholds | Per-image tracking | Enforced with PR gates |
| Secret Scanning | Triple-layer (excellent) | Basic | Basic | Multi-tool (matching) |
| Pre-commit | 11+ hooks (excellent) | Standard set | Minimal | Comprehensive (matching) |
| Agent Rules | None | Comprehensive | Basic | Full test type coverage |
| SAST | None | CodeQL | None | CodeQL + language-specific |
| Container Testing | None | N/A (web app) | 5-layer validation | Runtime + security scan |

## File Paths Reference

### CI/CD
- `.github/workflows/code-quality.yml` — Linting, formatting, secret scanning
- `.github/workflows/notebook-tests.yml` — Validation and smoke tests

### Testing
- `tests/conftest.py` — Shared fixtures (repo_root, all_notebooks, all_pyproject_files)
- `tests/validation/` — 7 validation test files (structure, content, syntax, metadata, examples)
- `tests/examples/knowledge_tuning/` — Smoke tests + utility tests with mocks
- `pyproject.toml` — pytest config, markers, coverage settings

### Code Quality
- `.pre-commit-config.yaml` — 11+ hooks across 7 repos
- `ruff.toml` — Ruff linter/formatter configuration
- `.markdownlint.json` — Markdown linting rules

### Security
- `.gitleaks.toml` — Gitleaks secret scanning config
- `.talismanrc` — Talisman secret scanning config
- `.secrets.baseline` — detect-secrets baseline

### Documentation
- `TESTING.md` — Comprehensive testing documentation
- `CONTRIBUTING.md` — Development setup and quality standards
- `docs/METADATA_SCHEMA.md` — example.yaml schema specification
- `docs/EXAMPLE_STYLE_GUIDE.md` — File naming and structure standards
