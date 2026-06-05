---
repository: "red-hat-data-services/product-pages-generator"
overall_score: 0.6
scorecard:
  - dimension: "Unit Tests"
    score: 1.0
    status: "Only a Spring Boot contextLoads() stub — no business logic tests"
  - dimension: "Integration/E2E"
    score: 0.0
    status: "No integration or end-to-end tests exist"
  - dimension: "Build Integration"
    score: 1.0
    status: "mvn clean install on push only; no PR-time validation"
  - dimension: "Image Testing"
    score: 0.0
    status: "No Dockerfile or container image pipeline"
  - dimension: "Coverage Tracking"
    score: 0.0
    status: "No coverage tooling or enforcement"
  - dimension: "CI/CD Automation"
    score: 2.0
    status: "Single workflow on push+cron; no PR triggers, outdated actions"
  - dimension: "Agent Rules"
    score: 0.0
    status: "No CLAUDE.md, .claude/ directory, or agent rules"
critical_gaps:
  - title: "Hardcoded API token in source code"
    impact: "SmartSheet API token is committed to public repository — active credential exposure"
    severity: "CRITICAL"
    effort: "1 hour"
  - title: "No meaningful test coverage"
    impact: "All business logic (date calculations, SmartSheet operations) is untested — regressions go undetected"
    severity: "HIGH"
    effort: "8-16 hours"
  - title: "No PR-triggered CI workflow"
    impact: "Broken code merges to main undetected; CI only runs after push"
    severity: "HIGH"
    effort: "1-2 hours"
  - title: "Outdated dependencies (Spring Boot 2.5.5, JDK 11)"
    impact: "Known CVEs in Spring Boot 2.x; JDK 11 approaching end-of-life for many vendors"
    severity: "HIGH"
    effort: "4-8 hours"
  - title: "No dependency or security scanning"
    impact: "Vulnerable transitive dependencies go undetected"
    severity: "HIGH"
    effort: "2-4 hours"
quick_wins:
  - title: "Rotate and remove the hardcoded API token"
    effort: "1 hour"
    impact: "Eliminate active credential exposure in public repository"
  - title: "Add PR trigger to CI workflow"
    effort: "30 minutes"
    impact: "Catch build failures before merge to main"
  - title: "Add unit tests for date calculation logic"
    effort: "4-6 hours"
    impact: "Test core business logic that calculates release schedules"
  - title: "Upgrade actions/checkout to v4 and use actions/setup-java"
    effort: "30 minutes"
    impact: "Faster, more reliable CI with proper Java setup and caching"
  - title: "Add Dependabot for dependency updates"
    effort: "30 minutes"
    impact: "Automated PRs for security-critical dependency updates"
recommendations:
  priority_0:
    - "IMMEDIATELY rotate the SmartSheet API token exposed in SmartsheetDateUtil.java:32 and revoke the old one"
    - "Add .gitleaks.toml and pre-commit secret scanning to prevent future credential leaks"
    - "Add PR-triggered CI workflow with build + test steps"
  priority_1:
    - "Write unit tests for calculateNextVersion(), getNextFriday(), getNextMonday(), getDatesWithoutWeekends(), getDateDifference()"
    - "Upgrade to Spring Boot 3.x and JDK 17+ (or 21 LTS)"
    - "Add JaCoCo coverage tracking with minimum threshold"
    - "Add dependency scanning (Dependabot or Snyk)"
  priority_2:
    - "Add integration tests with SmartSheet API mocking"
    - "Add code quality tools (Checkstyle, SpotBugs, or SonarQube)"
    - "Containerize the application for consistent execution"
    - "Create agent rules (.claude/rules/) for test patterns and coding standards"
---

# Quality Analysis: product-pages-generator

## Executive Summary

- **Overall Score: 0.6/10** — This repository has critical quality gaps across every measured dimension.
- **Repository Type**: Java Spring Boot CLI application (SmartSheet automation tool)
- **Primary Language**: Java 11 (Spring Boot 2.5.5) + 1 Python utility script
- **Size**: Very small — 4 main Java classes, 1 test file, 1 Python file
- **Purpose**: Automates OpenShift AI release schedule planning by reading/writing SmartSheet data
- **Key Strengths**: Solves a real operational need; uses environment variables for secrets in CI
- **Critical Gaps**: Hardcoded API token in source, zero meaningful tests, no PR validation, outdated stack
- **Agent Rules Status**: Missing — no CLAUDE.md, no .claude/ directory

