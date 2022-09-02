"""Test suite to check the general setup of a mail server."""

# Python imports
import argparse
import logging
import sys

# app imports
from test_suite.log import add_level
from test_suite.smtp import SmtpStarttlsTestSuite, SmtpTestSuite

# get the general logger object
logger = logging.getLogger("test_suite")

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
    logger.setLevel(logging.SUMMARY)

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
        "-v", "--verbose", help="Enable verbose messages", action="count", default=0
    )
    parser.add_argument(
        "-d", "--debug", help="Enable debug messages", action="store_true"
    )

    args = parser.parse_args()

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

    logger.summary("Starting test suites...")
    # Test plain old SMTP
    # These tests simulate getting mail from another server
    try:
        smtp = SmtpTestSuite(target_ip=args.target_host)
        smtp_result = smtp.run()
    except SmtpTestSuite.SmtpOperationalError:
        logger.critical("Operational error! Aborting!")
        sys.exit(1)
    except SmtpTestSuite.SmtpTestSuiteError as e:
        logger.info("Error while running test suite: {}".format(e))
        logger.error("SMPT test suite finished with errors! Aborting!")
        sys.exit(1)

    try:
        smtp_tls = SmtpStarttlsTestSuite(
            target_ip=args.target_host, mail_count_offset=smtp_result.get_mail_count()
        )
        smtp_tls_result = smtp_tls.run()
    except SmtpStarttlsTestSuite.SmtpOperationalError:
        logger.critical("Operational error! Aborting!")
        sys.exit(1)
    except SmtpStarttlsTestSuite.SmtpTestSuiteError as e:
        logger.info("Error while running test suite: {}".format(e))
        logger.error("SMPT (STARTTLS) test suite finished with errors! Aborting!")
        sys.exit(1)

    smtp_results = smtp_result + smtp_tls_result
    logger.debug(smtp_results)

    logger.summary("[OK] Test suites completed successfully!")
    sys.exit(0)
