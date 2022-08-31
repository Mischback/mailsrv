"""Test suite to check the general setup of a mail server."""

# Python imports
import argparse
import logging
import sys

# app imports
# from test_suite.pop3 import Pop3sTestCase, Pop3TestCase
from test_suite.smtp import SmtpTestSuite

# get the general logger object
logger = logging.getLogger("test_suite")

if __name__ == "__main__":

    # logging setup
    #
    # The actual setup has to be provided only if this script is called by
    # itsself.
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(logging.DEBUG)
    log_formatter_default = logging.Formatter("%(message)s")
    log_formatter_debug = logging.Formatter(
        "[%(levelname)s] - [%(name)s] - %(message)s"
    )
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

    # Test plain old SMTP
    # These tests simulate getting mail from another server
    try:
        SmtpTestSuite(target_ip=args.target_host).run()
    except SmtpTestSuite.SmtpOperationalError as e:
        logger.critical("Operational error! Aborting!")
        logger.debug(e, exc_info=1)
        sys.exit(1)
    except SmtpTestSuite.SmtpTestSuiteError as e:
        logger.info("Error while running test suite: {}".format(e))
        logger.debug(e, exc_info=1)
        logger.critical("SMPT test suite finished with errors! Aborting!")
        sys.exit(1)

    # Run pop3 related tests
    # try:
    #    pop3_tests = Pop3TestCase(
    #        username=target_recipient_1,
    #        password="foobar",
    #        target_host=target_host,
    #        expected_messages=mails_queued[0],
    #    )
    #    pop3_tests.run()
    # except MailsrvTestSuiteConfigurationException as e:
    #    logger.error("Configuration error for Pop3TestCase: {}".format(e))
    #    logger.error("Configuration invalid! Aborting!")
    #    sys.exit(1)
    # except Pop3TestCase.Pop3TestOperationalError:
    #    logger.critical("Operational error! Aborting!")
    #    sys.exit(1)
    # except Pop3TestCase.Pop3TestError:
    #    logger.critical("POP3 test suite finished with errors! Aborting!")
    #    sys.exit(1)

    # try:
    #    pop3_tests = Pop3sTestCase(
    #        username=target_recipient_1,
    #        password="foobar",
    #        target_host=target_host,
    #        expected_messages=mails_queued[0],
    #    )
    #    pop3_tests.run()
    # except MailsrvTestSuiteConfigurationException as e:
    #    logger.error("Configuration error for Pop3TestCase: {}".format(e))
    #    logger.error("Configuration invalid! Aborting!")
    #    sys.exit(1)
    # except Pop3TestCase.Pop3TestOperationalError:
    #    logger.critical("Operational error! Aborting!")
    #    sys.exit(1)
    # except Pop3TestCase.Pop3TestError:
    #    logger.critical("POP3 test suite finished with errors! Aborting!")
    #    sys.exit(1)

    logger.info("Test suite completed successfully!")
    sys.exit(0)
