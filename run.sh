#!/usr/bin/env bash

set -e
set -o pipefail
set -C


APP=$(basename $PWD | sed -e 's/^docker\-//')
TAG="$USER/$APP"

DOCKER_OPT=""

if [[ -f "$PWD/.env" ]]; then
    DOCKER_OPT="--env-file $PWD/.env"
fi

docker run --rm $DOCKER_OPT -it $TAG:latest $@
