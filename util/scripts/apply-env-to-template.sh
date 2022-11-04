#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# Create actual configuration files off of the provided templates/samples.
#
# This applies the settings as provided in an environment file to the
# placeholders in the provided samples using ``envsubst``.
#
# References:
#   - hint for ``envsubst``: https://stackoverflow.com/a/14157575
#   - use ``env`` in combination with ``xargs``: https://stackoverflow.com/a/20909045


# Be really strict and defensive about the script!
#
# -e : exit immediatly
# -u : undefined variables as errors
# -x : print all executed commands to the terminal
# -o pipefail : cause pipes to fail
#
# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euo pipefail

# Determine the script's directory, required for includes of auxiliary scripts.
#
# See https://stackoverflow.com/a/12694189
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi

# Include auxiliary scripts
source "$DIR/backup-existing-target.sh"

# Fetch parameters.
OUTPUT_FILE=$1
INPUT_FILE=$2
ENV_FILE=$3

echo "[INFO] (Re-)generating ${OUTPUT_FILE}"

# Create a backup if the output file already exists.
backup_existing_target ${OUTPUT_FILE}

# This is where the magic happens!
#
# This might look like arcane sorcery, but in fact it is just using ``envsubst``
# in combination with ``env``:
#
# ``env`` is used to prepare a clean (``-i``) environment for calling
# ``envsubst``. The provided environment variables are read from an input file
# ``ENV_FILE``, using ``grep`` to ignore comments in that file. ``xargs`` is
# only used to provide the required structure.
#
# ``envsubst`` then reads ``INPUT_FILE``, performs the substitution and writes
# the result to ``OUTPUT_FILE``. The first parameter given to ``envsubst``
# determines, which variables will get substituted. This list limits the
# operation to the set of variables that are required in this repository,
# leaving other occurences of the pattern``$something`` untouched.
env -i $(grep -v '^#' ${ENV_FILE} | xargs -d '\n') \
  envsubst '
    $MAILSRV_HOSTNAME
    $MAILSRV_POSTFIX_INTERFACES
    $MAILSRV_BIND_IPV4
    $MAILSRV_BIND_IPV6
    $MAILSRV_IP_VERSION
    $MAILSRV_IP_PREFERENCE
    $MAILSRV_DNS_LOOKUP
    $MAILSRV_TLS_CERT
    $MAILSRV_TLS_KEY
    ' \
    < ${INPUT_FILE} \
    > ${OUTPUT_FILE}
