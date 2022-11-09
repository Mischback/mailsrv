#!/bin/sh

# This script notifies the user about the usage of the mailbox. If the user
# comes closer to the actual mailbox quota, a simple warning message is
# provided to the mailbox.
#
# This script bypasses all quota checks itsself, to make sure this message is
# delivered to the mailbox.

# Provide the actual usage (in percent)
USAGE=$1

# Provide the user who will be recipient of this warning
USER=$2

cat << EOF | /usr/lib/dovecot/dovecot-lda -d $USER -o "plugin/quota=maildir:User Quota:noenforcing"
From: postmaster@mischback.de
Subject: Quota warning - $USAGE% reached

Your mailbox can only store a limited amount of emails.
Currently it is $USAGE% full. If you reach 100% then
new emails cannot be stored. Thank you for your understanding.
EOF
