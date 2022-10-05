#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""Run the test suite."""


# Python imports
import argparse
import collections
import logging
import logging.config
import os
import sys
from typing import Any

# app imports
from mailsrv_aux.common import parser
from mailsrv_aux.common.exceptions import MailsrvBaseException, MailsrvIOException
from mailsrv_aux.common.log import LOGGING_DEFAULT_CONFIG, add_level
from mailsrv_aux.common.parser import PostfixAliasResolver
from mailsrv_aux.test_suite.pop3 import NoNonSecureAuth, VerifyMailGotDelivered
from mailsrv_aux.test_suite.protocols import SmtpTestProtocol
from mailsrv_aux.test_suite.smtp import (
    OtherMtaTestSuite,
    OtherMtaTlsTestSuite,
    SubmissionTestSuite,
)

# get a module-level logger
logger = logging.getLogger()

# add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


def get_password_plain(
    username: str,
    userdb: parser.PasswdFileParser,
) -> str:
    """Return plain text passwords from userdb."""
    ret = userdb.get_password(username)

    if "{plain}" not in ret:
        logger.error("Did not find plain text password")
        return ""

    return ret.removeprefix("{plain}")


def map_mails_to_mailboxes(
    smtp_protocol: SmtpTestProtocol,
    postfix_vmailboxes: list[str],
    postfix_valiases: dict[str, list[str]],
    postfix_vdomains: list[str],
) -> dict[str, list[str]]:
    """Map the mails to actual mailboxes."""
    resolved_aliases, _, _ = PostfixAliasResolver(
        postfix_vmailboxes, postfix_valiases, postfix_vdomains
    ).resolve()

    logger.debug("smtp protocol: %r", smtp_protocol)
    logger.debug("resolved aliases: %r", resolved_aliases)

    result: dict[str, list[str]] = collections.defaultdict(list)

    aliases = resolved_aliases.keys()
    for rcpt in smtp_protocol._accepted.keys():
        if rcpt in postfix_vmailboxes:
            logger.debug("Found RCPT with mailbox: %s", rcpt)
            result[rcpt] += smtp_protocol._accepted[rcpt]

        if rcpt in aliases:
            logger.debug("Fount RCPT as alias: %s", rcpt)

            for alias_target in resolved_aliases[rcpt]:
                result[alias_target] += smtp_protocol._accepted[rcpt]

    logger.debug("Result: %r", dict(result))

    return dict(result)


