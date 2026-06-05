---
repository: "red-hat-data-services/devops-runner-images"
overall_score: 4.6
scorecard:
  - dimension: "Unit Tests"
    score: 0.0
    status: "No test files exist — zero unit tests for Python scripts or Containerfile logic"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or E2E tests — no runtime validation of built images"
  - dimension: "Build Integration"
    score: 7.0
    status: "Konflux Tekton pipelines with CEL-based path filtering and multi-arch builds"
  - dimension: "Image Testing"
    score: 3.0
    status: "Multi-arch builds present but no image startup, runtime, or functional tests"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tracking — no codecov, no coverage thresholds, no reporting"
  - dimension: "CI/CD Automation"
    score: 7.5
    status: "Well-templated Tekton pipelines with Renovate for dependency updates"
  - dimension: "Security Scanning"
    score: 7.0
    status: "Clair, Snyk, Coverity, ClamAV, RPM signature scans in pipeline — but skip-checks=true on PR builds"
  - dimension: "Agent Rules"
    score: 3.0
    status: "Onboarding skill exists but no CLAUDE.md, no test rules, no quality guidelines"
critical_gaps:
  - title: "Zero test coverage — no tests of any kind"
    impact: "Python generation scripts and Containerfile correctness are entirely unvalidated; regressions go undetected"
    severity: "HIGH"
    effort: "8-12 hours"
  - title: "Security checks skipped on PR builds (skip-checks: true)"
    impact: "Clair, Snyk, Coverity, ClamAV, RPM scans only run post-merge — vulnerabilities merge uncaught"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "No image runtime validation"
    impact: "Built images are never tested for startup, tool availability, or functional correctness"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No linting or static analysis for Python scripts"
    impact: "Code quality of generation scripts is not enforced — no ruff, mypy, or pre-commit hooks"
    severity: "MEDIUM"
    effort: "2-3 hours"
quick_wins:
  - title: "Enable security checks on PR builds"
    effort: "1-2 hours"
    impact: "Surface vulnerabilities before merge — change skip-checks from true to false in PR templates"
  - title: "Add ruff linting for Python scripts"
    effort: "1-2 hours"
    impact: "Catch Python errors and enforce style in the two generation scripts"
  - title: "Add Containerfile linting with hadolint"
    effort: "1-2 hours"
    impact: "Catch Dockerfile best-practice violations and security issues in all four Containerfiles"
  - title: "Add image smoke tests that verify tool availability"
    effort: "3-4 hours"
    impact: "Validate that yq, skopeo, oc, kubectl, opm are present and executable in built images"
recommendations:
  priority_0:
    - "Enable security scanning on PR builds (set skip-checks: false in pull-request template)"
    - "Add image startup and tool-availability smoke tests for all four images"
    - "Add unit tests for generate-pipelines.py and generate-pds.py"
  priority_1:
    - "Add Python linting (ruff) and Containerfile linting (hadolint)"
    - "Add pre-commit hooks for YAML validation and Python formatting"
    - "Create CLAUDE.md with project conventions and quality standards"
    - "Add .claude/rules/ for test automation guidance"
  priority_2:
    - "Add Jinja2 template validation tests"
    - "Add YAML schema validation for generated Tekton PipelineRun files"
    - "Add SBOM generation to the pipeline"
    - "Consider image signing/attestation with cosign"
---

# Quality Analysis: devops-runner-images

## Executive Summary

- **Overall Score: 4.6/10**
- **Repository Type**: Container image factory — builds and publishes pre-built CI/CD runner images to `quay.io/rhoai-devops`
- **Primary Languages**: Python (generation scripts), Dockerfile/Containerfile, YAML (Tekton pipelines)
- **Framework**: Konflux/Tekton pipelines with Jinja2-templated PipelineRuns

### Key Strengths
- Well-architected config-driven pipeline generation (single `config.yaml` drives all Tekton YAMLs)
- Multi-architecture support (linux/x86_64 and linux/arm64) for all images
- Renovate configured for automated dependency updates with digest pinning
- Comprehensive security scanning pipeline (Clair, Snyk, Coverity, ClamAV, ShellCheck, Unicode check, RPM signature scan)
- CEL-based path filtering ensures only affected components rebuild
- Good onboarding documentation and a Claude Code skill for guided image creation

