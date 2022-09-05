"""Validate the provided mail-related configuration."""
# Python imports
import argparse
import logging
import sys

# external imports
from config_validator import checks, parser
from utility.log import add_level

# get the general logger object
logger = logging.getLogger("config_validator")

# Add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)

if __name__ == "__main__":

    # logging setup
    #
    # The actual setup has to be provided only if this script is called by
    # itsself.
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(logging.DEBUG)
    log_formatter_default = logging.Formatter("%(message)s")
    log_formatter_debug = logging.Formatter(
        "%(levelname)-8s - [%(module)s] - %(message)s (%(filename)s:%(lineno)d)"
    )
    log_handler.setFormatter(log_formatter_default)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    # setup the argument parser
    arg_parser = argparse.ArgumentParser(
        description="Run some tests against a mail server."
    )

    # positional arguments
    arg_parser.add_argument(
        "dovecot_userdb", action="store", help="Dovecot's passwd-like userdb file"
    )
    arg_parser.add_argument(
        "postfix_vdomain", action="store", help="Postfix's virtual_domains file"
    )
    arg_parser.add_argument(
        "postfix_vmailbox", action="store", help="Postfix's virtual_mailbox file"
    )
    arg_parser.add_argument(
        "postfix_valias", action="store", help="Postfix's virtual_alias file"
    )

    # optional arguments
    arg_parser.add_argument(
        "-v", "--verbose", help="Enable verbose messages", action="count", default=0
    )
    arg_parser.add_argument(
        "-d", "--debug", help="Enable debug messages", action="store_true"
    )

    args = arg_parser.parse_args()

    if args.verbose == 1:
        logger.setLevel(logging.INFO)
    if args.verbose == 2:
        logger.setLevel(logging.VERBOSE)
        logger.verbose("Verbose logging enabled!")
    # enable debug messages
    if args.debug:
        # set a formatter that has more information
        log_handler.setFormatter(log_formatter_debug)
        # set the logging level to DEBUG
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled!")

    logger.summary("Running validation...")

    userdb = parser.DovecotUserdbPasswdfileParser(args.dovecot_userdb)
    logger.debug(userdb.get_usernames())

    v_domains = parser.PostfixOnlyKeysParser(args.postfix_vdomain).get_keys()
    logger.debug(v_domains)

    v_mailboxes = parser.PostfixOnlyKeysParser(args.postfix_vmailbox).get_keys()
    logger.debug(v_mailboxes)

    v_aliases = parser.PostfixKeyValueParser(args.postfix_valias).get_key_value()
    logger.debug(v_aliases)

    # Actually run the checks
    try:
        checks.mailbox_has_account(v_mailboxes, userdb.get_usernames())
        checks.address_matches_domains(list(v_aliases.keys()) + v_mailboxes, v_domains)
        checks.external_alias_targets(v_aliases, v_domains)
    except checks.ConfigValidatorWarning as e:
        # TODO: Include logic to treat warnings as errors here
        logger.warning(e)
    except checks.ConfigValidatorError as e:
        logger.error("[FAIL] {}".format(e))
        sys.exit(1)

    logger.summary("Validation of configuration completed successfully")
