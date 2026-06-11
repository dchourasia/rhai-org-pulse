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
                "effectiveUntil": ex.get("effectiveUntil"),
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


def summarize_guidance(guidance_text: str) -> str:
    """Use Claude to summarize guidance docs into a compact reference for categorization."""
    prompt = f"""Summarize the following RHOAI security compliance guidance documents into a compact reference (under 3000 chars) for use by an AI categorizing Conforma EC policy exceptions.

Focus on:
- Category definitions and resolution paths (partner_permanent, platform_adoption, package_onboarding, component_update, risk_accepted, resolved)
- Target release timelines (which versions map to which resolution effort)
- Which ProdSec policies are compliance-blocking vs non-blocking
- Specific packages/images mentioned and their status
- Key decisions and rules

Output plain text, no markdown fences. Be dense and factual — this will be embedded in another prompt.

---

{guidance_text}"""

    prompt_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="claude-summarize-", delete=False
        ) as pf:
            pf.write(prompt)
            prompt_path = pf.name

        result = subprocess.run(
            ["bash", "-c",
             f'cat "{prompt_path}" | claude'
             " --model claude-sonnet-4-6"
             " --output-format text"
             " --max-turns 1"
             " --dangerously-skip-permissions"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"  WARNING: Summarization failed (exit {result.returncode}), using raw docs", file=sys.stderr)
            return guidance_text
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        print(f"  WARNING: Summarization failed ({exc}), using raw docs", file=sys.stderr)
        return guidance_text
    finally:
        if prompt_path and os.path.exists(prompt_path):
            os.unlink(prompt_path)


def build_prompt(exceptions: list[dict], version: str, all_versions: list[str],
                 guidance_summary: str, release_schedule: list[dict]) -> str:
    jira_prefix = "https://redhat.atlassian.net/browse/"
    image_prefix = "quay.io/rhoai/"
    compact = []
    for i, ex in enumerate(exceptions):
        name = ex["fullName"]
        if image_prefix in name:
            name = name.replace(image_prefix, "~")
        entry = {"i": i, "n": name, "p": ex["policyFile"][0], "t": ex["type"][0].upper()}
        ref = ex.get("reference") or ""
        if ref.startswith(jira_prefix):
            entry["ref"] = ref[len(jira_prefix):]
        elif ref:
            entry["ref"] = ref
        if ex.get("effectiveUntil"):
            entry["exp"] = ex["effectiveUntil"][:10]
        comment = (ex.get("comment") or "").strip()
        if comment:
            lines = [l.strip() for l in comment.splitlines() if l.strip()]
            entry["c"] = " | ".join(lines[-3:])[:120]
        compact.append(entry)
    exceptions_json = json.dumps(compact, separators=(",", ":"))

    target_release_options = " | ".join(all_versions + ["permanent"])
    schedule_lines = "\n".join(
        f"- {r['version']} (GA: {r['gaDate']})" for r in release_schedule
    )

    return f"""Categorize {len(exceptions)} EC policy exceptions for RHOAI {version}.

Input fields: i=index, n=fullName(~ = quay.io/rhoai/), p=policy(f=fbc,r=registry), t=type(P=permanent,V=volatile), ref=Jira key, exp=effectiveUntil(YYYY-MM-DD), c=recent comments.

Guidance:
{guidance_summary}

Categories: partner_permanent (partner binaries, no source), platform_adoption (AIPCC migration fixes FIPS/SBOM/hermetic/RPM), package_onboarding (build from source, bazel/haskell/C), component_update (bump pins/constraints), risk_accepted (PRODSECRM VP sign-off), resolved (stale, removable).

Upcoming release schedule:
{schedule_lines}

Target releases (use exact version strings): {target_release_options}

CRITICAL — Target release assignment rules:
1. REALISTIC FEASIBILITY: The targetRelease should be the release where the fix can realistically ship, not just when the exception expires. Exceptions can be renewed/extended if the fix isn't ready yet — expiry does NOT mean "must be done by then." Spread work across upcoming releases based on what's achievable:
   - If many exceptions share the same resolution path (e.g., 40+ hermetic builds all need AIPCC migration), split them across EA1, EA2, and GA proportionally — don't dump everything into one release.
   - Consider dependencies: if image A depends on image B being migrated first, assign B to an earlier release than A.
   - Simple items (resolved, component_update, already-in-progress platform fixes) → nearest EA release.
   - Medium items (standard platform_adoption, straightforward hermetic builds) → spread across EA1 and EA2.
   - Complex items (cross-team dependencies, multi-sprint work, complex builds) → GA or later.
2. EXPIRY AS A SIGNAL: If a volatile exception has an "exp" (effectiveUntil) date that falls BEFORE the next release's GA, it signals urgency — prioritize it for the nearest release. But if dozens of exceptions all expire at the same date, that's an extension batch, not a realistic deadline for fixing all of them.
3. HARD ITEMS GO LATER: Only defer to the next major release (e.g., 3.6) for genuinely complex work — C extension builds (bazel/haskell), accelerator-specific packages, or items explicitly blocked on external dependencies not yet available.
4. PERMANENT: Use only for partner binaries (NVIDIA, Intel, AMD, etc.) and formally accepted risks that will never be resolved.

ProdSec mapped: true=CVE/hermetic/RPM-sig/FIPS/SBOM/source/build-from-source. false=step_image_registries/schedule/non-security.

Input:
{exceptions_json}

Return ONLY valid JSON, no markdown. Use index-based compact format:
{{"e":[{{"i":0,"cat":"platform_adoption","tr":"{all_versions[0] if all_versions else 'permanent'}","pm":true,"r":"short reason"}}]}}

Fields: i=input index, cat=category, tr=targetRelease, pm=policyMapped(bool), r=reasoning(under 15 words).
Include ALL {len(exceptions)} items."""


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
        deadline = time.monotonic() + 1200

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
                print("ERROR: Claude CLI timed out after 1200s", file=sys.stderr)
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
            if assistant_texts:
                print(f"  WARN: Claude CLI exited with code {rc}, but assistant output was captured — attempting to parse", file=sys.stderr)
            else:
                print(f"ERROR: Claude CLI exited with code {rc} and no output was captured", file=sys.stderr)
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
    # Strip all markdown code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'```(?:json)?\s*\n?', '', text).strip()

    # Strip control characters that Claude may inject into JSON string values
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Large responses may be split across multiple assistant text blocks,
    # producing concatenated JSON objects: {"e":[...]}{"e":[...]}.
    # Try to parse each object separately and merge the "e" arrays.
    parsed_objects = []
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(text):
        # Skip whitespace between JSON objects
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1
        if pos >= len(text):
            break
        try:
            obj, end = decoder.raw_decode(text, pos)
            parsed_objects.append(obj)
            pos = end
        except json.JSONDecodeError:
            # Skip ahead to the next '{' and try again (handles truncated blocks)
            next_brace = text.find('{', pos + 1)
            if next_brace == -1:
                break
            pos = next_brace

    if parsed_objects:
        # Prefer the object with the most items (handles duplicated/truncated blocks)
        best = max(parsed_objects, key=lambda o: len(o.get("e") or o.get("exceptions", [])))
        items = best.get("e") or best.get("exceptions", [])
        if len(parsed_objects) > 1:
            print(f"  Parsed {len(parsed_objects)} JSON objects, using best with {len(items)} items")
        return {"e": items} if "e" in best else best

    print(f"ERROR: Could not parse Claude response as JSON", file=sys.stderr)
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


def expand_ai_response(raw: dict, exceptions: list[dict]) -> dict:
    """Expand compact AI response back to the full format expected downstream."""
    items = raw.get("e") or raw.get("exceptions", [])
    expanded = []
    for item in items:
        idx = item.get("i")
        if idx is not None and 0 <= idx < len(exceptions):
            src = exceptions[idx]
            expanded.append({
                "fullName": src["fullName"],
                "policyFile": src["policyFile"],
                "type": src["type"],
                "category": item.get("cat", item.get("category", "")),
                "targetRelease": item.get("tr", item.get("targetRelease", "")),
                "policyMapped": item.get("pm", item.get("policyMapped", True)),
                "reasoning": item.get("r", item.get("reasoning", "")),
            })
        else:
            expanded.append({
                "fullName": item.get("fullName", f"(unknown index {idx})"),
                "policyFile": item.get("policyFile", ""),
                "type": item.get("type", ""),
                "category": item.get("cat", item.get("category", "")),
                "targetRelease": item.get("tr", item.get("targetRelease", "")),
                "policyMapped": item.get("pm", item.get("policyMapped", True)),
                "reasoning": item.get("r", item.get("reasoning", "")),
            })
    return {"exceptions": expanded}


def validate_ai_response(ai_data: dict, expected_count: int, valid_versions: set[str]) -> list[str]:
    """Return a list of warnings about the AI response."""
    warnings = []
    exceptions = ai_data.get("exceptions", [])
    valid_targets = valid_versions | {"permanent"}

    if len(exceptions) != expected_count:
        warnings.append(
            f"Expected {expected_count} exceptions, got {len(exceptions)}"
        )

    for i, ex in enumerate(exceptions):
        cat = ex.get("category", "")
        if cat not in VALID_CATEGORIES:
            warnings.append(f"  [{i}] Invalid category: {cat!r}")
        target = ex.get("targetRelease", "")
        if target not in valid_targets:
            warnings.append(f"  [{i}] Invalid targetRelease: {target!r} (valid: {sorted(valid_targets)})")
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

    print("[1/5] Fetching releases from API…")
    releases = fetch_releases(backend_url, api_token)
    print(f"  Found {len(releases)} releases")

    print("\n[2/5] Finding latest unshipped release…")
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

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    release_schedule = sorted(
        [{"version": r["version"], "gaDate": r["gaDate"]}
         for r in releases if r.get("version") and r.get("gaDate", "") >= today],
        key=lambda r: r["gaDate"],
    )
    all_versions = [r["version"] for r in release_schedule]
    print(f"  Available versions for targetRelease: {all_versions}")
    print(f"  Upcoming release schedule: {[(r['version'], r['gaDate']) for r in release_schedule]}")

    print(f"\n[3/5] Summarizing guidance documents…")
    check_claude_env()
    check_claude_health()
    guidance_text = load_guidance_docs()
    print(f"  Raw guidance size: {len(guidance_text)} chars")
    guidance_summary = summarize_guidance(guidance_text)
    print(f"  Summary size: {len(guidance_summary)} chars")

    print(f"\n[4/5] Running AI categorization via Claude CLI…")
    prompt = build_prompt(exceptions, version, all_versions, guidance_summary, release_schedule)
    print(f"  Prompt size: {len(prompt)} chars")
    raw_data = run_claude(prompt)
    ai_data = expand_ai_response(raw_data, exceptions)

    warnings = validate_ai_response(ai_data, len(exceptions), set(all_versions))
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

    print(f"\n[5/5] Pushing AI categorization to API…")
    push_ai_categorization(backend_url, api_token, releases, version, ai_data)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