### Critical Gaps
- **Zero tests of any kind** — no unit, integration, E2E, or smoke tests exist
- **Security checks are skipped on PR builds** (`skip-checks: true`) — all scanning only runs post-merge
- **No image runtime validation** — images are built but never tested for correctness
- **No code quality tooling** — no linting, no pre-commit hooks, no static analysis for Python or Containerfiles

### Agent Rules Status: **Incomplete**
- `.claude/skills/onboarding/` exists with a useful image-creation skill
- No `CLAUDE.md` or `AGENTS.md` for project-level conventions
- No `.claude/rules/` directory for test or quality automation guidance

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 0/10 | No test files exist — zero unit tests for Python scripts or Containerfile logic |
| Integration/E2E | 0/10 | No integration or E2E tests — no runtime validation of built images |
| **Build Integration** | **7/10** | **Konflux Tekton pipelines with CEL-based path filtering and multi-arch builds** |
| Image Testing | 3/10 | Multi-arch builds present but no image startup, runtime, or functional tests |
| Coverage Tracking | 0/10 | No coverage tracking — no codecov, no coverage thresholds, no reporting |
| CI/CD Automation | 7.5/10 | Well-templated Tekton pipelines with Renovate for dependency updates |
| Security Scanning | 7/10 | Clair, Snyk, Coverity, ClamAV, RPM scans in pipeline — but skip-checks=true on PRs |
| Agent Rules | 3/10 | Onboarding skill exists but no CLAUDE.md, no test rules, no quality guidelines |

## Critical Gaps

### 1. Zero Test Coverage — No Tests of Any Kind
- **Impact**: Python generation scripts (`generate-pipelines.py`, `generate-pds.py`) and Containerfile correctness are entirely unvalidated. Regressions in template rendering, YAML structure, or tool installation go undetected until downstream consumers fail.
- **Severity**: HIGH
- **Effort**: 8-12 hours
- **Details**: The repo has 2 Python scripts (93 lines) and 4 Containerfiles. None have associated tests. There is no `test/` directory, no `*_test.py` files, no `pytest.ini`, no test framework configuration.

### 2. Security Checks Skipped on PR Builds
- **Impact**: The Tekton pipeline includes 7 security scanning tasks (Clair, Snyk SAST, Coverity SAST, ClamAV, ShellCheck, Unicode check, RPM signature scan), but all are gated by `skip-checks` which is set to `true` in both pull-request and push templates. This means vulnerabilities are not caught at any stage.
- **Severity**: HIGH
- **Effort**: 1-2 hours (change `skip-checks: true` to `skip-checks: false` in the pull-request Jinja2 template)
- **File**: `.tekton/templates/pull-request.yaml.j2` line 54, `.tekton/templates/push.yaml.j2` line 52

### 3. No Image Runtime Validation
- **Impact**: Built images are pushed to quay.io without any verification that installed tools work. If `yq`, `skopeo`, `oc`, `kubectl`, or `opm` fail to install or are the wrong version, it's only discovered when a downstream CI job fails.
- **Severity**: HIGH
- **Effort**: 4-8 hours
- **Details**: No Testcontainers, no `docker run` smoke tests, no tool-version assertions.

### 4. No Linting or Static Analysis
- **Impact**: Python code quality is unenforced. Containerfiles could contain security antipatterns or inefficiencies without detection.
- **Severity**: MEDIUM
- **Effort**: 2-3 hours
- **Details**: No `ruff.toml`, `.flake8`, `mypy.ini`, `.golangci.yaml`, `.eslintrc`, `.pre-commit-config.yaml`, or `hadolint` configuration found.

## Quick Wins

### 1. Enable Security Checks on PR Builds (1-2 hours)
Change `skip-checks: true` to `skip-checks: false` in the pull-request template. This immediately enables Clair vulnerability scanning, Snyk SAST, Coverity SAST, ClamAV malware scanning, ShellCheck, Unicode check, and RPM signature validation on every PR.

```yaml
# .tekton/templates/pull-request.yaml.j2, line 54
# Change:
  - name: skip-checks
    value: true
# To:
  - name: skip-checks
    value: "false"
```

Then regenerate: `uv run scripts/generate-pipelines.py`

### 2. Add Ruff Linting for Python Scripts (1-2 hours)
Create a `ruff.toml` and add a pre-commit or CI check:

```toml
# ruff.toml
target-version = "py311"
line-length = 120

[lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B"]
```

### 3. Add Hadolint for Containerfile Linting (1-2 hours)
Add hadolint to validate all Containerfiles for best practices:

```bash
# Run locally or in CI
hadolint builds/*/Containerfile
```

### 4. Add Image Smoke Tests (3-4 hours)
Create a simple test script that validates tool availability after image build:

```bash
#!/bin/bash
# test-image.sh <image-name>
IMAGE=$1
echo "Testing $IMAGE..."

# Verify tools are present and executable
podman run --rm "$IMAGE" yq --version
podman run --rm "$IMAGE" skopeo --version
podman run --rm "$IMAGE" git --version
podman run --rm "$IMAGE" jq --version

# For openshift-utils image
if [[ "$IMAGE" == *"openshift-utils"* ]]; then
  podman run --rm "$IMAGE" oc version --client
  podman run --rm "$IMAGE" kubectl version --client
  podman run --rm "$IMAGE" opm version
fi
```

## Detailed Findings

### CI/CD Pipeline

**Architecture**: The repo uses Konflux/Tekton for CI/CD with a config-driven approach:
- `config.yaml` defines all components (4 images)
- `scripts/generate-pipelines.py` generates Tekton PipelineRun YAMLs from Jinja2 templates
- Each component gets a pull-request and push PipelineRun
- CEL expressions in `pipelinesascode.tekton.dev/on-cel-expression` ensure only affected components rebuild

**Strengths**:
- DRY pipeline generation — adding a new image only requires a `config.yaml` entry + `Containerfile`
- Path-based triggering via CEL expressions avoids unnecessary builds
- `cancel-in-progress: true` on PR builds prevents resource waste
- `max-keep-runs: 3` keeps PipelineRun history manageable
- PR images tagged `on-pr-{revision}` with 5-day expiry
- Push images tagged with commit SHA + `latest`

**Weaknesses**:
- `skip-checks: true` on ALL PipelineRuns (both PR and push) — security scanning is effectively disabled
- No test tasks in the pipeline — build-only, no validation
- No GitHub Actions workflows — everything runs in Konflux (no local CI option)

**Pipeline Tasks** (from `multi-arch-container-build.yaml`):
1. `init` — cache proxy setup
2. `clone-repository` — git clone via OCI trusted artifacts
3. `prefetch-dependencies` — dependency caching
4. `build-images` — multi-arch buildah builds (matrix over platforms)
5. `build-image-index` — create OCI image index
6. `build-source-image` — source image generation (optional)
7. `deprecated-base-image-check` — deprecated image detection
8. `clair-scan` — vulnerability scanning (SKIPPED)
9. `ecosystem-cert-preflight-checks` — Red Hat certification checks (SKIPPED)
10. `sast-snyk-check` — Snyk SAST analysis (SKIPPED)
11. `clamav-scan` — malware scanning (SKIPPED)
12. `sast-coverity-check` — Coverity SAST analysis (SKIPPED)
13. `sast-shell-check` — ShellCheck analysis (SKIPPED)
14. `sast-unicode-check` — Unicode trojan detection (SKIPPED)
15. `apply-tags` — tag management
16. `push-dockerfile` — Dockerfile archival
17. `rpms-signature-scan` — RPM signature verification (SKIPPED)

### Test Coverage

**Status**: No tests exist. Zero test files found in the repository.

- No `*_test.py`, `test_*.py`, `*.spec.*`, or `*_test.*` files
- No `test/`, `tests/`, `e2e/`, or `integration/` directories
- No `pytest.ini`, `setup.cfg` test config, or `pyproject.toml` with test configuration
- No `Makefile` with test targets
- No test framework dependencies declared

**What should be tested**:
1. `generate-pipelines.py` — does it produce valid YAML? Does it handle all config fields correctly?
2. `generate-pds.py` — does it produce valid Konflux ProjectDevelopmentStream YAML?
3. Jinja2 templates — do they render correctly with various inputs (with/without `additional_secret`)?
4. Built images — do they contain the expected tools at the expected versions?
5. `argfile.conf` — are digest references valid and resolvable?

### Code Quality

**Status**: No code quality tooling is configured.

- No linter configuration (no `ruff.toml`, `.flake8`, `mypy.ini`)
- No pre-commit hooks (no `.pre-commit-config.yaml`)
- No static analysis tools
- No code formatters configured
- No Containerfile linting (no hadolint)
- No YAML validation (no yamllint)

The two Python scripts are clean and well-structured (PEP 723 inline dependencies, proper `__main__` guard), but there's nothing to enforce that quality going forward.

