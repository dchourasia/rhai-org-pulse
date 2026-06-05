---
repository: "red-hat-data-services/agentic-starter-kits"
overall_score: 7.4
scorecard:
  - dimension: "Unit Tests"
    score: 6.5
    status: "Good tool-level unit tests per agent; no coverage tracking or enforcement"
  - dimension: "Integration/E2E"
    score: 8.5
    status: "Excellent behavioral test suite with adversarial, API contract, and deployment integration tests"
  - dimension: "Build Integration"
    score: 5.0
    status: "No PR-time container build validation; nightly-only deployment tests"
  - dimension: "Image Testing"
    score: 5.5
    status: "UBI9 base, non-root, .dockerignore present but no image scanning or runtime validation on PRs"
  - dimension: "Coverage Tracking"
    score: 2.0
    status: "No codecov, no coverage thresholds, no coverage reporting"
  - dimension: "CI/CD Automation"
    score: 8.0
    status: "Well-organized workflows with concurrency control, change detection, test reporting, and nightly deployment tests"
  - dimension: "Agent Rules"
    score: 7.0
    status: "Strong AGENTS.md and CLAUDE.md; 9 Claude skills for tracing; no .claude/rules/ for test patterns"
critical_gaps:
  - title: "No code coverage tracking or enforcement"
    impact: "Cannot measure test coverage trends or set minimum thresholds; regressions go undetected"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No container image security scanning"
    impact: "Vulnerabilities in base images and dependencies not caught before deployment"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No PR-time container build validation"
    impact: "Dockerfile breakages discovered only at nightly deployment time, not on PRs"
    severity: "MEDIUM"
    effort: "4-8 hours"
  - title: "Behavioral/integration tests not automated on PRs"
    impact: "Agent regressions in response quality, tool usage, and safety only caught nightly or manually"
    severity: "MEDIUM"
    effort: "8-12 hours"
quick_wins:
  - title: "Add pytest-cov and coverage reporting to agent-tests.yml"
    effort: "2-3 hours"
    impact: "Immediate visibility into test coverage across all agents"
  - title: "Add Trivy container scanning to code-quality.yml"
    effort: "1-2 hours"
    impact: "Early detection of CVEs in UBI9 base images and Python dependencies"
  - title: "Enable more Ruff lint rules (S for security, B for bugbear)"
    effort: "1-2 hours"
    impact: "Catch common Python security anti-patterns and bugs at lint time"
  - title: "Add .claude/rules/ directory with test creation guidelines"
    effort: "2-3 hours"
    impact: "Improve AI-generated test consistency across agent frameworks"
recommendations:
  priority_0:
    - "Add coverage tracking with pytest-cov and codecov/coveralls integration"
    - "Add Trivy or Grype container scanning in CI for all Dockerfiles"
  priority_1:
    - "Add PR-time Dockerfile build validation (build but don't push) for changed agents"
    - "Create .claude/rules/ with test patterns for unit, behavioral, and integration tests"
    - "Run a lightweight behavioral test subset on PRs (API contract tests against a local agent)"
  priority_2:
    - "Add SAST scanning (CodeQL or Semgrep) for Python code"
    - "Add Dependabot or Renovate for automated dependency updates"
    - "Expand Ruff rules to include security (S), bugbear (B), and type annotation (ANN) checks"
    - "Add multi-architecture container builds for ARM64 support"
---

# Quality Analysis: agentic-starter-kits

## Executive Summary

