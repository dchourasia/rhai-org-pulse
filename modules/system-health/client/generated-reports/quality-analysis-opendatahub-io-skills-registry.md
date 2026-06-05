---
repository: "opendatahub-io/skills-registry"
overall_score: 3.0
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "No unit tests for 1,745 lines of Python across 7 scripts"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "CI sync checks serve as basic integration validation; eval dataset infrastructure exists"
  - dimension: "Build Integration"
    score: 7.0
    status: "CI validates schema and generated file sync, but no script-level testing"
  - dimension: "Image Testing"
    score: -1
    status: "N/A — repository does not build container images"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tool configured (no codecov, coveralls, or .coveragerc)"
  - dimension: "CI/CD Automation"
    score: 7.0
    status: "Well-structured workflows with pinned actions and sync validation, but no test/lint execution"
  - dimension: "Agent Rules"
    score: 7.0
    status: "Comprehensive CLAUDE.md, ARCHITECTURE.md, 2 skills; missing .claude/rules/"
critical_gaps:
  - title: "Zero test coverage for all Python scripts"
    impact: "Regressions in validate_registry.py, sync_marketplace.py, generate_catalog.py, generate_site.py, check_versions.py, sync_drawio_from_svg.py, and extract_diagram_feedback.py could silently ship broken logic"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No linting or static analysis configured"
    impact: "Code style inconsistencies, potential bugs, and security issues go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No dependency scanning or Dependabot/Renovate"
    impact: "Vulnerable dependencies (pyyaml, jsonschema, mkdocs) go unpatched"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No secret detection (gitleaks/trufflehog)"
    impact: "Accidental credential exposure in commits would go unnoticed"
    severity: "MEDIUM"
    effort: "1-2 hours"
quick_wins:
  - title: "Add ruff linting to CI"
    effort: "1-2 hours"
    impact: "Catch style issues, unused imports, and potential bugs across all 7 scripts"
  - title: "Enable Dependabot for pip dependencies"
    effort: "30 minutes"
    impact: "Automated security updates for pyyaml, jsonschema, mkdocs-material"
  - title: "Add pip dependency caching to validate.yml"
    effort: "30 minutes"
    impact: "Faster CI runs by caching pip installs"
  - title: "Add pytest with a few smoke tests for validate_registry.py"
    effort: "2-3 hours"
    impact: "Catch regressions in the most critical script (schema validation)"
recommendations:
  priority_0:
    - "Add unit tests for all Python scripts — especially validate_registry.py, sync_marketplace.py, and generate_site.py which are critical path"
    - "Configure ruff for linting and formatting; add to CI workflow"
  priority_1:
    - "Enable Dependabot for Python dependency scanning"
    - "Add mypy type checking (scripts already use Python 3.12 type hints like list[str] and dict[str, list])"
    - "Create .claude/rules/ with test patterns for future contributors"
  priority_2:
    - "Add pre-commit hooks for local development"
    - "Add CodeQL or Semgrep for static security analysis"
    - "Add gitleaks for secret detection"
---

# Quality Analysis: skills-registry

## Executive Summary

- **Overall Score: 3.0/10**
- **Repository Type**: Plugin marketplace / registry (Python scripts + YAML config)
- **Primary Language**: Python (7 scripts, 1,745 lines)
- **Key Strengths**: Excellent developer documentation (CLAUDE.md, ARCHITECTURE.md, CONTRIBUTING.md), well-designed CI sync validation, pinned action SHAs, clean single-source-of-truth architecture
- **Critical Gaps**: Zero test coverage, no linting, no dependency scanning, no code coverage tracking
- **Agent Rules Status**: Present (CLAUDE.md is strong) — missing `.claude/rules/`

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1/10 | No unit tests for any of the 7 Python scripts |
| Integration/E2E | 2/10 | CI sync checks provide basic integration validation |
| Build Integration | 7/10 | Schema validation and generated-file sync checks in CI |
| Image Testing | N/A | Repository does not build container images |
| Coverage Tracking | 0/10 | No coverage tool configured |
| CI/CD Automation | 7/10 | Good workflow structure, but no test/lint execution |
| Agent Rules | 7/10 | Strong CLAUDE.md, ARCHITECTURE.md; no `.claude/rules/` |