## Quality Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Unit Tests | 1/10 | Only a Spring Boot contextLoads() stub — no business logic tests |
| Integration/E2E | 0/10 | No integration or end-to-end tests exist |
| **Build Integration** | **1/10** | **mvn clean install on push only; no PR-time validation** |
| Image Testing | 0/10 | No Dockerfile or container image pipeline |
| Coverage Tracking | 0/10 | No coverage tooling or enforcement |
| CI/CD Automation | 2/10 | Single workflow on push+cron; no PR triggers, outdated actions |
| Agent Rules | 0/10 | No CLAUDE.md, .claude/ directory, or agent rules |

## Critical Gaps

### 1. CRITICAL: Hardcoded API Token in Source Code
- **File**: `src/main/java/com/smartsheet/smartsheetautomation/SmartsheetDateUtil.java:32`
- **Detail**: `String accessToken = "h9ffps5tfyPBUOCArgYpsA02lQdcgnOIMEUkn";` — a SmartSheet API token is committed to a public GitHub repository
- **Impact**: Anyone with access to this repo can use this token to read/modify SmartSheet data
- **Severity**: CRITICAL
- **Effort**: 1 hour (rotate token, remove from source, add .gitleaks.toml)
- **Action**: Rotate this token IMMEDIATELY and scrub git history

### 2. No Meaningful Test Coverage
- **Detail**: The only test file (`SmartsheetAutomationApplicationTests.java`) contains a single `contextLoads()` test that verifies Spring Boot starts — no business logic is tested
- **Impact**: Core date calculation logic (version incrementing, day-of-week adjustments, release schedule generation) has zero test coverage — any change risks silent regressions
- **Severity**: HIGH
- **Effort**: 8-16 hours for comprehensive unit test suite
- **Key untested methods**: `calculateNextVersion()`, `getNextFriday()`, `getNextMonday()`, `getDatesWithoutWeekends()`, `getDateDifference()`, `writeSmartsheetData()`

### 3. No PR-Triggered CI Workflow
- **Detail**: `java-ci.yml` only triggers on `push: main` and weekly cron — there is no `pull_request` trigger
- **Impact**: Contributors can merge broken code to main without any CI feedback
- **Severity**: HIGH
- **Effort**: 1-2 hours

### 4. Outdated Dependencies
- **Detail**: Spring Boot 2.5.5 (released Oct 2021, EOL), JDK 11 (older LTS), actions/checkout@v2 (current is v4), SmartSheet SDK 2.146.0
- **Impact**: Known CVEs in Spring Boot 2.x; no security patches; incompatibility with modern tooling
- **Severity**: HIGH
- **Effort**: 4-8 hours for full upgrade

### 5. No Dependency or Security Scanning
- **Detail**: No Dependabot, Snyk, Trivy, CodeQL, or any scanning tool configured
- **Impact**: Vulnerable transitive dependencies go completely undetected
- **Severity**: HIGH
- **Effort**: 2-4 hours

## Quick Wins

### 1. Rotate and Remove Hardcoded API Token (1 hour)
Revoke the exposed token in SmartSheet, generate a new one, and remove the hardcoded value from source code. Add a `.gitleaks.toml` configuration:

```yaml
# .gitleaks.toml
title = "gitleaks config"
[extend]
useDefault = true
```

### 2. Add PR Trigger to CI Workflow (30 minutes)
Update `.github/workflows/java-ci.yml`:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'
```

### 3. Add Unit Tests for Date Logic (4-6 hours)
The date calculation methods are pure functions that are highly testable:

```java
@Test
void testCalculateNextVersion() {
    UpdateSmartsheetDateCalculation calc = ...; // needs refactoring for testability
    assertEquals("2.8", calc.calculateNextVersion("2.7"));
    assertEquals("3.0", calc.calculateNextVersion("2.9"));
}