- **Overall Score: 7.4/10**
- **Repository Type**: Python monorepo — collection of LLM agent starter kits (LangGraph, LlamaIndex, CrewAI, AutoGen, Google ADK, Langflow, and more)
- **Primary Language**: Python 3.12 (~22,600 LOC across 198 files, 52 test files with ~6,100 test LOC)
- **Key Strengths**: Exceptional behavioral test framework with adversarial safety tests, API contract tests, custom eval harness with scorers, nightly OpenShift deployment integration tests, comprehensive pre-commit hooks, thorough AGENTS.md and Claude skills
- **Critical Gaps**: No coverage tracking or enforcement, no container security scanning, no PR-time build validation, behavioral tests only run nightly
- **Agent Rules Status**: Present and strong — AGENTS.md provides thorough onboarding; 9 Claude skills exist for tracing; however, no `.claude/rules/` directory for test creation patterns

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 6.5/10 | Good tool-level tests per agent; missing coverage tracking |
| Integration/E2E | 8.5/10 | Excellent behavioral suite with adversarial, contract, and deployment tests |
| **Build Integration** | **5.0/10** | **No PR-time container build; nightly-only deployment tests** |
| Image Testing | 5.5/10 | UBI9 base, non-root, dockerignore; no scanning or runtime validation |
| Coverage Tracking | 2.0/10 | No codecov, no thresholds, no coverage reporting at all |
| CI/CD Automation | 8.0/10 | Well-organized workflows; concurrency control; JUnit reporting |
| Agent Rules | 7.0/10 | Strong AGENTS.md + 9 Claude skills; missing .claude/rules/ |

## Critical Gaps

### 1. No Code Coverage Tracking or Enforcement
- **Impact**: Cannot measure coverage, set minimum thresholds, or detect coverage regressions
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No `.codecov.yml`, no `pytest-cov` in test dependencies, no coverage flags in CI. The `pyproject.toml` test dependencies include pytest but no coverage tools. There is no way to know what percentage of agent source code is exercised by unit tests.

### 2. No Container Image Security Scanning
- **Impact**: Vulnerabilities in UBI9 base images, Python dependencies, and application code not detected
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: 13 Dockerfiles/Containerfiles exist across agents. No Trivy, Snyk, Grype, or any other scanner is configured. The `.gitleaks.toml` covers secret scanning but not vulnerability scanning. No SBOM generation or image signing.

### 3. No PR-Time Container Build Validation
- **Impact**: Dockerfile syntax errors, dependency resolution failures, and build breakages discovered only at nightly deployment time or when manually tested
- **Severity**: MEDIUM
- **Effort**: 4-8 hours
- **Details**: The `agent-deployment-test.yaml` workflow runs nightly and deploys to OpenShift. The `agent-tests.yml` workflow runs unit tests on PRs but does not build container images. A broken Dockerfile could be merged without CI catching it.

### 4. Behavioral/Integration Tests Not Automated on PRs
- **Impact**: Regressions in agent response quality, tool usage accuracy, adversarial safety, and API contract compliance caught only nightly
- **Severity**: MEDIUM
- **Effort**: 8-12 hours
- **Details**: The behavioral test suite (API contract, adversarial, tool usage, response quality, cost/latency) requires a running agent endpoint. These tests run nightly on OpenShift but not on PRs. The API contract tests could potentially run against a locally-started agent on PR.

## Quick Wins

### 1. Add pytest-cov and Coverage Reporting (2-3 hours)
- Add `pytest-cov` to `[project.optional-dependencies] test`
- Update `agent-tests.yml` to pass `--cov` flags and upload coverage
- Configure codecov.yml with minimum thresholds

### 2. Add Trivy Container Scanning (1-2 hours)
- Add a `container-scanning` job to `code-quality.yml`
- Scan each Dockerfile with `aquasecurity/trivy-action`
- Set severity threshold (CRITICAL, HIGH)

### 3. Enable More Ruff Lint Rules (1-2 hours)
- Current rules: `["E", "F", "I"]` (errors, pyflakes, isort)
- Add `"S"` (flake8-bandit security), `"B"` (bugbear), `"UP"` (pyupgrade)
- Catches SQL injection, eval usage, and common Python footguns

### 4. Add .claude/rules/ for Test Patterns (2-3 hours)
- Create rules for unit test, behavioral test, and integration test creation
- Include framework-specific patterns (pytest-asyncio, httpx, golden query fixtures)
- Reference existing test examples as templates

## Detailed Findings

### CI/CD Pipeline

**Workflows (4 total):**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `agent-tests.yml` | PR + push to main | Unit tests per agent with change detection |
| `code-quality.yml` | PR + push to main | Ruff lint, Ruff format, markdownlint, actionlint, Gitleaks |
| `agent-deployment-test.yaml` | Nightly (3 AM UTC) | Deploy 4 agents to OpenShift, health check, tear down |
| `pr-labeler.yml` | PR opened/synced | Auto-label PRs by area and size |

