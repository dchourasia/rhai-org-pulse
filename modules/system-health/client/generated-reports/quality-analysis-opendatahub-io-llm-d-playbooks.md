---
repository: "opendatahub-io/llm-d-playbooks"
overall_score: 2.1
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No source code or unit tests exist - this is a documentation/playbook repository"
  - dimension: "Integration/E2E"
    score: 3.0
    status: "Validation playbooks exist in README form but no automated test scripts"
  - dimension: "Build Integration"
    score: 0.0
    status: "No build system, no container images, no PR validation"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images are built by this repository"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No code coverage - no source code to cover"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "No GitHub Actions workflows, no CI/CD pipeline of any kind"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "No CI/CD pipeline at all"
    impact: "No automated validation of playbook content, YAML manifests, or scripts"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No automated validation of Kubernetes manifests"
    impact: "Broken YAML, invalid Kustomize overlays, or incorrect CRD references go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
  - title: "Validation playbooks are documentation-only, not executable scripts"
    impact: "Steps 03, 05, and 07 describe validation but provide no runnable scripts to perform it"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No linting or formatting enforcement"
    impact: "Markdown inconsistencies, YAML formatting errors, and broken links accumulate"
    severity: "MEDIUM"
    effort: "2-3 hours"
  - title: "Shell scripts lack validation"
    impact: "bench-all.sh scripts have hardcoded URLs and no error handling (set -e, shellcheck)"
    severity: "MEDIUM"
    effort: "1-2 hours"
  - title: "No agent rules for contribution guidance"
    impact: "AI-assisted contributions have no guardrails for playbook quality or manifest correctness"
    severity: "LOW"
    effort: "2-3 hours"
quick_wins:
  - title: "Add YAML/Kustomize linting workflow"
    effort: "2-3 hours"
    impact: "Catch invalid Kubernetes manifests and Kustomize overlays before merge"
  - title: "Add Markdown linting and link checking"
    effort: "1-2 hours"
    impact: "Ensure consistent documentation quality and no broken links"
  - title: "Add ShellCheck for bash scripts"
    effort: "1 hour"
    impact: "Catch common shell scripting errors in bench-all.sh and generate-all.sh scripts"
  - title: "Add kustomize build validation to CI"
    effort: "2-3 hours"
    impact: "Verify all kustomize overlays render correctly on every PR"
recommendations:
  priority_0:
    - "Create a GitHub Actions CI pipeline with YAML linting (yamllint), Kustomize build validation, and Markdown linting"
    - "Convert validation README playbooks (Steps 03, 05, 07) into executable shell scripts that can be run against a live cluster"
  priority_1:
    - "Add ShellCheck linting for all shell scripts in the repository"
    - "Add link checking for markdown files to catch broken cross-references"
    - "Create a Kustomize build matrix that validates all overlays (llm-d/qwen, vllm/qwen, etc.)"
  priority_2:
    - "Add CLAUDE.md or agent rules for AI-assisted playbook contributions"
    - "Add Python linting (ruff) for the test data generator scripts"
    - "Add a pre-commit configuration for local development"
---

# Quality Analysis: llm-d-playbooks

## Executive Summary
- **Overall Score: 2.1/10**
- **Repository Type**: Documentation / Deployment Playbook (no source code)
- **Primary Languages**: Markdown, YAML (Kubernetes manifests), Python (utility scripts), Shell (benchmark scripts)
- **Framework**: Kubernetes (KServe, LLM-D, Kustomize)
- **Agent Rules Status**: Missing

This repository is a **documentation-focused deployment playbook** for llm-d across multiple Kubernetes platforms (OpenShift, AKS, CKS). It contains no source code, no CI/CD pipelines, no automated tests, and no quality tooling. The repository consists of:

- **8 step-by-step playbook directories** (01-cluster-bring-up through 08-benchmarking)
- **Kubernetes manifests** (Kustomize overlays for vLLM and LLM-D deployments)
- **Python utility scripts** for generating benchmark test data
- **Shell scripts** for running GuideLLM benchmarks
- **Validation playbooks** described in READMEs but not implemented as executable scripts