## Critical Gaps

### 1. Zero Test Coverage for All Python Scripts
- **Impact**: Regressions in core scripts could silently break the marketplace, catalog, site generation, and schema validation
- **Severity**: HIGH
- **Effort**: 8-16 hours
- **Details**: The repository has 7 Python scripts totaling 1,745 lines with zero test files. Key scripts at risk:
  - `validate_registry.py` (300 lines) — schema validation, duplicate detection, remote plugin validation
  - `generate_site.py` (750 lines) — the largest and most complex script, generates MkDocs pages
  - `sync_marketplace.py` (120 lines) — generates marketplace.json consumed by Claude Code
  - `generate_catalog.py` (184 lines) — generates human-readable catalog
  - `check_versions.py` (124 lines) — polls repos for version bumps
  - `sync_drawio_from_svg.py` (128 lines) — SVG/drawio sync with XML manipulation
  - `extract_diagram_feedback.py` (139 lines) — eval dataset extraction

### 2. No Linting or Static Analysis
- **Impact**: No automated code quality enforcement; style drift, unused imports, type errors go undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No `.flake8`, `ruff.toml`, `mypy.ini`, `.pylintrc`, or any linting config. The code already uses Python 3.12 features (type hints like `list[str]`, `dict[str, list]`, `str | None`) which would benefit from mypy verification.

### 3. No Dependency Scanning
- **Impact**: Known vulnerabilities in pyyaml, jsonschema, or mkdocs could go unpatched indefinitely
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No Dependabot configuration, no Renovate, no Snyk. Dependencies are manually pinned in CI (`pyyaml==6.0.3`, `jsonschema==4.26.0`) which is good for reproducibility but means no automated vulnerability alerts.

### 4. No Secret Detection
- **Impact**: Accidental credential exposure in commits would go unnoticed
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No gitleaks, trufflehog, or similar tool configured. While this repo primarily contains YAML/Python config, contributors could accidentally commit API tokens or credentials.

## Quick Wins

### 1. Add ruff Linting to CI (1-2 hours)
Catch style issues, unused imports, and potential bugs across all 7 scripts.

```yaml
# Add to .github/workflows/validate.yml
- name: Lint with ruff
  run: |
    pip install ruff
    ruff check scripts/
    ruff format --check scripts/
```

Create `ruff.toml`:
```toml
target-version = "py312"
line-length = 100

[lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM"]
```

### 2. Enable Dependabot (30 minutes)
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
```

### 3. Add pip Caching to CI (30 minutes)
```yaml
# In validate.yml, after setup-python
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

### 4. Add Smoke Tests for validate_registry.py (2-3 hours)
```python
# tests/test_validate_registry.py
import pytest
from scripts.validate_registry import (
    load_registry, validate_schema, check_duplicates,
    check_categories, check_strict_consistency,
)

@pytest.fixture
def sample_registry():
    return load_registry("registry.yaml")

@pytest.fixture
def schema():
    from scripts.validate_registry import load_schema
    return load_schema("schema/registry.schema.json")

def test_schema_valid(sample_registry, schema):
    errors = validate_schema(sample_registry, schema)
    assert errors == []

def test_no_duplicates(sample_registry):
    errors = check_duplicates(sample_registry)
    assert errors == []

def test_categories_valid(sample_registry):
    errors = check_categories(sample_registry)
    assert errors == []

def test_strict_consistency(sample_registry):
    errors = check_strict_consistency(sample_registry)
    assert errors == []
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory (4 workflows):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate.yml` | PR (paths), push to main | Schema validation + sync checks |
| `unicode-safety.yml` | All PRs | Hidden unicode character detection |
| `diagram-pr.yml` | PRs modifying SVGs | SVG→drawio sync + eval dataset extraction |
| `deploy-site.yml` | Push to main, manual | MkDocs build + GitHub Pages deployment |

**Strengths:**
- All GitHub Actions pinned to exact commit SHAs (e.g., `actions/checkout@34e114876b...`)
- Path-based trigger filtering (only runs on relevant file changes)
- Concurrency control on deploy-site with `cancel-in-progress: false`
- Minimal permissions (contents: read for most workflows)
- Sync-check pattern: regenerate → `git diff --exit-code` catches drift