**Strengths:**
- Concurrency control on all workflows (`cancel-in-progress: true`)
- Smart change detection: unit tests only run for changed agents on PRs
- JUnit test report publishing with `mikepenz/action-junit-report`
- Pinned action versions with SHA hashes (not tags) — excellent supply chain security
- Nightly OpenShift deployment tests with matrix strategy (4 agents)
- Reusable composite action for cluster setup

**Gaps:**
- No container build step on PRs
- No coverage collection or reporting
- No SAST (CodeQL/Semgrep)
- No dependency scanning (Dependabot/Renovate)
- Behavioral tests not gated on PRs

### Test Coverage

**Test Architecture (Impressive):**

The repository has a multi-layer test strategy:

1. **Unit Tests** (`agents/*/tests/test_*.py`): Per-agent tool and schema tests. 7 agents have unit tests covering tool invocation, input schemas, and basic behavior. Tests are discovered automatically and run per-agent via Makefile.

2. **Behavioral Tests** (`tests/behavioral/` + `agents/*/tests/behavioral/`): Cross-agent and agent-specific behavioral evals covering:
   - **API Contract** (`test_api_contract.py`): Health endpoint, chat completion schema, SSE streaming, request validation
   - **Adversarial/Safety** (`test_prompt_injection.py`, `test_safety.py`, `test_boundary_conditions.py`): Prompt injection resistance, PII handling, dangerous operations
   - **Tool Usage** (`test_tool_usage.py`): Tool selection accuracy, hallucinated tool detection, tool call validity
   - **Response Quality** (`test_response_quality.py`): Answer relevance and completeness
   - **Cost/Latency** (`test_cost_latency.py`): Token budget and response time
   - **Reliability** (`test_reliability.py`): pass@k consistency
   - **Streaming Parity** (`test_streaming_parity.py`): Streaming vs non-streaming equivalence

3. **Integration Tests** (`agents/*/tests/integration/test_deployment.py`): Full OpenShift deployment cycle (build → deploy → health check → teardown). 4 agents have integration tests.

4. **Eval Harness** (`evals/harness/`): Custom evaluation framework with:
   - Task runner (`runner.py`)
   - Scorers: tool sequence, safety, plan coherence, latency
   - MLflow integration for tracking
   - EvalHub adapter for standardized evaluation

5. **Eval Hub Adapter Tests** (`evals/evalhub_adapter/tests/`): Unit and integration tests for the evaluation adapter itself.

**Test-to-Code Ratio**: ~6,100 test LOC / ~22,600 total LOC = **27%** — good for a project of this type.

**Fixtures**: YAML-based golden queries per agent, adversarial injection payloads, and threshold configurations. Well-organized and data-driven.

**Gaps:**
- No coverage measurement or reporting
- Some agents lack unit tests (a2a, langflow, openclaw, human_in_the_loop)
- Behavioral tests require a deployed agent (not runnable in pure CI without infrastructure)

### Code Quality

**Linting (Strong):**
- **Ruff**: Configured in `ruff.toml` with `E`, `F`, `I` rules. Python 3.12 target, 88 char line length.
- **Markdownlint**: `.markdownlint.jsonc` with `markdownlint-cli2`
- **Actionlint**: Validates GitHub Actions workflow files
- Both CI and pre-commit enforce the same tools

**Pre-commit Hooks (Excellent — 6 repos, 11 hooks):**
1. Conventional commit linting (espressif/conventional-precommit-linter)
2. Standard file hygiene (trailing whitespace, YAML/JSON/TOML validation, large file check, private key detection, no-commit-to-branch)
3. Ruff linting + formatting
4. Markdownlint
5. Gitleaks secret scanning
6. Actionlint for workflow files

**Gaps:**
- Ruff only uses basic rules — missing security (S), bugbear (B), type checking (ANN)
- No mypy or pyright for static type checking
- No SAST tools (CodeQL, Semgrep)

### Container Images

