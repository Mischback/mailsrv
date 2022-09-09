#!/usr/bin/env python3
"""Run the validation suite."""


# Python imports
import argparse
import logging
import logging.config
import sys
from typing import Any, Callable, Dict, Optional, Tuple  # noqa: F401

# app imports
from mailsrv_aux.common import parser
from mailsrv_aux.common.exceptions import MailsrvBaseException
from mailsrv_aux.common.log import LOGGING_DEFAULT_CONFIG, add_level
from mailsrv_aux.validation import checks, messages
from mailsrv_aux.validation.exceptions import MailsrvValidationException

# get a module-level logger
logger = logging.getLogger()

# add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


class MailsrvValidationFailedException(MailsrvValidationException):
    """Indicate a failure during validation."""


class MailsrvValidationFailFastException(MailsrvValidationException):
    """Indicate a failure while running if fail-fast mode."""


def log_message(
    message: messages.TValidationMessage, skip: Optional[bool] = False
) -> None:
    """Log a message of a check function.

    Skipped checks are still put to log level VERBOSE. Hints are always printed
    to VERBOSE.
    """
    template = "%s %d: %s"
    template_hint = "Hint: %s"

    if skip:
        template = "[SKIPPED] " + template
        template_hint = "[SKIPPED] " + template_hint
        logger.verbose(  # type: ignore [attr-defined]
            template, message.id, message.level, message.msg
        )
    else:
        logger.log(message.level, template, message.id, message.level, message.msg)

    logger.verbose(template_hint, message.hint)  # type: ignore [attr-defined]


def check_wrapper(
    check_func: Callable[
        [checks.TCheckArg, checks.TCheckArg], list[messages.TValidationMessage]
    ],
    *args: checks.TCheckArg,
    fail_fast: bool = False,
    ignore: tuple = tuple(),
    **kwargs: Optional[Any],
) -> bool:
    """Wrap a check function and handle its return value."""
    got_errors = False
    ret_val = check_func(*args, **kwargs)

    for message in ret_val:
        if message.id in ignore:
            log_message(message, True)
            continue
        else:
            log_message(message)

        if message.level > messages.WARNING:
            got_errors = True
            if fail_fast:
                raise MailsrvValidationFailFastException("Fail fast, fail hard")

    return got_errors


def run_checks(
    postfix_vmailboxes: list[str],
    dovecot_users: list[str],
    fail_fast: bool = False,
    ignore: tuple = tuple(),
) -> None:
    """Run the actual check functions.

    The check functions are provided in the ``validation`` package. They are
    run from this function, wrapped to aggregate the results.
    """
    logger.info("Running checks")

    got_errors = False

    # actually run the check functions with a wrapper
    got_errors = got_errors or check_wrapper(
        checks.check_mailbox_has_account,
        postfix_vmailboxes,
        dovecot_users,
        fail_fast=fail_fast,
        ignore=ignore,
    )

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
        logger.verbose("Reading configuration files")  # type: ignore [attr-defined]

        logger.debug("dovecot_userdb_file=%s", args.dovecot_userdb_file)
        dovecot_users = parser.PasswdFileParser(
            args.dovecot_userdb_file
        ).get_usernames()
        logger.debug("dovecot_users: %r", dovecot_users)

        logger.debug("postfix_vmailbox_file=%s", args.postfix_vmailbox_file)
        postfix_vmailboxes = parser.KeyParser(args.postfix_vmailbox_file).get_values()
        logger.debug("postfix_vmailboxes: %r", postfix_vmailboxes)

        try:
            run_checks(postfix_vmailboxes, dovecot_users, fail_fast=args.fail_fast)
            sys.exit(0)
        except (MailsrvValidationFailedException, MailsrvValidationFailFastException):
            logger.error("Validation failed!")
            sys.exit(2)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.exception(e)  # noqa: G200
        sys.exit(1)
