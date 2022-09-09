#!/usr/bin/env python3
"""Run the validation suite."""


# Python imports
import argparse
import logging
import logging.config
import sys

# app imports
from mailsrv_aux.common.exceptions import MailsrvBaseException
from mailsrv_aux.common.log import LOGGING_DEFAULT_CONFIG, add_level
from mailsrv_aux.validation.exceptions import MailsrvValidationException

# get a module-level logger
logger = logging.getLogger()

# add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


class MailsrvValidationFailedException(MailsrvValidationException):
    """Indicate a failure during validation."""


def run_checks(fail_fast: bool = False, ignore: tuple = tuple()) -> None:
    """Run the actual check functions.

    The check functions are provided in the ``validation`` package. They are
    run from this function, wrapped to aggregate the results.
    """
    logger.info("Running checks")

    got_errors = False

    # actually run the check functions with a wrapper
    # got_errors = got_errors or check_wrapper(
    #    checks.check_mailbox_has_account,
    #    postfix_vmailboxes,
    #    dovecot_users,
    #    fail_fast=fail_fast,
    #    ignore=ignore
    # )

    if got_errors:
        raise MailsrvValidationFailedException("There were errors during validation")

    logger.info("All checks completed")


if __name__ == "__main__":
    # setup the logging module
    logging.config.dictConfig(LOGGING_DEFAULT_CONFIG)

    # prepare the argument parser
    arg_parser = argparse.ArgumentParser(
        description="Check and validate the interdependent configuration files of the mail setup"
    )

    # mandatory arguments (positional arguments)
    arg_parser.add_argument(
        "dovecot_userdb_file", action="store", help="Dovecot's passwd-like userdb file"
    )
    arg_parser.add_argument(
        "postfix_vmailbox_file", action="store", help="Postfix's virtual mailbox file"
    )

    # optional arguments (keyword arguments)
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Be more verbose; may be specified up to two times",
    )

    args = arg_parser.parse_args()

    if args.verbose == 1:
        logger.setLevel(logging.INFO)
    if args.verbose == 2:
        logger.setLevel(logging.VERBOSE)  # type: ignore [attr-defined]
        logger.verbose("Verbose logging enabled")  # type: ignore [attr-defined]

    try:
        # temporary
        run_checks()
        sys.exit(0)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.exception(e)  # noqa: G200
        sys.exit(1)
