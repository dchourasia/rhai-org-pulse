---
repository: "red-hat-data-services/Cloud-Cost-Optimization"
overall_score: 1.6
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "Zero test files exist in the repository - no unit tests at all"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests - all validation is manual via workflow dispatch"
  - dimension: "Build Integration"
    score: 1.0
    status: "No PR workflows exist - all workflows are schedule/dispatch only"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images built - scripts run directly on GitHub Actions runners"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling, no codecov, no coverage thresholds"
  - dimension: "CI/CD Automation"
    score: 5.0
    status: "15 operational workflows with schedule triggers, but no PR validation"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, no .claude directory, no agent rules of any kind"
critical_gaps:
  - title: "Zero test coverage across 4,068 lines of Python and 400 lines of Bash"
    impact: "Any code change can silently break cluster hibernation, cloud cleanup, or IAM role deletion - operations that directly affect production AWS infrastructure and cost"
    severity: "HIGH"
    effort: "16-24 hours"
  - title: "No PR validation workflow"
    impact: "Code is merged without any automated checks - no linting, no tests, no syntax validation"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Bare except clauses and os.popen() usage create silent failures"
    impact: "Errors in AWS resource cleanup are swallowed silently, leading to resource leaks and unexpected cloud costs"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "No dry-run validation in CI for destructive operations"
    impact: "Scripts that delete VPCs, IAM roles, EC2 instances, and EBS volumes have no automated safeguards"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "Duplicated oc_cluster class across multiple files"
    impact: "Inconsistent parsing logic between cloud_cleaner.py and hibernate_cluster.py could cause misidentification of clusters"
    severity: "MEDIUM"
    effort: "4-6 hours"
quick_wins:
  - title: "Add a PR validation workflow with Python linting (ruff) and syntax checks"
    effort: "2-3 hours"
    impact: "Catches syntax errors, import issues, and basic code quality problems before merge"
  - title: "Add unit tests for pure functions (sanitize_cluster_name, tag-matching logic)"
    effort: "4-6 hours"
    impact: "Validates critical cluster identification logic that gates destructive AWS operations"
  - title: "Replace bare except clauses with specific exception handling"
    effort: "2-3 hours"
    impact: "Makes failures visible instead of silently continuing with potentially dangerous operations"
  - title: "Add pre-commit hooks with ruff and basic Python checks"
    effort: "1-2 hours"
    impact: "Enforces consistent code quality at commit time"
recommendations:
  priority_0:
    - "Add a PR validation workflow with ruff linting, mypy type checking, and pytest execution"
    - "Write unit tests for all cluster identification and tag-matching functions - these gate destructive AWS operations"
    - "Replace os.popen() with subprocess.run() across all files for proper error handling"
    - "Replace all bare except clauses with specific exception types"
  priority_1:
    - "Add integration tests using moto (AWS mock library) for boto3-based cleanup logic"
    - "Consolidate duplicated oc_cluster class into a shared module"
    - "Add dry-run CI validation that exercises all cleanup scripts in simulation mode"
    - "Pin GitHub Actions versions (actions/checkout@v3 -> actions/checkout@v4) and use setup-python@v5"
  priority_2:
    - "Add dependabot or renovate for automated dependency updates"
    - "Create CLAUDE.md and agent rules for test patterns and code conventions"
    - "Add CODEOWNERS file for review requirements"
    - "Add type hints consistently and enforce with mypy"
---

# Quality Analysis: Cloud-Cost-Optimization

## Executive Summary

