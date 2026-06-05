---
repository: "opendatahub-io/rhai-wiki"
overall_score: 3.2
scorecard:
  - dimension: "Unit Tests"
    score: 7.0
    status: "Well-structured pytest suite with 9 test files, 3,520 lines; 3 tests currently failing"
  - dimension: "Integration/E2E"
    score: 5.0
    status: "Good integration and contract tests but no E2E; limited scenario coverage"
  - dimension: "Build Integration"
    score: 0.0
    status: "No CI/CD pipeline, no automated build or test triggers"
  - dimension: "Image Testing"
    score: 0.0
    status: "N/A — not a container-based project (Python CLI/library, stdlib only)"
  - dimension: "Coverage Tracking"
    score: 1.0
    status: "No coverage tool; mypy strict is the only automated quality gate"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "No CI/CD whatsoever — tests exist but only run manually via uv run pytest"
  - dimension: "Agent Rules"
    score: 6.0
    status: "Extensive custom skills (16+) and speckit specs, but no .claude/rules/ for test patterns"
critical_gaps:
  - title: "No CI/CD pipeline exists"
    impact: "Tests, linting, and type checking never run automatically — regressions can merge undetected"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No code coverage tracking"
    impact: "No visibility into which code paths are tested; coverage regressions invisible"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No linter configured (ruff, flake8, pylint)"
    impact: "Code style inconsistencies and common Python pitfalls not caught"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "3 unit tests currently failing"
    impact: "Broken tests erode confidence in the suite; may mask real regressions"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No security scanning (dependency, secret, SAST)"
    impact: "Vulnerabilities in dev dependencies or leaked secrets not detected"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add a GitHub Actions CI workflow for pytest + mypy"
    effort: "2-3 hours"
    impact: "Automated quality gate on every PR — catches regressions before merge"
  - title: "Add ruff for linting and formatting"
    effort: "1 hour"
    impact: "Fast Python linter/formatter that replaces flake8+isort+black in one tool"
  - title: "Add pytest-cov and codecov integration"
    effort: "1-2 hours"
    impact: "Visibility into test coverage with PR annotations"
  - title: "Fix the 3 failing tests in test_query_standalone.py"
    effort: "30 minutes"
    impact: "Clean test suite baseline; builds trust in automated gates"
  - title: "Create .claude/rules/ for test patterns"
    effort: "2-3 hours"
    impact: "Consistent AI-generated tests following project conventions"
recommendations:
  priority_0:
    - "Create a GitHub Actions workflow that runs pytest, mypy --strict, and a linter on every PR"
    - "Fix the 3 failing tests in test_query_standalone.py to establish a green baseline"
    - "Add pytest-cov and enforce a coverage floor (start at current level, ratchet up)"
  priority_1:
    - "Add ruff to pyproject.toml for linting and auto-formatting"
    - "Create .claude/rules/ with unit-test and integration-test patterns specific to this project"
    - "Add pre-commit hooks for ruff, mypy, and test execution"
    - "Add tests for untested modules (cli/main.py, wiki/generator.py, wiki/index.py, pipeline/output.py)"
  priority_2:
    - "Add secret detection with gitleaks or trufflehog"
    - "Add dependency vulnerability scanning (pip-audit, safety)"
    - "Add E2E tests that run a full pipeline cycle with fixture data"
    - "Consider property-based testing (Hypothesis) for data models with hash-based identity"
---

# Quality Analysis: rhai-wiki

## Executive Summary

- **Overall Score: 3.2/10**
- **Repository Type**: Python CLI + agentic knowledge pipeline (compile knowledge from Jira, GitHub, Confluence, Google Sheets into a persistent wiki)
- **Language**: Python 3.12+ (stdlib only, zero third-party runtime dependencies)
- **Key Strengths**: Well-designed test suite with unit/integration/contract layers; strong type safety with `mypy --strict`; extensive Claude Code skills ecosystem; thorough speckit specifications
- **Critical Gaps**: **Zero CI/CD** — no GitHub Actions, no GitLab CI, no Makefile. Tests exist but only run manually. No linting, no coverage tracking, no security scanning.
- **Agent Rules Status**: Partial — extensive skills present, but no `.claude/rules/` for test creation patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 7.0/10 | Well-structured pytest suite (9 files, 3,520 lines), good patterns — but 3 tests failing |
| Integration/E2E | 5.0/10 | Integration + contract tests present; no E2E tests; limited scenario coverage |
| **Build Integration** | **0.0/10** | **No CI/CD pipeline of any kind — tests never run automatically** |
| Image Testing | N/A | Not a container-based project (Python CLI with stdlib-only deps) |
| Coverage Tracking | 1.0/10 | No coverage tool; mypy strict mode is the only automated quality signal |
| CI/CD Automation | 1.0/10 | No workflows — tests, linting, and type checking run only manually |
| Agent Rules | 6.0/10 | Extensive skills (16+) and speckit specs; no test creation rules |

