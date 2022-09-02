"""Validate the provided mail-related configuration."""
# Python imports
import argparse
import logging
import sys

# external imports
from config_validator import parser
from utility.log import add_level

# get the general logger object
logger = logging.getLogger("validator")

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

    # DEVELOPMENT IN PROGRESS
    userdb = parser.DovecotUserdbPasswdfileParser(args.dovecot_userdb)

    logger.debug(userdb.get_usernames())