**Build Process (Solid):**
- 13 Dockerfiles/Containerfiles across agents
- UBI9 Python 3.12 base image (`registry.access.redhat.com/ubi9/python-312`) — Red Hat enterprise standard
- Non-root user (UID 1001) with OpenShift arbitrary UID support
- Multi-stage dependency installation with `uv`
- `.dockerignore` files exclude tests, docs, and dev files
- Port 8080 (OpenShift standard)

**Gaps:**
- No container image scanning (Trivy, Grype, Snyk)
- No SBOM generation
- No image signing or attestation
- No multi-architecture builds (x86_64 only)
- No PR-time build validation
- No runtime validation (image startup, health check) on PRs

### Security

**Strengths:**
- Gitleaks secret scanning in both pre-commit and CI
- `.gitleaksignore` for false positive management
- Pinned GitHub Actions with SHA hashes (not tags) — prevents supply chain attacks
- Conventional commits enforced
- `detect-private-key` pre-commit hook
- Adversarial safety tests (prompt injection, PII detection, dangerous operations)

**Gaps:**
- No SAST (CodeQL, Semgrep, Bandit)
- No container vulnerability scanning
- No dependency scanning (Dependabot, Renovate)
- Ruff doesn't include security rules (`S`)

### Agent Rules (Agentic Flow Quality)

**Status**: Present and strong at the project level

**What exists:**
- `CLAUDE.md`: Single-line pointer to AGENTS.md (minimal)
- `AGENTS.md`: Comprehensive 73-line guide covering structure, commands, code style, workflow, boundaries, non-standard agents, common gotchas, and references. This is one of the better AGENTS.md files seen in practice.
- `.claude/skills/`: 9 Claude skills, all focused on MLflow tracing integration:
  - `add-manual-tracing`, `check-autolog-support`, `create-tracing-module`
  - `integrate-tracing`, `review-tracing-code`, `test-tracing`
  - `verify-traces`, `wire-into-lifespan`, `kagenti-deploy`

**What's missing:**
- No `.claude/rules/` directory for test creation patterns
- Skills are tracing-focused only — no test-writing or quality skills
- No agent rules for behavioral test creation (despite excellent test patterns)
- No rules for unit test patterns across frameworks

**Recommendation**: The test infrastructure is mature enough to codify into rules. The behavioral test patterns (golden queries, scorers, conftest structure) should be captured in `.claude/rules/` so AI agents can consistently create tests following the established patterns. Use `/test-rules-generator` to bootstrap these.

## Recommendations

### Priority 0 (Critical)

1. **Add coverage tracking with pytest-cov and codecov** — Add `pytest-cov` to test dependencies, configure `.codecov.yml` with minimum thresholds (e.g., 60% to start), and update `agent-tests.yml` to collect and upload coverage per agent.

2. **Add container vulnerability scanning** — Add Trivy scanning to `code-quality.yml` for all Dockerfiles. Set severity threshold at HIGH/CRITICAL. Example:
   ```yaml
   - uses: aquasecurity/trivy-action@0.28.0
     with:
       scan-type: 'fs'
       scan-ref: 'agents/langgraph/react_agent'
       severity: 'CRITICAL,HIGH'
   ```

### Priority 1 (High Value)

3. **Add PR-time container build validation** — For changed agents, run `docker build` (or `podman build`) without pushing. This catches Dockerfile errors and dependency issues before merge.

4. **Create .claude/rules/ with test patterns** — Codify the behavioral test patterns, golden query format, conftest structure, and scorer usage into rules. This ensures AI agents generate tests consistent with the established patterns.

5. **Run API contract tests on PRs** — The API contract tests (`test_api_contract.py`) could run against a locally-started agent on PR. Start the agent in the background, run contract tests, and shut down. This catches API regressions immediately.

6. **Expand Ruff rules** — Add `"S"` (bandit/security), `"B"` (bugbear), `"UP"` (pyupgrade), and `"T20"` (print statements) to catch more issues at lint time.

### Priority 2 (Nice-to-Have)

7. **Add CodeQL or Semgrep SAST** — Python security scanning for injection vulnerabilities, unsafe eval, and insecure deserialization.

