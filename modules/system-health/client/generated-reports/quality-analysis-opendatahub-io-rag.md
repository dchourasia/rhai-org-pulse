---
repository: "opendatahub-io/rag"
overall_score: 2.1
scorecard:
  - dimension: "Unit Tests"
    score: 0.5
    status: "Virtually no unit tests — 1 Go test file in entire repo, 0 Python unit tests"
  - dimension: "Integration/E2E"
    score: 1.0
    status: "No automated integration or E2E tests; manual deployment verification only"
  - dimension: "Build Integration"
    score: 0.5
    status: "No PR-time build validation; Dockerfiles exist but are never built in CI"
  - dimension: "Image Testing"
    score: 0.5
    status: "4 Dockerfiles present but zero image build, scan, or runtime validation in CI"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tools, no codecov integration, no thresholds"
  - dimension: "CI/CD Automation"
    score: 4.0
    status: "Single pre-commit workflow with good linting; no test, build, or deploy workflows"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude/ directory, no agent rules of any kind"
critical_gaps:
  - title: "Zero automated test suite"
    impact: "No automated validation of any code path — regressions go undetected until manual testing"
    severity: "HIGH"
    effort: "20-40 hours"
  - title: "No CI build validation for Docker images"
    impact: "4 Dockerfiles are never built in CI; broken images discovered only at deploy time"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No coverage tracking"
    impact: "Cannot measure or enforce code quality; impossible to set quality gates"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "No security scanning"
    impact: "Container images and dependencies not scanned for vulnerabilities"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "No agent rules for test automation"
    impact: "AI-assisted contributions have no test quality guidance"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add Trivy container scanning to CI"
    effort: "1-2 hours"
    impact: "Detect vulnerabilities in all 4 Docker images before merge"
  - title: "Add Docker build validation workflow"
    effort: "2-3 hours"
    impact: "Catch broken Dockerfiles at PR time instead of deploy time"
  - title: "Add pytest for Python utility modules"
    effort: "4-6 hours"
    impact: "Cover evaluation_utilities.py (900 LOC) and benchmarks with basic unit tests"
  - title: "Add ruff type checking to pre-commit"
    effort: "1 hour"
    impact: "Catch type errors in 25 Python files at lint time"
recommendations:
  priority_0:
    - "Create a comprehensive test suite for evaluation_utilities.py and beir_benchmarks.py — these are the most complex and critical code paths"
    - "Add Docker image build-and-smoke-test workflow to CI for all 4 Dockerfiles"
    - "Add Trivy or Snyk vulnerability scanning for container images and Python dependencies"
  priority_1:
    - "Add Go unit tests for the whatsapp-bot handlers and utilities"
    - "Implement codecov integration with minimum coverage thresholds"
    - "Add Kustomize build validation (kustomize build stack/base/) to CI"
    - "Create CLAUDE.md and .claude/rules/ for test automation guidance"
  priority_2:
    - "Add integration tests using Testcontainers for the voice-api-server FastAPI application"
    - "Add notebook execution validation (papermill) for Jupyter notebooks"
    - "Implement SBOM generation for container images"
    - "Add CodeQL or Semgrep SAST scanning"
---

# Quality Analysis: opendatahub-io/rag

## Executive Summary

- **Overall Score: 2.1/10**
- **Repository Type**: Demo/reference architecture repository — RAG Stack deployment guides, benchmarks, evaluation notebooks, and demo applications on Kubernetes/OpenShift
- **Primary Languages**: Python (25 files, ~4,700 LOC), Go (12 files, ~3,900 LOC)
- **Key Strengths**: Well-configured pre-commit hooks with Ruff linting, license enforcement, and YAML validation; good contributing guidelines and deployment documentation
- **Critical Gaps**: Virtually zero automated tests, no CI beyond linting, no coverage tracking, no security scanning, no image validation, no agent rules
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

This repository is a demo and reference architecture project, not a production application, which partially explains the minimal test infrastructure. However, it contains substantial application code (voice-api-server, whatsapp-bot, MCP server, benchmarking framework, evaluation utilities) that would benefit significantly from automated testing and CI validation.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0.5/10 | 1 Go test file, 0 Python test files |
| Integration/E2E | 1.0/10 | No automated integration or E2E tests |
| **Build Integration** | **0.5/10** | **4 Dockerfiles never built in CI** |
| Image Testing | 0.5/10 | No image build, scan, or runtime validation |
| Coverage Tracking | 0.0/10 | No coverage tools whatsoever |
| CI/CD Automation | 4.0/10 | Good pre-commit; no test/build/deploy automation |
| Agent Rules | 0.0/10 | No CLAUDE.md, no .claude/ directory |

