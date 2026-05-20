#!/bin/bash
# Create the claude-ci user, install Claude Code CLI, and configure GCP credentials.
set -euo pipefail

echo "--- Preflight checks ---"
fail=0
for var in GCP_PROJECT_ID GCP_SERVICE_ACCOUNT_KEY CI_PROJECT_DIR; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set"
    fail=1
  else
    echo "OK: $var is set"
  fi
done
[[ "$fail" -eq 1 ]] && exit 1

echo "--- Installing system packages ---"
dnf install -y --nodocs curl git-core shadow-utils util-linux python3 python3-pip jq which

echo "--- Writing GCP credentials ---"
echo "$GCP_SERVICE_ACCOUNT_KEY" | base64 -d > /tmp/gcp-key.json
chmod 644 /tmp/gcp-key.json

echo "--- Creating claude-ci user ---"
useradd -m claude-ci 2>/dev/null || echo "User claude-ci already exists"

echo "--- Installing Claude Code CLI ---"
curl -fsSL https://claude.ai/install.sh | runuser -l claude-ci -c bash

echo "--- Verifying Claude installation ---"
runuser -u claude-ci -- bash -c 'export PATH="$HOME/.local/bin:$PATH"; claude --version'

echo "--- Configuring file permissions ---"
chown -R claude-ci:claude-ci "$CI_PROJECT_DIR"
runuser -u claude-ci -- git config --global --add safe.directory "$CI_PROJECT_DIR"
