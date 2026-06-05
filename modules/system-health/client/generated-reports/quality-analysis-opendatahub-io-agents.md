---
repository: "opendatahub-io/agents"
overall_score: 2.6
scorecard:
  - dimension: "Unit Tests"
    score: 4.0
    status: "rfe-dedup plugin has strong pytest coverage (2,783 lines), but rest of repo has zero tests"
  - dimension: "Integration/E2E"
    score: 0.5
    status: "No integration or E2E test infrastructure; example test files are manual scripts, not automated tests"
  - dimension: "Build Integration"
    score: 0.0
    status: "No CI/CD pipeline exists; no PR-time validation of any kind"
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfiles, no container builds, no image testing"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling (codecov, coveralls, etc.); no coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 0.0
    status: "No GitHub Actions workflows, no Makefile, no CI configuration whatsoever"
  - dimension: "Agent Rules"
    score: 6.0
    status: "CLAUDE.md and AGENTS.md exist with good project context, but no .claude/rules/ for test patterns"
critical_gaps:
  - title: "No CI/CD pipeline"
    impact: "No automated checks on PRs - broken code, regressions, and quality issues merge freely"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No automated test execution"
    impact: "2,783 lines of rfe-dedup tests exist but never run automatically; regressions go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No coverage tracking"
    impact: "Cannot measure or enforce test coverage; no visibility into untested code paths"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "Most code has zero tests"
    impact: "Benchmarking tools, examples, MCP tools have no tests; bugs ship silently"
    severity: "MEDIUM"
    effort: "16-24 hours"
  - title: "No linting or static analysis"
    impact: "Code quality inconsistencies, potential bugs, and style drift across contributors"
    severity: "MEDIUM"
    effort: "2-4 hours"
  - title: "No security scanning"
    impact: "Dependency vulnerabilities and secrets in code go undetected"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Add GitHub Actions workflow to run rfe-dedup pytest suite on PRs"
    effort: "1-2 hours"
    impact: "Immediately protects the most mature component from regressions"
  - title: "Add ruff linting to PR workflow"
    effort: "1-2 hours"
    impact: "Catches style issues and common bugs across all Python code"
  - title: "Add Dependabot or Renovate for dependency updates"
    effort: "30 minutes"
    impact: "Automated security patches for Python and Go dependencies"
  - title: "Add pre-commit hooks configuration"
    effort: "1-2 hours"
    impact: "Local quality checks before code reaches the repo"
recommendations:
  priority_0:
    - "Create a GitHub Actions CI pipeline with pytest for agent-plugins/tests/"
    - "Add ruff or flake8 linting for all Python files"
    - "Enable Dependabot for security vulnerability scanning"
  priority_1:
    - "Add codecov integration with coverage thresholds for rfe-dedup plugin"
    - "Add unit tests for benchmarking/significance-testing/ scripts"
    - "Create .claude/rules/ with test automation guidance for contributors"
    - "Add Go linting (golangci-lint) for example Go code"
  priority_2:
    - "Add notebook validation workflow (nbval or papermill) for Jupyter notebooks"
    - "Add JSON schema validation for mcp-discovery-configmap/schema.json"
    - "Add pre-commit hooks with ruff, mypy, and gitleaks"
    - "Create integration tests for MCP examples using mock servers"
---

# Quality Analysis: opendatahub-io/agents

## Executive Summary

- **Overall Score: 2.6/10**
- **Repository Type**: Experimental sandbox / examples repository
- **Primary Languages**: Python 3.13+ (primary), Go 1.24 (secondary)
- **Frameworks**: OpenAI SDK, LangChain/LangGraph, CrewAI, FastMCP, MLflow
- **Key Strengths**: Excellent AGENTS.md/CLAUDE.md documentation; rfe-dedup plugin has professional-grade unit tests
- **Critical Gaps**: Zero CI/CD pipeline, no automated test execution, no linting, no coverage tracking, no security scanning
- **Agent Rules Status**: Partial (CLAUDE.md and AGENTS.md exist with project context, but no `.claude/rules/` directory for test automation patterns)

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 4.0/10 | rfe-dedup plugin has 2,783 lines of pytest tests; rest of repo untested |
| Integration/E2E | 0.5/10 | No integration test infrastructure; 2 manual test scripts in examples |
| **Build Integration** | **0.0/10** | **No CI/CD pipeline exists at all** |
| Image Testing | 0.0/10 | No Dockerfiles or container builds (except docker-compose for MCP reporting) |
| Coverage Tracking | 0.0/10 | No coverage tooling, thresholds, or reporting |
| CI/CD Automation | 0.0/10 | No GitHub Actions, Makefile, or any CI configuration |
| Agent Rules | 6.0/10 | CLAUDE.md/AGENTS.md provide good project context; no .claude/rules/ |

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: No automated checks on pull requests. Broken code, regressions, dependency issues, and quality problems can merge freely without any gate.
- **Severity**: HIGH
- **Effort**: 4-8 hours to establish a basic pipeline
- **Details**: The repository has no `.github/workflows/` directory, no `Makefile`, no `.gitlab-ci.yml`, no `Jenkinsfile`. This is the most fundamental gap.

