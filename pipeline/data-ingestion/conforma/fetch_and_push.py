"""Fetch RHOAI conforma policy exceptions from GitLab and push to org-pulse API.

Data sources:
  - Smartsheet: RHOAI GA schedule (Code Freeze + GA dates per release version)
  - GitLab (gitlab.cee.redhat.com): git history of two Enterprise Contract Policy YAMLs
    * fbc-rhoai-prod.yaml
    * registry-rhoai-prod.yaml

For each release (GA date >= MIN_DATE) we:
  1. Find the git commit just before the GA date for each policy YAML.
  2. Fetch and parse the YAML at that snapshot.
  3. Extract permanent config exclusions and volatile time-bound exclusions.
  4. Push all releases to the org-pulse API (DELETE existing, then POST bulk).
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import quote

import requests
import yaml
from dateutil import parser as dateutil_parser

# ─── Constants ───────────────────────────────────────────────────────────────

SMARTSHEET_BASE = "https://api.smartsheet.com/2.0"
SMARTSHEET_SHEET_ID = "rRgRc8jPQpQPfJpqvJwf3M6fXJvRpFhqhWXgHpW1"

GITLAB_BASE = "https://gitlab.cee.redhat.com/api/v4"
GITLAB_PROJECT = "releng%2Fkonflux-release-data"

FBC_FILE = "config/stone-prod-p02.hjvn.p1/product/EnterpriseContractPolicy/fbc-rhoai-prod.yaml"
REGISTRY_FILE = "config/stone-prod-p02.hjvn.p1/product/EnterpriseContractPolicy/registry-rhoai-prod.yaml"

# Only RHOAI 2.x and 3.x releases
VERSION_PATTERN = re.compile(r'^rhoai-[23]\.\d')

# Task name keyword matching
GA_KEYWORDS = re.compile(r'\bGA\b|\bRELEASE\b', re.IGNORECASE)
GA_EXCLUDES  = re.compile(r'code\s*freeze|release\s*notes|release\s*window|release\s*candidate|release\s*checklist|CCS\s*content|planning\s*freeze|initial\s*RC', re.IGNORECASE)
CF_KEYWORDS  = re.compile(r'code\s*freeze', re.IGNORECASE)
RELEASE_WINDOW_RE = re.compile(r'release\s*window', re.IGNORECASE)

TIMEOUT = 30  # seconds for HTTP requests


# ─── Env helpers ─────────────────────────────────────────────────────────────

def env(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "").strip()
    if required and not val:
        print(f"ERROR: Required environment variable {name!r} is not set.", file=sys.stderr)
        sys.exit(1)
    return val


# ─── Smartsheet ───────────────────────────────────────────────────────────────

PAGE_SIZE = 500

def fetch_smartsheet_rows(token: str) -> list[dict]:
    """Paginate through the sheet and return all rows as dicts with column titles as keys."""
    headers = {"Authorization": f"Bearer {token}"}
    all_rows = []
    page = 1
    cols = None

    while True:
        url = f"{SMARTSHEET_BASE}/sheets/{SMARTSHEET_SHEET_ID}?pageSize={PAGE_SIZE}&page={page}"
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        if cols is None:
            cols = {c["id"]: c["title"] for c in data.get("columns", [])}

        rows = data.get("rows", [])
        for row in rows:
            cells = {
                cols.get(c["columnId"], str(c["columnId"])):
                    c.get("displayValue") or c.get("value") or ""
                for c in row.get("cells", [])
            }
            all_rows.append(cells)

        print(f"  Page {page}: {len(rows)} rows (total so far: {len(all_rows)})")

        # Stop when we receive fewer rows than the page size — no more pages
        if len(rows) < PAGE_SIZE:
            break
        page += 1

    return all_rows


def parse_finish_date(raw: str) -> str | None:
    """Parse a Smartsheet finish date string to YYYY-MM-DD."""
    if not raw:
        return None
    try:
        # Smartsheet returns ISO 8601 strings like "2026-04-10T16:59:59"
        return dateutil_parser.parse(raw).date().isoformat()
    except Exception:
        return None


def extract_releases_from_smartsheet(rows: list[dict], min_date: str) -> list[dict]:
    """Group rows by shortname and extract GA + Code Freeze dates.

    Falls back to the 'Release Window' Finish date as GA date ONLY when no
    explicit GA / RHOAI RELEASE row exists at all for a version.  This prevents
    old versions (e.g. rhoai-2.16.x) whose maintenance Release Window rows have
    recent dates from being incorrectly treated as new releases.  EA and z-stream
    releases that never have an explicit GA row pick up the Release Window date
    as intended.
    """
    grouped: dict[str, dict] = {}
    rw_dates: dict[str, str] = {}  # shortname → Release Window Finish (GA fallback)

    for row in rows:
        shortname = (row.get("shortname") or "").strip()
        if not shortname or not VERSION_PATTERN.match(shortname):
            continue

        task = (row.get("Task Name") or "").strip()
        finish = parse_finish_date(row.get("Finish") or "")
        if not finish:
            continue

        entry = grouped.setdefault(shortname, {
            "version": shortname,
            "gaDate": None,
            "codeFreezeDate": None,
            "_hasExplicitGA": False,  # removed before pushing to API
        })

        if CF_KEYWORDS.search(task) and not GA_EXCLUDES.search(task):
            # Keep the latest code freeze date if multiple rows match
            if entry["codeFreezeDate"] is None or finish > entry["codeFreezeDate"]:
                entry["codeFreezeDate"] = finish

        elif GA_KEYWORDS.search(task) and not GA_EXCLUDES.search(task):
            # Explicit GA / RHOAI RELEASE row — always takes priority
            if entry["gaDate"] is None or finish > entry["gaDate"]:
                entry["gaDate"] = finish
            entry["_hasExplicitGA"] = True

        elif RELEASE_WINDOW_RE.search(task):
            # Track as fallback; applied only when _hasExplicitGA is False
            if shortname not in rw_dates or finish > rw_dates[shortname]:
                rw_dates[shortname] = finish

    result = []
    for entry in grouped.values():
        has_explicit = entry.pop("_hasExplicitGA", False)
        ga = entry.get("gaDate")

        if not ga and not has_explicit:
            # No explicit GA row found anywhere → try Release Window fallback
            ga = rw_dates.get(entry["version"])
            if ga:
                entry["gaDate"] = ga
                print(f"  INFO: {entry['version']}: no explicit GA row, using Release Window date {ga}")

        if not ga or ga < min_date:
            continue
        result.append(entry)

    return sorted(result, key=lambda r: r["gaDate"], reverse=True)


# ─── GitLab ──────────────────────────────────────────────────────────────────

def gitlab_headers(token: str) -> dict:
    return {"PRIVATE-TOKEN": token}


def find_commit_before_date(file_path: str, before_date: str, token: str) -> str | None:
    """Return SHA of the latest commit touching file_path strictly before before_date."""
    encoded_path = quote(file_path, safe="")
    # Append T23:59:59Z so all commits on GA day itself are included
    until = f"{before_date}T23:59:59Z"
    url = (
        f"{GITLAB_BASE}/projects/{GITLAB_PROJECT}/repository/commits"
        f"?path={encoded_path}&until={until}&per_page=1&ref_name=main"
    )
    resp = requests.get(url, headers=gitlab_headers(token), timeout=TIMEOUT)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    commits = resp.json()
    if not commits:
        return None
    return commits[0]["id"]


def fetch_file_at_commit(file_path: str, commit_sha: str, token: str) -> str | None:
    """Fetch raw file content at a specific commit SHA."""
    encoded_path = quote(file_path, safe="")
    url = f"{GITLAB_BASE}/projects/{GITLAB_PROJECT}/repository/files/{encoded_path}/raw?ref={commit_sha}"
    resp = requests.get(url, headers=gitlab_headers(token), timeout=TIMEOUT)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.text


# ─── YAML parsing ────────────────────────────────────────────────────────────

def extract_comments_before_value_blocks(raw_yaml: str) -> dict[str, str]:
    """Scan raw YAML text to find comment lines immediately preceding '- value:' entries.

    Returns a dict mapping the value string to the concatenated comment text.
    Comment blocks start when a line begins with '          #' (indented) and end
    at the '- value:' line they precede.
    """
    result = {}
    lines = raw_yaml.splitlines()
    pending_comments = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            # Accumulate comment lines
            pending_comments.append(stripped.lstrip("#").strip())
        elif stripped.startswith("- value:"):
            # Extract the value from this line
            m = re.match(r"-\s+value:\s+(.+)", stripped)
            if m:
                value = m.group(1).strip().strip('"').strip("'")
                if pending_comments:
                    result[value] = " ".join(pending_comments)
            pending_comments = []
        elif stripped and not stripped.startswith("#"):
            # Non-comment, non-value line resets the comment buffer
            pending_comments = []

    return result


def parse_policy_yaml(raw_text: str) -> dict:
    """Parse an Enterprise Contract Policy YAML and extract exception lists.

    Returns:
        {
          "configExcludes": ["rule.name", ...],        # permanent, always-on
          "volatileExcludes": [                        # time-bounded
              {
                "value": "...",
                "effectiveUntil": "2026-...",
                "reference": "https://...",
                "imageUrl": None | "quay.io/...",
                "comment": "..."
              }, ...
          ]
        }
    """
    try:
        doc = yaml.safe_load(raw_text) or {}
    except yaml.YAMLError as exc:
        print(f"    WARN: YAML parse error: {exc}")
        return {"configExcludes": [], "volatileExcludes": []}

    comments_map = extract_comments_before_value_blocks(raw_text)

    sources = (doc.get("spec") or {}).get("sources") or []
    source = sources[0] if sources else {}

    # Permanent config exclusions
    config_excludes_raw = (source.get("config") or {}).get("exclude") or []
    config_excludes = []
    for entry in config_excludes_raw:
        if isinstance(entry, str) and entry.strip():
            config_excludes.append(entry.strip())
        elif isinstance(entry, dict) and entry.get("value"):
            config_excludes.append(str(entry["value"]).strip())

    # Volatile time-bounded exclusions
    volatile_raw = (source.get("volatileConfig") or {}).get("exclude") or []
    volatile_excludes = []
    for entry in volatile_raw:
        if isinstance(entry, str):
            # Some older policies may have string entries here
            volatile_excludes.append({
                "value": entry.strip(),
                "effectiveUntil": None,
                "reference": None,
                "imageUrl": None,
                "comment": comments_map.get(entry.strip())
            })
        elif isinstance(entry, dict):
            value = str(entry.get("value") or "").strip()
            if not value:
                continue
            volatile_excludes.append({
                "value": value,
                "effectiveUntil": str(entry["effectiveUntil"]) if entry.get("effectiveUntil") else None,
                "reference": str(entry["reference"]) if entry.get("reference") else None,
                "imageUrl": str(entry["imageUrl"]) if entry.get("imageUrl") else None,
                "comment": comments_map.get(value)
            })

    return {"configExcludes": config_excludes, "volatileExcludes": volatile_excludes}


# ─── Jira extension detection ──────────────────────────────────────────────

EXTENSION_TEMPLATE_KEY = "RHOAIENG-62569"

def full_exception_name(exclude: dict) -> str:
    value = exclude.get("value", "")
    image = exclude.get("imageUrl") or ""
    return f"{value}:{image}" if image else value


def detect_extension_jira_issues(release: dict, jira_base_url: str, jira_email: str, jira_token: str) -> None:
    """Find Jira issues cloned from EXTENSION_TEMPLATE_KEY that match volatile exceptions.

    Matches by label 'Exception: <full-exception-name>'. Updates volatile excludes
    in-place with extensionJiraKey and extensionJiraUrl.
    """
    all_volatiles = []
    for pf in ["fbc", "registry"]:
        for ex in (release.get("exceptions", {}).get(pf, {}).get("volatileExcludes") or []):
            all_volatiles.append(ex)

    if not all_volatiles:
        print("    No volatile exceptions to check")
        return

    name_to_excludes: dict[str, list[dict]] = {}
    for ex in all_volatiles:
        name = full_exception_name(ex)
        name_to_excludes.setdefault(name, []).append(ex)

    jql = (
        f'project = RHOAIENG AND issue in linkedIssues("{EXTENSION_TEMPLATE_KEY}", "is cloned by") '
        f'AND status not in ("Closed", "Done", "Resolved")'
    )
    auth = (jira_email, jira_token)
    url = f"{jira_base_url.rstrip('/')}/rest/api/3/search"
    params = {"jql": jql, "fields": "key,labels", "maxResults": 200}

    try:
        resp = requests.get(url, params=params, auth=auth, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as exc:
        print(f"    WARN: Jira extension detection failed: {exc}")
        return

    issues = resp.json().get("issues", [])
    print(f"    Found {len(issues)} open extension Jira issues")

    matched = 0
    for issue in issues:
        key = issue["key"]
        labels = issue.get("fields", {}).get("labels", [])
        for label in labels:
            if not label.startswith("Exception: "):
                continue
            exc_name = label[len("Exception: "):]
            if exc_name in name_to_excludes:
                for ex in name_to_excludes[exc_name]:
                    ex["extensionJiraKey"] = key
                    ex["extensionJiraUrl"] = f"{jira_base_url.rstrip('/')}/browse/{key}"
                    matched += 1

    print(f"    Matched {matched} volatile exception(s) to existing Jira issues")


# ─── API calls ───────────────────────────────────────────────────────────────

def api_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def clear_existing(backend_url: str, token: str) -> None:
    url = f"{backend_url.rstrip('/')}/api/modules/release-analysis/conforma"
    resp = requests.delete(url, headers=api_headers(token), timeout=TIMEOUT)
    if resp.status_code not in (204, 404):
        resp.raise_for_status()
    print(f"  Cleared existing data (HTTP {resp.status_code})")


def push_bulk(backend_url: str, token: str, releases: list[dict], min_date: str) -> dict:
    url = f"{backend_url.rstrip('/')}/api/modules/release-analysis/conforma/bulk"
    payload = {"releases": releases, "minDate": min_date}
    resp = requests.post(url, headers=api_headers(token), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    backend_url   = env("ORG_PULSE_BACKEND_URL")
    api_token     = env("ORG_PULSE_API_TOKEN")
    smartsheet_tk = env("SMARTSHEET_TOKEN")
    gitlab_token  = env("GITLAB_TOKEN")
    min_date      = env("MIN_DATE", required=False) or "2024-01-01"

    jira_base_url = env("JIRA_BASE_URL", required=False) or "https://redhat.atlassian.net"
    jira_email    = env("JIRA_EMAIL", required=False)
    jira_token    = env("JIRA_API_TOKEN", required=False)

    print("=== Conforma Exceptions Sync ===")
    print(f"Backend  : {backend_url}")
    print(f"Min date : {min_date}")
    print()

    # Step 1: Fetch smartsheet release schedule
    print("[1/5] Fetching release schedule from Smartsheet…")
    rows = fetch_smartsheet_rows(smartsheet_tk)
    print(f"  Fetched {len(rows)} rows total")

    releases_meta = extract_releases_from_smartsheet(rows, min_date)
    print(f"  Found {len(releases_meta)} RHOAI releases with GA date >= {min_date}")
    for r in releases_meta:
        print(f"    {r['version']:20s}  GA: {r['gaDate']}  CodeFreeze: {r['codeFreezeDate'] or 'n/a'}")

    if not releases_meta:
        print("\nWARN: No qualifying releases found. Nothing to push.", file=sys.stderr)
        return

    # Step 2: For each release, fetch GitLab snapshot and parse exceptions
    print("\n[2/5] Fetching GitLab policy snapshots…")
    releases = []

    for meta in releases_meta:
        version = meta["version"]
        ga_date = meta["gaDate"]
        print(f"\n  [{version}]  GA: {ga_date}")

        fbc_sha = find_commit_before_date(FBC_FILE, ga_date, gitlab_token)
        reg_sha = find_commit_before_date(REGISTRY_FILE, ga_date, gitlab_token)
        print(f"    FBC commit:      {fbc_sha or '(none found)'}")
        print(f"    Registry commit: {reg_sha or '(none found)'}")

        fbc_exceptions = {"configExcludes": [], "volatileExcludes": []}
        reg_exceptions = {"configExcludes": [], "volatileExcludes": []}

        if fbc_sha:
            raw = fetch_file_at_commit(FBC_FILE, fbc_sha, gitlab_token)
            if raw:
                fbc_exceptions = parse_policy_yaml(raw)
                print(f"    FBC:      {len(fbc_exceptions['configExcludes'])} permanent, {len(fbc_exceptions['volatileExcludes'])} volatile")
            else:
                print("    WARN: FBC file not found at snapshot")
        else:
            print("    WARN: No FBC commit found before GA date")

        if reg_sha:
            raw = fetch_file_at_commit(REGISTRY_FILE, reg_sha, gitlab_token)
            if raw:
                reg_exceptions = parse_policy_yaml(raw)
                print(f"    Registry: {len(reg_exceptions['configExcludes'])} permanent, {len(reg_exceptions['volatileExcludes'])} volatile")
            else:
                print("    WARN: Registry file not found at snapshot")
        else:
            print("    WARN: No registry commit found before GA date")

        releases.append({
            "version": version,
            "gaDate": ga_date,
            "codeFreezeDate": meta.get("codeFreezeDate"),
            "gaSnapshotCommits": {
                "fbc": fbc_sha,
                "registry": reg_sha
            },
            "exceptions": {
                "fbc": fbc_exceptions,
                "registry": reg_exceptions
            }
        })

    # Step 3: Detect Jira extension issues for latest unshipped release
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    unshipped = [r for r in releases if r["gaDate"] > today_str]

    if unshipped and jira_email and jira_token:
        latest = unshipped[0]
        print(f"\n[3/5] Detecting Jira extension issues for {latest['version']}…")
        detect_extension_jira_issues(latest, jira_base_url, jira_email, jira_token)
    elif unshipped and (not jira_email or not jira_token):
        print("\n[3/5] Skipping Jira extension detection (JIRA_EMAIL / JIRA_API_TOKEN not set)")
    else:
        print("\n[3/5] Skipping Jira extension detection (no unshipped releases)")

    # Step 4: Clear existing data
    print(f"\n[4/5] Clearing existing data…")
    clear_existing(backend_url, api_token)

    # Step 5: Push all releases
    print(f"\n[5/5] Pushing {len(releases)} releases to API…")
    result = push_bulk(backend_url, api_token, releases, min_date)

    print("\n=== Summary ===")
    print(f"  Releases pushed : {result.get('count', len(releases))}")
    print(f"  Saved at        : {result.get('savedAt', 'unknown')}")
    if result.get("errors"):
        print(f"  Validation errors: {result['errors']}", file=sys.stderr)

    print("\nDone.")


if __name__ == "__main__":
    main()