**Gaps:**
- No pip dependency caching (installs from scratch each run)
- No linting step in any workflow
- No test execution step
- No matrix testing across Python versions
- `diagram-pr.yml` has `contents: write` and pushes commits — no branch protection enforcement visible

### Test Coverage

**Current State: Zero test files.**

The repository has 7 Python scripts (1,745 lines total) with no corresponding test files. No `tests/` directory, no `*_test.py` files, no `pytest.ini`, no `conftest.py`.

**What passes for testing:**
- `validate_registry.py` running in CI validates the registry against a JSON Schema — this is effectively a data validation test, not a code test
- CI sync checks verify generated files match source of truth — a form of integration check
- `eval/diagram-feedback/eval.yaml` exists for testing the diagram-layout skill — this tests an external skill, not this repository's code

**Test-to-code ratio**: 0:1,745 (0%)

**Scripts that most need tests:**
1. `generate_site.py` (750 lines) — complex template logic, scope handling, enrichment merging
2. `validate_registry.py` (300 lines) — 6 validation functions that need unit tests
3. `sync_marketplace.py` (120 lines) — field mapping logic
4. `sync_drawio_from_svg.py` (128 lines) — XML parsing and compression handling

### Code Quality

**No quality tools configured.**

| Tool | Status |
|------|--------|
| Linter (ruff/flake8/pylint) | Not configured |
| Formatter (black/ruff format) | Not configured |
| Type checker (mypy/pyright) | Not configured |
| Pre-commit hooks | Not configured |
| Import sorter (isort/ruff) | Not configured |

**Observations:**
- Code is generally clean and well-structured despite no tooling
- Consistent style across scripts (docstrings, argparse usage, clean function boundaries)
- Uses Python 3.12 type hints (`list[str]`, `dict[str, list]`, `str | None`) but no type checker validates them
- No `pyproject.toml` or `setup.cfg` for project metadata

### Container Images

**N/A** — This repository does not build container images. It is a metadata registry that references external repositories.

### Security

| Practice | Status |
|----------|--------|
| Unicode safety check | Present (unicode-safety.yml) |
| Action SHA pinning | Present (all actions pinned) |
| Minimal permissions | Present (contents: read for most) |
| Secret detection | Missing |
| SAST/CodeQL | Missing |
| Dependency scanning | Missing (no Dependabot/Renovate) |
| Vulnerability scanning | Missing |

**Positive:** The repo demonstrates good supply chain security practices for GitHub Actions (SHA pinning, minimal permissions). The unicode safety check is a nice touch for a registry that processes user-submitted YAML.

**Gaps:** No automated secret detection, no static analysis, and no dependency vulnerability monitoring.

### Agent Rules (Agentic Flow Quality)

**Status: Present and strong at the documentation level**

| Component | Status | Quality |
|-----------|--------|---------|
| `CLAUDE.md` | Present | Comprehensive — covers commands, architecture, key rules, common pitfalls |
| `ARCHITECTURE.md` | Present | Excellent — ASCII diagrams, data flow, CI pipeline, plugin model |
| `CONTRIBUTING.md` | Present | Detailed step-by-step guide with strict/non-strict examples |
| `.claude-plugin/plugin.json` | Present | Minimal but functional |
| `skills/` (2 skills) | Present | Detailed SKILL.md files with multi-step instructions |
| `.claude/rules/` | Missing | No test automation guidance for AI agents |

**Strengths:**
- CLAUDE.md includes the critical "before committing, run all four generators" rule
- Architecture documentation uses clear ASCII diagrams
- Two well-documented skills (generate-site, analyze-plugin) with comprehensive instructions
- CONTRIBUTING.md covers both strict and non-strict plugin modes

**Gaps:**
- No `.claude/rules/` directory for test patterns
- No guidance on how AI agents should write tests for this repo's scripts
- No linting/formatting rules for AI-generated code

**Recommendation**: Generate test automation rules with `/test-rules-generator` once tests are added.

## Recommendations

### Priority 0 (Critical)

1. **Add pytest-based unit tests for all Python scripts**
   - Start with `validate_registry.py` (most critical — gatekeeps all PRs)
   - Add tests for `sync_marketplace.py` (field mapping correctness)
   - Add tests for `generate_site.py` (template rendering, scope handling)
   - Target: 80%+ coverage on core validation/generation functions
   - Effort: 8-16 hours