### 2. No Automated Test Execution
- **Impact**: The rfe-dedup plugin has 2,783 lines of well-written pytest tests across 11 test files, but they never run automatically. Regressions to this carefully tested code go completely undetected.
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: Tests exist at `agent-plugins/tests/rfe-dedup/` covering fetch, find, filter, form, merge, assemble, and more. These are professional-quality tests with fixtures, monkeypatching, and edge cases. They just need a CI trigger.

### 3. No Coverage Tracking
- **Impact**: Cannot measure test coverage, set thresholds, or enforce coverage on new contributions. Zero visibility into how much code is actually tested.
- **Severity**: HIGH
- **Effort**: 2-3 hours

### 4. Majority of Code Untested
- **Impact**: The benchmarking tools (`significance_test.py`, `bootstrap.py`, `bfcl_loader.py`), all MCP example code, and utility scripts have no tests whatsoever. Bugs in these components ship silently.
- **Severity**: MEDIUM
- **Effort**: 16-24 hours for meaningful coverage

### 5. No Linting or Static Analysis
- **Impact**: No ruff, flake8, mypy, pylint, or golangci-lint. Code quality inconsistencies and potential bugs go undetected.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours

### 6. No Security Scanning
- **Impact**: No Dependabot, Trivy, Snyk, CodeQL, or gitleaks. Dependency vulnerabilities and accidentally committed secrets go undetected.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours

## Quick Wins

### 1. Add GitHub Actions CI for rfe-dedup Tests (1-2 hours)
```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test-rfe-dedup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: |
          cd agent-plugins
          uv run --with pytest --with numpy pytest tests/rfe-dedup/ -v
```

### 2. Add Ruff Linting (1-2 hours)
```yaml
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
```

### 3. Enable Dependabot (30 minutes)
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "gomod"
    directory: "/examples/kubernetes-mcp"
    schedule:
      interval: "weekly"