- **Overall Score: 1.6/10**
- **Repository Type**: Python/Bash DevOps automation toolkit for AWS cloud cost optimization
- **Primary Function**: Automated cluster hibernation, cloud resource cleanup, and cost management for Red Hat OpenShift AI infrastructure
- **Critical Risk**: This repository manages **destructive AWS operations** (deleting VPCs, IAM roles, EC2 instances, EBS volumes) across production and staging accounts with **zero automated test coverage**
- **Key Strengths**: Well-organized GitHub Actions workflows with schedule-based automation
- **Critical Gaps**: No tests, no PR validation, no linting, no coverage tracking, no agent rules
- **Agent Rules Status**: Missing - no CLAUDE.md, no .claude directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | Zero test files in the entire repository |
| Integration/E2E | 0/10 | No integration or E2E tests whatsoever |
| **Build Integration** | **1/10** | **No PR workflows - all workflows are schedule/dispatch only** |
| Image Testing | N/A | No container images (scripts run on GHA runners) |
| Coverage Tracking | 0/10 | No coverage tooling of any kind |
| CI/CD Automation | 5/10 | 15 operational workflows, but no PR validation |
| Agent Rules | 0/10 | No agent rules, no CLAUDE.md, no .claude directory |

## Critical Gaps

### 1. Zero Test Coverage (Severity: HIGH)
- **Impact**: 4,068 lines of Python and 400 lines of Bash that manage destructive AWS operations have no automated tests
- **Risk**: Any code change can silently break cluster hibernation (affecting all RHOAI dev clusters), cloud cleanup (leading to resource leaks), or IAM role deletion (security implications)
- **Files at Risk**:
  - `src/cleanup_openshift_ci_on_aws.py` (707 lines) - Deletes VPCs, instances, security groups, NAT gateways
  - `src/hibernate_cluster.py` (271 lines) - Stops EC2 instances, detaches and deletes EBS volumes
  - `src/iam_role_cleaner.py` (203 lines) - Deletes IAM roles and policies
  - `src/cloud_cleaner.py` (308 lines) - Cleans up ELBs, EBS volumes, networking resources
- **Effort**: 16-24 hours for comprehensive unit test suite
- **Priority**: P0 - These scripts operate on production AWS infrastructure

### 2. No PR Validation Pipeline (Severity: HIGH)
- **Impact**: Code merges without any automated checks
- **Current State**: All 15 workflows are either `schedule` or `workflow_dispatch` triggered - none run on `pull_request`
- **What's Missing**:
  - No syntax/import validation
  - No linting (no ruff, flake8, or pylint configuration)
  - No type checking (no mypy or pyright)
  - No test execution
  - No code review requirements
- **Effort**: 4-6 hours to create a comprehensive PR workflow
- **Priority**: P0

### 3. Silent Failure Patterns (Severity: HIGH)
- **Impact**: Errors in destructive operations are silently swallowed
- **Examples**:
  - `src/hibernate_cluster.py:96` - `except:` (bare except with no logging, retries volume deletion 7 times silently)
  - `src/hibernate_cluster.py:38` - `except:` (catches all exceptions when getting IPI cluster name)
  - `src/cloud_cleaner.py:32-33` - `run_command()` uses `os.popen()` which doesn't check exit codes
  - `src/hibernate_cluster.py:199` - `os.popen()` executes shell commands without error checking
- **Effort**: 8-12 hours to audit and fix all error handling
- **Priority**: P0

### 4. No Dry-Run CI Validation (Severity: HIGH)
- **Impact**: Scripts that delete AWS resources have dry-run modes but these are never exercised in CI
- **Risk**: Regression in dry-run logic could cause unintended deletions
- **Affected Scripts**: `cleanup_openshift_ci_on_aws.py`, `iam_role_cleaner.py`, `instance_profile_cleaner.py`, `elastic_ip_cleaner.py`
- **Effort**: 8-12 hours
- **Priority**: P0

### 5. Duplicated Code and Inconsistent Patterns (Severity: MEDIUM)
- **Impact**: The `oc_cluster` class is defined differently in `cloud_cleaner.py` (missing fields) vs `hibernate_cluster.py` (more complete)
- **Risk**: Inconsistent cluster parsing could lead to misidentification when performing destructive operations
- **Effort**: 4-6 hours to consolidate
- **Priority**: P1

## Quick Wins

### 1. Add PR Validation Workflow with Ruff Linting (2-3 hours)
- **Impact**: Catches syntax errors, unused imports, and code quality issues before merge
- **Implementation**:
```yaml
# .github/workflows/pr-validation.yaml
name: PR Validation
on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check src/
      - run: ruff format --check src/

  syntax-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m py_compile src/*.py
```