## Critical Gaps

### 1. No CI/CD Pipeline Exists
- **Impact**: Tests, linting, and type checking never run automatically. Regressions can merge undetected.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The repository has zero CI configuration — no `.github/workflows/`, no `.gitlab-ci.yml`, no `Makefile`, no `Jenkinsfile`. The only CI-adjacent tooling is `.specify/workflows/` which is a project management tool (speckit), not test automation.

### 2. No Code Coverage Tracking
- **Impact**: No visibility into which code paths are tested. Coverage regressions are invisible.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No `.coveragerc`, no `codecov.yml`, no `pytest-cov` in dependencies. The project has 37 source files and 12 test files, but there's no way to know what percentage of code is actually exercised.

### 3. No Linter Configured
- **Impact**: Code style inconsistencies and common Python pitfalls not caught automatically.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: No `ruff.toml`, no `.flake8`, no `pylint` configuration. The project uses `mypy --strict` for type checking, which is excellent, but doesn't catch style issues, unused imports, or dead code.

### 4. Three Unit Tests Currently Failing
- **Impact**: Broken tests erode confidence in the suite. Without CI, these may have been broken for some time without anyone noticing.
- **Severity**: MEDIUM
- **Effort**: 1-2 hours
- **Details**: `tests/unit/test_query_standalone.py` has 3 failures — the query script appears to have been refactored without updating the tests. Specifically:
  - `test_no_non_stdlib_imports` — references path changed
  - `test_uses_relative_references_path` — assertion doesn't match current code
  - `test_all_modes_run_without_error_in_isolation` — CLI argument parsing changed

### 5. No Security Scanning
- **Impact**: Vulnerabilities in dev dependencies or leaked secrets not detected.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: No gitleaks, no trivy, no pip-audit, no CodeQL, no Semgrep. The project has zero runtime dependencies (stdlib only), which mitigates supply chain risk significantly, but dev dependencies (pytest, mypy) are unscanned.

## Quick Wins

### 1. Add GitHub Actions CI Workflow (2-3 hours)
Create `.github/workflows/ci.yml` to run on PRs:

```yaml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest --tb=short
      - run: uv run mypy --strict src/
```

### 2. Add ruff for Linting and Formatting (1 hour)
Add to `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "TCH"]

[dependency-groups]
dev = ["pytest", "mypy", "ruff"]
```

### 3. Add pytest-cov and Coverage Tracking (1-2 hours)
```toml
[dependency-groups]
dev = ["pytest", "pytest-cov", "mypy"]
```

```yaml
# In CI workflow
- run: uv run pytest --cov=src --cov-report=xml
- uses: codecov/codecov-action@v4
```

### 4. Fix Failing Tests (30 minutes)
The 3 failures in `test_query_standalone.py` are due to the query script being refactored. Update the tests to match the current CLI interface and path structure.

### 5. Create .claude/rules/ for Test Patterns (2-3 hours)
Create rules that capture the project's testing conventions:
- Use `from __future__ import annotations` in all test files
- Organize tests in classes with descriptive names
- Use `tmp_path` fixture for file system tests
- Mock external tools with `unittest.mock.patch`
- Follow the existing contract test pattern for new adapters

## Detailed Findings

### CI/CD Pipeline
**Status: Non-existent**

There is no CI/CD infrastructure in this repository. The `.specify/` directory contains speckit project management workflows, not CI automation. No test, lint, type-check, or build steps run on PRs or pushes.

| Aspect | Status |
|--------|--------|
| PR-triggered tests | None |
| Periodic test runs | None |
| Lint automation | None |
| Type check automation | None |
| Build automation | None |
| Concurrency control | N/A |
| Caching strategy | N/A |

