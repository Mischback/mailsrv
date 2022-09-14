#!/usr/bin/env python3
"""Run the test suite."""


# Python imports
import argparse
import logging
import logging.config
import os
import sys

# app imports
from mailsrv_aux.common import parser
from mailsrv_aux.common.exceptions import MailsrvBaseException, MailsrvIOException
from mailsrv_aux.common.log import LOGGING_DEFAULT_CONFIG, add_level
from mailsrv_aux.test_suite.smtp import OtherMtaTestSuite

# get a module-level logger
logger = logging.getLogger()

# add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


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
        except MailsrvIOException as e:
            logger.error("Could not read config files")
            raise e

        suite = OtherMtaTestSuite(
            valid_recipients=postfix_addresses,
            invalid_recipients=[],
            target_ip=args.target_host,
        )
        suite.run()

        logger.summary("Test suite completed successfully!")  # type: ignore [attr-defined]
        sys.exit(0)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.debug(e, exc_info=True)  # noqa: G200
        sys.exit(1)