@Test
void testGetNextFriday() {
    LocalDate wednesday = LocalDate.of(2024, 3, 6); // Wednesday
    LocalDate result = calc.getNextFriday(wednesday);
    assertEquals(DayOfWeek.FRIDAY, result.getDayOfWeek());
    assertEquals(LocalDate.of(2024, 3, 8), result);
}
```

### 4. Upgrade GitHub Actions (30 minutes)
Replace outdated actions:

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '11'
    cache: 'maven'
```

### 5. Add Dependabot (30 minutes)
Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Detailed Findings

### CI/CD Pipeline

**Workflow Inventory**: 1 workflow total

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `java-ci.yml` | push:main, cron(weekly) | Build + run the application |

**Issues Found**:
- **No PR trigger**: CI only runs on push to main — broken code reaches main before CI catches it
- **Outdated actions**: `actions/checkout@v2` (current: v4)
- **Fragile Java setup**: Uses `sudo apt-get install openjdk-11-jdk` instead of `actions/setup-java`
- **No caching**: Maven downloads all dependencies every run
- **No concurrency control**: Multiple pushes can run simultaneously
- **CI runs the application**: The workflow actually executes the JAR against the live SmartSheet API, not just tests — this is both a build step and a production operation in a single workflow
- **Secret exposure risk**: `ACCESS_TOKEN` is properly in secrets, but `SHEET_ID` is not (hardcoded in config.properties)

### Test Coverage

**Test Files**: 1

| File | Tests | Description |
|------|-------|-------------|
| `SmartsheetAutomationApplicationTests.java` | 1 | Spring Boot context load check only |

**Test-to-Code Ratio**: ~0.02 (1 trivial test / ~500 lines of business logic)

**Completely Untested Business Logic**:
- `calculateNextVersion()` — version string incrementing
- `getNextFriday()` / `getNextMonday()` — day-of-week calculations
- `getDatesWithoutWeekends()` — weekend skipping logic
- `getDateDifference()` — period calculations
- `writeSmartsheetData()` — entire SmartSheet write flow
- `getVersion()` — regex-based version extraction
- `getMonthDate()` — date formatting
- All Python API code (`ProductPageAPI.py`)

**Coverage Tracking**: None — no JaCoCo, Codecov, or any coverage tool

### Code Quality

**Linting**: None configured (no Checkstyle, PMD, SpotBugs, or SonarQube)

**Pre-commit Hooks**: None

**Static Analysis**: None

**Code Quality Observations**:
- Hardcoded API token in source (CRITICAL security issue)
- Hardcoded dates in `CombinedDateMonthDifference.java` (`LocalDate.of(2024,02,12)`, `"2024-06-10"`)
- Hardcoded sheet ID in `SmartsheetDateUtil.java` (`long sheetId = 812000691048324L`)
- Hardcoded parent ID (`Long parentIdToSearch = 2012022049378180L`)
- `printStackTrace()` used for error handling (no proper logging)
- Public mutable fields violating encapsulation (`version`, `Cells`, `rowMap`, etc.)
- Field naming convention violations (`Cells` should be `cells`)
- No logging framework (all `System.out.println`)
- Mixed responsibilities — classes do too much
- No dependency injection — manual instantiation everywhere
- Python script has placeholder values (`'YOUR_API_URL'`, `'YOUR_TOKEN'`)

### Container Images

**Status**: No container strategy

- No Dockerfile or Containerfile
- No docker-compose
- No .dockerignore
- Application is run as a bare JAR from CI
- No multi-architecture support
- No image security scanning

### Security

**Critical Issues**:
1. **Hardcoded API token**: `SmartsheetDateUtil.java:32` contains a live SmartSheet API token
2. **No secret scanning**: No Gitleaks, TruffleHog, or GitHub secret scanning
3. **No dependency scanning**: No Dependabot, Snyk, or OWASP dependency-check
4. **No SAST**: No CodeQL, Semgrep, or static analysis
5. **Outdated framework**: Spring Boot 2.5.5 has known CVEs

### Agent Rules (Agentic Flow Quality)

