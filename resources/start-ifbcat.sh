#!/usr/bin/env bash
set -e

PRUNE=0
if [[ "$1" == "--prune" ]]; then
    PRUNE=1
fi

cd /var/ifbcat-src

export CI_COMMIT_SHA=$(git rev-parse HEAD)
export CI_COMMIT_DATE="$(git log -1 --format='%ai')"

echo "Starting IFB Catalogue with commit ${CI_COMMIT_SHA}"

docker compose down --remove-orphans

if [[ $PRUNE -eq 1 ]]; then
docker image prune -a --force --filter "until=672h"
fi

docker compose pull --quiet --ignore-pull-failures

docker compose build \
    --pull \
    --build-arg CI_COMMIT_SHA="$CI_COMMIT_SHA" \
    --build-arg CI_COMMIT_DATE="$CI_COMMIT_DATE"

exec docker compose up --remove-orphans