#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# Install required packages.
#
# This script contains a list of required packages and the means to make them
# available **on a Debian-based** OS.


# Be really strict and defensive about the script!
#
# -e : exit immediatly
# -u : undefined variables as errors
# -x : print all executed commands to the terminal
# -o pipefail : cause pipes to fail
#
# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euxo pipefail


DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  postfix/stable \
  dovecot-core/stable \
  dovecot-imapd/stable \
  dovecot-lmtpd/stable \
  dovecot-pop3d/stable