## Critical Gaps

### 1. Zero Automated Test Suite
- **Impact**: No automated validation of any code path — regressions in evaluation utilities, benchmarks, API servers, or bot logic go entirely undetected until manual testing or production failure
- **Severity**: HIGH
- **Effort**: 20-40 hours
- **Details**: The repo has ~8,600 LOC across Python and Go. There is exactly 1 test file (`test_audio_send_test.go`) which is a manual integration test requiring a live WhatsApp connection — not a CI-runnable test. There are 0 Python test files despite 25 Python source files including complex evaluation logic.

### 2. No CI Build Validation for Docker Images
- **Impact**: 4 Dockerfiles (`voice-api-server`, `chat-ui`, `whatsapp-bot`, `mcp-server`) are never built in CI. Broken images are only discovered at deploy time.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The Dockerfiles use proper multi-stage builds, UBI9 base images, and non-root users — good practices that deserve CI validation to prevent regression.

### 3. No Coverage Tracking
- **Impact**: Cannot measure, enforce, or trend code coverage; no quality gates possible
- **Severity**: HIGH
- **Effort**: 4-6 hours (after tests exist)

### 4. No Security Scanning
- **Impact**: Dependencies and container images not scanned for vulnerabilities. Multiple requirements.txt files pin specific versions that may have known CVEs.
- **Severity**: HIGH
- **Effort**: 2-4 hours

### 5. No Agent Rules
- **Impact**: AI-assisted code contributions have no test quality guidance, no testing standards, no framework-specific patterns
- **Severity**: MEDIUM
- **Effort**: 4-6 hours

## Quick Wins

### 1. Add Docker Build Validation Workflow (2-3 hours)
- **Impact**: Catch broken Dockerfiles at PR time
- **Implementation**:
```yaml
name: Build Images
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        context:
          - demos/redbank-demo/chat-bot/voice-api-server
          - demos/redbank-demo/chat-bot/ui
          - demos/redbank-demo/chat-bot/whatsapp-bot
          - demos/redbank-demo/mcp-server
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t test-${{ matrix.context }} ${{ matrix.context }}
```