### Container Images

**Architecture**: 4 images in a layered hierarchy:

```
UBI 9
└── base-runner (yq, skopeo, podman, git, jq, gettext)
    ├── openshift-utils (oc, kubectl, opm)
    ├── tracer (tracer.sh from private repo)
    └── slack-notifier (tracer.sh, send-slack-message.sh, tracer-diff.sh)
```

**Strengths**:
- All images build for linux/x86_64 and linux/arm64
- Base images pinned with SHA256 digests in `argfile.conf` for reproducible builds
- Renovate auto-updates base image digests and Tekton bundle references
- Multi-stage builds used for images requiring private repo access (tracer, slack-notifier)
- Build secrets properly mounted via `--mount=type=secret` (not baked into image layers)

**Weaknesses**:
- No `.dockerignore` files (the `.gitignore` only ignores `.konflux/`)
- No image labels (no `LABEL maintainer`, `version`, `description`)
- No `HEALTHCHECK` instructions
- `base/Containerfile` runs `dnf install` without `dnf clean all` (larger image size)
- No USER instruction — images run as root by default
- `openshift-utils/Containerfile` hardcodes `TARGETARCH=arm64` as default (may confuse local x86 builds)
- No runtime validation — no smoke tests verify tool availability post-build

### Security

**Status**: Strong scanning pipeline is defined but entirely disabled.

**Pipeline Security Tasks** (all gated by `skip-checks` which is `true`):
- **Clair scan** — container vulnerability scanning (per-platform matrix)
- **Snyk SAST** — static application security testing
- **Coverity SAST** — advanced static analysis (gated by availability check)
- **ClamAV** — malware scanning (per-platform matrix)
- **ShellCheck SAST** — shell script analysis
- **Unicode check** — Unicode-based trojan source detection
- **RPM signature scan** — RPM package signature verification
- **Ecosystem cert preflight** — Red Hat certification checks
- **Deprecated image check** — base image deprecation detection

**Positive**:
- Renovate pins digests for all base images — supply chain security
- Build secrets use Tekton `--mount=type=secret` — never baked into layers
- Trusted artifacts (OCI-based) for pipeline data sharing
- Source image generation capability for compliance

**Gaps**:
- `skip-checks: true` on all PipelineRuns — no scanning runs at all
- No `.trivyignore` or vulnerability exception management
- No SBOM generation
- No image signing (cosign/sigstore)
- No secret scanning (gitleaks/trufflehog) on the repo itself

### Agent Rules (Agentic Flow Quality)

**Status**: Incomplete

- **Present**: `.claude/skills/onboarding/SKILL.md` — a well-designed guided skill for adding new images
- **Missing**:
  - No `CLAUDE.md` root configuration file
  - No `AGENTS.md` for agent behavior guidelines
  - No `.claude/rules/` directory
  - No test automation rules
  - No code quality rules
  - No Containerfile best-practice rules

**Quality of existing skill**: Good. The onboarding skill is conversational, step-by-step, and references actual project documentation. It restricts allowed tools appropriately.

**Recommendation**: Generate missing rules with `/test-rules-generator` to add:
- Unit test rules for Python scripts
- Containerfile best practices
- YAML validation rules for Tekton pipelines

## Recommendations

### Priority 0 (Critical)

1. **Enable security scanning on PR builds**
   - Change `skip-checks: true` to `false` in `.tekton/templates/pull-request.yaml.j2`
   - Also enable on push builds in `.tekton/templates/push.yaml.j2`
   - Regenerate all PipelineRun YAMLs with `uv run scripts/generate-pipelines.py`
   - **Effort**: 1-2 hours | **Impact**: Immediate security coverage

2. **Add image smoke tests**
   - Create a Tekton task or post-build script that validates tool availability in each image
   - Test that `yq`, `skopeo`, `podman`, `git`, `jq`, `gettext` exist and are executable in base-runner
   - Test `oc`, `kubectl`, `opm` in openshift-utils
   - Test `tracer.sh` in tracer image
   - **Effort**: 4-8 hours | **Impact**: Catch broken images before they hit downstream CI

3. **Add unit tests for Python generation scripts**
   - Test `generate-pipelines.py` produces valid YAML for each component
   - Test `generate-pds.py` produces valid Konflux PDS YAML
   - Test template rendering with and without `additional_secret`
   - Test edge cases (empty components list, missing fields)
   - **Effort**: 4-6 hours | **Impact**: Prevent template regressions