### 2. Add Unit Tests for Tag-Matching Functions (4-6 hours)
- **Impact**: Validates the most critical logic that determines which AWS resources to delete
- **Key Functions to Test**:
  - `worker_node_belongs_to_the_hcp_cluster()` - HCP cluster tag matching
  - `worker_node_belongs_to_the_ipi_cluster()` - IPI cluster tag matching
  - `_validate_resource_build_id()` - Build ID validation before deletion
  - `sanitize_cluster_name()` - Cluster name parsing
  - `check_if_given_tag_exists()` - Tag existence checks
  - `filter_tagged_roles()` / `calculate_expired_roles()` - IAM role expiration logic
- **Implementation**:
```python
# tests/test_hibernate_cluster.py
import pytest
from unittest.mock import MagicMock
import sys
sys.path.insert(0, 'src')
import hibernate_cluster as hc

def test_sanitize_cluster_name_short():
    assert hc.sanitize_cluster_name("my-cluster") == "my-cluster"

def test_sanitize_cluster_name_with_four_dashes():
    name = "my-cluster-with-four-dashes"
    assert len(hc.sanitize_cluster_name(name)) <= 28

def test_worker_node_belongs_to_hcp_cluster_match():
    ec2 = {'Tags': [{'Key': 'api.openshift.com/name', 'Value': 'test-cluster'}]}
    assert hc.worker_node_belongs_to_the_hcp_cluster(ec2, 'test-cluster') is True

def test_worker_node_belongs_to_hcp_cluster_no_match():
    ec2 = {'Tags': [{'Key': 'api.openshift.com/name', 'Value': 'other-cluster'}]}
    assert hc.worker_node_belongs_to_the_hcp_cluster(ec2, 'test-cluster') is False
```

### 3. Replace Bare Except Clauses (2-3 hours)
- **Impact**: Makes errors visible; prevents silent continuation of destructive operations
- **Example Fix**:
```python
# Before (src/hibernate_cluster.py:96)
except:
    time.sleep(5)

# After
except botocore.exceptions.ClientError as e:
    print(f'Failed to delete volume {volume_id}: {e}')
    time.sleep(5)
```

### 4. Add Pre-commit Configuration (1-2 hours)
- **Impact**: Enforces code quality at commit time
- **Implementation**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory** (15 workflows, all operational):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `hibernate_cluster.yaml` | workflow_dispatch | On-demand cluster hibernation |
| `hibernate_clusters_daily.yaml` | cron (*/30 * * * *) | Daily automated hibernation |
| `hibernate_clusters_weeend.yaml` | cron (0 1 * * 6) | Weekend hibernation |
| `hibernate_untracked_clusters_during_shutdown.yaml` | cron | Untracked cluster shutdown |
| `resume_cluster.yaml` | workflow_dispatch | On-demand cluster resume |
| `resume_clusters_daily.yaml` | cron | Daily automated resume |
| `resume_clusters_weekend.yaml` | cron (30 10 * * 1) | Monday morning resume |
| `cloud_cleaner.yaml` | cron (0 */4 * * *) | CI resource cleanup (every 4h) |
| `additional_cloud_cleaner.yaml` | cron (0 0 * * *) | Daily IAM/EIP/hosted-zone cleanup |
| `check_instance_status.yaml` | schedule | EC2 instance status check |
| `update_cluster_smartsheet.yaml` | schedule | Smartsheet data sync |
| `send_weekly_reminder.yaml` | cron (0 11 * * 3) | Wednesday cost reminders |
| `prune_rosa_roles.yaml` | cron (0 4 * * 6) | Weekly ROSA role pruning |
| `prune_oci_gcp.yaml` | schedule | GCP OCI resource pruning |

**Critical Issues**:
- No PR-triggered workflows at all
- Using outdated action versions: `actions/checkout@v3`, `actions/setup-python@v1`
- No dependency caching (pip install on every run)
- No concurrency controls on schedule-triggered workflows
- Daily hibernation runs every 30 minutes (`*/30 * * * *`) which seems excessive