### 2. Add Trivy Scanning (1-2 hours)
- **Impact**: Detect vulnerabilities in container images and Python dependencies
- **Implementation**:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
```

### 3. Add Pytest for Evaluation Utilities (4-6 hours)
- **Impact**: Cover the most complex code — `evaluation_utilities.py` (900 LOC) includes JSON parsing, LLM prompt construction, Excel output, and statistical significance testing — all highly testable without external dependencies
- **Implementation**: Create `notebooks/evaluation/test_evaluation_utilities.py` with tests for `parse_llm_relevance_response`, `clean_label_for_excel`, `load_rag_progress`, `save_rag_progress`, etc.

### 4. Add Kustomize Validation (1 hour)
- **Impact**: Catch manifest errors before merge
- **Implementation**: Add `kustomize build stack/base/` and `kustomize build stack/overlays/*` to CI

## Detailed Findings

### CI/CD Pipeline

**Workflows Found**: 1 (`.github/workflows/pre-commit.yaml`)

The sole CI workflow runs pre-commit checks on PRs and pushes to main:
- **Triggers**: Pull requests and pushes to main branch
- **Concurrency**: Properly configured with `cancel-in-progress: true`
- **Caching**: Python pip cache enabled using requirements.txt and pre-commit config as cache keys
- **Post-check**: Verifies no uncommitted changes or new files after pre-commit

**What's Missing**:
- No test execution workflow
- No Docker image build workflow
- No Kustomize validation workflow
- No security scanning workflow
- No periodic/scheduled jobs
- No deployment validation

### Test Coverage

**Python Tests**: 0 test files out of 25 Python source files
- `evaluation_utilities.py` (900 LOC) — complex evaluation, RAG processing, statistical analysis — zero tests
- `beir_benchmarks.py` (520 LOC) — benchmarking framework — zero tests
- `voice-api-server/` (7 Python files) — FastAPI application — zero tests
- `mcp-server/` (3 Python files) — MCP server — zero tests

**Go Tests**: 1 test file out of 12 Go source files
- `test_audio_send_test.go` — manual integration test requiring live WhatsApp connection; not CI-runnable
- `handlers/`, `models/`, `utils/`, `config/` packages — zero tests

**Notebooks**: 16 Jupyter notebooks — no automated execution or validation

**Test-to-Code Ratio**: ~0% (effectively no automated tests)

### Code Quality Tools

**Pre-commit Configuration** (`.pre-commit-config.yaml`) — **Well Done**:
- `check-merge-conflict`, `trailing-whitespace`, `check-added-large-files` (1MB limit)
- `end-of-file-fixer`, `no-commit-to-branch`, `check-yaml`, `detect-private-key`
- `requirements-txt-fixer`, `mixed-line-ending`, `check-executables-have-shebangs`
- `check-json`, `check-shebang-scripts-are-executable`
- **License enforcement**: `insert-license` for `.py` and `.sh` files
- **Ruff**: Linting with `--fix` and formatting
- **blacken-docs**: Code formatting in documentation
- **pre-commit.ci**: Auto-fix and auto-update configured

**What's Missing**:
- No Go linting (`golangci-lint`)
- No type checking (mypy, pyright)
- No static analysis (CodeQL, Semgrep, gosec)
- No dependency scanning
- No secret detection beyond `detect-private-key`

### Container Images

**4 Dockerfiles found**:

1. **voice-api-server** (`demos/redbank-demo/chat-bot/voice-api-server/Dockerfile`)
   - Base: `registry.access.redhat.com/ubi9/python-312:latest`
   - Non-root user (1001), group 0 permissions for OpenShift compatibility
   - Single-stage build

2. **chat-ui** (`demos/redbank-demo/chat-bot/ui/Dockerfile`)
   - Base: `registry.access.redhat.com/ubi9/python-312:latest`
   - Non-root user (1001), proper permissions

3. **whatsapp-bot** (`demos/redbank-demo/chat-bot/whatsapp-bot/Dockerfile`)
   - Multi-stage build (Go builder + UBI9 minimal runtime)
   - CGO enabled for SQLite, static ffmpeg binaries
   - Non-root user, proper directory structure

4. **mcp-server** (`demos/redbank-demo/mcp-server/Dockerfile`)
   - Base: `registry.access.redhat.com/ubi9/python-312:latest`
   - Single-stage, minimal configuration

**Strengths**: All use Red Hat UBI9 base images, all configure non-root users
**Gaps**: No image scanning, no SBOM generation, no multi-arch support, no image signing, no CI build validation

### Security Practices

- **detect-private-key**: Pre-commit hook for basic key detection
- **No container scanning** (Trivy, Snyk)
- **No SAST** (CodeQL, Semgrep)
- **No dependency scanning** (Dependabot, Renovate)
- **No secret detection** (Gitleaks, TruffleHog)
- **Hardcoded recipient in test**: `test_audio_send_test.go` contains a hardcoded WhatsApp JID

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **.claude/ directory**: Not present
- **Coverage**: No test type rules exist
- **Quality**: N/A
- **Gaps**: Everything — no test automation guidance, no testing standards, no framework-specific patterns
- **Recommendation**: Generate rules with `/test-rules-generator` covering Python pytest patterns, Go testing patterns, notebook validation, and Kustomize validation

## Recommendations

### Priority 0 (Critical)

1. **Create pytest test suite for evaluation utilities**
   - `parse_llm_relevance_response()` — pure function, trivially testable
   - `clean_label_for_excel()` — pure function, edge cases matter
   - `load_rag_progress()` / `save_rag_progress()` — file I/O with crash recovery logic
   - `run_rag_with_progress()` — mock the processor function, test progress/resume flow
   - Estimated effort: 8-12 hours for good coverage

2. **Add Docker image build workflow**
   - Build all 4 images on every PR
   - Fail fast on broken Dockerfiles
   - Estimated effort: 2-3 hours

3. **Add security scanning**
   - Trivy for container images and filesystem
   - Dependabot or Renovate for dependency updates
   - Estimated effort: 2-4 hours

### Priority 1 (High Value)

4. **Add Go unit tests for whatsapp-bot**
   - `utils/validation.go`, `utils/file.go` — utility functions
   - `config/config.go` — configuration parsing
   - `handlers/` — HTTP handler tests with httptest
   - Estimated effort: 8-12 hours

5. **Add Kustomize validation to CI**
   - `kustomize build stack/base/`
   - `kustomize build` for each overlay
   - Estimated effort: 1-2 hours

6. **Add codecov integration**
   - After test suites exist, add coverage reporting
   - Set minimum thresholds (start at 30%, increase over time)
   - Estimated effort: 2-3 hours (after tests exist)

7. **Create CLAUDE.md and agent rules**
   - Testing standards for Python (pytest) and Go
   - Notebook validation guidelines
   - Kustomize manifest validation
   - Estimated effort: 4-6 hours

### Priority 2 (Nice-to-Have)

8. **Add notebook execution validation**
   - Use papermill to run notebooks in CI (with mocked/lightweight backends)
   - Catch import errors and cell execution failures
   - Estimated effort: 8-12 hours

9. **Add integration tests for FastAPI server**
   - Use TestClient for voice-api-server endpoint testing
   - Mock external services (LlamaStack, Whisper)
   - Estimated effort: 6-8 hours

10. **Add golangci-lint for Go code**
    - Configure `.golangci.yml` with standard linters
    - Add to pre-commit or separate CI workflow
    - Estimated effort: 1-2 hours

11. **Add SBOM generation**
    - Generate SBOMs for container images
    - Estimated effort: 2-3 hours

## Comparison to Gold Standards

| Practice | rag | odh-dashboard | notebooks | kserve |
|----------|-----|---------------|-----------|--------|
| Unit Test Files | 1 (non-CI) | 500+ | 50+ | 200+ |
| Integration Tests | None | Contract tests | Image tests | envtest |
| E2E Tests | None | Cypress suite | 5-layer validation | Multi-version |
| CI Workflows | 1 (lint only) | 15+ | 10+ | 20+ |
| Coverage Tracking | None | Codecov + thresholds | N/A | Codecov |
| Security Scanning | detect-private-key | Trivy + CodeQL | Trivy | Trivy + gosec |
| Image Testing | None | Build + smoke | Full 5-layer | Build + test |
| Pre-commit | Excellent | Good | Basic | Good |
| Agent Rules | None | Comprehensive | Basic | None |

## File Paths Reference

### CI/CD
- `.github/workflows/pre-commit.yaml` — Only CI workflow
- `.pre-commit-config.yaml` — Pre-commit configuration (comprehensive)

### Source Code (Python)
- `benchmarks/beir-benchmarks/beir_benchmarks.py` — Benchmark framework (520 LOC)
- `notebooks/evaluation/evaluation_utilities.py` — Evaluation utilities (900 LOC)
- `demos/redbank-demo/chat-bot/voice-api-server/app/` — FastAPI voice API (7 files)
- `demos/redbank-demo/mcp-server/redbank-mcp/` — MCP server (3 files)
- `demos/kubeflow-pipelines/*/` — Pipeline definitions (4 files)

### Source Code (Go)
- `demos/redbank-demo/chat-bot/whatsapp-bot/` — WhatsApp bot (12 files, ~3,900 LOC)

### Tests
- `demos/redbank-demo/chat-bot/whatsapp-bot/test_audio_send_test.go` — Only test file (manual, not CI-runnable)

### Container Images
- `demos/redbank-demo/chat-bot/voice-api-server/Dockerfile`
- `demos/redbank-demo/chat-bot/ui/Dockerfile`
- `demos/redbank-demo/chat-bot/whatsapp-bot/Dockerfile`
- `demos/redbank-demo/mcp-server/Dockerfile`

### Deployment
- `stack/base/` — Kustomize base (KServe + vLLM + LlamaStack)
- `stack/overlays/` — Deployment variants (Granite, Llama, remote inference)
- `demos/redbank-demo/Makefile` — Demo deployment automation
- `DEPLOYMENT.md` — Comprehensive deployment guide

### Documentation
- `README.md` — Project overview
- `CONTRIBUTING.md` — Contributing guidelines with pre-commit instructions
- `DEPLOYMENT.md` — Detailed deployment guide
