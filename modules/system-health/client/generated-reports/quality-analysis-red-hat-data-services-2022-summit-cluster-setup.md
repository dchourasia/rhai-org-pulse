---
repository: "red-hat-data-services/2022-summit-cluster-setup"
overall_score: 1.2
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No tests of any kind exist in the repository"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E testing; scripts apply manifests blindly"
  - dimension: "Build Integration"
    score: 0.0
    status: "No build process; repo contains only static YAML manifests and shell scripts"
  - dimension: "Image Testing"
    score: 0.0
    status: "No container images built; references external images only"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tools, no metrics, no tracking of any kind"
  - dimension: "CI/CD Automation"
    score: 1.0
    status: "Makefile with login/deploy targets but no CI pipeline"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, AGENTS.md, or .claude/ directory"
critical_gaps:
  - title: "No CI/CD pipeline at all"
    impact: "No automated validation — manifests can break silently on any commit"
    severity: "HIGH"
    effort: "4-6 hours"
  - title: "Zero test coverage"
    impact: "No verification that manifests are valid YAML, valid K8s resources, or deployable"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "Hardcoded cluster URLs and credentials in committed files"
    impact: "Credential leakage risk; .env.local.example contains sample secrets pattern but .env is committed"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No manifest validation"
    impact: "Invalid kustomize overlays or malformed resources not caught before deploy"
    severity: "MEDIUM"
    effort: "2-4 hours"
quick_wins:
  - title: "Add a GitHub Actions workflow for YAML/kustomize lint"
    effort: "1-2 hours"
    impact: "Catch malformed manifests and kustomize build failures on every push"
  - title: "Add .env to .gitignore and remove from tracking"
    effort: "30 minutes"
    impact: "Prevent accidental credential commits"
  - title: "Add kubeval/kubeconform validation"
    effort: "1-2 hours"
    impact: "Validate K8s resource schemas against target API version"
  - title: "Add shellcheck CI step for shell scripts"
    effort: "1 hour"
    impact: "Catch common shell scripting bugs in deploy/undeploy scripts"
recommendations:
  priority_0:
    - "Add a basic CI pipeline (GitHub Actions) that validates YAML syntax, runs kustomize build, and lints shell scripts"
    - "Remove .env from version control and add to .gitignore to prevent credential leakage"
  priority_1:
    - "Add kubeconform or kubeval to validate manifests against Kubernetes API schemas"
    - "Add a dry-run deployment test using a Kind cluster in CI"
    - "Pin all image references to digests or immutable tags"
  priority_2:
    - "Add pre-commit hooks for YAML lint and gitleaks"
    - "Create agent rules (.claude/) for manifest quality standards"
    - "Document deployment verification steps and expected outcomes"
---

# Quality Analysis: 2022-summit-cluster-setup

## Executive Summary

- **Overall Score: 1.2/10**
- **Repository Type**: Infrastructure / Cluster Setup Scripts (Kubernetes manifests + shell scripts)
- **Primary Language**: Shell scripts + YAML manifests
- **Key Strengths**: Gitleaks configuration present; clean kustomize overlay structure; Makefile automation for login/deploy
- **Critical Gaps**: No CI/CD pipeline, zero tests, no manifest validation, committed .env file, no security scanning in automation
- **Agent Rules Status**: Missing — no CLAUDE.md, AGENTS.md, or .claude/ directory

This repository is a small, single-purpose deployment toolkit created for Red Hat Summit 2022. It contains 26 files (5 shell scripts, 15 YAML manifests) with a single commit. It deploys Open Data Hub (ODH) onto an OpenShift cluster using kustomize overlays. Given its nature as event-specific infrastructure tooling, the absence of quality practices is understandable but still presents risks for anyone reusing or adapting this setup.

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No tests of any kind exist |
| Integration/E2E | 0/10 | No integration or E2E testing |
| **Build Integration** | **0/10** | **No build process; static manifests only** |
| Image Testing | 0/10 | No container images built; references external images |
| Coverage Tracking | 0/10 | No coverage tools or metrics |
| CI/CD Automation | 1/10 | Makefile targets but no CI pipeline |
| Agent Rules | 0/10 | No agent rules or AI guidance |

## Critical Gaps