### Test Coverage

**Status: ZERO**
- No `test_*.py` or `*_test.py` files anywhere in the repository
- No `tests/` or `test/` directory
- No pytest configuration (`pytest.ini`, `pyproject.toml`, `setup.cfg`)
- No test dependencies in `requirements.txt` (only boto3, smartsheet-python-sdk, requests, botocore)
- `.gitignore` includes pytest/coverage patterns (suggesting intent but no follow-through)

**Test-to-Code Ratio**: 0:4,068 (0%)

### Code Quality

**Linting**: None configured
- No `.flake8`, `ruff.toml`, `pyproject.toml`, or `pylintrc`
- No linting in any workflow

**Type Checking**: Minimal
- Some Python type hints used (e.g., `cluster:oc_cluster`, `region: str`)
- No mypy or pyright configuration
- Inconsistent type annotation style

**Pre-commit Hooks**: None
- No `.pre-commit-config.yaml`

**Code Smells**:
1. **`os.popen()` usage** - Used in `hibernate_cluster.py:199` and `cloud_cleaner.py:32` instead of `subprocess.run()`. Does not capture exit codes or stderr.
2. **Bare except clauses** - Multiple instances that swallow all exceptions silently
3. **Duplicate class definitions** - `oc_cluster` defined in both `cloud_cleaner.py` and `hibernate_cluster.py` with different field sets
4. **Commented-out code** - Large blocks of commented-out code in `cloud_cleaner.py` (lines 42-43, 86, 195-199, 218-225, 293-305)
5. **Typos in function names** - `hybernate_hypershift_cluster()` (should be "hibernate")
6. **Magic strings** - VPC IDs hardcoded (`vpc-00331e896a900165b`), NAT gateway IDs hardcoded (`nat-0fe88f6e5c09c380a`)
7. **No logging framework** - All output via `print()` statements with no structured logging

### Container Images

**Status: N/A**
- This repository does not build container images
- All Python scripts run directly on GitHub Actions `ubuntu-latest` runners
- A bundled `bin/ocm` binary (OCM CLI) is committed to the repository rather than installed from a release

### Security

**Status: Critical Gaps**
- **No SAST/CodeQL**: No static analysis configured
- **No dependency scanning**: No dependabot, renovate, or snyk
- **No secret scanning**: No gitleaks or trufflehog
- **Hardcoded resource IDs**: VPC and NAT gateway exception IDs hardcoded in source
- **Committed binary**: `bin/ocm` is a committed binary with no verification (no checksum, no signature check)
- **Command injection risk**: `os.popen(f'script/./get_all_cluster_details.sh {ocm_account}')` - if `ocm_account` input is not sanitized, shell injection is possible (mitigated by GitHub Actions input validation but still a code-level concern)
- **Broad AWS permissions implied**: Scripts require extensive AWS permissions (EC2, IAM, ELB, Route53) with no principle of least privilege documentation

### Agent Rules (Agentic Flow Quality)

**Status: Missing**
- No `CLAUDE.md` or `AGENTS.md` in root
- No `.claude/` directory
- No `.claude/rules/` for test creation guidance
- No `.claude/skills/` for custom skills
- No testing documentation in `docs/` (no docs directory exists)
- **Recommendation**: Generate comprehensive agent rules with `/test-rules-generator` covering:
  - Unit test patterns for boto3-based scripts (using moto)
  - Integration test patterns for AWS cleanup operations
  - Code conventions (error handling, logging, type hints)

## Recommendations

### Priority 0 (Critical - Safety of AWS Operations)

1. **Create a PR validation workflow** with ruff linting, py_compile syntax checks, and pytest execution. Without this, any code change can break scripts that manage production AWS resources.

2. **Write unit tests for all tag-matching and cluster identification functions**. These functions determine which AWS resources get deleted - a bug here means deleting the wrong VPCs, instances, or IAM roles.