```

### 4. Add Pre-commit Hooks (1-2 hours)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

## Detailed Findings

### CI/CD Pipeline

**Status**: Non-existent

The repository has absolutely no CI/CD configuration:
- No `.github/workflows/` directory
- No `Makefile` with test targets
- No `.gitlab-ci.yml` or `Jenkinsfile`
- No task runner (Taskfile, justfile, etc.)

This means:
- PRs merge without any automated validation
- Tests exist but never run automatically
- No build verification of any kind
- No automated linting or formatting checks

### Test Coverage

**Test Files Found**: 13 files total

| Component | Test Files | Test Lines | Source Lines | Ratio |
|-----------|-----------|------------|--------------|-------|
| rfe-dedup plugin | 11 (+ conftest.py) | 2,783 | 2,017 | 1.38:1 |
| langchain examples | 2 | ~130 | ~450 | 0.29:1 |
| benchmarking | 0 | 0 | ~600 | 0:1 |
| MCP examples | 0 | 0 | ~350 (Go) | 0:1 |
| tools | 0 | 0 | ~200 | 0:1 |

**rfe-dedup Tests (Strong)**:
- 11 test files covering all 11 scripts 1:1
- Uses pytest with fixtures, monkeypatching, tmp_path
- Tests edge cases: empty inputs, invalid JSON, path traversal, rate limiting
- Mocks heavy ML dependencies (faiss, sentence_transformers) with FakeIndex
- Good isolation using `monkeypatch.setattr` and `monkeypatch.setenv`

**langchain-langgraph Tests (Weak)**:
- `test_langchain_guardrails.py` and `test_langchain_mcp.py` are manual scripts, not pytest tests
- They use `if __name__ == '__main__'` entry points
- Require running infrastructure (Llama Stack, MCP servers, Ollama)
- No assertions - just print output and catch exceptions
- These are effectively demos, not tests

**Untested Components**:
- `benchmarking/significance-testing/` - statistical testing scripts (bootstrap, BFCL loader) with no tests
- All Go example code (5 files, ~350 lines)
- `tools/mcp-tester/test-mcp-server.py` - despite the name, this is a diagnostic tool, not a test
- All Jupyter notebooks (15 notebooks) - no notebook validation

### Code Quality

**Status**: No quality tooling configured

- No `.golangci.yaml` or `.golangci.yml`
- No `.eslintrc` or TypeScript config
- No `ruff.toml`, `.flake8`, `mypy.ini`, or `pylint` config
- No `.pre-commit-config.yaml`
- No `Makefile` with lint targets
- `.gitignore` is comprehensive (covers Python, JS, Go artifacts)
- `pyproject.toml` files exist per-example but have no `[tool.ruff]` or `[tool.pytest]` sections

### Container Images

**Status**: Not applicable (mostly)

- No `Dockerfile` or `Containerfile` in the repository
- One `docker-compose.yml` in `examples/mcp-project-reporting/` for running MCP servers
- The repo is primarily examples and tools, not a deployable service
- Llama Stack runs from pre-built images or venvs via `run.yaml`

### Security

**Status**: No security tooling

- No Dependabot or Renovate configuration
- No Trivy, Snyk, or vulnerability scanning
- No CodeQL or SAST analysis
- No gitleaks or secret detection
- No `.trivyignore` or security policy
- Dependencies are pinned in `pyproject.toml` (good practice) but never scanned
- API keys and tokens are loaded from environment variables (good practice)
- `fetch_rfes.py` validates HTTPS-only connections and sanitizes Jira keys with regex (good security hygiene)

### Agent Rules (Agentic Flow Quality)

**Status**: Partial

**Present**:
- `CLAUDE.md` - Points to AGENTS.md (1 line)
- `AGENTS.md` - Comprehensive 80-line document covering:
  - Repository purpose and architecture
  - Tech stack details (languages, frameworks, models)
  - Important files index
  - Common setup patterns with code examples
  - Coding conventions
  - Plugin development workflow
- `CONTRIBUTING.md` - Plugin development guide
- `adr/` directory with architectural decision records

**Missing**:
- No `.claude/` directory
- No `.claude/rules/` for test automation guidance
- No test creation rules (unit-tests.md, e2e-tests.md, etc.)
- No testing standards documentation
- No quality gates or checklists for contributions

**Quality Assessment**:
- AGENTS.md is well-structured and actionable - a model for project context
- Conventions section establishes clear patterns (OpenAI SDK, LangGraph state, uv packaging)
- Plugin development workflow is documented
- Missing: test expectations, quality bars, coverage requirements

## Recommendations

### Priority 0 (Critical)

1. **Create GitHub Actions CI pipeline** (4-8 hours)
   - Run rfe-dedup pytest suite on every PR
   - Add ruff linting for all Python files
   - Add Go build verification for example Go code
   - Block merge on test failure

2. **Enable Dependabot** (30 minutes)
   - Configure for pip and gomod ecosystems
   - Weekly security update checks
   - Cover all `pyproject.toml` and `go.mod` locations

3. **Add coverage tracking** (2-3 hours)
   - Generate coverage reports with pytest-cov
   - Integrate with codecov or coveralls
   - Set minimum threshold (e.g., 80% for rfe-dedup, informational for rest)

### Priority 1 (High Value)

4. **Add unit tests for benchmarking scripts** (8-12 hours)
   - `bootstrap.py` - test bootstrap resampling with known distributions
   - `bfcl_loader.py` - test file loading and result alignment
   - `significance_test.py` - test end-to-end with fixture data (example.json exists)

5. **Create `.claude/rules/` for test automation** (2-3 hours)
   - `unit-tests.md` - pytest patterns, fixture usage, monkeypatching
   - `plugin-tests.md` - patterns for testing Claude Code plugin scripts
   - `example-tests.md` - guidance for testable example code

6. **Add Go linting** (1-2 hours)
   - Add golangci-lint to CI for example Go code
   - Enforce `go vet` and `staticcheck`

7. **Add pre-commit hooks** (1-2 hours)
   - ruff (format + lint)
   - gitleaks (secret detection)
   - trailing whitespace, YAML validation

### Priority 2 (Nice-to-Have)

8. **Notebook validation** (4-6 hours)
   - Add nbval or papermill to validate Jupyter notebooks don't have syntax errors
   - Ensure notebooks have clean outputs or are properly cleared

9. **JSON schema validation** (1-2 hours)
   - Validate `mcp-discovery-configmap/schema.json` against JSON Schema meta-schema
   - Add schema validation to CI

10. **Integration test framework for MCP examples** (8-16 hours)
    - Create mock MCP servers for testing
    - Verify example scripts can initialize and handle tool calls
    - Test error handling paths

11. **Add SECURITY.md and security policy** (1-2 hours)
    - Define vulnerability reporting process
    - Document security practices (env var usage, HTTPS enforcement)

## Comparison to Gold Standards

| Practice | agents | odh-dashboard | notebooks | kserve |
|----------|--------|---------------|-----------|--------|
| CI/CD Pipeline | None | Multi-workflow | Comprehensive | Multi-workflow |
| Unit Tests | Partial (1 component) | Extensive | Moderate | Extensive |
| Integration Tests | None | Contract tests | Image testing | Multi-version |
| E2E Tests | None | Cypress suite | 5-layer validation | E2E suite |
| Coverage Tracking | None | Codecov + thresholds | Basic | Codecov + enforcement |
| Linting | None | ESLint + Prettier | Shell checks | golangci-lint |
| Security Scanning | None | Dependabot + Snyk | Trivy | CodeQL + Trivy |
| Pre-commit Hooks | None | Configured | N/A | Configured |
| Agent Rules | AGENTS.md only | Comprehensive rules | N/A | N/A |
| Container Testing | N/A | Build validation | 5-layer testing | Build + runtime |

**Gap to Gold Standard**: The repository is an experimental sandbox, so some gaps are expected. However, the rfe-dedup plugin is production-quality code that deserves production-quality CI/CD. The most critical gap is the complete absence of any CI pipeline - even a minimal workflow running the existing tests would be a massive improvement.

## File Paths Reference

### Key Configuration Files
- `CLAUDE.md` - Root agent context (points to AGENTS.md)
- `AGENTS.md` - Comprehensive project documentation for AI agents
- `CONTRIBUTING.md` - Plugin development guide
- `.gitignore` - Comprehensive Python/Go/JS ignore rules
- `adr/minimal-sdk.md` - Key architectural decision (Option 8: no custom SDK)

### Test Files
- `agent-plugins/tests/rfe-dedup/conftest.py` - Shared fixtures and FakeIndex
- `agent-plugins/tests/rfe-dedup/test_*.py` - 11 test modules (2,783 lines)
- `examples/langchain-langgraph/test_langchain_guardrails.py` - Manual test script
- `examples/langchain-langgraph/test_langchain_mcp.py` - Manual test script

### Source Code (rfe-dedup plugin)
- `agent-plugins/rfe-dedup/skills/rfe.dedup/scripts/*.py` - 11 scripts (2,017 lines)
- `agent-plugins/rfe-dedup/.claude-plugin/plugin.json` - Plugin manifest
- `agent-plugins/rfe-dedup/agents/` - Agent definitions (eval-pair, report-group)

### Examples
- `examples/langchain-langgraph/` - LangGraph multi-agent workflow
- `examples/ai_assistant_for_troubleshooting_apps/` - CrewAI multi-agent crew
- `examples/kubernetes-mcp/` - Kubernetes MCP client (Python + Go)
- `examples/github-mcp/` - GitHub MCP client (Python + Go)

### Benchmarking
- `benchmarking/significance-testing/significance_test.py` - BFCL comparison CLI
- `benchmarking/significance-testing/bootstrap.py` - Bootstrap resampling
- `benchmarking/significance-testing/bfcl_loader.py` - BFCL result loader

### Schema
- `mcp-discovery-configmap/schema.json` - MCP discovery ConfigMap schema
