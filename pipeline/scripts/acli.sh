#!/bin/bash
# acli.sh — Atlassian CLI helper functions for agentic CI projects.
#
# Provides install_acli() to download the binary and setup_acli_auth()
# to authenticate against a Jira Cloud site.
#
# Requires: curl
# Auth env vars: JIRA_EMAIL (or JIRA_USER), JIRA_API_TOKEN
#
# Usage:
#   source /path/to/acli.sh
#   install_acli            # downloads to /usr/local/bin/acli
#   setup_acli_auth         # logs in to redhat.atlassian.net

[[ -n "${_ACLI_LOADED:-}" ]] && return 0
readonly _ACLI_LOADED=1

# Site to authenticate against (override for testing)
ACLI_JIRA_SITE="${ACLI_JIRA_SITE:-redhat.atlassian.net}"

# Install the Atlassian CLI binary.
# See https://developer.atlassian.com/cloud/acli/guides/use-acli-on-ci/
install_acli() {
    local dest="${1:-/usr/local/bin/acli}"
    if command -v acli &>/dev/null; then
        return 0
    fi
    curl -fsSL "https://acli.atlassian.com/linux/latest/acli_linux_amd64/acli" \
        -o "$dest"
    chmod +x "$dest"
}

# Authenticate acli against the configured Jira site.
# Requires JIRA_EMAIL (or JIRA_USER) and JIRA_API_TOKEN environment variables.
setup_acli_auth() {
    local email="${JIRA_EMAIL:-${JIRA_USER:-}}"
    local token="${JIRA_API_TOKEN:-}"
    if [[ -z "$email" ]] || [[ -z "$token" ]]; then
        echo "ERROR: JIRA_EMAIL (or JIRA_USER) and JIRA_API_TOKEN must be set for acli auth" >&2
        return 1
    fi
    echo "$token" | acli jira auth login \
        --email "$email" \
        --site "$ACLI_JIRA_SITE" \
        --token
}
