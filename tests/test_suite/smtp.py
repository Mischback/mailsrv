"""Test cases for SMTP.

These tests are meant to test the smtp functions of a server.
"""
# Python imports
import logging
import smtplib  # noqa: F401

# app imports
from test_suite.exceptions import (
    MailsrvTestSuiteConfigurationException,
    MailsrvTestSuiteException,
)

# get a module-level logger
logger = logging.getLogger(__name__)


class SmtpTestCase:
    """Test the SMTP setup of a mail server.

    The included tests verify, that the delivery of valid mails to mailboxes
    is working. This includes possible alias addresses.
    """

    class SmtpTestOperationalError(MailsrvTestSuiteException):
        """Raised for operational errors."""

    class SmtpTestError(MailsrvTestSuiteException):
        """Raised if the test fails."""

    def __init__(
        self,
        target_host=None,
        target_smtp_port=None,
        from_address=None,
        target_recipient_1=None,
        target_recipient_nonexistent=None,
    ):
        if target_host is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_host'"
            )
        self.target_host = target_host
        logger.debug("target_host: {}".format(self.target_host))

        if target_smtp_port is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_smtp_port'"
            )
        self.target_port = target_smtp_port
        logger.debug("target_port: {}".format(self.target_port))

        if from_address is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'from_address'"
            )
        self.from_address = from_address
        logger.debug("from_address: {}".format(self.from_address))

        if target_recipient_1 is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_recipient_1'"
            )
        self.recipient_1 = target_recipient_1
        logger.debug("recipient_1: {}".format(self.recipient_1))

        if target_recipient_nonexistent is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_recipient_nonexistent'"
            )
        self.recipient_nonexistent = target_recipient_nonexistent
        logger.debug("recipient_nonexistent: {}".format(self.recipient_nonexistent))

    def __sendmail(self, mail_from, rcpt_to, msg):
        try:
            self.smtp.sendmail(mail_from, rcpt_to, msg)
        except smtplib.SMTPRecipientsRefused:
            return False
        except Exception as e:
            raise e

        return True

    def _test01_mail_to_invalid_mailbox(self):
        logger.debug("Test 01: Mail to invalid mailbox")
        if self.__sendmail(self.from_address, self.recipient_nonexistent, "foobar"):
            raise self.SmtpTestError(
                "Mail to non-existent recipient got delivered successfully"
            )

    def _test02_mail_to_valid_mailbox(self):
        logger.debug("Test 02: Mail to valid mailbox")
        if not self.__sendmail(self.from_address, self.recipient_1, "foobar"):
            raise self.SmtpTestError("Mail to valid user got rejected")

    def run(self):
        """Run the actual tests.

        Establishes the SMTP connection using Python's ``smtplib`` and then
        executes the actual test methods.
        """
        logger.info("Running SMTP tests...")

        logger.debug("Connecting to target ({})".format(self.target_host))
        try:
            with smtplib.SMTP(
                host=self.target_host, port=self.target_port
            ) as self.smtp:
                try:
                    suite_completed = True
                    self._test01_mail_to_invalid_mailbox()
                    self._test02_mail_to_valid_mailbox()
                except self.SmtpTestError as e:
                    logger.error("Test failed!")
                    logger.error(e)
                    suite_completed = False
                finally:
                    self.smtp.quit()
                    if not suite_completed:
                        raise self.SmtpTestError("Test suite failed!")
        except smtplib.SMTPServerDisconnected as e:
            logger.error(
                "target ({}) closed the connection unexpectedly.".format(
                    self.target_host
                )
            )
            logger.debug(e, exc_info=1)
            raise self.SmtpTestOperationalError("Target closed the connection")
        except ConnectionRefusedError as e:
            logger.error("target ({}) refused the connection.".format(self.target_host))
            logger.debug(e, exc_info=1)
            raise self.SmtpTestOperationalError("Target refused the connection")

        logger.info("SMTP tests finished successfully.")
