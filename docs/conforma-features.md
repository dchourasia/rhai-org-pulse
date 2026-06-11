# Conforma Insights Dashboard — Feature Inventory

## Production (main branch)

**Live at:** https://team-tracker.apps.int.spoke.prod.us-west-2.aws.paas.redhat.com/#/releases/deliver?tab=conforma-insights

### Top 10 Features

1. **Release Version Banner** — Prominent gradient card showing release version, GA date, code freeze date, and shipped/upcoming status badge. Previous/Next navigation when multiple releases match the filter.

2. **Summary Statistics Cards** — Four-card grid showing Total Exceptions, FBC Policy count, Components Policy count, and Volatile (time-bound) count with permanent sub-count.

3. **Exceptions by Rule Category Bar Chart** — Horizontal stacked bar chart breaking down exception counts by category (FIPS, hermetic_task, test, tasks, schedule, sbom_spdx, rpm_signature, cve, source_image, step_image_registries, other) with FBC vs Components stacking.

4. **Exception Distribution Donut Charts** — Two side-by-side donut charts: FBC vs Components policy split, and Volatile vs Permanent type split.

5. **Exception Trend Line Chart** — Multi-line chart tracking Total, FIPS, FBC, Components, and Volatile exception counts across all releases over time, sorted by GA date.

6. **Volatile Expiry Scatter Chart** — Scatter plot showing when volatile exceptions expire relative to GA date. Color-coded: green (>60 days after GA), amber (0-60 days), red (before GA -- risk).

7. **Detailed Exceptions Table** — Full-width sortable table with 9 columns: Policy, Type, Rule Value, Category, Image, Effective Until, Days After GA, Reference, and Docs link. Row highlighting for at-risk exceptions (red for expired, amber for <30 days).

8. **Multi-Dimension Table Filtering** — Search box (searches rule value, reference, comment, imageUrl, category) plus dropdown filters for Policy, Type, and Category. Clear-all button when filters are active.

9. **Conforma Documentation Links** — Docs column with icon buttons linking to category-specific documentation at `conforma.dev/docs/policy/packages/` for each exception rule.

10. **Product/Version Filter Integration** — Respects the parent Deliver module's release filter. Filters releases by product extraction and version normalization. Auto-selects first upcoming release or most recent shipped.

---

## Dev Server (conforma branch)

**Deployed at:** http://10.0.96.93:5174/#/release-analysis/conforma-exceptions

### Top 10 Additional Features (on top of main)

1. **AI-Powered Exception Categorization** — Full AI analysis section with summary cards (Policy Mapped, Resolved, Component Updates, Permanent Partner), a Resolution Path Distribution bar chart (FBC vs Components per AI category), and a Release Burndown Forecast stacked bar chart showing exception reduction targets by release.

2. **Exceptions by Team Bar Chart** — Horizontal bar chart showing exception count per team (sorted descending). Clickable bars filter the table and update the URL hash for deep-linking. Hidden when already filtering by a team.

3. **Team-Based Filtering & URL Navigation** — Team dropdown filter in table toolbar, URL parameter support (`?team=TeamName`), team filter banner with "View all teams" clear button, and team name displayed in the version banner when filtered.

4. **Multi-Reference Jira Links** — Exceptions can have multiple linked references (migrated from single `reference` string to `references` array). Displayed as clickable badge-style links extracting Jira ticket keys (e.g., `RHOAIENG-31398`).

5. **Actionable Exception Workflow** — "Immediate Action Needed" toggle button highlights exceptions expiring within 7 days of an unshipped release. Auto-sorts by days-after-GA ascending. Scatter chart highlights actionable dots with larger red markers.

6. **Jira Extension Creation with Security Compliance Modal** — One-click "Extend" button on actionable exceptions opens a security policy compliance notice (referencing Chris Wright's May 2026 directive about ProdSec policy changes, VP sign-off requirements, PRODSECRM tracking). Confirmation opens a Jira template for extension requests.

7. **Scatter Chart Interactive Tooltips** — In actionable mode, hovering over scatter dots shows persistent tooltips with full exception details: category badge, rule value, policy file, expiration date, days after GA, and either a green "Extension Jira" link or red "Create Jira" button.

8. **AI Assessment & ProdSec Filters** — Additional table filter dropdowns: AI Assessment (Partner Content, Platform Adoption, Package Build, Component Update, Risk Accepted, Resolved), Target Release, and ProdSec Policy Mapped status. Total of 9+ simultaneous filter dimensions.

9. **Contextual Help Tooltips on Charts** — Each chart section includes help tooltips with three tiers: Good (what healthy looks like), Attention (warning signs), and Action (what to do). Provides actionable guidance for interpreting the data.

10. **Google Sheets Override Pipeline** — New CI pipeline step (`apply_overrides.py`) reads two Google Spreadsheets to apply manual team overrides (assessment corrections, Jira references, ignore flags) and map images to owning teams. Runs as third step after fetch + AI categorize, with fallback matching for image-specific overrides against imageless entries.