The low score reflects the complete absence of automation, not a judgment on the documentation quality itself, which is well-structured and thorough.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No source code or unit tests exist |
| Integration/E2E | 3/10 | Validation playbooks exist as README documentation but no automated scripts |
| Build Integration | 0/10 | No build system, no container images, no PR validation |
| Image Testing | 0/10 | No container images are built by this repository |
| Coverage Tracking | 0/10 | No code coverage - no source code to cover |
| CI/CD Automation | 1/10 | No GitHub Actions, no CI/CD pipeline of any kind |
| Agent Rules | 0/10 | No CLAUDE.md, AGENTS.md, or .claude/ directory |

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: No automated validation of any repository content on PRs or merges
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: The `.github/workflows/` directory does not exist. There is no GitHub Actions, Jenkins, or GitLab CI configuration. Every change is merged without any automated checks.

### 2. No Automated Validation of Kubernetes Manifests
- **Impact**: Broken YAML, invalid Kustomize overlays, or incorrect CRD references go undetected until someone attempts deployment
- **Severity**: HIGH
- **Effort**: 2-4 hours
- **Details**: The repository contains 20+ Kustomize YAML files across `08-benchmarking/intelligent-inference-scheduler/` including overlays for llm-d (qwen, phi, granite), vllm (qwen, phi, granite), guidellm, and monitoring. None are validated in CI. A `kustomize build` step would catch structural errors immediately.

### 3. Validation Playbooks Are Documentation-Only
- **Impact**: Steps 03 (Control Plane Readiness), 05 (RDMA Network Validation), and 07 (LLM Deployment Validation) describe validation categories and directories but the referenced subdirectories (`crds-present/`, `operators-healthy/`, `connectivity/`, `bandwidth/`, `functional/`, `performance/`) do not exist in the repository
- **Severity**: HIGH
- **Effort**: 16-24 hours
- **Details**: The READMEs reference validation directories that don't exist yet:
  - `03-control-plane-readiness/validation/crds-present/` - not present
  - `03-control-plane-readiness/validation/operators-healthy/` - not present
  - `03-control-plane-readiness/validation/llm-d-deployable/` - not present
  - `05-rdma-network-validation/validation/connectivity/` - not present
  - `05-rdma-network-validation/validation/bandwidth/` - not present
  - `05-rdma-network-validation/validation/latency-stability/` - not present
  - `07-llm-deployment-validation/validation/functional/` - not present
  - `07-llm-deployment-validation/validation/performance/` - not present
  - `shared/scripts/` - not present
  - `shared/assets/` - not present

### 4. No Linting or Formatting Enforcement
- **Impact**: Markdown inconsistencies, YAML formatting errors, and broken links accumulate over time
- **Severity**: MEDIUM
- **Effort**: 2-3 hours

### 5. Shell Scripts Lack Validation
- **Impact**: `bench-all.sh` scripts contain hardcoded URLs (including an AWS ELB URL in `heterogeneous/bench-all.sh`), no `set -e` for error handling, and would not pass ShellCheck
- **Severity**: MEDIUM
- **Effort**: 1-2 hours

### 6. Python Scripts Have No Tests or Linting
- **Impact**: The `kv-cache-prompt-generator.py` and `heterogeneous-workload-generator.py` scripts (~350 lines total) have no unit tests and no linting configuration
- **Severity**: MEDIUM
- **Effort**: 3-4 hours

## Quick Wins

### 1. Add YAML/Kustomize Linting Workflow (2-3 hours)
**Impact**: Catch invalid Kubernetes manifests and Kustomize overlays before merge

```yaml
# .github/workflows/validate.yml
name: Validate
on: [pull_request]
jobs:
  yaml-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: YAML Lint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: .
          config_data: |
            extends: default
            rules:
              line-length:
                max: 200
  kustomize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Kustomize
        uses: imranismail/setup-kustomize@v2
      - name: Validate overlays
        run: |
          for dir in $(find . -name kustomization.yaml -exec dirname {} \;); do
            echo "Building $dir..."
            kustomize build "$dir" > /dev/null
          done
```

### 2. Add Markdown Linting and Link Checking (1-2 hours)
**Impact**: Ensure consistent documentation quality and catch broken cross-references

```yaml
  markdown-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DavidAnson/markdownlint-cli2-action@v19
      - name: Check links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
```

### 3. Add ShellCheck for Bash Scripts (1 hour)
**Impact**: Catch common shell scripting errors

```yaml
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: ShellCheck
        uses: ludeeus/action-shellcheck@master
        with:
          scandir: '.'
```

### 4. Add kustomize build validation (2-3 hours)
**Impact**: Verify all 7 Kustomize overlay combinations render correctly

