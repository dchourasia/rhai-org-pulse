"""AI-powered categorization of conforma exceptions using Claude CLI.

Fetches the latest unshipped release from the org-pulse API, sends all its
exceptions to Claude for classification into four categories, and pushes the
enriched aiCategorization block back to the API.

Categories:
  - always_expected: inherently needed, cannot be resolved
  - long_term_fix: known resolution path but requires significant effort
  - quick_fix: straightforward fix that could be done quickly
  - already_fixed: root cause addressed, exception likely removable
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import requests

TIMEOUT = 30


def env(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "").strip()
    if required and not val:
        print(f"ERROR: Required environment variable {name!r} is not set.", file=sys.stderr)
        sys.exit(1)
    return val


def api_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def fetch_releases(backend_url: str, token: str) -> list[dict]:
    url = f"{backend_url.rstrip('/')}/api/modules/release-analysis/conforma/releases"
    resp = requests.get(url, headers=api_headers(token), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("releases", [])


def find_latest_unshipped(releases: list[dict]) -> dict | None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for r in sorted(releases, key=lambda x: x.get("gaDate", ""), reverse=True):
        if r.get("gaDate", "") > today:
            return r
    return None


def collect_exceptions(release: dict) -> list[dict]:
    """Flatten all exceptions from a release into a list for AI analysis."""
    result = []
    for policy_file in ("fbc", "registry"):
        policy_data = release.get("exceptions", {}).get(policy_file, {})

        for value in policy_data.get("configExcludes", []):
            result.append({
                "fullName": value,
                "policyFile": policy_file,
                "type": "permanent",
                "reference": None,
                "comment": None,
                "imageUrl": None,
            })

        for ex in policy_data.get("volatileExcludes", []):
            value = ex.get("value", "")
            image = ex.get("imageUrl") or ""
            full_name = f"{value}:{image}" if image else value
            result.append({
                "fullName": full_name,
                "policyFile": policy_file,
                "type": "volatile",
                "reference": ex.get("reference"),
                "comment": ex.get("comment"),
                "imageUrl": image or None,
            })

    return result


def build_prompt(exceptions: list[dict], version: str) -> str:
    exceptions_json = json.dumps(exceptions, indent=2)

    return f"""You are an expert in Red Hat OpenShift AI (RHOAI) release engineering and Enterprise Contract (EC) policies.

Analyze these EC policy exceptions for RHOAI release {version} and categorize each one.

## Context

Enterprise Contract policies enforce compliance rules on container images before release.
Exceptions (exclusions) bypass specific rules:
- **Permanent (config)**: Always-on exclusions in the policy config
- **Volatile**: Time-bounded exclusions with an effectiveUntil date, often with Jira references

## Categories

Classify each exception into exactly one category:

- **always_expected**: This exception is inherently needed and cannot be resolved. Common for rules that don't apply to RHOAI's build/release model (e.g., hermetic build requirements for certain image types, FIPS waivers for non-cryptographic components).
- **long_term_fix**: There is a known resolution path but it requires significant engineering effort (multi-sprint or cross-team coordination). The Jira reference often points to an epic or long-running tracker.
- **quick_fix**: A straightforward fix exists — updating a label, fixing test config, adding a missing annotation. Could be resolved in days, not weeks.
- **already_fixed**: The underlying issue has been addressed (merged fix, upstream update). The exception entry itself is stale and can likely be removed from the policy YAML.

## Guidelines

- Permanent exceptions without Jira references are usually **always_expected** — they represent known, accepted deviations.
- Volatile exceptions with Jira references to closed/resolved issues are likely **already_fixed**.
- Test-related exceptions (test.no_erred_tests, test.required_tests) often have clear fixes in CI configuration.
- FIPS-related exceptions may be always_expected (non-crypto components) or long_term_fix (components that need FIPS certification).
- Exceptions mentioning specific container images should be evaluated based on whether the image is still actively built.

## Exceptions to Analyze

```json
{exceptions_json}
```

## Required Output Format

Return ONLY valid JSON with this exact structure — no markdown, no explanation, no code fences:

{{"exceptions": [
  {{
    "fullName": "<exact fullName from input>",
    "policyFile": "<fbc or registry>",
    "type": "<permanent or volatile>",
    "category": "<always_expected|long_term_fix|quick_fix|already_fixed>",
    "reasoning": "<1-2 sentence explanation>"
  }}
]}}