### Test Coverage

**Test Inventory:**

| Category | Files | Lines | Key Coverage |
|----------|-------|-------|-------------|
| Unit | 9 | 3,520 | Models, pipeline, schema, adapters, catalog aliases/extract/store/synthesize |
| Integration | 2 | 273 | Contradiction pipeline end-to-end, source addition lifecycle |
| Contract | 1 | 141 | Adapter interface contract (all 10 adapter types) |
| **Total** | **12** | **4,639** | **Test-to-code ratio: 0.69** |

**Test Quality Assessment:**
- Well-structured class-based organization (`TestClaim`, `TestContradiction`, etc.)
- Good use of pytest fixtures and parametrization (`@pytest.fixture(params=...)`)
- Appropriate mocking with `unittest.mock.patch` for external dependencies
- Contract tests verify all adapter implementations satisfy the `SourceAdapter` ABC
- Integration tests cover realistic multi-step scenarios (source → ingest → validate)
- Edge case coverage: empty inputs, invalid values, missing files, boundary conditions

**Notable Untested Modules:**

| Module | Lines | Why It Matters |
|--------|-------|---------------|
| `src/cli/main.py` | 484 | CLI entry point — untested argument parsing and dispatch |
| `src/wiki/generator.py` | 957 | Largest file in the project — wiki page generation logic |
| `src/wiki/index.py` | 413 | Wiki index generation |
| `src/pipeline/output.py` | 377 | Output persistence and report generation (partially tested via integration) |
| `src/adapters/github.py` | 264 | GitHub adapter (contract-tested but no unit tests for fetch logic) |

### Code Quality

| Tool | Status | Details |
|------|--------|---------|
| mypy --strict | Enabled | Full strict mode in `pyproject.toml` — strong type safety |
| Linter | None | No ruff, flake8, or pylint configured |
| Formatter | None | No black, ruff format, or yapf |
| Pre-commit | None | No `.pre-commit-config.yaml` |
| isort | None | Import sorting not enforced |

**Positive Observations:**
- All source files use `from __future__ import annotations` for modern type hint syntax
- Consistent dataclass-based models with `field(default_factory=...)` for mutable defaults
- Clean module separation (adapters, models, pipeline, schema, wiki, lib)
- No third-party runtime dependencies — pure stdlib

### Container Images
**N/A** — This is a Python CLI tool that runs locally. No Dockerfile, no container builds, no image testing applicable.

### Security

| Practice | Status |
|----------|--------|
| Secret detection | None |
| Dependency scanning | None |
| SAST / CodeQL | None |
| Vulnerability scanning | None |
| SBOM generation | None |

**Mitigating factors**: The project has zero runtime dependencies (stdlib only), which eliminates supply chain risk for the production code. Dev dependencies (pytest, mypy) are minimal and well-known.

### Agent Rules (Agentic Flow Quality)

**Status**: Partial — extensive skills, no test rules

**CLAUDE.md**: Present with basic configuration (tool runner instructions, speckit plan reference). Minimal but functional.

**Skills Ecosystem** (`.claude/skills/`):
- **Wiki operations**: 7 skills (wiki-ingest, wiki-extract, wiki-contradict, wiki-synthesize, wiki-commit, wiki-add-source, wiki-cycle)
- **Catalog query**: 1 skill (software-catalog-query) with extensive reference data
- **Speckit integration**: 9 skills (speckit-analyze, speckit-plan, speckit-implement, speckit-tasks, etc.)
- **Quality**: Skills are well-documented with clear steps, input/output descriptions, and error handling

**Speckit Specifications** (`specs/`):
- 5 feature specifications with full structure (spec, plan, tasks, checklists, contracts, research, data model)
- Contract definitions for adapter interfaces, pipeline stages, and skills
- Requirement checklists with acceptance criteria

**Gaps**:
- No `.claude/rules/` directory for test creation patterns
- No rules for code style, review, or quality gates
- No guidance on when to write unit vs. integration vs. contract tests
- **Recommendation**: Generate rules with `/test-rules-generator` to capture the project's testing conventions

## Recommendations

