"""Test suite to check the general setup of a mail server."""

# Python imports
import argparse
import logging
import os
import smtplib
import sys

# get the general logger object
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # logging setup
    #
    # The actual setup has to be provided only if this script is called by
    # itsself.
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(logging.DEBUG)
    log_formatter_default = logging.Formatter("%(message)s")
    log_formatter_debug = logging.Formatter("[%(levelname)s] - %(message)s")
    log_handler.setFormatter(log_formatter_default)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    # setup the argument parser
    parser = argparse.ArgumentParser(
        description="Run some tests against a mail server."
    )

    # positional arguments
    parser.add_argument(
        "target_host", action="store", help="The subject under test (SUT)"
    )

    # optional arguments
    parser.add_argument(
        "-v", "--verbose", help="Enable debug messages", action="store_true"
    )

    args = parser.parse_args()

    # enable debug messages
    if args.verbose:
        # set a formatter that has more information
        log_handler.setFormatter(log_formatter_debug)
        # set the logging level to DEBUG
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled!")

    target_host = args.target_host
    logger.debug("target_host: {}".format(target_host))
    target_smtp_port = os.getenv("MAILSRV_TEST_TARGET_SMTP_PORT", 25)
    logger.debug("target_smtp_port: {}".format(target_smtp_port))

    # start the actual test suite
    try:
        with smtplib.SMTP(host=target_host, port=target_smtp_port) as smtp:
            smtp.quit()
    except smtplib.SMTPServerDisconnected as e:
        logger.error(
            "target_host ({}) closed the connection unexpectedly.".format(target_host)
        )
        logger.debug(e)
    except ConnectionRefusedError as e:
        logger.error("target_host ({}) refused the connection.".format(target_host))
        logger.debug(e)

    logger.info("Test suite completed successfully!")
    sys.exit(0)