### Priority 1 (High Value)

4. **Add Python linting with ruff**
   - Configure `ruff.toml` for the two generation scripts
   - Add a CI check or pre-commit hook
   - **Effort**: 1-2 hours

5. **Add Containerfile linting with hadolint**
   - Validate all 4 Containerfiles for best practices
   - Add `dnf clean all` to base Containerfile
   - Add image labels and USER instruction
   - **Effort**: 2-3 hours

6. **Create CLAUDE.md with project conventions**
   - Document code style, commit conventions, PR requirements
   - Define quality standards for new images
   - **Effort**: 2-3 hours

7. **Add .claude/rules/ for test automation**
   - Create rules for Python unit tests
   - Create rules for Containerfile validation
   - Create rules for YAML structure validation
   - **Effort**: 3-4 hours

8. **Add pre-commit hooks**
   - YAML validation (yamllint)
   - Python formatting (ruff format)
   - Containerfile linting (hadolint)
   - **Effort**: 2-3 hours

### Priority 2 (Nice-to-Have)

9. **Add YAML schema validation for generated Tekton files**
   - Validate generated PipelineRun YAMLs against Tekton schema
   - **Effort**: 4-6 hours

10. **Add SBOM generation to the pipeline**
    - Use Syft or Trivy to generate SBOMs for all images
    - **Effort**: 2-4 hours

11. **Add image signing with cosign**
    - Sign images after build for supply chain integrity
    - **Effort**: 4-6 hours

12. **Add `.dockerignore` files**
    - Reduce build context size for each image
    - **Effort**: 1 hour

13. **Add Renovate-generated YAML validation**
    - Validate that Renovate PRs produce valid PipelineRun YAMLs after auto-merge
    - **Effort**: 2-3 hours

## Comparison to Gold Standards

| Dimension | devops-runner-images | odh-dashboard | notebooks | kserve |
|-----------|---------------------|---------------|-----------|--------|
| Unit Tests | 0/10 - None | 9/10 - Jest/Cypress | 7/10 - pytest | 8/10 - Go testing |
| Integration/E2E | 0/10 - None | 9/10 - Cypress E2E | 8/10 - Robot | 9/10 - Envtest |
| Build Integration | 7/10 - Konflux | 7/10 - GitHub Actions | 6/10 - GitHub Actions | 7/10 - Prow |
| Image Testing | 3/10 - Build only | 6/10 - Container tests | 9/10 - 5-layer validation | 7/10 - Image build |
| Coverage Tracking | 0/10 - None | 8/10 - Codecov | 5/10 - Basic | 8/10 - Codecov |
| CI/CD Automation | 7.5/10 - Tekton + Renovate | 9/10 - Full automation | 8/10 - Periodic + PR | 9/10 - Prow + periodic |
| Security Scanning | 7/10 - Defined but skipped | 7/10 - Snyk/CodeQL | 6/10 - Basic Trivy | 8/10 - Multiple tools |
| Agent Rules | 3/10 - Onboarding only | 8/10 - Comprehensive | 3/10 - Basic | 2/10 - None |

**Key Takeaway**: The repository has excellent CI/CD architecture (config-driven Tekton pipelines, Renovate, multi-arch) but is severely lacking in testing and quality enforcement. The security scanning infrastructure is comprehensive but disabled. Enabling existing capabilities and adding basic tests would dramatically improve the score.

## File Paths Reference

| File | Purpose |
|------|---------|
| `config.yaml` | Central component configuration |
| `scripts/generate-pipelines.py` | Generates Tekton PipelineRun YAMLs |
| `scripts/generate-pds.py` | Generates Konflux PDS YAML |
| `.tekton/templates/pull-request.yaml.j2` | PR PipelineRun template |
| `.tekton/templates/push.yaml.j2` | Push PipelineRun template |
| `.tekton/pipelines/multi-arch-container-build.yaml` | Multi-arch build pipeline |
| `builds/base/Containerfile` | Base runner image |
| `builds/openshift-utils/Containerfile` | OpenShift utils image |
| `builds/tracer/Containerfile` | Tracer image |
| `builds/slack-notifier/Containerfile` | Slack notifier image |
| `builds/*/argfile.conf` | Pinned base image digests |
| `renovate.json5` | Renovate dependency update config |
| `.claude/skills/onboarding/SKILL.md` | Image onboarding skill |
| `docs/onboarding.md` | Onboarding documentation |
