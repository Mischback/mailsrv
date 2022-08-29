"""Test cases for SMTP.

These tests are meant to test the smtp functions of a server.
"""
# Python imports
import logging
import smtplib  # noqa: F401

# external imports
from test_suite.exceptions import MailsrvTestSuiteConfigurationException

logger = logging.getLogger(__name__)


class SmtpTestCase:
    """Test the SMTP setup of a mail server.

    The included tests verify, that the delivery of valid mails to mailboxes
    is working. This includes possible alias addresses.
    """

    def __init__(
        self,
        target_host=None,
        target_smtp_port=None,
        from_address=None,
        target_recipient_1=None,
    ):
        if target_host is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_host'"
            )
        self.target_host = target_host

        if target_smtp_port is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_smtp_port'"
            )
        self.target_port = target_smtp_port

        if from_address is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'from_address'"
            )
        self.from_address = from_address

        if target_recipient_1 is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_recipient_1'"
            )
        self.recipient_1 = target_recipient_1

    def run(self):
        """Run the actual tests.

        Establishes the SMTP connection using Python's ``smtplib`` and then
        executes the actual test methods.
        """
        # start the actual test suite
        # try:
        #    with smtplib.SMTP(host=target_host, port=target_smtp_port) as smtp:
        #        # actually send a mail
        #        smtp.sendmail(from_address, target_recipient_1, "foobar")
        #        smtp.quit()
        # except smtplib.SMTPServerDisconnected as e:
        #    logger.error(
        #        "target_host ({}) closed the connection unexpectedly.".format(target_host)
        #    )
        #    logger.debug(e)
        # except ConnectionRefusedError as e:
        #    logger.error("target_host ({}) refused the connection.".format(target_host))
        #    logger.debug(e)
        logger.info("Running SMTP tests...")