8. **Add Dependabot or Renovate** — Automated dependency updates for Python packages and GitHub Actions.

9. **Add mypy or pyright** — Static type checking for the eval harness and agent source code.

10. **Multi-architecture container builds** — Add ARM64 builds for Apple Silicon development and ARM-based cloud instances.

## Comparison to Gold Standards

| Dimension | agentic-starter-kits | odh-dashboard | notebooks | kserve |
|-----------|---------------------|---------------|-----------|--------|
| Unit Tests | 6.5 — Per-agent tool tests | 9.0 — Jest + React Testing Library | 7.0 — Notebook validation | 8.5 — Go unit tests |
| Integration/E2E | 8.5 — Behavioral + deployment | 9.0 — Cypress E2E + contract | 8.0 — Multi-image testing | 9.0 — E2E with KinD |
| Build Integration | 5.0 — Nightly only | 8.0 — PR builds | 7.0 — Image build matrix | 7.5 — PR builds |
| Image Testing | 5.5 — UBI9, non-root | 7.0 — Multi-stage | 9.0 — 5-layer validation | 7.0 — Runtime tests |
| Coverage | 2.0 — None | 8.0 — Codecov enforced | 5.0 — Basic | 9.0 — Enforced thresholds |
| CI/CD | 8.0 — Well-organized | 9.0 — Comprehensive | 8.5 — Matrix builds | 9.0 — Mature |
| Agent Rules | 7.0 — AGENTS.md + skills | 8.0 — Comprehensive rules | 5.0 — Basic | 6.0 — Docs only |

**Notable Strengths vs. Gold Standards:**
- The behavioral test framework (adversarial safety, tool sequence scoring, golden queries) is unique and ahead of most gold standards
- The custom eval harness with scorers (tool_sequence, safety, plan_coherence, latency) is production-grade
- AGENTS.md quality rivals the best CLAUDE.md files in the ecosystem
- Pre-commit hook coverage (6 repos, 11 hooks) is exemplary

**Key Differentiator:**
This repository's testing philosophy is fundamentally different from traditional repos. Rather than unit test coverage of internal functions, it emphasizes behavioral evaluation of deployed agents — testing what matters (does the agent respond correctly, safely, and efficiently?) rather than implementation details. This is appropriate for an agentic AI project but should be complemented with traditional coverage tracking.

## File Paths Reference

### CI/CD
- `.github/workflows/agent-tests.yml` — Unit test runner (PR + push)
- `.github/workflows/code-quality.yml` — Lint, format, secret scan (PR + push)
- `.github/workflows/agent-deployment-test.yaml` — Nightly OpenShift deployment tests
- `.github/workflows/pr-labeler.yml` — Auto PR labeling
- `.github/actions/setup-cluster/action.yaml` — Reusable OpenShift setup

### Testing
- `tests/behavioral/` — Cross-agent behavioral tests (adversarial, API contract)
- `agents/*/tests/` — Per-agent unit tests
- `agents/*/tests/behavioral/` — Per-agent behavioral tests
- `agents/*/tests/integration/` — Per-agent deployment integration tests
- `evals/harness/` — Custom eval harness (runner, scorers, MLflow)
- `evals/evalhub_adapter/` — EvalHub integration adapter
- `tests/behavioral/fixtures/adversarial/` — Adversarial test payloads

### Code Quality
- `ruff.toml` — Python linter configuration
- `.pre-commit-config.yaml` — Pre-commit hooks (6 repos, 11 hooks)
- `.markdownlint.jsonc` — Markdown linting rules
- `.gitleaks.toml` — Secret scanning configuration

### Container Images
- `agents/*/Dockerfile` — Per-agent container builds (13 total)
- `agents/*/.dockerignore` — Docker build context exclusions

### Agent Rules
- `AGENTS.md` — Comprehensive agent development guide
- `CLAUDE.md` — Pointer to AGENTS.md
- `.claude/skills/` — 9 Claude skills for tracing integration

### Project Configuration
- `pyproject.toml` — Python project config, pytest settings, test markers
- `charts/agent/` — Shared Helm chart for standard agents
