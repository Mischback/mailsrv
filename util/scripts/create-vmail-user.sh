#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# FIXME: ADD DOCUMENTATION!
#
# References:
#   - https://stackoverflow.com/a/36131231


# Be really strict and defensive about the script!
#
# -e : exit immediatly
# -u : undefined variables as errors
# -x : print all executed commands to the terminal
# -o pipefail : cause pipes to fail
#
# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euxo pipefail

# Create the ``vmail`` group.
#
# Note: This checks, if the group already exists! It does not verify, if the
# existing group is the same group ID as specified here. It silently assumes
# that this will work out, even if the ``vmail`` group was created manually
# with another group ID (which should work).
if [ ! $(getent group vmail) ]; then
  groupadd -g 5000 vmail
fi

# Create the dedicated directory for virtual mailboxes.
# This will be the home directory of the user ``vmail``.
#
# ``mkdir -p`` will do nothing, if the directory already exists. All existing
# sub-directories and files are left untouched.
mkdir -p /var/vmail

# Create the ``vmail`` user and deactivate login for this user.
#
# Note: This checks, if the user already exists! It does not verify, if the
# existing user has the same user ID as specified here, if the user's home
# directory is set as specified here or if the user's shell is set as
# specified here.
# If you have created the user manually, make sure to limit its access rights
# as far as possible.
if [ ! $(getent passwd vmail) ]; then
  useradd -g vmail -u 5000 -d /var/vmail vmail
  chsh -s /usr/sbin/nologin vmail
fi

# Transfer ownership for ``/var/vmail``.
chown -R vmail:vmail /var/vmail