### 1. No CI/CD Pipeline
- **Impact**: No automated validation — manifests can break silently on any commit. Kustomize overlays could reference non-existent files, YAML could be malformed, and nobody would know until deployment fails on a live cluster.
- **Severity**: HIGH
- **Effort**: 4-6 hours
- **Details**: No `.github/workflows/` directory exists. No `.gitlab-ci.yml` or `Jenkinsfile`. The only automation is a Makefile with `login`, `deploy`, and `undeploy` targets that shell out to bash scripts.

### 2. Zero Test Coverage
- **Impact**: No verification whatsoever that the manifests are valid YAML, valid Kubernetes resources, or successfully deployable. Shell scripts have no error handling beyond basic `oc apply -k`.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: No test files of any kind (`*_test.*`, `*spec*`, `test/`, `tests/`). The repository has a test-to-code ratio of 0:1.

### 3. Credentials Risk — Committed .env File
- **Impact**: The `.env` file is committed to version control. While it currently contains only commented-out defaults, the pattern encourages storing credentials in tracked files. The `.env.local.example` shows token and password patterns.
- **Severity**: HIGH
- **Effort**: 1-2 hours
- **Details**: `.env` is tracked by git (not in `.gitignore`). The gitleaks config allowlists `storage/minio/sample-minio.yaml` and `serving/example/secret.yaml`, which means those files contain secrets that are intentionally committed.

### 4. No Manifest Validation
- **Impact**: Invalid kustomize overlays or malformed Kubernetes resources are not caught before deployment.
- **Severity**: MEDIUM
- **Effort**: 2-4 hours
- **Details**: Five kustomization.yaml files exist but are never validated in automation. A simple `kustomize build` check would catch missing resource references.

## Quick Wins

### 1. Add GitHub Actions YAML/Kustomize Lint (1-2 hours)
```yaml
# .github/workflows/validate.yml
name: Validate Manifests
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install kustomize
        run: |
          curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
          sudo mv kustomize /usr/local/bin/
      - name: Validate kustomize overlays
        run: |
          for dir in $(find . -name kustomization.yaml -exec dirname {} \;); do
            echo "Validating $dir..."
            kustomize build "$dir" > /dev/null
          done
      - name: YAML lint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: .
          config_data: |
            extends: relaxed
            rules:
              line-length: {max: 200}
```

### 2. Add .env to .gitignore (30 minutes)
Remove `.env` from tracking and add it to `.gitignore`. Keep `.env.local.example` as the template.

### 3. Add kubeval/kubeconform Validation (1-2 hours)
```yaml
      - name: Validate K8s schemas
        run: |
          wget https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz
          tar xf kubeconform-linux-amd64.tar.gz
          for dir in $(find . -name kustomization.yaml -exec dirname {} \;); do
            kustomize build "$dir" | ./kubeconform -strict -summary
          done
```

### 4. Add shellcheck for Shell Scripts (1 hour)
```yaml
      - name: ShellCheck
        uses: ludeeus/action-shellcheck@master
        with:
          scandir: '.'
```

## Detailed Findings

### CI/CD Pipeline

**Score: 1/10**

The repository has no CI/CD pipeline. The only automation is a `Makefile` with three targets:

| Target | Description |
|--------|-------------|
| `login` | Authenticates to OpenShift via `oc login` using token or user/password |
| `deploy` | Runs `kfdef/deploy.sh` — applies kustomize overlay to cluster |
| `undeploy` | Runs `kfdef/undeploy.sh` — deletes KfDef and project |

The Makefile loads environment variables from `.env` and `.env.local` files. There is no CI trigger, no workflow definition, and no automated validation.

### Test Coverage

**Score: 0/10**

Zero test files exist. No testing framework is present. No test dependencies are declared. The repository contains only deployment scripts that run `oc apply -k` commands.

### Code Quality

**Score: 1/10 (partial credit for gitleaks config)**

- **Linting**: None configured. No YAML linter, no shell linter, no manifest validator.
- **Pre-commit hooks**: None (`.pre-commit-config.yaml` does not exist).
- **Static analysis**: None.
- **Secret detection**: `.gitleaks.toml` exists and is properly configured to allowlist known sample secret files (`sample-minio.yaml`, `secret.yaml`). This is the only quality tool present.

### Container Images

**Score: 0/10**

No container images are built by this repository. It references external images in Kubernetes manifests:
- MinIO images for sample storage
- ODH notebook images
- KServe serving runtime images

No Dockerfile, Containerfile, or image build process exists.

### Security

**Score: 1/10**

