#!/usr/bin/env bash
# Rollback deployment to a previous git state
set -euo pipefail

cd "$(dirname "$0")/.."

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <git_commit_or_tag>"
    exit 1
fi

TARGET_REF="$1"

echo "Rolling back to $TARGET_REF..."
# Ensure working directory is clean before rollback
git fetch --all
git checkout "$TARGET_REF"

echo "Restarting containers with previous configuration..."
docker compose up -d --remove-orphans

echo "Rollback initiated. Running healthcheck..."
./scripts/healthcheck.sh