### Priority 0 (Critical)
1. **Create a GitHub Actions CI workflow** — Run `pytest`, `mypy --strict`, and a linter on every PR. This is the single highest-impact improvement. Without CI, the test suite is decorative.
2. **Fix the 3 failing tests** — Establish a green baseline before enabling CI. The failures in `test_query_standalone.py` appear to be test rot from a refactor.
3. **Add coverage tracking** — Install `pytest-cov`, generate XML reports, integrate with Codecov. Set the initial threshold at the current level and ratchet up.

### Priority 1 (High Value)
4. **Add ruff for linting and formatting** — Single tool replaces flake8 + isort + black. Configure in `pyproject.toml` and add to CI.
5. **Create `.claude/rules/` with test patterns** — Document the project's testing conventions so AI agents produce consistent tests. Include patterns for:
   - Unit tests (class-based, fixtures, edge cases)
   - Integration tests (multi-step pipelines, `tmp_path`)
   - Contract tests (parametrized adapter validation)
   - Mocking patterns (patching subprocess calls, external tools)
6. **Add pre-commit hooks** — Enforce ruff, mypy, and basic formatting locally before push.
7. **Write tests for untested modules** — Prioritize `cli/main.py` (484 lines, untested CLI), `wiki/generator.py` (957 lines, largest file), and `wiki/index.py` (413 lines).

### Priority 2 (Nice-to-Have)
8. **Add secret detection** — Configure gitleaks in CI to catch accidental credential commits.
9. **Add dependency scanning** — Run `pip-audit` in CI against dev dependencies.
10. **Add E2E tests** — Create a full pipeline cycle test with fixture data (ingest → extract → contradict → synthesize → validate wiki output).
11. **Consider property-based testing** — The hash-based identity system in `Claim` and `Contradiction` models would benefit from Hypothesis-based property tests.

## Comparison to Gold Standards

| Dimension | rhai-wiki | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | Good (7/10) | Excellent (9/10) | Good (7/10) | Excellent (9/10) |
| Integration/E2E | Moderate (5/10) | Excellent (9/10) | Good (7/10) | Excellent (9/10) |
| CI/CD | **None (0/10)** | Excellent (9/10) | Excellent (9/10) | Excellent (9/10) |
| Coverage | **None (0/10)** | Strong (8/10) | Moderate (6/10) | Strong (8/10) |
| Linting | Partial (3/10) | Strong (8/10) | Moderate (6/10) | Strong (8/10) |
| Security | **None (0/10)** | Moderate (6/10) | Moderate (6/10) | Strong (8/10) |
| Agent Rules | Moderate (6/10) | Strong (8/10) | Low (2/10) | Low (2/10) |
| **Overall** | **3.2/10** | **8.5/10** | **6.5/10** | **8.0/10** |

### Key Differentiators

**rhai-wiki's strength** is its agentic design — the extensive skills ecosystem and speckit specifications represent a mature approach to AI-assisted development. The test quality (when tests exist) is on par with gold standards.

**The critical weakness** is zero CI/CD automation. All gold standard projects have multi-stage CI pipelines. rhai-wiki's tests are essentially a local-only safety net that depends on developers remembering to run them.

## File Paths Reference

| Category | Path | Status |
|----------|------|--------|
| Project Config | `pyproject.toml` | mypy strict, pytest + mypy dev deps |
| Agent Rules | `CLAUDE.md` | Basic tool runner instructions |
| Agent Skills | `.claude/skills/` (16+ skills) | Extensive, well-documented |
| Agent Test Rules | `.claude/rules/` | **Missing** |
| CI/CD | `.github/workflows/` | **Missing** |
| Pre-commit | `.pre-commit-config.yaml` | **Missing** |
| Coverage | `.coveragerc` or `codecov.yml` | **Missing** |
| Linting | `ruff.toml` or `.flake8` | **Missing** |
| Security | `.gitleaks.toml` or `.trivyignore` | **Missing** |
| Unit Tests | `tests/unit/` (9 files) | Present, 3 failing |
| Integration Tests | `tests/integration/` (2 files) | Present, passing |
| Contract Tests | `tests/contract/` (1 file) | Present, passing |
| Source Code | `src/` (37 files, 6,678 lines) | Well-structured |
| Specifications | `specs/` (5 features) | Comprehensive |
| Ingestion Config | `ingestion-config.json` | 8 sources configured |