- **Gitleaks**: Configuration present (`.gitleaks.toml`) — this is a positive signal
- **Container scanning**: N/A (no images built)
- **SAST/CodeQL**: Not configured
- **Dependency scanning**: N/A (no application dependencies)
- **Credential management**: Weak — `.env` committed, sample secrets in allowlisted YAML files
- **Hardcoded URLs**: `notebooks/create-notebook.sh` contains a hardcoded cluster URL

### Agent Rules (Agentic Flow Quality)

**Score: 0/10**

- **Status**: Missing
- **Coverage**: No agent rules exist for any dimension
- **Quality**: N/A
- **Gaps**: No `CLAUDE.md`, `AGENTS.md`, `.claude/` directory, or any AI-assisted development guidance
- **Recommendation**: Given the repository's small size and archival nature, agent rules would only be valuable if the repo were actively maintained or used as a template for future summit setups

## Recommendations

### Priority 0 (Critical)

1. **Add a basic CI pipeline** — Even a minimal GitHub Actions workflow that runs `kustomize build` on all overlays would catch the most obvious breakages.
2. **Remove .env from version control** — Add to `.gitignore`, remove from git tracking, ensure no credentials leak.

### Priority 1 (High Value)

1. **Add kubeconform validation** — Validate all generated manifests against Kubernetes API schemas.
2. **Add a dry-run deployment test** — Use a Kind cluster in CI to verify the full deployment flow.
3. **Pin image references** — Replace mutable tags with digests or immutable version tags in all manifest files.

### Priority 2 (Nice-to-Have)

1. **Add pre-commit hooks** — YAML lint, gitleaks, and shellcheck as pre-commit hooks.
2. **Create agent rules** — If the repo template is reused, add `.claude/rules/` with manifest authoring guidelines.
3. **Document verification steps** — Add expected deployment outcomes and manual verification checklist to README.

## Comparison to Gold Standards

| Dimension | This Repo | odh-dashboard | notebooks | kserve |
|-----------|-----------|---------------|-----------|--------|
| Unit Tests | 0/10 | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 0/10 | 9/10 | 8/10 | 9/10 |
| Build Integration | 0/10 | 8/10 | 8/10 | 7/10 |
| Image Testing | 0/10 | 7/10 | 9/10 | 7/10 |
| Coverage Tracking | 0/10 | 8/10 | 6/10 | 9/10 |
| CI/CD Automation | 1/10 | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 | 8/10 | 3/10 | 2/10 |
| **Overall** | **1.2/10** | **8.5/10** | **7.5/10** | **8.0/10** |

**Note**: This comparison is intentionally unfair. The gold standard repositories are large, actively-maintained application projects. This repository is a small, archival, event-specific cluster setup toolkit. The comparison is included for completeness but should be interpreted with this context.

## File Paths Reference

| File | Purpose |
|------|---------|
| `Makefile` | Login, deploy, undeploy automation |
| `.env` | Default environment variables (committed — risk) |
| `.env.local.example` | Template for local credential overrides |
| `.gitleaks.toml` | Secret detection allowlist configuration |
| `.gitignore` | Git ignore patterns |
| `kfdef/deploy.sh` | Deploys ODH via kustomize |
| `kfdef/undeploy.sh` | Removes ODH deployment |
| `kfdef/odh/kustomization.yaml` | Main ODH kustomize overlay |
| `kfdef/odh/kfdef.yaml` | KfDef custom resource for ODH |
| `storage/create-sample-storage.sh` | Creates MinIO sample storage |
| `storage/minio/kustomization.yaml` | MinIO kustomize overlay |
| `serving/create-example-predictors.sh` | Creates model serving examples |
| `serving/example/kustomization.yaml` | Serving example kustomize overlay |
| `notebooks/create-notebook.sh` | Creates example notebook |
| `notebooks/odh-notebooks/kustomization.yaml` | Notebook kustomize overlay |

## Context & Caveats

This repository was created for **Red Hat Summit 2022** as a one-time cluster setup utility. It has:
- **1 commit** (single initial setup)
- **26 non-git files** total
- **No application code** — only infrastructure manifests and deployment scripts

The low scores reflect the absence of quality practices, but this is partially explained by the repository's nature as event-specific, disposable infrastructure tooling rather than a maintained software project. If this pattern is reused for future events, investing in the Priority 0 and Quick Win items would provide significant value.
