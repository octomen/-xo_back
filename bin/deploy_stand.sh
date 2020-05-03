#!/usr/bin/env bash

set -x

COMPOSE="docker-compose -f docker/docker-compose.yaml"

BRANCH=$1
if [ -z "$BRANCH" ]
then
  BRANCH=origin/release
fi

git fetch
git reset --hard
git checkout "$BRANCH"

${COMPOSE} stop
docker pull octoman/xo_back
${COMPOSE} up -d
