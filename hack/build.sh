#!/usr/bin/env bash

if [[ ${#} -ne 1 ]]; then
    echo "Usage: ${0} CONATINER_RUNTIME"
    exit 1
fi

CONATINER_RUNTIME=${1}

PARENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
BUILD_ARGS="--tag localhost/openshift4-mirror:latest ${PARENT_DIR}"

${CONATINER_RUNTIME} build ${BUILD_ARGS}