def map_logins_to_aliases(
    postfix_sendermap: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Map allowed sender aliases to logins."""
    logger.debug("postfix_sendermap: %r", postfix_sendermap)

    result: dict[str, list[str]] = collections.defaultdict(list)

    for sender in postfix_sendermap:
        for account in postfix_sendermap[sender]:
            result[account].append(sender)

    logger.debug("Result: %r", dict(result))

    return dict(result)


if __name__ == "__main__":
    # setup the logging module
    logging.config.dictConfig(LOGGING_DEFAULT_CONFIG)

    # find the script's path
    my_dir = os.path.dirname(os.path.realpath(__file__))
    test_config_dir = os.path.join(my_dir, "test_configs")

    # prepare the argument parser
    arg_parser = argparse.ArgumentParser(
        description="Run a test suite against a mail server setup"
    )

    # mandatory arguments (positional arguments)
    arg_parser.add_argument(
        "target_host", action="store", help="IP address of the system under test (SUT)"
    )

    # optional arguments (keyword arguments)
    arg_parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug messages"
    )
    arg_parser.add_argument(
        "-f",
        "--fail-fast",
        action="store_true",
        help="Fail and abort on the first error",
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Be more verbose; may be specified up to two times",
    )

    # provide overrides for the test config files
    arg_parser.add_argument(
        "--dovecot-userdb",
        action="store",
        default=os.path.join(test_config_dir, "dovecot_vmail_users"),
        help="Specify a Dovecot user database file (passwd-like file)",
    )
    arg_parser.add_argument(
        "--postfix-vmailboxes",
        action="store",
        default=os.path.join(test_config_dir, "postfix_vmailboxes"),
        help="Specify a Postfix virtual mailbox file",
    )
    arg_parser.add_argument(
        "--postfix-valiases",
        action="store",
        default=os.path.join(test_config_dir, "postfix_valiases"),
        help="Specify a Postfix virtual alias file",
    )
    arg_parser.add_argument(
        "--postfix-vdomains",
        action="store",
        default=os.path.join(test_config_dir, "postfix_vdomains"),
        help="Specify a Postfix virtual domain file",
    )
    arg_parser.add_argument(
        "--postfix-sendermap",
        action="store",
        default=os.path.join(test_config_dir, "postfix_sender-login-map"),
        help="Specify the Postfix sender to login map file",
    )

    args = arg_parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("DEBUG messages enabled")
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    elif args.verbose == 2:
        logger.setLevel(logging.VERBOSE)  # type: ignore [attr-defined]
        logger.verbose("Verbose logging enabled")  # type: ignore [attr-defined]

    try:
        try:
            # Read and parse the configuration files
            logger.verbose("Reading configuration files")  # type: ignore [attr-defined]

            dovecot_passwd = parser.PasswdFileParser(args.dovecot_userdb)
            dovecot_users = dovecot_passwd.get_usernames()
            logger.debug("dovecot_users: %r", dovecot_users)

            postfix_vmailboxes = parser.KeyParser(args.postfix_vmailboxes).get_values()
            logger.debug("postfix_vmailboxes: %r", postfix_vmailboxes)

            postfix_valiases = parser.KeyValueParser(args.postfix_valiases).get_values()
            logger.debug("postfix_valiases: %r", postfix_valiases)

            postfix_vdomains = parser.KeyParser(args.postfix_vdomains).get_values()
            logger.debug("postfix_vdomains: %r", postfix_vdomains)

            postfix_sendermap = parser.KeyValueParser(
                args.postfix_sendermap
            ).get_values()
            logger.debug("postfix_sendermap: %r", postfix_sendermap)

            # The addresses are the actual virtual mailboxes combined with the RHS
            # of the virtual aliases.
            postfix_addresses = postfix_vmailboxes + list(postfix_valiases.keys())
            logger.debug("postfix_addresses: %r", postfix_addresses)

            # Generate an invalid recipient (this means: a non-existing address
            # on one of the SUT's (virtual) domains)
            # This is not verified. Will clash during the test run. However, the
            # generated address is highly unlikely to be included in the server's
            # configuration.
            # Yeah, this is crazy. Basically: hash the first address, omit the
            # first character and append the first virtual domain for the
            # domain part.
            invalid_recipient = "{}@{}".format(
                str(hash(postfix_addresses[0]))[1:], postfix_vdomains[0]
            )
            logger.debug("invalid_recipient: %s", invalid_recipient)
        except MailsrvIOException as e:
            logger.error("Could not read config files")
            raise e

        # Queue some mails to the mailserver (non-secure)
        suite: Any = OtherMtaTestSuite(
            valid_recipients=postfix_addresses,
            invalid_recipients=[invalid_recipient],
            target_ip=args.target_host,
        )
        overall_result = suite.run()

        # Queue some more mails to the mailserver (using STARTTLS)
        suite = OtherMtaTlsTestSuite(
            valid_recipients=postfix_addresses,
            invalid_recipients=[invalid_recipient],
            target_ip=args.target_host,
            mail_count_offset=overall_result.get_mail_count(),
        )
        overall_result += suite.run()

        mapped_aliases = map_logins_to_aliases(postfix_sendermap)

        for account in mapped_aliases:
            suite = SubmissionTestSuite(
                username=account,
                password=get_password_plain(account, dovecot_passwd),
                valid_from=mapped_aliases[account],
                target_ip=args.target_host,
                mail_count_offset=overall_result.get_mail_count(),
            )
            overall_result += suite.run()

        logger.info("Result: %s", overall_result)
        logger.debug("Result (detail): %r", overall_result)

        # Minimal test suite to verify, that logins to POP3 have to be
        # performed over a secure connection (using STARTTLS)
        suite = NoNonSecureAuth(
            target_ip=args.target_host,
        )
        suite.run()

        # Map the mails to mailboxes
        # This result is then used to verify the actual delivery of the
        # messages as required, using the POP3 protocol, see
        # ``VerifyMailGotDelivered``
        mapped_mails = map_mails_to_mailboxes(
            overall_result, postfix_vmailboxes, postfix_valiases, postfix_vdomains
        )
        logger.debug("Mapped Mails: %r", mapped_mails)

        for rcpt in mapped_mails:
            if rcpt not in dovecot_users:
                logger.debug("Skipping mailbox check for '%s'", rcpt)
                continue

            logger.verbose("Checking mailbox of '%s'", rcpt)  # type: ignore [attr-defined]
            suite = VerifyMailGotDelivered(
                target_ip=args.target_host,
                username=rcpt,
                password=get_password_plain(rcpt, dovecot_passwd),
                expected_messages=mapped_mails[rcpt],
            )
            suite.run()

        logger.summary("Test suite completed successfully!")  # type: ignore [attr-defined]
        sys.exit(0)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.debug(e, exc_info=True)  # noqa: G200
        sys.exit(1)
