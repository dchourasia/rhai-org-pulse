"""AI-powered categorization of conforma exceptions using Claude CLI.

Fetches the latest unshipped release from the org-pulse API, sends all its
exceptions to Claude for classification into resolution-path categories aligned
with the Security Policy Compliance Directive, and pushes the enriched
aiCategorization block back to the API.

Categories:
  - partner_permanent: binary content from hardware partners, no source available
  - platform_adoption: resolvable by migrating to AIPCC base containers/packages
  - package_onboarding: requires building new packages from source
  - component_update: component team needs to bump version pins
  - risk_accepted: formally accepted via PRODSECRM risk register with VP sign-off
  - resolved: root cause addressed, exception removable
"""

import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time
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


def find_next_upcoming(releases: list[dict]) -> dict | None:
    """Return the nearest upcoming release (earliest GA date after today).

    Matches the frontend logic which auto-selects the closest upcoming release.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming = [r for r in releases if r.get("gaDate", "") > today]
    if not upcoming:
        return None
    return min(upcoming, key=lambda x: x.get("gaDate", ""))


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


def load_guidance_docs() -> str:
    """Read all markdown files from the guidance/ directory next to this script."""
    guidance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guidance")
    docs = []
    for path in sorted(glob.glob(os.path.join(guidance_dir, "*.md"))):
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            docs.append(f"### {name}\n\n{content}")
    return "\n\n---\n\n".join(docs)


def build_prompt(exceptions: list[dict], version: str) -> str:
    exceptions_json = json.dumps(exceptions, indent=2)
    guidance_text = load_guidance_docs()

    return f"""You are an expert in Red Hat OpenShift AI (RHOAI) release engineering, Enterprise Contract (EC) policies, and the Security Policy Compliance Directive (May 2026).

Analyze these EC policy exceptions for RHOAI release {version} and categorize each one by resolution path, target release, and ProdSec policy mapping.

## Context

Enterprise Contract policies enforce compliance rules on container images before release.
Exceptions (exclusions) bypass specific rules:
- **Permanent (config)**: Always-on exclusions in the policy config
- **Volatile**: Time-bounded exclusions with an effectiveUntil date, often with Jira references

Per Chris Wright's mandate (May 2026), ProdSec will no longer grant exceptions. Products not meeting security requirements don't ship. Only Conforma exceptions mapping to ProdSec Policies are compliance-blocking (Decision #2). VP-level sign-off is required for genuinely unavoidable exceptions, tracked in PRODSECRM risk register.

## Guidance Documents

Use the following guidance documents to inform your categorization decisions — they contain the latest policy decisions, resolution paths, package triage, and compliance strategy:

{guidance_text}

## Resolution Path Categories

Classify each exception into exactly one category:

- **partner_permanent**: Binary content from hardware partners (NVIDIA, Intel, AWS, Google) — no source code available. These are permanent exceptions requiring recurring ProdSec review. Partner agreements cover redistribution rights.
- **platform_adoption**: Resolvable by migrating images to AIPCC base containers and packages. Active rollout across RHOAI python images is in progress. Includes FIPS, SBOM, base image, and hermetic build issues fixable through platform migration.
- **package_onboarding**: Requires building new packages from source or resolving complex build dependencies (bazel, haskell, C extensions). Involves cross-team coordination with AIPCC Ecosystems team.
- **component_update**: Component team needs to bump version pins, relax constraints, or make a straightforward Containerfile change (e.g., registry migration). Low complexity, single-team ownership.
- **risk_accepted**: Fundamental engineering limitation formally accepted via PRODSECRM risk register with VP sign-off. Cannot be resolved through engineering work alone (e.g., CVE triage process deviations, FBC images not shipping source containers).
- **resolved**: Root cause has been addressed (merged fix, signed RPMs available, upstream update). Exception entry is stale and can be removed from the policy YAML.

## Target Release

Estimate when each exception can realistically be resolved:

- **3.5-EA**: Already resolved or auto-extended per Decision #4. Straightforward fixes already in flight.
- **3.5-GA**: Platform adoption rollout, pure Python package onboarding, component team version bumps. Near-term.
- **3.6**: C extension packages, accelerator-specific packages, complex builds (bazel, haskell). H2 2026.
- **permanent**: Partner content, formally accepted risks. Will never be fully resolved.

## ProdSec Policy Mapping

Determine whether each exception maps to a ProdSec Security Policy (compliance-blocking):

- **true** for: CVE/vulnerability rules, hermetic build requirements, RPM signature validation, FIPS compliance, SBOM completeness, source image requirements, build-from-source requirements.
- **false** for: step_image_registries (internal tooling), schedule/weekday restrictions, task-level exceptions not tied to security policy.

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
    "category": "<partner_permanent|platform_adoption|package_onboarding|component_update|risk_accepted|resolved>",
    "targetRelease": "<3.5-EA|3.5-GA|3.6|permanent>",
    "policyMapped": true,
    "reasoning": "<1-2 sentence explanation>"
  }}
]}}