2. **Configure ruff for linting and formatting**
   - Add `ruff.toml` with reasonable defaults
   - Add ruff check + format steps to `validate.yml`
   - Effort: 2-4 hours

### Priority 1 (High Value)

3. **Enable Dependabot for pip + GitHub Actions**
   - Automated vulnerability alerts for dependencies
   - Automated PR creation for action updates
   - Effort: 30 minutes

4. **Add mypy type checking**
   - Scripts already use modern type hints — validate them
   - Create `mypy.ini` or `[tool.mypy]` in `pyproject.toml`
   - Add to CI workflow
   - Effort: 2-3 hours

5. **Create `.claude/rules/` for test automation guidance**
   - Document pytest patterns for registry validation
   - Provide fixture examples for registry data
   - Effort: 2-3 hours

### Priority 2 (Nice-to-Have)

6. **Add pre-commit hooks**
   - ruff (lint + format), mypy, trailing whitespace, YAML validation
   - Effort: 1-2 hours

7. **Add CodeQL or Semgrep for static security analysis**
   - Catch SQL injection-like patterns in YAML/JSON handling
   - Effort: 1-2 hours

8. **Add gitleaks for secret detection**
   - Prevent accidental credential commits
   - Effort: 1 hour

9. **Add a `pyproject.toml` for project metadata**
   - Consolidate tool configuration (ruff, mypy, pytest)
   - Define project dependencies properly
   - Effort: 1 hour

## Comparison to Gold Standards

| Dimension | skills-registry | odh-dashboard | notebooks | kserve |
|-----------|----------------|---------------|-----------|--------|
| Unit Tests | None | Comprehensive Jest suite | Shell-based validation | Go unit tests with coverage |
| Integration | CI sync checks only | Cypress E2E, contract tests | Multi-layer image testing | envtest, multi-version |
| Coverage Tracking | None | Codecov with enforcement | N/A | Coverage thresholds |
| Linting | None | ESLint + Prettier | ShellCheck | golangci-lint (30+ linters) |
| Pre-commit | None | Present | Present | Present |
| Security Scanning | Unicode check only | Snyk, CodeQL | Trivy | CodeQL, gosec |
| Agent Rules | Strong CLAUDE.md | Comprehensive rules | Limited | N/A |
| CI Quality | Good structure, no testing | Multi-stage with testing | Comprehensive | Comprehensive |

## File Paths Reference

### CI/CD
- `.github/workflows/validate.yml` — Main CI: schema validation + sync checks
- `.github/workflows/unicode-safety.yml` — Unicode character detection
- `.github/workflows/diagram-pr.yml` — SVG/drawio sync automation
- `.github/workflows/deploy-site.yml` — MkDocs site deployment

### Scripts (Core Code)
- `scripts/validate_registry.py` (300 lines) — Schema validation, duplicate/category/strict checks
- `scripts/generate_site.py` (750 lines) — MkDocs page generation with enrichment
- `scripts/generate_catalog.py` (184 lines) — Human-readable catalog generation
- `scripts/sync_marketplace.py` (120 lines) — marketplace.json generation
- `scripts/check_versions.py` (124 lines) — Remote version polling
- `scripts/sync_drawio_from_svg.py` (128 lines) — SVG→drawio XML extraction
- `scripts/extract_diagram_feedback.py` (139 lines) — Eval dataset case extraction

### Configuration
- `registry.yaml` — Single source of truth (12 plugins, ~600 lines)
- `schema/registry.schema.json` — JSON Schema for registry validation
- `.claude-plugin/marketplace.json` — Generated Claude Code marketplace format

### Documentation
- `CLAUDE.md` — AI agent guidance
- `ARCHITECTURE.md` — System design documentation
- `CONTRIBUTING.md` — Contributor guide
- `README.md` — Project overview

### Skills
- `skills/generate-site/SKILL.md` — Site generation orchestration skill
- `skills/analyze-plugin/SKILL.md` — Plugin analysis and enrichment skill

### Eval
- `eval/diagram-feedback/eval.yaml` — Diagram layout evaluation configuration
