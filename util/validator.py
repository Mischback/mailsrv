#!/usr/bin/env python3
"""Run the validation suite."""


# Python imports
import argparse
import logging
import logging.config
import sys
from typing import Any, Callable, Optional, TypeVar

# app imports
from mailsrv_aux.common import parser
from mailsrv_aux.common.exceptions import MailsrvBaseException
from mailsrv_aux.common.log import LOGGING_DEFAULT_CONFIG, add_level
from mailsrv_aux.validation import checks, messages
from mailsrv_aux.validation.exceptions import MailsrvValidationException

# Typing stuff
TCheckFunc = TypeVar("TCheckFunc", bound=Callable[..., Any])

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
    message: messages.ValidationMessage, skip: Optional[bool] = False
) -> None:
    """Log a message of a check function.

    Skipped checks are still put to log level VERBOSE. Hints are always printed
    to VERBOSE.

    Parameters
    ----------
    message : ``ValidationMessage``
        An instance of ``ValidationMessage`` or its derived classes.
    skip : bool, optional
        Flag to indicate, that this message should be *skipped*. In fact, this
        only causes the message to be printed to VERBOSE level, instead of the
        actual level.
    """
    # NOTE: This function uses dynamically added logging levels. The statements
    #       have to be marked with an ``type: ignore`` comment.
    template = "%s: %s"
    template_hint = "Hint: %s"

    if skip:
        template = "[SKIPPED] " + template
        template_hint = "[SKIPPED] " + template_hint
        logger.verbose(template, message.id, message.msg)  # type: ignore [attr-defined]
    else:
        logger.log(message.level, template, message.id, message.msg)

    if message.hint:
        logger.verbose(template_hint, message.hint)  # type: ignore [attr-defined]


def check_wrapper(
    check_func: TCheckFunc,
    *args: Any,
    fail_fast: bool = False,
    skip: tuple = (),
    **kwargs: Optional[Any],
) -> bool:
    """Wrap a check function and handle its return value.

    The basic interface of check functions is returning a list of
    ``ValidationMessage`` instances. These messages are processed in this
    wrapper by a) logging them (using ``log_message()``) and b) evaluating
    them to decide if an error causes a fast failing of the validator.

    Parameters
    ----------
    check_func : func
        The function to run.
    *args :
        These list of arguments is passed to the ``check_func``.
    fail_fast : bool
        Enable the fast failing, if set to ``True`` (default: ``False``)
    skip : tuple
        A ``tuple`` of ``ValidationMessage`` *id*'s that will be ignored.
    **kwargs :
        Any other keyword arguments are passed to the ``check_func``.

    Returns
    -------
    bool
        Returns ``True`` if the ``check_func`` did return with
        ``ValidationMessage`` instances of ``level`` ``ERROR``, otherwise
        ``False``.

    Raises
    ------
    MailsrvValidationFailFastException
        If a ``ValidationMessage`` with level above ``WARNING`` is encountered
        while ``fail_fast`` is ``True``, this exception is raised to stop the
        run of checks immediatly.
    """
    got_errors = False
    ret_val = check_func(*args, **kwargs)

    for message in ret_val:
        if message.id in skip:
            log_message(message, True)
            continue
        else:
            log_message(message)

        if message.level > messages.WARNING:
            got_errors = True
            if fail_fast:
                logger.debug("Encountered an error while running in fail-fast mode")
                raise MailsrvValidationFailFastException("Fail fast, fail hard")

    return got_errors


