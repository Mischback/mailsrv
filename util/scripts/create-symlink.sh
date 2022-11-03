#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# Create a symbolic link to the actual config file.
#
# @param $1 The link's name
# @param $2 The target of the link, the file to be referenced
#
# The script will create a backup of existing files / directories, see
# ``util/scripts/backup-existing-target.sh``.

# Be really strict and defensive about the script!
#
# -e : exit immediatly
# -u : undefined variables as errors
# -x : print all executed commands to the terminal
# -o pipefail : cause pipes to fail
#
# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euxo pipefail

# Determine the script's directory, required for includes of auxiliary scripts.
#
# See https://stackoverflow.com/a/12694189
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi

# Include auxiliary scripts
source "$DIR/backup-existing-target.sh"

# Fetch parameters.
LINK_NAME=$1
TARGET=$2

# Create a backup if the output file already exists.
backup_existing_target ${LINK_NAME}

# Actually create the symlink.
ln -s ${TARGET} ${LINK_NAME}
