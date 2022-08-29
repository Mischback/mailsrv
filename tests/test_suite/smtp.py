"""Test cases for SMTP.

These tests are meant to test the smtp functions of a server.
"""
# Python imports
import logging
import smtplib

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
        target_alias_1=None,
        target_recipient_nonexistent=None,
        relay_recipient_1=None,
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

        if target_alias_1 is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_alias_1'"
            )
        self.alias_1 = target_alias_1
        logger.debug("alias_1: {}".format(self.alias_1))

        if target_recipient_nonexistent is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_recipient_nonexistent'"
            )
        self.recipient_nonexistent = target_recipient_nonexistent
        logger.debug("recipient_nonexistent: {}".format(self.recipient_nonexistent))

        if relay_recipient_1 is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'relay_recipient_1'"
            )
        self.relay_recipient = relay_recipient_1
        logger.debug("relay_recipient: {}".format(self.relay_recipient))

    def __sendmail(self, mail_from, rcpt_to, msg):
        try:
            self.smtp.sendmail(mail_from, rcpt_to, msg)
        except smtplib.SMTPRecipientsRefused:
            return False
        except Exception as e:
            raise e

        return True

    def _test01_mail_to_invalid_mailbox(self):
        if self.__sendmail(self.from_address, self.recipient_nonexistent, "foobar"):
            raise self.SmtpTestError(
                "Mail to non-existent recipient got delivered successfully"
            )
        logger.debug("Test 01: [SUCCESS] Mail to non-existent mailbox was rejected!")
        return (0, 1)

    def _test02_mail_to_valid_mailbox(self):
        if not self.__sendmail(self.from_address, self.recipient_1, "foobar"):
            raise self.SmtpTestError("Mail to valid user got rejected")
        logger.debug("Test 02: [SUCCESS] Mail to valid mailbox was accepted!")
        return (1, 0)

    def _test03_mail_to_valid_alias(self):
        if not self.__sendmail(self.from_address, self.alias_1, "foobar"):
            raise self.SmtpTestError("Mail to valid alias got rejected")
        logger.debug("Test 03: [SUCCESS] Mail to valid alias was accepted!")
        return (1, 0)

    def _test04_mail_to_other_domain(self):
        if self.__sendmail(self.from_address, self.relay_recipient, "foobar"):
            raise self.SmtpTestError("Mail to another domain was accepted")
        logger.debug("Test 04: [SUCCESS] Mail to another domain was rejected!")
        return (0, 1)

    def run(self):
        """Wrapp around ``_run()``."""
        logger.info("Running SMTP tests...")
        result = self._run()
        logger.info("SMTP tests finished successfully.")
        logger.debug("Delivered: {} / Rejected: {}".format(result[0], result[1]))
        return result

    def _pre_test(self):
        """Execute additional commands before the actual mails are sent.

        This is meant to add additional commands before queuing mail, e.g.
        ``STARTTLS``.
        """
        return

    def _run(self):
        """Run the actual tests.

        Establishes the SMTP connection using Python's ``smtplib`` and then
        executes the actual test methods.
        """
        logger.debug("Connecting to target ({})".format(self.target_host))
        try:
            with smtplib.SMTP(
                host=self.target_host, port=self.target_port
            ) as self.smtp:
                try:
                    # Prepare the overall result
                    result = (0, 0)
                    suite_completed = True
                    self._pre_test()
                    # Each test function returns a tuple of (queued, rejected)
                    # The results are summed, so that at the end of the run,
                    # a overall result may be returned to the calling test
                    # runner for further processing.
                    #
                    # The syntax is Python magic, see
                    # https://stackoverflow.com/a/498103
                    result = tuple(
                        map(sum, zip(result, self._test01_mail_to_invalid_mailbox()))
                    )
                    result = tuple(
                        map(sum, zip(result, self._test02_mail_to_valid_mailbox()))
                    )
                    result = tuple(
                        map(sum, zip(result, self._test03_mail_to_valid_alias()))
                    )
                    result = tuple(
                        map(sum, zip(result, self._test04_mail_to_other_domain()))
                    )
                    # Actually return the overall result
                    # If any test fails, the exception handling will terminate
                    # the overall run.
                    return result
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


class SmtpStarttlsTestCase(SmtpTestCase):
    """Test the SMTP setup of a mail server, with STARTTLS.

    The included tests verify, that the delivery of valid mails to mailboxes
    is working. This includes possible alias addresses.
    """

    def _pre_test(self):
        """Execute ``STARTTLS`` command before mails are queued."""
        self.smtp.starttls()
        logger.debug("Executing STARTTLS...")

    def run(self):
        """Wrap around ``_run()``."""
        logger.info("Running SMTP (STARTTLS) tests...")
        result = self._run()
        logger.info("SMTP (STARTTLS) tests finished successfully.")
        logger.debug("Delivered: {} / Rejected: {}".format(result[0], result[1]))
        return result
