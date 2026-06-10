"""Apply manual overrides and team mapping to conforma exception data.

Reads two Google Spreadsheets:
  1. "RHOAI Conforma Data" — manual overrides (assessment, context, jira refs, ignore)
  2. "RHOAI Images Components Map" — image-to-team mapping

For each upcoming release (GA date > today), applies overrides to registry
volatile exceptions: updates categories, reasoning, references, and removes
ignored entries. Then maps teams to ALL exceptions across ALL releases based
on imageUrl.

Runs as the third CI step after fetch_and_push.py and ai_categorize.py.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ─── Constants ───────────────────────────────────────────────────────────────

CONFORMA_DATA_SHEET_ID = "14U_w2PjKqyeuxZJDwwVacxCIES1X8DxIrTE_MF4PtzY"
IMAGES_MAP_SHEET_ID = "1q_30FTzPCyMFMdQOkMpZFzylu6LCYI3bMEs5XcV0kOY"
IMAGES_MAP_TAB = "rhoai-image-to-jira-component"

IMAGE_PREFIX = "quay.io/rhoai/"

ASSESSMENT_TO_CATEGORY = {
    "partner content": "partner_permanent",
    "platform adoption": "platform_adoption",
    "package build": "package_onboarding",
    "component update": "component_update",
    "risk accepted": "risk_accepted",
    "resolved": "resolved",
}

DEFAULT_TARGET_RELEASE = "rhoai-3.6"

TIMEOUT = 30


# ─── Env helpers ─────────────────────────────────────────────────────────────

def env(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "").strip()
    if required and not val:
        print(f"ERROR: Required environment variable {name!r} is not set.", file=sys.stderr)
        sys.exit(1)
    return val


# ─── API helpers ─────────────────────────────────────────────────────────────

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


def push_bulk(backend_url: str, token: str, releases: list[dict]) -> dict:
    url = f"{backend_url.rstrip('/')}/api/modules/release-analysis/conforma/bulk"
    payload = {"releases": releases}
    resp = requests.post(url, headers=api_headers(token), json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


# ─── Google Sheets ───────────────────────────────────────────────────────────

def get_sheets_service():
    key_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY_FILE", "/etc/secrets/google-sa-key.json")
    creds = Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    return build("sheets", "v4", credentials=creds)


def read_sheet(service, spreadsheet_id: str, tab: str = "Sheet1") -> list[list[str]]:
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=tab)
        .execute()
    )
    return result.get("values", [])


# ─── Spreadsheet parsing ────────────────────────────────────────────────────

def split_multi(value: str) -> list[str]:
    """Split a cell value by newline and comma, strip, deduplicate, preserve order."""
    parts = []
    seen = set()
    for chunk in re.split(r'[\n,]', value):
        v = chunk.strip()
        if v and v.lower() != "n/a" and v not in seen:
            seen.add(v)
            parts.append(v)
    return parts


def parse_jira_urls(value: str) -> list[str]:
    """Extract all URLs from a Jira URL cell."""
    if not value or not value.strip():
        return []
    urls = []
    for part in re.split(r'[\s,\n]+', value.strip()):
        part = part.strip()
        if part.startswith("http"):
            urls.append(part)
    return urls


def normalize_version(raw: str, known_versions: set[str]) -> str | None:
    raw = raw.strip()
    if not raw or raw.lower() == "n/a":
        return None
    v = raw.lstrip("v")
    candidate = f"rhoai-{v}"
    if candidate in known_versions:
        return candidate
    norm = lambda s: s.lower().replace(".", "").replace("-", "")
    for kv in known_versions:
        if norm(kv) == norm(candidate):
            return kv
    return None


def parse_override_rows(rows: list[list[str]], known_versions: set[str]) -> list[dict]:
    """Parse RHOAI Conforma Data spreadsheet into expanded override entries.

    Each row may produce multiple entries via Cartesian product of
    violation names × image names × affects versions.
    """
    if not rows:
        return []

    headers = [h.strip() for h in rows[0]]
    overrides = []

    for row_idx, row in enumerate(rows[1:], start=2):
        cells = row + [""] * (len(headers) - len(row))
        get = lambda col: cells[headers.index(col)].strip() if col in headers else ""

        violations = split_multi(get("Violation Name(s)"))
        images_raw = split_multi(get("Image Name(s)"))
        images = images_raw if images_raw else [None]
        context = get("Context") or None
        assessment_raw = get("Assessment").strip().lower()
        affects_raw = split_multi(get("Affects Version"))
        fix_version_raw = get("Fix Version").strip()
        jira_urls = parse_jira_urls(get("Jira URL"))
        ignore = get("Ignore").strip().lower() == "yes"

        if "expired" in assessment_raw:
            category = None
        else:
            category = ASSESSMENT_TO_CATEGORY.get(assessment_raw)

        affects_versions = []
        for av in affects_raw:
            nv = normalize_version(av, known_versions)
            if nv:
                affects_versions.append(nv)

        fix_version = None
        if fix_version_raw:
            fix_version = normalize_version(fix_version_raw, known_versions)
            if not fix_version:
                fix_version = f"rhoai-{fix_version_raw.lstrip('v')}"

        if not violations:
            continue

        for violation in violations:
            for image in images:
                for version in (affects_versions if affects_versions else [None]):
                    overrides.append({
                        "value": violation,
                        "imageShort": image,
                        "version": version,
                        "context": context,
                        "category": category,
                        "fixVersion": fix_version or DEFAULT_TARGET_RELEASE,
                        "jiraUrls": jira_urls,
                        "ignore": ignore,
                        "sourceRow": row_idx,
                    })

    return overrides


def build_team_map(rows: list[list[str]]) -> dict[str, str]:
    """Build containerImage → Team lookup from Images Components Map."""
    if not rows:
        return {}
    headers = [h.strip() for h in rows[0]]
    if "containerImage" not in headers or "Team" not in headers:
        print(f"  WARN: Images map missing expected columns. Headers: {headers}")
        return {}

    img_idx = headers.index("containerImage")
    team_idx = headers.index("Team")
    team_map = {}
    for row in rows[1:]:
        if len(row) <= max(img_idx, team_idx):
            continue
        image = row[img_idx].strip()
        team = row[team_idx].strip()
        if image and team:
            team_map[image] = team
    return team_map


# ─── Override logic ──────────────────────────────────────────────────────────

def make_match_key(value: str, image_url: str | None) -> str:
    """Build a match key from value and imageUrl, stripping quay prefix for comparison."""
    if image_url:
        short = image_url.replace(IMAGE_PREFIX, "")
        return f"{value}:{short}".lower()
    return value.lower()


def migrate_references(exclude: dict) -> None:
    """In-place migration: reference (string) → references (array)."""
    if "references" in exclude:
        return
    ref = exclude.pop("reference", None)
    exclude["references"] = [ref] if ref else []


def apply_overrides_to_release(release: dict, overrides: list[dict]) -> dict:
    """Apply override entries to a single release's registry exceptions.

    Returns stats dict with counts of actions taken.
    """
    stats = {"updated": 0, "added": 0, "removed": 0, "skipped": 0}

    registry = release.get("exceptions", {}).get("registry", {})
    volatile = registry.get("volatileExcludes", [])
    ai_cat = release.get("aiCategorization", {})
    ai_exceptions = ai_cat.get("exceptions", [])

    vol_by_key = {}
    for i, ex in enumerate(volatile):
        key = make_match_key(ex.get("value", ""), ex.get("imageUrl"))
        vol_by_key[key] = i

    ai_by_fullname = {}
    for i, ae in enumerate(ai_exceptions):
        fn = ae.get("fullName", "").lower()
        ai_by_fullname[fn] = i

    to_remove = set()

    for ov in overrides:
        ov_key = make_match_key(ov["value"], ov["imageShort"])
        vol_idx = vol_by_key.get(ov_key)

        full_name = f"{ov['value']}:{IMAGE_PREFIX}{ov['imageShort']}" if ov["imageShort"] else ov["value"]
        ai_fullname_key = full_name.lower()

        if ov["ignore"]:
            if vol_idx is not None:
                to_remove.add(vol_idx)
                stats["removed"] += 1
            ai_idx = ai_by_fullname.get(ai_fullname_key)
            if ai_idx is not None:
                ai_exceptions[ai_idx] = None
            continue

        if vol_idx is not None:
            ex = volatile[vol_idx]
            migrate_references(ex)

            if ov["jiraUrls"]:
                existing = set(ex["references"])
                new_refs = [u for u in ov["jiraUrls"] if u not in existing]
                ex["references"] = new_refs + ex["references"]

            ai_idx = ai_by_fullname.get(ai_fullname_key)
            if ai_idx is not None:
                ae = ai_exceptions[ai_idx]
            else:
                ae = {
                    "fullName": full_name,
                    "policyFile": "registry",
                    "type": "volatile",
                    "category": "",
                    "targetRelease": DEFAULT_TARGET_RELEASE,
                    "policyMapped": True,
                    "reasoning": "",
                }
                ai_exceptions.append(ae)
                ai_by_fullname[ai_fullname_key] = len(ai_exceptions) - 1

            if ov["context"]:
                ae["reasoning"] = ov["context"]
            if ov["category"]:
                ae["category"] = ov["category"]
            if ov["fixVersion"]:
                ae["targetRelease"] = ov["fixVersion"]

            stats["updated"] += 1

        else:
            image_url = f"{IMAGE_PREFIX}{ov['imageShort']}" if ov["imageShort"] else None
            new_ex = {
                "value": ov["value"],
                "effectiveUntil": None,
                "references": list(ov["jiraUrls"]),
                "imageUrl": image_url,
                "comment": ov["context"],
            }
            volatile.append(new_ex)
            new_key = make_match_key(ov["value"], image_url)
            vol_by_key[new_key] = len(volatile) - 1

            if ov["category"] or ov["fixVersion"]:
                ae = {
                    "fullName": full_name,
                    "policyFile": "registry",
                    "type": "volatile",
                    "category": ov["category"] or "",
                    "targetRelease": ov["fixVersion"] or DEFAULT_TARGET_RELEASE,
                    "policyMapped": True,
                    "reasoning": ov["context"] or "",
                }
                ai_exceptions.append(ae)
                ai_by_fullname[ai_fullname_key] = len(ai_exceptions) - 1

            stats["added"] += 1

    if to_remove:
        volatile[:] = [ex for i, ex in enumerate(volatile) if i not in to_remove]

    ai_exceptions[:] = [ae for ae in ai_exceptions if ae is not None]

    registry["volatileExcludes"] = volatile
    if ai_exceptions:
        if "aiCategorization" not in release:
            release["aiCategorization"] = {}
        release["aiCategorization"]["exceptions"] = ai_exceptions

    return stats


def migrate_all_references(releases: list[dict]) -> int:
    """Migrate reference→references for ALL volatile excludes across ALL releases."""
    count = 0
    for release in releases:
        for pf in ("fbc", "registry"):
            for ex in release.get("exceptions", {}).get(pf, {}).get("volatileExcludes", []):
                if "reference" in ex or "references" not in ex:
                    migrate_references(ex)
                    count += 1
    return count


def apply_team_mapping(releases: list[dict], team_map: dict[str, str]) -> dict[str, int]:
    """Assign team to ALL volatile exceptions based on imageUrl.

    Returns stats: {matched, unmatched, no_image}.
    """
    stats = {"matched": 0, "unmatched": 0, "no_image": 0}
    for release in releases:
        for pf in ("fbc", "registry"):
            for ex in release.get("exceptions", {}).get(pf, {}).get("volatileExcludes", []):
                image_url = ex.get("imageUrl")
                if not image_url:
                    stats["no_image"] += 1
                    continue
                if image_url in team_map:
                    ex["team"] = team_map[image_url]
                    stats["matched"] += 1
                else:
                    short = image_url.replace(IMAGE_PREFIX, "")
                    found = False
                    for full_url, team in team_map.items():
                        if full_url.endswith(f"/{short}") or full_url == short:
                            ex["team"] = team
                            stats["matched"] += 1
                            found = True
                            break
                    if not found:
                        ex["team"] = None
                        stats["unmatched"] += 1
    return stats


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    backend_url = env("ORG_PULSE_BACKEND_URL")
    api_token = env("ORG_PULSE_API_TOKEN")

    print("=== Conforma Overrides & Team Mapping ===")
    print(f"Backend: {backend_url}")
    print()

    # Step 1: Fetch all releases from API
    print("[1/5] Fetching releases from API…")
    releases = fetch_releases(backend_url, api_token)
    print(f"  Found {len(releases)} releases")

    known_versions = {r["version"] for r in releases if r.get("version")}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming = [r for r in releases if r.get("gaDate", "") > today]
    print(f"  Upcoming releases (GA > {today}): {[r['version'] for r in upcoming]}")

    if not releases:
        print("  No releases found. Nothing to do.")
        return

    # Step 2: Read override spreadsheet
    print("\n[2/5] Reading RHOAI Conforma Data spreadsheet…")
    sheets = get_sheets_service()
    override_rows = read_sheet(sheets, CONFORMA_DATA_SHEET_ID)
    print(f"  Read {len(override_rows)} rows (including header)")

    overrides = parse_override_rows(override_rows, known_versions)
    print(f"  Parsed {len(overrides)} expanded override entries")

    ignore_count = sum(1 for o in overrides if o["ignore"])
    versioned = sum(1 for o in overrides if o["version"])
    print(f"  Ignore entries: {ignore_count}, version-targeted: {versioned}")

    # Step 3: Read images-to-team map
    print("\n[3/5] Reading RHOAI Images Components Map…")
    map_rows = read_sheet(sheets, IMAGES_MAP_SHEET_ID, tab=IMAGES_MAP_TAB)
    print(f"  Read {len(map_rows)} rows (including header)")

    team_map = build_team_map(map_rows)
    print(f"  Built team map: {len(team_map)} image→team entries")
    unique_teams = sorted(set(team_map.values()))
    print(f"  Unique teams: {len(unique_teams)}")

    # Step 4: Apply overrides to upcoming releases
    print("\n[4/5] Applying overrides + team mapping…")

    total_stats = {"updated": 0, "added": 0, "removed": 0, "skipped": 0}
    for release in upcoming:
        version = release.get("version", "?")
        version_overrides = [o for o in overrides if o["version"] == version or o["version"] is None]
        if not version_overrides:
            print(f"  [{version}] No overrides applicable")
            continue

        stats = apply_overrides_to_release(release, version_overrides)
        for k in total_stats:
            total_stats[k] += stats[k]
        print(f"  [{version}] updated={stats['updated']}, added={stats['added']}, removed={stats['removed']}")

    print(f"\n  Override totals: {total_stats}")

    ref_count = migrate_all_references(releases)
    print(f"  Migrated reference→references: {ref_count} entries")

    team_stats = apply_team_mapping(releases, team_map)
    print(f"  Team mapping: matched={team_stats['matched']}, unmatched={team_stats['unmatched']}, no_image={team_stats['no_image']}")

    # Step 5: Push all releases back
    print(f"\n[5/5] Pushing {len(releases)} releases to API…")
    result = push_bulk(backend_url, api_token, releases)

    print("\n=== Summary ===")
    print(f"  Releases pushed : {result.get('count', len(releases))}")
    print(f"  Saved at        : {result.get('savedAt', 'unknown')}")
    print(f"  Overrides applied: {total_stats['updated']} updated, {total_stats['added']} added, {total_stats['removed']} removed")
    print(f"  Teams mapped    : {team_stats['matched']} matched, {team_stats['unmatched']} unmatched")

    print("\nDone.")


if __name__ == "__main__":
    main()