3. **Replace `os.popen()` with `subprocess.run()`** across all files. `os.popen()` silently ignores non-zero exit codes, meaning shell script failures go unnoticed.

4. **Replace all bare `except:` clauses** with specific exception types (`botocore.exceptions.ClientError`, `ValueError`, etc.) and add proper error logging.

### Priority 1 (High Value)

5. **Add integration tests using `moto`** (AWS mock library) to test boto3-based cleanup logic without hitting real AWS APIs. Critical for `cleanup_openshift_ci_on_aws.py` (707 lines of VPC/resource deletion logic).

6. **Consolidate the duplicated `oc_cluster` class** into a shared `models.py` module. The versions in `cloud_cleaner.py` and `hibernate_cluster.py` parse cluster details differently, which could cause misidentification.

7. **Add a dry-run CI job** that exercises all cleanup scripts in simulation mode on schedule, validating that the dry-run codepaths don't crash.

8. **Update GitHub Actions versions**: `actions/checkout@v3` → `v4`, `actions/setup-python@v1` → `v5`.

### Priority 2 (Nice-to-Have)

9. **Add Dependabot** for automated dependency updates (boto3, requests have known CVEs in older versions).

10. **Create `CLAUDE.md` and agent rules** for consistent AI-assisted development patterns.

11. **Add structured logging** (Python `logging` module) to replace `print()` statements, enabling log levels and structured output.

12. **Add `CODEOWNERS`** to require reviews for changes to destructive scripts.

## Comparison to Gold Standards

| Capability | Cloud-Cost-Optimization | odh-dashboard | notebooks | kserve |
|------------|------------------------|---------------|-----------|--------|
| Unit Tests | None (0%) | Comprehensive (Jest) | Present | Extensive (Go) |
| Integration Tests | None | Contract tests | Image testing | envtest |
| E2E Tests | None | Cypress suite | Multi-arch validation | Multi-version |
| PR Validation | None | Multi-stage | Build + test | Full CI |
| Coverage Tracking | None | Codecov enforced | Partial | Codecov |
| Linting | None | ESLint + Prettier | shellcheck | golangci-lint |
| Security Scanning | None | Dependabot + CodeQL | Trivy | Snyk + CodeQL |
| Pre-commit | None | Husky | Partial | golangci |
| Agent Rules | None | Comprehensive | Partial | Partial |
| **Overall** | **1.6/10** | **9/10** | **7/10** | **8.5/10** |

## File Paths Reference

### Source Code (Python)
- `src/hibernate_cluster.py` - Core cluster hibernation logic (271 lines)
- `src/hibernate_clusters_daily.py` - Daily scheduled hibernation (261 lines)
- `src/hibernate_clusters_weekend.py` - Weekend hibernation (202 lines)
- `src/resume_cluster.py` - Cluster resume logic (277 lines)
- `src/resume_clusters_daily.py` - Daily scheduled resume (220 lines)
- `src/cleanup_openshift_ci_on_aws.py` - AWS VPC/resource cleanup (707 lines)
- `src/cloud_cleaner.py` - ELB/EBS/networking cleanup (308 lines)
- `src/iam_role_cleaner.py` - IAM role cleanup (203 lines)
- `src/elastic_ip_cleaner.py` - Elastic IP cleanup (214 lines)
- `src/instance_profile_cleaner.py` - Instance profile cleanup (237 lines)
- `src/cluster_aggregator.py` - Smartsheet cluster data aggregation (268 lines)
- `src/weekly_reminder.py` - Cost reminder notifications (121 lines)

### Shell Scripts
- `script/rosa_role_cleanup.sh` - ROSA operator role pruning (54 lines)
- `script/clean-hosted-zones.sh` - Route53 hosted zone cleanup (175 lines)
- `gcp/oci-pruner.sh` - GCP OCI resource pruning

### CI/CD
- `.github/workflows/*.yaml` - 15 operational workflows (all schedule/dispatch)

### Dependencies
- `requirements.txt` - boto3, smartsheet-python-sdk, requests, botocore
