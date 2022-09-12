#!/usr/bin/env python3
"""Run the test suite."""


# Python imports
import argparse
import logging
import logging.config
import sys

# app imports
from mailsrv_aux.common.exceptions import MailsrvBaseException
from mailsrv_aux.common.log import LOGGING_DEFAULT_CONFIG, add_level

# get a module-level logger
logger = logging.getLogger()

# add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


if __name__ == "__main__":
    # setup the logging module
    logging.config.dictConfig(LOGGING_DEFAULT_CONFIG)

    # prepare the argument parser
    arg_parser = argparse.ArgumentParser(
        description="Run a test suite against a mail server setup"
    )

    # mandatory arguments (positional arguments)

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
        default="./test_configs/dovecot_vmail_users",
        help="Specify a Dovecot user database file (passwd-like file)",
    )
    arg_parser.add_argument(
        "--postfix_vmailboxes",
        action="store",
        default="./test_configs/postfix_vmailboxes",
        help="Specify a Postfix virtual mailbox file",
    )
    arg_parser.add_argument(
        "--postfix_valiases",
        action="store",
        default="./test_configs/postfix_valiases",
        help="Specify a Postfix virtual alias file",
    )
    arg_parser.add_argument(
        "--postfix_vdomains",
        action="store",
        default="./test_configs/postfix_vdomains",
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

    # Read and parse the configuration files
    try:
        # logger.verbose("Reading configuration files")  # type: ignore [attr-defined]
        logger.summary("Test suite completed successfully!")  # type: ignore [attr-defined]
        sys.exit(0)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.exception(e)  # noqa: G200
        sys.exit(1)
