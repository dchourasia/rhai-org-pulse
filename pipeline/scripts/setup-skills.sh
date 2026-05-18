#!/bin/bash
# Clone aiops-infra to a tmp workdir and install its Claude skills for the claude-ci user.
set -euo pipefail

AIOPS_INFRA_WORKDIR="/tmp/aiops-infra"

echo "--- Preflight checks ---"
fail=0
for var in AIOPS_INFRA_REPO AIOPS_INFRA_BRANCH; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set"
    fail=1
  else
    echo "OK: $var=${!var}"
  fi
done
[[ "$fail" -eq 1 ]] && exit 1

echo "--- Cloning aiops-infra (branch: $AIOPS_INFRA_BRANCH) to $AIOPS_INFRA_WORKDIR ---"
rm -rf "$AIOPS_INFRA_WORKDIR"
git clone \
  --branch "$AIOPS_INFRA_BRANCH" \
  --depth 1 \
  "$AIOPS_INFRA_REPO" \
  "$AIOPS_INFRA_WORKDIR"

echo "--- Configuring permissions for claude-ci ---"
chown -R claude-ci:claude-ci "$AIOPS_INFRA_WORKDIR"
runuser -u claude-ci -- git config --global --add safe.directory "$AIOPS_INFRA_WORKDIR"

SKILLS_DIR="$AIOPS_INFRA_WORKDIR/.claude/skills"

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "ERROR: skills directory not found at $SKILLS_DIR"
  exit 1
fi

echo "--- Installing skill dependencies ---"
if [[ -f "$SKILLS_DIR/install-dependencies.sh" ]]; then
  bash "$SKILLS_DIR/install-dependencies.sh"
else
  echo "WARNING: install-dependencies.sh not found in $SKILLS_DIR, skipping"
fi

echo "--- Installing Claude skills for claude-ci ---"
if [[ -f "$SKILLS_DIR/install.sh" ]]; then
  bash "$SKILLS_DIR/install.sh" --user claude-ci
else
  echo "ERROR: install.sh not found in $SKILLS_DIR"
  exit 1
fi

echo "--- Verifying skill installation ---"
SKILL_COUNT=$(runuser -u claude-ci -- bash -c \
  'export PATH="$HOME/.local/bin:$PATH"; claude skills list 2>/dev/null | wc -l' || echo 0)
echo "Skills installed: $SKILL_COUNT entries"
