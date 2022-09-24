#!/usr/bin/env python3
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
from mailsrv_aux.test_suite.smtp import OtherMtaTestSuite, OtherMtaTlsTestSuite

# get a module-level logger
logger = logging.getLogger()

# add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


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

            dovecot_users = parser.PasswdFileParser(args.dovecot_userdb).get_usernames()
            logger.debug("dovecot_users: %r", dovecot_users)

            postfix_vmailboxes = parser.KeyParser(args.postfix_vmailboxes).get_values()
            logger.debug("postfix_vmailboxes: %r", postfix_vmailboxes)

            postfix_valiases = parser.KeyValueParser(args.postfix_valiases).get_values()
            logger.debug("postfix_valiases: %r", postfix_valiases)

            postfix_vdomains = parser.KeyParser(args.postfix_vdomains).get_values()
            logger.debug("postfix_vdomains: %r", postfix_vdomains)

            # The addresses are the actual virtual mailboxes combined with the RHS
            # of the virtual aliases.
            postfix_addresses = postfix_vmailboxes + list(postfix_valiases.keys())
            logger.debug("postfix_addresses: %r", postfix_addresses)

            # Generate an invalid recipient (this means: a non-existing address
            # on one of the SUT's (virtual) domains)
            # This is not verified. Will clash during the test run. However, the
            # generated address is highly unlikely to be included in the server's
            # configuratio.
            invalid_recipient = "{}@{}".format(
                hash(postfix_addresses[0]), postfix_vdomains[0]
            )
            logger.debug("invalid_recipient: %s", invalid_recipient)
        except MailsrvIOException as e:
            logger.error("Could not read config files")
            raise e

        suite: Any = OtherMtaTestSuite(
            valid_recipients=postfix_addresses,
            invalid_recipients=[invalid_recipient],
            target_ip=args.target_host,
        )
        overall_result = suite.run()

        suite = OtherMtaTlsTestSuite(
            valid_recipients=postfix_addresses,
            invalid_recipients=[invalid_recipient],
            target_ip=args.target_host,
            mail_count_offset=overall_result.get_mail_count(),
        )
        overall_result += suite.run()

        logger.info("Result: %s", overall_result)
        logger.debug("Result (detail): %r", overall_result)

        mapped_mails = map_mails_to_mailboxes(
            overall_result, postfix_vmailboxes, postfix_valiases, postfix_vdomains
        )

        logger.debug("Mapped Mails: %r", mapped_mails)

        suite = NoNonSecureAuth(
            target_ip=args.target_host,
        )
        suite.run()

        # FIXME: Fetch username/password from dovecot's userdb
        # FIXME: Apply ``expected_mails`` from ``mapped_mails``
        suite = VerifyMailGotDelivered(
            target_ip=args.target_host,
            username="user_one@sut-one.test",
            password="foobar",
            expected_mails=["foo"],
        )
        suite.run()

        logger.summary("Test suite completed successfully!")  # type: ignore [attr-defined]
        sys.exit(0)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.debug(e, exc_info=True)  # noqa: G200
        sys.exit(1)
