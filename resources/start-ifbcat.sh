#!/usr/bin/env bash
set -e

cd /var/ifbcat-src

export CI_COMMIT_SHA=$(git rev-parse HEAD)
export CI_COMMIT_DATE="$(git log -1 --format='%ai')"

echo "Starting IFB Catalogue with commit ${CI_COMMIT_SHA}"

docker compose down --remove-orphans

docker image prune -a --force --filter "until=672h"

docker compose pull --quiet --ignore-pull-failures

docker compose build \
    --pull \
    --build-arg CI_COMMIT_SHA="$CI_COMMIT_SHA" \
    --build-arg CI_COMMIT_DATE="$CI_COMMIT_DATE"

exec docker compose up -d --remove-orphans