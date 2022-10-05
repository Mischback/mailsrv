# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""Provide mails for the test cases."""

GENERIC_VALID_MAIL = (
    "Subject: {subject}\r\n"
    "From: {mail_from}\r\n"
    "To: {rcpt_to}\r\n"
    "\r\n"
    "This is the actual text of the mail. Nothing fancy here, because this is "
    "not really regarded during the actual tests. Just make it look like a "
    "valid mail, that does not get flagged as spam immediatly.\r\n\r\n"
    "Yours,\r\n"
    "Mischback"
)