Include ALL {len(exceptions)} exceptions from the input. Do not skip any."""


def check_claude_env() -> None:
    """Print diagnostic info about Claude CLI environment."""
    print("  Claude CLI diagnostics:")
    for var in (
        "CLAUDE_CODE_USE_VERTEX", "ANTHROPIC_VERTEX_PROJECT_ID",
        "CLOUD_ML_REGION", "GOOGLE_APPLICATION_CREDENTIALS",
        "ANTHROPIC_API_KEY",
    ):
        val = os.environ.get(var, "")
        if var == "ANTHROPIC_API_KEY" and val:
            print(f"    {var} = {'*' * 8}...{val[-4:]}")
        elif val:
            print(f"    {var} = {val}")
        else:
            print(f"    {var} = (not set)")

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if creds_path:
        print(f"    Credentials file exists: {os.path.exists(creds_path)}")

    import shutil
    claude_path = shutil.which("claude")
    print(f"    claude binary: {claude_path or '(not in PATH)'}")


def check_claude_health() -> None:
    """Quick health check — verify Claude CLI can start and authenticate."""
    print("  Running health check (echo 'say ok' | claude --max-turns 1)...")
    try:
        result = subprocess.run(
            ["bash", "-c",
             "echo 'Respond with exactly: ok' | claude"
             " --model claude-sonnet-4-6"
             " --output-format stream-json"
             " --verbose"
             " --max-turns 1"
             " --dangerously-skip-permissions"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(f"    Exit code: {result.returncode}")
        if result.stderr:
            print(f"    stderr (first 300 chars): {result.stderr[:300]}")
        if result.stdout:
            print(f"    stdout (first 300 chars): {result.stdout[:300]}")
        if result.returncode != 0:
            print("  ERROR: Health check failed — Claude CLI cannot authenticate or run.", file=sys.stderr)
            sys.exit(1)
        print("  Health check passed.")
    except subprocess.TimeoutExpired:
        print("  ERROR: Health check timed out after 60s — Claude CLI is hanging.", file=sys.stderr)
        print("    This usually means Vertex AI authentication is not configured correctly.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("  ERROR: 'claude' CLI not found in PATH.", file=sys.stderr)
        sys.exit(1)


def _stream_event(event: dict) -> None:
    """Pretty-print a single stream-json event (mirrors stream-claude-output.py)."""
    etype = event.get("type", "")

    if etype == "assistant":
        for block in event.get("message", {}).get("content", []):
            bt = block.get("type")
            if bt == "text":
                print(f"    {block['text']}", flush=True)
            elif bt == "tool_use":
                name = block.get("name", "")
                inp = block.get("input", {})
                if name in ("Bash", "Shell"):
                    print(f"    > [{name}] {inp.get('command', '')}", flush=True)
                elif name in ("Edit", "Write", "Read", "StrReplace"):
                    print(f"    > [{name}] {inp.get('file_path', '')}", flush=True)
                else:
                    print(f"    > [{name}]", flush=True)

    elif etype == "result":
        cost = event.get("cost_usd")
        dur = event.get("duration_ms")
        if cost is not None:
            print(f"    Cost: ${cost:.4f}", flush=True)
        if dur is not None:
            print(f"    Duration: {dur / 1000:.1f}s", flush=True)


def run_claude(prompt: str) -> dict:
    """Run claude CLI with streaming output, mirroring run-claude.sh.

    Writes prompt to a temp file, pipes it via stdin, uses stream-json
    output format for real-time CI log visibility, then extracts the
    final result JSON.
    """
    prompt_path = None
    result_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="claude-prompt-", delete=False
        ) as pf:
            pf.write(prompt)
            prompt_path = pf.name

        result_fd, result_path = tempfile.mkstemp(
            suffix=".jsonl", prefix="claude-result-"
        )
        os.close(result_fd)

        print(f"  Prompt written to {prompt_path}")
        print(f"  Result log: {result_path}")

        # Launch Claude in background, writing stream-json to result file.
        # Mirrors run-claude.sh: claude writes to file, tail -f streams to parser.
        cmd = (
            f'cat "{prompt_path}" | claude'
            f" --model claude-sonnet-4-6"
            f" --output-format stream-json"
            f" --max-turns 1"
            f" --verbose"
            f" --dangerously-skip-permissions"
            f' >> "{result_path}" 2>&1'
        )

        proc = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Stream and pretty-print events as they arrive (like tail -f | parser).
        # Accumulate assistant text blocks — the result event may not contain
        # the full response for large outputs.
        last_size = 0
        assistant_texts: list[str] = []
        result_event = None
        deadline = time.monotonic() + 600

        def process_event(event: dict) -> None:
            nonlocal result_event
            _stream_event(event)
            etype = event.get("type", "")
            if etype == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        assistant_texts.append(block["text"])
            elif etype == "result":
                result_event = event

        def read_new_events(rf_path: str, from_pos: int) -> int:
            try:
                with open(rf_path, "r") as rf:
                    rf.seek(from_pos)
                    new_data = rf.read()
                    if new_data:
                        from_pos += len(new_data)
                        for line in new_data.splitlines():
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                process_event(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            except FileNotFoundError:
                pass
            return from_pos

        while proc.poll() is None:
            if time.monotonic() > deadline:
                proc.kill()
                proc.wait()
                print("ERROR: Claude CLI timed out after 600s", file=sys.stderr)
                try:
                    with open(result_path, "r") as rf:
                        print(f"  Partial output:\n{rf.read()[:2000]}", file=sys.stderr)
                except FileNotFoundError:
                    pass
                sys.exit(1)
            time.sleep(0.5)
            last_size = read_new_events(result_path, last_size)

        # Read any remaining output after process exits
        read_new_events(result_path, last_size)

        rc = proc.returncode
        if rc != 0:
            print(f"ERROR: Claude CLI exited with code {rc}", file=sys.stderr)
            try:
                with open(result_path, "r") as rf:
                    print(f"  Full output:\n{rf.read()[:2000]}", file=sys.stderr)
            except FileNotFoundError:
                pass
            sys.exit(1)

    finally:
        if prompt_path and os.path.exists(prompt_path):
            os.unlink(prompt_path)
        if result_path and os.path.exists(result_path):
            os.unlink(result_path)

    # Build the full response text: prefer accumulated assistant text blocks,
    # fall back to the result event's result field.
    if assistant_texts:
        text = "".join(assistant_texts)
    elif result_event:
        result_body = result_event.get("result", "")
        if isinstance(result_body, dict):
            parts = []
            for block in result_body.get("content", []):
                if block.get("type") == "text":
                    parts.append(block["text"])
            text = "\n".join(parts)
        else:
            text = str(result_body)
    else:
        print("ERROR: No assistant response or result event found", file=sys.stderr)
        sys.exit(1)

    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    # Strip control characters that Claude may inject into JSON string values
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse Claude response as JSON: {exc}", file=sys.stderr)
        print(f"  Response text (first 200 chars): {text[:200]}", file=sys.stderr)
        print(f"  Response text (last 200 chars): {text[-200:]}", file=sys.stderr)
        sys.exit(1)


def push_ai_categorization(
    backend_url: str, token: str, all_releases: list[dict],
    target_version: str, ai_data: dict
) -> None:
    """Attach aiCategorization to the target release and push ALL releases back.

    The /conforma/bulk endpoint does a full replace, so we must include every
    release — not just the one we categorized.
    """
    for release in all_releases:
        if release.get("version") == target_version:
            release["aiCategorization"] = {
                "analyzedAt": datetime.now(timezone.utc).isoformat(),
                "exceptions": ai_data.get("exceptions", []),
            }
            break

    url = f"{backend_url.rstrip('/')}/api/modules/release-analysis/conforma/bulk"
    payload = {"releases": all_releases}
    resp = requests.post(url, headers=api_headers(token), json=payload, timeout=120)
    resp.raise_for_status()
    print(f"  Pushed {len(all_releases)} releases with AI categorization (HTTP {resp.status_code})")


VALID_CATEGORIES = {
    "partner_permanent", "platform_adoption", "package_onboarding",
    "component_update", "risk_accepted", "resolved",
}
VALID_TARGET_RELEASES = {"3.5-EA", "3.5-GA", "3.6", "permanent"}


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
        target = ex.get("targetRelease", "")
        if target not in VALID_TARGET_RELEASES:
            warnings.append(f"  [{i}] Invalid targetRelease: {target!r}")
        if not isinstance(ex.get("policyMapped"), bool):
            warnings.append(f"  [{i}] policyMapped must be boolean, got: {type(ex.get('policyMapped')).__name__}")
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
    release = find_next_upcoming(releases)
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
    check_claude_env()
    check_claude_health()
    prompt = build_prompt(exceptions, version)
    print(f"  Prompt size: {len(prompt)} chars")
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
    push_ai_categorization(backend_url, api_token, releases, version, ai_data)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
