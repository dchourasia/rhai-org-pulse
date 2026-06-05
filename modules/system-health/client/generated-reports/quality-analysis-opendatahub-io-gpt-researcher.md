---
repository: "opendatahub-io/gpt-researcher"
overall_score: 2.3
scorecard:
  - dimension: "Unit Tests"
    score: 3.0
    status: "Tests exist but most require external API keys; only 4 files use mocking for true isolation"
  - dimension: "Integration/E2E"
    score: 2.0
    status: "No automated E2E tests; docker-compose test profile is manual-only and references missing files"
  - dimension: "Build Integration"
    score: 1.5
    status: "No PR-triggered workflows; PR test workflow trigger is commented out; zero PR gates"
  - dimension: "Image Testing"
    score: 3.0
    status: "Multi-stage Dockerfiles with non-root user but no vulnerability scanning or runtime validation"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage generation, no codecov/coveralls integration, no thresholds"
  - dimension: "CI/CD Automation"
    score: 2.0
    status: "Only push-to-master build+deploy; PR test workflow commented out; no PR quality gates"
  - dimension: "Agent Rules"
    score: 4.0
    status: "Good .claude/SKILL.md development guide and .cursorrules but no test creation rules"
critical_gaps:
  - title: "PR test workflow is commented out — zero automated quality gates on PRs"
    impact: "Any code can be merged to master without running tests, linting, or type checks"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No code coverage tracking or enforcement"
    impact: "No visibility into test coverage; regressions go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Most tests require live API keys (OpenAI, Tavily)"
    impact: "Tests cannot run in CI without expensive API calls; no fast feedback loop"
    severity: "HIGH"
    effort: "12-20 hours"
  - title: "No Python linting or type checking in CI"
    impact: "Style inconsistencies, type errors, and code smells accumulate unchecked"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container vulnerability scanning"
    impact: "Vulnerable dependencies in production images go undetected"
    severity: "HIGH"
    effort: "2-3 hours"
  - title: "Zero frontend tests"
    impact: "Next.js UI regressions are invisible; no automated verification of frontend behavior"
    severity: "MEDIUM"
    effort: "16-24 hours"
quick_wins:
  - title: "Uncomment PR trigger on docker-build.yml and add basic pytest run"
    effort: "1-2 hours"
    impact: "Immediate automated testing on every PR"
  - title: "Add ruff linting + mypy type checking to a PR workflow"
    effort: "2-3 hours"
    impact: "Catch style issues and type errors before merge"
  - title: "Add Trivy container scanning to build workflow"
    effort: "1-2 hours"
    impact: "Automated vulnerability detection for Docker images"
  - title: "Add pytest-cov and codecov integration"
    effort: "2-3 hours"
    impact: "Coverage visibility and trend tracking on every PR"
  - title: "Separate unit tests from integration tests with pytest markers"
    effort: "2-4 hours"
    impact: "Fast CI with unit tests on PR; integration tests on schedule"
recommendations:
  priority_0:
    - "Enable PR-triggered test workflow — currently commented out in docker-build.yml"
    - "Add pytest-cov coverage generation and codecov integration with minimum threshold"
    - "Add ruff linting and mypy type checking as PR gates"
    - "Add Trivy container scanning to the build pipeline"
  priority_1:
    - "Refactor tests to separate true unit tests (mocked) from integration tests (API-dependent)"
    - "Add frontend testing framework (Jest + React Testing Library or Playwright)"
    - "Create .claude/rules/ with test creation guidelines for unit, integration, and E2E tests"
    - "Add pre-commit hooks for linting, formatting, and type checking"
  priority_2:
    - "Add SAST scanning (CodeQL or Semgrep) for security vulnerability detection"
    - "Add secret detection (gitleaks) to prevent credential leaks"
    - "Integrate hallucination eval suite into CI as a periodic job"
    - "Add image startup validation tests using Testcontainers"
---

# Quality Analysis: opendatahub-io/gpt-researcher

## Executive Summary