Include ALL {len(exceptions)} exceptions from the input. Do not skip any."""


def run_claude(prompt: str) -> dict:
    """Run claude CLI and parse JSON output."""
    try:
        result = subprocess.run(
            [
                "claude",
                "-p", prompt,
                "--model", "claude-sonnet-4-6",
                "--output-format", "json",
                "--max-turns", "1",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        print("ERROR: 'claude' CLI not found. Is it installed?", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: Claude CLI timed out after 300s", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"ERROR: Claude CLI exited with code {result.returncode}", file=sys.stderr)
        print(f"  stderr: {result.stderr[:500]}", file=sys.stderr)
        sys.exit(1)

    raw = result.stdout.strip()
    try:
        outer = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse Claude CLI output as JSON: {exc}", file=sys.stderr)
        print(f"  Raw output (first 500 chars): {raw[:500]}", file=sys.stderr)
        sys.exit(1)

    text = outer.get("result", raw)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse Claude response text as JSON: {exc}", file=sys.stderr)
        print(f"  Response text (first 500 chars): {text[:500]}", file=sys.stderr)
        sys.exit(1)


def push_ai_categorization(
    backend_url: str, token: str, release: dict, ai_data: dict
) -> None:
    """Push the release back with aiCategorization attached."""
    release["aiCategorization"] = {
        "analyzedAt": datetime.now(timezone.utc).isoformat(),
        "exceptions": ai_data.get("exceptions", []),
    }

    url = f"{backend_url.rstrip('/')}/api/modules/release-analysis/conforma/bulk"
    payload = {"releases": [release], "minDate": "2020-01-01"}
    resp = requests.post(url, headers=api_headers(token), json=payload, timeout=60)
    resp.raise_for_status()
    print(f"  Pushed AI categorization (HTTP {resp.status_code})")


VALID_CATEGORIES = {"always_expected", "long_term_fix", "quick_fix", "already_fixed"}


def validate_ai_response(ai_data: dict, expected_count: int) -> list[str]:
    """Return a list of warnings about the AI response."""
    warnings = []
    exceptions = ai_data.get("exceptions", [])

    if len(exceptions) != expected_count:
        warnings.append(
            f"Expected {expected_count} exceptions, got {len(exceptions)}"
        )

    for i, ex in enumerate(exceptions):
        cat = ex.get("category", "")
        if cat not in VALID_CATEGORIES:
            warnings.append(f"  [{i}] Invalid category: {cat!r}")
        if not ex.get("reasoning"):
            warnings.append(f"  [{i}] Missing reasoning")
        if not ex.get("fullName"):
            warnings.append(f"  [{i}] Missing fullName")

    return warnings


def main() -> None:
    backend_url = env("ORG_PULSE_BACKEND_URL")
    api_token = env("ORG_PULSE_API_TOKEN")

    print("=== Conforma AI Categorization ===")
    print(f"Backend: {backend_url}")
    print()

    print("[1/4] Fetching releases from API…")
    releases = fetch_releases(backend_url, api_token)
    print(f"  Found {len(releases)} releases")

    print("\n[2/4] Finding latest unshipped release…")
    release = find_latest_unshipped(releases)
    if not release:
        print("  No unshipped release found. Nothing to categorize.")
        return

    version = release.get("version", "unknown")
    print(f"  Target: {version} (GA: {release.get('gaDate')})")

    exceptions = collect_exceptions(release)
    print(f"  Collected {len(exceptions)} exceptions ({sum(1 for e in exceptions if e['type'] == 'permanent')} permanent, {sum(1 for e in exceptions if e['type'] == 'volatile')} volatile)")

    if not exceptions:
        print("  No exceptions to categorize.")
        return

    print(f"\n[3/4] Running AI categorization via Claude CLI…")
    prompt = build_prompt(exceptions, version)
    ai_data = run_claude(prompt)

    warnings = validate_ai_response(ai_data, len(exceptions))
    if warnings:
        print("  Validation warnings:")
        for w in warnings:
            print(f"    {w}")

    categorized = ai_data.get("exceptions", [])
    by_cat = {}
    for ex in categorized:
        cat = ex.get("category", "unknown")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    print(f"  Categorized {len(categorized)} exceptions:")
    for cat, count in sorted(by_cat.items()):
        print(f"    {cat}: {count}")

    print(f"\n[4/4] Pushing AI categorization to API…")
    push_ai_categorization(backend_url, api_token, release, ai_data)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
