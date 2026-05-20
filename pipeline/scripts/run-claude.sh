#!/bin/bash
# Wrapper script for running Claude in CI.
# When run as root, re-execs itself as the claude-ci user.
set -euo pipefail

# Re-exec as claude-ci when running as root
if [[ "$(id -u)" -eq 0 ]]; then
  exec runuser -u claude-ci -- bash "$0" "$@"
fi

export PATH="$HOME/.local/bin:$PATH"

echo "--- Preflight checks ---"
fail=0
for var in JIRA_USER_EMAIL JIRA_API_TOKEN JIRA_URL; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set"
    fail=1
  else
    echo "OK: $var is set"
  fi
done

if [[ "${JIRA_URL:-}" != https://* ]]; then
  echo "ERROR: JIRA_URL does not look like a valid URL: '${JIRA_URL:-}'"
  fail=1
fi

[[ "$fail" -eq 1 ]] && exit 1

echo "--- Claude version ---"
claude --version

# STDERR_LOG="/tmp/claude-stderr.log"
RESULT_LOG="/tmp/claude-result.json"

echo "--- Running skill: ${1:?Usage: $0 <prompt>} ---"

# Write Claude output to a file; tail -f streams it to the parser in parallel.
# This decouples Claude from the display pipeline so a parser crash can never
# kill Claude via SIGPIPE.
: > "$RESULT_LOG"
claude -p "$1" \
  --model "${CLAUDE_MODEL:-claude-opus-4-6}" \
  --dangerously-skip-permissions \
  --output-format stream-json \
  --verbose \
  >> "$RESULT_LOG" &
CLAUDE_PID=$!

# Stream the log file and pretty-print events as they arrive.
# If the parser dies, Claude keeps running unaffected.
PARSER="$(dirname "$0")/stream-claude-output.py"
tail -f "$RESULT_LOG" --pid="$CLAUDE_PID" 2>/dev/null \
  | python3 -u "$PARSER" || true

wait "$CLAUDE_PID"
rc=$?

# if [[ "$rc" -ne 0 ]]; then
#   echo "--- Claude exited with code $rc; last stderr output ---"
#   tail -50 "$STDERR_LOG" >&2
# fi

exit $rc