- **Overall Score: 2.3/10**
- **Repository Type**: Python AI research agent with Next.js frontend (fork of [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher))
- **Primary Languages**: Python (~15,772 LOC), TypeScript/JavaScript (frontend)
- **Framework**: FastAPI backend, Next.js frontend, LangChain/LangGraph AI orchestration

### Key Strengths
- Multi-stage Dockerfiles with non-root user and security-conscious design
- Dependabot configured for pip and Docker dependency updates
- Hallucination evaluation framework exists in `evals/` directory
- Comprehensive `.claude/SKILL.md` development guide with architecture documentation
- Security-focused test for path traversal vulnerability (`test_security_fix.py`)

### Critical Gaps
- **PR test workflow is commented out** — zero automated quality gates on pull requests
- **No code coverage** tracking, generation, or enforcement anywhere
- **Most tests require live API keys** — cannot run in standard CI
- **No Python linting or type checking** (no ruff, flake8, mypy, pylint in CI)
- **No container vulnerability scanning** (no Trivy, Snyk, or equivalent)
- **Zero frontend tests** — no Jest, Cypress, or Playwright

### Agent Rules Status: **Partial** — Development guide exists but no test creation rules

---

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 3/10 | Tests exist but most require API keys; only 4/18 files use mocking |
| Integration/E2E | 2/10 | No automated E2E; docker-compose test profile is manual-only |
| **Build Integration** | **1.5/10** | **No PR-triggered workflows; PR trigger commented out; zero gates** |
| Image Testing | 3/10 | Multi-stage Dockerfiles but no scanning or runtime validation |
| Coverage Tracking | 0/10 | No coverage generation, no codecov, no thresholds |
| CI/CD Automation | 2/10 | Only push-to-master build+deploy; no PR quality gates |
| Agent Rules | 4/10 | Good SKILL.md guide but no test creation rules |

---

## Critical Gaps

### 1. PR Test Workflow Completely Disabled
- **Impact**: Any code merges to master without automated testing
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: In `.github/workflows/docker-build.yml`, the PR trigger is explicitly commented out:
  ```yaml
  on:
    workflow_dispatch:  # Manual only
    # pull_request:    # COMMENTED OUT
    #   types: [opened, synchronize]
  ```
  This means PRs receive zero automated validation before merge.

### 2. No Code Coverage Tracking
- **Impact**: No visibility into test coverage; regressions are invisible
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: No `pytest-cov` in dependencies, no `.codecov.yml`, no coverage thresholds. The project has no way to measure or enforce test coverage.

### 3. Tests Require Live API Keys
- **Impact**: CI cannot run tests without expensive external API calls; no fast feedback
- **Severity**: HIGH
- **Effort**: 12-20 hours
- **Details**: Most test files import `GPTResearcher` and call `conduct_research()` which requires `OPENAI_API_KEY` and `TAVILY_API_KEY`. Only `test_quick_search.py`, `test_security_fix.py`, and `test_logging.py` use proper mocking for isolation.

### 4. No Python Linting or Type Checking
- **Impact**: Style inconsistencies and type errors accumulate unchecked
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No ruff, flake8, pylint, or mypy configuration. The `pyproject.toml` has dev dependencies for type stubs but no mypy config to use them. The project relies solely on developer discipline for code quality.

### 5. No Container Vulnerability Scanning
- **Impact**: Vulnerable dependencies in production images go undetected
- **Severity**: HIGH
- **Effort**: 2-3 hours
- **Details**: Despite multiple Dockerfiles and ECR push in CI, there is no Trivy, Snyk, or equivalent scanning. The Dependabot config helps with source dependencies but doesn't scan built container images.

### 6. Zero Frontend Tests
- **Impact**: UI regressions in the Next.js app are invisible
- **Severity**: MEDIUM
- **Effort**: 16-24 hours
- **Details**: The `frontend/nextjs` directory has no test files, no test framework in devDependencies (no Jest, Cypress, Playwright), and no test script in package.json. Only `lint` is available.

---

## Quick Wins

### 1. Enable PR Test Trigger (1-2 hours)
Uncomment the PR trigger in `docker-build.yml` and add a lightweight pytest step:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]" pytest pytest-asyncio
      - run: python -m pytest tests/test_security_fix.py tests/test_quick_search.py tests/test_logging.py -v
