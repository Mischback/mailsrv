#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# Create the required path to place Dovecot's sockets in Postfix's chroot.


# Be really strict and defensive about the script!
#
# -e : exit immediatly
# -u : undefined variables as errors
# -x : print all executed commands to the terminal
# -o pipefail : cause pipes to fail
#
# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euo pipefail

# The provided configuration for Dovecot places all sockets, that are required
# to interact with Postfix in Postfix's chroot environment. As the corresponding
# path does not exist, it has to be created manually.
#
# The sockets get populated in:
#   - /etc/dovecot/conf.d/10-master.conf
#   - /etc/dovecot/conf.d/90-quota.conf
mkdir -p /var/spool/postfix/socket/dovecot
chown -R postfix:root /var/spool/postfix/socket
chmod -R u=rwx,g=,o= /var/spool/postfix/socket

echo "[INFO] Created required paths for Dovecot's sockets"