The repository has overlays at:
- `08-benchmarking/intelligent-inference-scheduler/llm-d/` (qwen, phi, granite)
- `08-benchmarking/intelligent-inference-scheduler/vllm/` (qwen, phi, granite)
- `08-benchmarking/intelligent-inference-scheduler/guidellm/` (llm-d, vllm, llm-d-phi, etc.)
- `08-benchmarking/intelligent-inference-scheduler/monitoring/`

## Detailed Findings

### CI/CD Pipeline
**Score: 1/10**

- **No `.github/workflows/` directory** - Zero CI/CD automation
- **No Makefile** - No build targets or convenience scripts
- **No pre-commit hooks** - No local validation before commits
- **No branch protection** - Cannot enforce CI checks on PRs (nothing to enforce)

The score is 1 rather than 0 because the Kustomize overlay structure itself provides a form of declarative build configuration, though it is never validated automatically.

### Test Coverage
**Score: 0/10 (Unit) / 3/10 (Integration/E2E)**

**Unit Tests**: None. The Python scripts (`kv-cache-prompt-generator.py`, `heterogeneous-workload-generator.py`) have no accompanying test files.

**Integration/E2E**: The repository describes validation in three areas but provides no executable validation scripts:

1. **Control Plane Readiness (Step 03)**: Describes CRD presence, operator health, and deployability checks. Directory structure planned but not populated.
2. **RDMA Network Validation (Step 05)**: Describes connectivity, bandwidth, and latency/stability checks. Directory structure planned but not populated.
3. **LLM Deployment Validation (Step 07)**: Describes functional and performance validation. Directory structure planned but not populated.

The 3/10 score reflects that the validation *taxonomy* is well-designed and the benchmarking infrastructure (GuideLLM jobs, Kustomize overlays, test data generators) is functional.

### Code Quality
**Score: 1/10**

- **No linting configuration** - No yamllint, markdownlint, shellcheck, ruff, or flake8
- **No formatting enforcement** - No prettier, black, or isort
- **No pre-commit hooks** - No `.pre-commit-config.yaml`
- **Hardcoded values in scripts** - `bench-all.sh` contains hardcoded AWS ELB URLs and model names
- **No `.editorconfig`** - No consistent formatting across editors

Positives:
- `.gitignore` exists (excludes `.DS_Store` and `prompts.csv`)
- Python scripts use `argparse` for configuration rather than hardcoding all values

### Container Images
**Score: 0/10**

- No `Dockerfile` or `Containerfile` in the repository
- No container images are built
- References external images (`ghcr.io/vllm-project/guidellm:latest`, `registry.access.redhat.com/ubi9/ubi:latest`) but does not build any

### Security
**Score: 1/10**

- **No security scanning** - No Trivy, Snyk, CodeQL, or Gitleaks
- **No dependency scanning** - `requirements.txt` has only 2 dependencies (`pandas`, `guidellm==0.3.1`) with no vulnerability checking
- **No secret detection** - No `.gitleaks.toml` or equivalent
- **Hardcoded URL in script** - `heterogeneous/bench-all.sh` contains an AWS ELB URL (`a970653680479411ea2687bb74860cd4-328874611.us-east-2.elb.amazonaws.com`)

Positive:
- Kubernetes manifests use `security.opendatahub.io/enable-auth` annotations
- LLM-D deployment uses TLS (`--cert-path`, `--secure-serving`)

### Agent Rules (Agentic Flow Quality)
**Score: 0/10**

- **Status**: Missing
- **Coverage**: No agent rules exist
- **CLAUDE.md**: Not present
- **AGENTS.md**: Not present
- **`.claude/` directory**: Not present
- **Recommendation**: Generate agent rules with `/test-rules-generator` covering:
  - Playbook contribution guidelines (markdown structure, step numbering)
  - Kubernetes manifest validation requirements
  - Kustomize overlay patterns and naming conventions
  - Shell script standards (`set -euo pipefail`, no hardcoded URLs)

## Recommendations

### Priority 0 (Critical)

1. **Create a GitHub Actions CI pipeline** with:
   - YAML linting (`yamllint`)
   - Kustomize build validation for all overlays
   - Markdown linting (`markdownlint`)
   - Link checking for broken cross-references
   - ShellCheck for bash scripts

2. **Implement the planned validation scripts** for Steps 03, 05, and 07:
   - Convert README descriptions into executable shell scripts
   - Add scripts for CRD presence checks, operator health, RDMA connectivity
   - Create functional test scripts for LLM deployment validation