def run_checks(
    postfix_vmailboxes: list[str],
    postfix_valiases: dict[str, list[str]],
    postfix_vdomains: list[str],
    postfix_sender_map: dict[str, list[str]],
    dovecot_passwd: parser.PasswdFileParser,
    fail_fast: bool = False,
    skip: tuple = (),
) -> None:
    """Run the actual check functions.

    The check functions are provided in the ``validation`` package. They are
    run from this function, wrapped to aggregate the results.
    """
    # FIXME: Function documentation must be completed when all parameters are
    #        included in the function definition!
    logger.info("Running checks")
    logger.verbose("Skipping: %r", skip)  # type: ignore [attr-defined]

    # Build temporary lists
    dovecot_users = dovecot_passwd.get_usernames()
    postfix_addresses = postfix_vmailboxes + list(postfix_valiases.keys())
    logger.debug("postfix_adresses: %r", postfix_addresses)

    got_errors = False

    # actually run the check functions with a wrapper
    got_errors = (
        check_wrapper(
            checks.check_mailbox_has_account,
            postfix_vmailboxes,
            dovecot_users,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_addresses_match_domains,
            postfix_addresses,
            postfix_vdomains,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_address_can_send,
            postfix_addresses,
            postfix_sender_map,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_sender_has_login,
            postfix_sender_map,
            dovecot_users,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_account_has_function,
            postfix_vmailboxes,
            postfix_sender_map,
            dovecot_users,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_domain_has_admin_addresses,
            postfix_vdomains,
            postfix_addresses,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_resolve_alias_configuration,
            postfix_vmailboxes,
            postfix_valiases,
            postfix_vdomains,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
    )

    got_errors = (
        check_wrapper(
            checks.check_no_plaintext_passwords,
            dovecot_passwd,
            fail_fast=fail_fast,
            skip=skip,
        )
        or got_errors
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
    arg_parser.add_argument(
        "postfix_valias_file", action="store", help="Postfix's virtual alias file"
    )
    arg_parser.add_argument(
        "postfix_vdomain_file", action="store", help="Postfix's virtual domain file"
    )
    arg_parser.add_argument(
        "postfix_sender_map_file", action="store", help="Postfix's sender login map"
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
        "-s",
        "--skip",
        action="extend",
        help="Do not care about these errors; may be specified multiple times; accepts a list",
        nargs="+",
        type=str,
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

    try:
        skip = tuple(args.skip)
    except TypeError:
        skip = ()

    # Read and parse the configuration files
    try:
        logger.verbose("Reading configuration files")  # type: ignore [attr-defined]

        logger.debug("dovecot_userdb_file=%s", args.dovecot_userdb_file)
        dovecot_passwd = parser.PasswdFileParser(args.dovecot_userdb_file)
        # logger.debug("dovecot_users: %r", dovecot_users)

        logger.debug("postfix_vmailbox_file=%s", args.postfix_vmailbox_file)
        postfix_vmailboxes = parser.KeyParser(args.postfix_vmailbox_file).get_values()
        logger.debug("postfix_vmailboxes: %r", postfix_vmailboxes)

        logger.debug("postfix_valias_file=%s", args.postfix_valias_file)
        postfix_valiases = parser.KeyValueParser(args.postfix_valias_file).get_values()
        logger.debug("postfix_valiases: %r", postfix_valiases)

        logger.debug("postfix_vdomain_file=%s", args.postfix_vdomain_file)
        postfix_vdomains = parser.KeyParser(args.postfix_vdomain_file).get_values()
        logger.debug("postfix_vdomains: %r", postfix_vdomains)

        logger.debug("postfix_sender_map_file=%s", args.postfix_sender_map_file)
        postfix_sender_map = parser.KeyValueParser(
            args.postfix_sender_map_file
        ).get_values()
        logger.debug("postfix_sender_map: %r", postfix_sender_map)

        try:
            run_checks(
                postfix_vmailboxes,
                postfix_valiases,
                postfix_vdomains,
                postfix_sender_map,
                dovecot_passwd,
                fail_fast=args.fail_fast,
                skip=skip,
            )
            logger.summary("Validation successful!")  # type: ignore [attr-defined]
            sys.exit(0)
        except (MailsrvValidationFailedException, MailsrvValidationFailFastException):
            logger.error("Validation failed!")
            sys.exit(2)
    except MailsrvBaseException as e:
        logger.critical("Execution failed!")
        logger.exception(e)  # noqa: G200
        sys.exit(1)
