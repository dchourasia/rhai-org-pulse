set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Source shared libraries from ai-agentic-lib ---
AI_AGENTIC_LIB_DIR="${AI_AGENTIC_LIB_DIR:-/tmp/ai-agentic-lib}"
if [[ ! -d "$AI_AGENTIC_LIB_DIR/lib" ]]; then
    _clone_url="https://gitlab.com/redhat/rhel-ai/agentic-ci/ai-agentic-lib.git"
    if [[ -n "${GITLAB_EXT_TOKEN:-}" ]]; then
        _clone_url="https://oauth2:${GITLAB_EXT_TOKEN}@gitlab.com/redhat/rhel-ai/agentic-ci/ai-agentic-lib.git"
    fi
    git clone --depth=1 --branch "${AI_AGENTIC_LIB_REF:-main}" \
        "$_clone_url" "$AI_AGENTIC_LIB_DIR" >/dev/null 2>&1 || {
        echo "ERROR: Failed to clone ai-agentic-lib. Set AI_AGENTIC_LIB_DIR to a local checkout." >&2
        exit 1
    }
    unset _clone_url
fi
# shellcheck source=/dev/null
source "$AI_AGENTIC_LIB_DIR/lib/shell-utils.sh"
# shellcheck source=/dev/null
source "$AI_AGENTIC_LIB_DIR/lib/claude-runner.sh"
# shellcheck source=/dev/null
source "$AI_AGENTIC_LIB_DIR/lib/acli.sh"