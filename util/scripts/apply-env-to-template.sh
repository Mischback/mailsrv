#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# FIXME: ADD DOCUMENTATION!
#
# References:
#   - https://stackoverflow.com/a/52111696


# Be really strict and defensive about the script!
#
# -e : exit immediatly
# -u : undefined variables as errors
# -x : print all executed commands to the terminal
# -o pipefail : cause pipes to fail
#
# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euxo pipefail


OUTPUT_FILE=$1
INPUT_FILE=$2
ENV_FILE=$3

env -vi $(grep -v '^#' ${ENV_FILE} | xargs -d '\n') \
  envsubst '$MAILSRV_TEST' < ${INPUT_FILE} > ${OUTPUT_FILE}