```

### 2. Add Ruff Linting + Mypy (2-3 hours)
Add to `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

### 3. Add Trivy Scanning (1-2 hours)
Add after the Docker build step in `build.yml`:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.login-ecr.outputs.registry }}/${{ steps.extract_short_name_repo.outputs.REPO_NAME }}:${{ steps.image-tag.outputs.tag }}
    format: 'sarif'
    severity: 'CRITICAL,HIGH'
```

### 4. Add Coverage Tracking (2-3 hours)
```bash
pip install pytest-cov
pytest --cov=gpt_researcher --cov-report=xml tests/
```
Then add `.codecov.yml` with a minimum threshold.

### 5. Separate Unit from Integration Tests (2-4 hours)
Add pytest markers:
```python
# conftest.py
import pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests requiring API keys")
```

---

## Detailed Findings

### CI/CD Pipeline

**Workflows Found**: 3
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `build.yml` | push to master | Build Docker image, push to ECR, trigger deploy |
| `deploy.yml` | push to master (terraform paths), workflow_dispatch | Terraform plan (PR) and apply (master) |
| `docker-build.yml` | workflow_dispatch only | Docker-compose test run (PR trigger commented out) |

**Key Issues**:
- **No PR quality gates**: The only workflow that runs tests (`docker-build.yml`) has its PR trigger commented out
- **No concurrency control**: Multiple pushes to master can trigger overlapping builds
- **No caching**: Python dependencies are installed fresh on every run
- **No test parallelization**: Tests run sequentially in a single docker-compose service
- **Build workflow pushes directly to ECR** without any test validation step
- The docker-compose test command references `tests/report-types.py` and `tests/vector-store.py` — neither follows the `test_*.py` naming convention from `pyproject.toml`

**Positive Aspects**:
- Dependabot configured for pip and Docker ecosystems (weekly)
- GitHub issue templates for bugs and features
- Terraform plan posted as PR comment (deploy.yml)

### Test Coverage

**Test Inventory**: 18 Python files in `tests/`, ~1,557 LOC
**Source Code**: 152 Python files, ~15,772 LOC
**Test-to-Code Ratio**: ~10% by LOC

| Test File | Type | Requires API Keys | Uses Mocking |
|-----------|------|-------------------|--------------|
| `test_security_fix.py` | Unit | No | Yes (mock FastAPI) |
| `test_quick_search.py` | Unit | No | Yes (AsyncMock) |
| `test_logging.py` | Unit | No | Yes (AsyncMock) |
| `test_logging_output.py` | Integration | Yes | Partial |
| `test_researcher_logging.py` | Integration | Yes | No |
| `test_logs.py` | Unit | No | No |
| `test_mcp.py` | Integration | Yes | No |
| `report-types.py` | Integration | Yes | Partial |
| `research_test.py` | Integration | Yes | No |
| `vector-store.py` | Integration | Yes | No |
| `documents-report-source.py` | Integration | Yes | No |
| `test-loaders.py` | Script | No | No |
| `test-openai-llm.py` | Script | Yes | No |
| `test-your-llm.py` | Script | Yes | No |
| `test-your-embeddings.py` | Script | Yes | No |
| `test-your-retriever.py` | Script | Yes | No |
| `gptr-logs-handler.py` | Script | Yes | No |

**Key Issues**:
- Only 3-4 files are true unit tests with proper mocking
- Many files in `tests/` are scripts, not pytest-compatible tests
- Inconsistent naming: mix of `test_*.py` (pytest-compatible) and `test-*.py` (not auto-discovered)
- No test markers to separate unit from integration tests
- No `conftest.py` with shared fixtures
- No coverage generation or reporting

**Evaluation Framework**:
- `evals/hallucination_eval/` — Hallucination detection eval using judges library
- `evals/simple_evals/` — SimpleQA factual accuracy benchmark
- These are valuable for research quality but not integrated into CI

### Code Quality

**Python**:
- No ruff, flake8, pylint, or mypy configuration
- Dev dependencies include type stubs (`types-aiofiles`, `types-beautifulsoup4`, etc.) but no mypy config
- `pyproject.toml` has pytest configuration with `asyncio_mode = "strict"`
- No `pre-commit-config.yaml`

**Frontend (Next.js)**:
- ESLint configured (`.eslintrc.json` with Next.js config)
- Prettier configured as devDependency
- TypeScript with strict mode (per `.cursorrules` guidance)
- No test framework installed

**Documentation**:
- `.cursorrules` — Comprehensive Cursor IDE project guidelines
- `CURSOR_RULES.md` — Extended rules documentation
- `CONTRIBUTING.md` — Generic contribution guide (no testing standards)
- `.claude/SKILL.md` — Comprehensive development guide with architecture, patterns, API reference

### Container Images

**Dockerfiles Found**: 5
| File | Purpose | Multi-stage | Non-root |
|------|---------|-------------|----------|
| `Dockerfile` | Backend API server | Yes (3 stages) | Yes |
| `Dockerfile.fullstack` | Full stack (backend + frontend) | Yes (4 stages) | No (runs as root via supervisord) |
| `backend/Dockerfile` | Backend only | Unknown | Unknown |
| `frontend/nextjs/Dockerfile` | Frontend production | Unknown | Unknown |
| `frontend/nextjs/Dockerfile.dev` | Frontend development | Unknown | Unknown |

**Positive Aspects**:
- Multi-stage builds reduce image size
- Main `Dockerfile` creates non-root user
- `.dockerignore` exists
- Multi-arch support via QEMU in docker-build.yml

**Issues**:
- `Dockerfile.fullstack` runs as root via supervisord
- No container vulnerability scanning
- No SBOM generation
- No image signing or attestation
- No runtime validation tests
- No healthcheck directives in Dockerfiles

### Security

| Practice | Status |
|----------|--------|
| Dependabot | Configured (pip + docker, weekly) |
| SAST/CodeQL | Not configured |
| Secret detection | Not configured |
| Container scanning | Not configured |
| Dependency scanning | Via Dependabot only |
| SBOM generation | Not configured |
| Image signing | Not configured |
| Path traversal protection | Yes (`test_security_fix.py`) |

### Agent Rules (Agentic Flow Quality)

- **Status**: Partial
- **`.claude/` directory**: Present with `SKILL.md` and `references/` subdirectory
- **SKILL.md Quality**: Excellent — comprehensive development guide covering architecture, patterns, config, API reference, and common gotchas
- **References**: 12+ detailed reference docs (architecture, components, flows, prompts, retrievers, MCP, etc.)
- **`.claude/rules/`**: Missing — no test creation rules
- **`.cursorrules`**: Present — project guidelines for Cursor IDE
- **`CURSOR_RULES.md`**: Present — extended Cursor rules documentation
- **CLAUDE.md**: Not present at root
- **AGENTS.md**: Not present

**Gaps**:
- No `.claude/rules/` directory with test creation guidelines
- No unit test pattern rules (mocking strategies, fixture management)
- No integration test rules (API key handling, test isolation)
- No E2E test rules
- SKILL.md is focused on development, not testing quality

**Recommendation**: Generate test creation rules with `/test-rules-generator` to establish consistent testing patterns for unit tests (mocked), integration tests (API-dependent), and frontend tests.

---

## Recommendations

### Priority 0 (Critical)

1. **Enable PR-triggered test workflow**
   - Uncomment PR trigger in `docker-build.yml`
   - Add a lightweight workflow that runs only true unit tests (no API keys needed)
   - Block merge until tests pass

2. **Add code coverage tracking**
   - Install `pytest-cov`
   - Configure codecov or coveralls integration
   - Set minimum coverage threshold (start at current level, ratchet up)

3. **Add Python linting and type checking**
   - Configure ruff for linting and formatting
   - Configure mypy for type checking (type stubs already in dev deps)
   - Add both as PR workflow steps

4. **Add container vulnerability scanning**
   - Integrate Trivy scanning after Docker build in `build.yml`
   - Set severity threshold (CRITICAL, HIGH)
   - Block deployment on critical vulnerabilities

### Priority 1 (High Value)

5. **Refactor test suite for CI compatibility**
   - Separate true unit tests from API-dependent integration tests using pytest markers
   - Add `conftest.py` with shared fixtures and markers
   - Create mock fixtures for GPTResearcher, Config, and LLM providers
   - Fix inconsistent file naming (`test-*.py` → `test_*.py`)

6. **Add frontend testing**
   - Install Jest + React Testing Library or Playwright
   - Start with critical UI component tests
   - Add to PR workflow

7. **Create `.claude/rules/` test guidelines**
   - Unit test rules with mocking patterns for LLM providers
   - Integration test rules with API key handling
   - Test naming and organization conventions

8. **Add pre-commit hooks**
   - Configure `.pre-commit-config.yaml` with ruff, mypy, trailing whitespace
   - Enforce on all commits

### Priority 2 (Nice-to-Have)

9. **Add SAST scanning**
   - Configure CodeQL or Semgrep for Python and JavaScript
   - Enable as GitHub Actions workflow

10. **Add secret detection**
    - Configure gitleaks or TruffleHog
    - Scan for API keys, tokens, and credentials in commits

11. **Integrate evaluation suite into CI**
    - Run hallucination eval as a periodic/nightly job
    - Track research quality metrics over time

12. **Add Docker healthchecks**
    - Add `HEALTHCHECK` directives to Dockerfiles
    - Add image startup validation tests

---

## Comparison to Gold Standards

| Dimension | gpt-researcher | odh-dashboard | notebooks | kserve |
|-----------|---------------|---------------|-----------|--------|
| PR Test Gates | None (commented out) | Multi-layer (unit, integration, E2E) | Automated per-image | Comprehensive |
| Unit Test Coverage | ~10% LOC, mostly API-dependent | >60%, well-isolated | N/A (image-focused) | >70% with mocks |
| Integration Tests | Manual docker-compose | Contract tests + API tests | 5-layer validation | Multi-version |
| Coverage Tracking | None | Codecov with enforcement | N/A | Codecov with thresholds |
| Container Scanning | None | Trivy integration | Multi-arch scanning | Trivy + Snyk |
| Python Linting | None | N/A (TypeScript) | Various | golangci-lint |
| Pre-commit Hooks | None | Configured | Configured | Configured |
| Agent Rules | SKILL.md (dev guide) | Comprehensive rules | Partial | N/A |
| Security Scanning | Dependabot only | CodeQL + Dependabot | Trivy + SBOM | CodeQL + Trivy |

---

## File Paths Reference

### CI/CD
- `.github/workflows/build.yml` — ECR build and deploy trigger
- `.github/workflows/deploy.yml` — Terraform infrastructure deployment
- `.github/workflows/docker-build.yml` — Docker-compose test runner (PR trigger disabled)
- `.github/dependabot.yml` — Dependency update automation

### Testing
- `tests/test_security_fix.py` — Security unit tests (mocked, no API keys)
- `tests/test_quick_search.py` — Quick search unit tests (mocked)
- `tests/test_logging.py` — Logging unit tests (mocked)
- `tests/test_mcp.py` — MCP integration test (requires API keys)
- `evals/hallucination_eval/` — Hallucination evaluation framework
- `evals/simple_evals/` — SimpleQA factual accuracy benchmark

### Configuration
- `pyproject.toml` — Python project config with pytest settings
- `frontend/nextjs/.eslintrc.json` — Frontend ESLint config
- `docker-compose.yml` — Multi-service Docker composition

### Container Images
- `Dockerfile` — Backend (3-stage, non-root)
- `Dockerfile.fullstack` — Full stack (4-stage, root)
- `frontend/nextjs/Dockerfile` — Frontend production
- `.dockerignore` — Docker build exclusions

### Agent Rules
- `.claude/SKILL.md` — Comprehensive development guide
- `.claude/references/` — 12+ architecture and API reference docs
- `.cursorrules` — Cursor IDE project guidelines
- `CURSOR_RULES.md` — Extended Cursor rules