### Priority 1 (High Value)

3. **Add Python linting and testing** for test-data-generator scripts:
   - Add `ruff` configuration for the Python scripts
   - Write unit tests for `kv-cache-prompt-generator.py` (argument parsing, capacity math, prompt generation)
   - Write unit tests for `heterogeneous-workload-generator.py` (ratio calculations, interleaving logic)

4. **Remove hardcoded values from shell scripts**:
   - Parameterize URLs, model names, and concurrency levels in `bench-all.sh`
   - Add `set -euo pipefail` to all shell scripts

5. **Add CLAUDE.md or agent rules** for AI-assisted contributions:
   - Playbook structure conventions
   - Kustomize overlay patterns
   - README template requirements

### Priority 2 (Nice-to-Have)

6. **Add a pre-commit configuration** (`.pre-commit-config.yaml`) for local development with:
   - yamllint
   - markdownlint
   - shellcheck
   - trailing whitespace/end-of-file fixes

7. **Add a CODEOWNERS file** for review assignment

8. **Add dependency vulnerability scanning** for the Python `requirements.txt`

## Comparison to Gold Standards

| Dimension | llm-d-playbooks | odh-dashboard | notebooks | kserve |
|-----------|:-:|:-:|:-:|:-:|
| CI/CD Pipeline | None | Multi-workflow, PR+periodic | Comprehensive image CI | Multi-version testing CI |
| Unit Tests | 0 files | 1000+ spec files | N/A (images) | Extensive Go tests |
| Integration/E2E | READMEs only | Cypress E2E suite | 5-layer validation | envtest + E2E |
| Coverage Tracking | None | Codecov enforced | N/A | Codecov enforced |
| Linting | None | ESLint + Prettier | yamllint | golangci-lint (20+ linters) |
| Security Scanning | None | Snyk, CodeQL | Trivy | CodeQL, Snyk |
| Agent Rules | None | Comprehensive | Basic | None |
| Pre-commit Hooks | None | Yes | Yes | No |
| Manifest Validation | None | Kustomize CI | N/A | Kustomize CI |

## File Paths Reference

### Repository Structure
```
llm-d-playbooks/
  01-cluster-bring-up/README.md
  02-operators/README.md
  03-control-plane-readiness/
    README.md
    validation/README.md           # References non-existent subdirectories
  04-rdma-networking/README.md
  05-rdma-network-validation/
    README.md
    validation/README.md           # References non-existent subdirectories
  06-llm-d-deploy/
    README.md
    apply/README.md
  07-llm-deployment-validation/
    README.md
    validation/README.md           # References non-existent subdirectories
  08-benchmarking/
    README.md
    intelligent-inference-scheduler/
      README.md                    # Comprehensive A/B benchmarking guide
      guidellm/                    # Kustomize overlays for GuideLLM jobs
      llm-d/                      # Kustomize overlays for LLM-D deployment
      vllm/                       # Kustomize overlays for vLLM deployment
      monitoring/                  # Grafana + Prometheus manifests
      test-data-generator/
        requirements.txt           # pandas, guidellm==0.3.1
        prefix/
          kv-cache-prompt-generator.py
          bench-all.sh
        heterogeneous/
          heterogeneous-workload-generator.py
          bench-all.sh
  shared/README.md                 # References non-existent scripts/ and assets/
  .gitignore
  LICENSE
  README.md
```

### Key Files Analyzed
- `README.md` - Root deployment guide
- `08-benchmarking/intelligent-inference-scheduler/README.md` - Detailed A/B benchmark playbook
- `08-benchmarking/intelligent-inference-scheduler/llm-d/base/llm-infra.yaml` - LLMInferenceService manifest
- `08-benchmarking/intelligent-inference-scheduler/guidellm/base/guidellm-job.yaml` - GuideLLM benchmark job
- `08-benchmarking/intelligent-inference-scheduler/test-data-generator/prefix/kv-cache-prompt-generator.py` - Benchmark data generator
- `08-benchmarking/intelligent-inference-scheduler/test-data-generator/heterogeneous/heterogeneous-workload-generator.py` - Heterogeneous workload generator
- `03-control-plane-readiness/validation/README.md` - Control plane validation plan
- `05-rdma-network-validation/validation/README.md` - RDMA validation plan
- `07-llm-deployment-validation/validation/README.md` - Deployment validation plan
