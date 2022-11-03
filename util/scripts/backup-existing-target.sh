#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# Create a backup of an existing file.
#
# @param: The path/name of the symlink, relative to the user's home directory
# @param: The target of the link, relative to this script's directory (which
#         should be the repository root)
#
# The function will remove existing symlinks and create backups of existing
# files and directories before creating the actual symlink.
function backup_existing_target {
  # Get the current date, if a backup has to be created.
  local date_str=$(date +%Y-%m-%d-%H%M)

  local dst="$1"

  # echo " [DEBUG] destination: $dst"  # just for debugging
  # echo " [DEBUG] source: $src"  # just for debugging

  if [ -h $dst ]; then
    # echo " [INFO] Removing existing symlink!"  # just for debugging
    rm $dst
  elif [ -f $dst ]; then
    # echo " [INFO] Creating backup of existing file!"  # just for debugging
    mv $dst{,.$date_str}
  elif [ -d $dst ]; then
    # echo " [INFO] Creating backup of existing directory!"  # just for debugging
    mv $dst{,.$date_str}
  fi
}