- **Status**: Missing
- **Coverage**: None — no `.claude/` directory, no `CLAUDE.md`, no `AGENTS.md`
- **Quality**: N/A
- **Gaps**: All test types lack agent rules; no coding standards documented for AI agents
- **Recommendation**: Generate rules with `/test-rules-generator` for unit test patterns (especially date calculation testing), integration test patterns (SmartSheet API mocking), and code quality standards

## Recommendations

### Priority 0 (Critical — Do Immediately)

1. **Rotate the exposed SmartSheet API token** — The token at `SmartsheetDateUtil.java:32` must be revoked immediately. Generate a new token and pass it exclusively via environment variables. Consider scrubbing git history with `git filter-repo`.

2. **Add secret scanning** — Configure GitHub secret scanning and add a `.gitleaks.toml` to prevent future credential commits.

3. **Add PR-triggered CI** — Update the workflow to trigger on `pull_request` events so broken code is caught before merge.

### Priority 1 (High Value — Next Sprint)

4. **Write unit tests for date calculation logic** — The pure functions (`calculateNextVersion`, `getNextFriday`, `getNextMonday`, `getDatesWithoutWeekends`, `getDateDifference`) are easily testable and form the core business logic.

5. **Upgrade to Spring Boot 3.x and JDK 17+** — Spring Boot 2.5.x is EOL. JDK 17 is the current minimum for Spring Boot 3.x and is a well-supported LTS release.

6. **Add JaCoCo coverage tracking** — Configure JaCoCo Maven plugin with at least 50% line coverage threshold on new code.

7. **Add Dependabot** — Enable automated dependency update PRs for Maven and GitHub Actions.

8. **Replace `System.out.println` with a logging framework** — Use SLF4J/Logback (already included in Spring Boot) for proper log levels and formatting.

### Priority 2 (Nice-to-Have — Backlog)

9. **Add integration tests with SmartSheet API mocking** — Use WireMock or MockServer to test SmartSheet API interactions without live credentials.

10. **Add code quality tooling** — Configure Checkstyle or SpotBugs via Maven plugin for automated code quality checks.

11. **Containerize the application** — Create a Dockerfile for reproducible builds and execution.

12. **Create agent rules** — Add `.claude/rules/` with test patterns and coding standards for AI-assisted development.

13. **Refactor for testability** — Extract date calculation logic into a standalone utility class with no SmartSheet dependencies, enabling pure unit tests.

## Comparison to Gold Standards

| Dimension | product-pages-generator | odh-dashboard | notebooks | kserve |
|-----------|------------------------|---------------|-----------|--------|
| Unit Tests | 1/10 (stub only) | 9/10 | 7/10 | 9/10 |
| Integration/E2E | 0/10 (none) | 9/10 | 8/10 | 9/10 |
| Build Integration | 1/10 (push only) | 8/10 | 8/10 | 8/10 |
| Image Testing | 0/10 (no images) | 7/10 | 9/10 | 7/10 |
| Coverage Tracking | 0/10 (none) | 8/10 | 6/10 | 9/10 |
| CI/CD Automation | 2/10 (minimal) | 9/10 | 8/10 | 9/10 |
| Agent Rules | 0/10 (none) | 8/10 | 3/10 | 2/10 |
| **Overall** | **0.6/10** | **8.5/10** | **7.5/10** | **8.0/10** |

## File Paths Reference

| Category | Path | Notes |
|----------|------|-------|
| CI/CD | `.github/workflows/java-ci.yml` | Only workflow; push+cron trigger |
| Build | `pom.xml` | Maven config; Spring Boot 2.5.5 |
| Main Source | `src/main/java/com/smartsheet/smartsheetautomation/` | 3 Java classes |
| Standalone Util | `src/main/java/CombinedDateMonthDifference.java` | Outside package; hardcoded dates |
| Test | `src/test/java/.../SmartsheetAutomationApplicationTests.java` | contextLoads() only |
| Python | `src/python/ProductPageAPI.py` | Placeholder API script |
| Config | `config.properties` | Contains sheetId, empty token fields |
| Security Issue | `src/main/java/.../SmartsheetDateUtil.java:32` | **Hardcoded API token** |
