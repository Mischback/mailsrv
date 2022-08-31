"""Test cases for SMTP.

These tests are meant to test the smtp functions of a server.
"""
# Python imports
import logging
import smtplib

# app imports
from test_suite.exceptions import MailsrvTestSuiteException
from test_suite.log import add_level

# get a module-level logger
logger = logging.getLogger(__name__)

# Add the VERBOSE log level
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


class SmtpGenericTestSuite:
    """Wrap a test suite around the SMTP protocol."""

    class SmtpGenericException(MailsrvTestSuiteException):
        """Base class for all exceptions of SMTP test suites."""

    class SmtpOperationalError(SmtpGenericException):
        """Indicate operational errors, most likely while using ``smtplib``."""

    class SmtpTestSuiteError(SmtpGenericException):
        """Indicate an actual test failure."""

    def __init__(
        self,
        target_ip="127.0.0.1",
        target_port=smtplib.SMTP_PORT,
        local_hostname="mail.another-host.test",
    ):
        self.target_ip = target_ip
        self.target_port = target_port
        self.local_hostname = local_hostname

        self._suite_name = "Generic Suite"

    def _pre_connect(self):
        pass

    def _pre_run(self):
        pass

    def _post_run(self):
        pass

    def _run_tests(self):
        raise NotImplementedError("Has to be implemented in real test suite")

    def _sendmail(self, from_addr, to_addrs, msg, mail_options=(), rcpt_options=()):
        logger.debug(
            "sendmail(): {}, {}, {:16.16}, {}, {}".format(
                from_addr, to_addrs, msg, mail_options, rcpt_options
            )
        )
        try:
            return self.smtp.sendmail(
                from_addr, to_addrs, msg, mail_options, rcpt_options
            )
        except smtplib.SMTPHeloError as e:
            logger.critical("SMTP HELO Error")
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("SMTP HELO Error")

    def run(self):
        """Run the test suite."""
        logger.summary("Running {}...".format(self._suite_name))

        self._pre_connect()

        try:
            with smtplib.SMTP(
                host=self.target_ip,
                port=self.target_port,
                local_hostname=self.local_hostname,
            ) as self.smtp:

                self._pre_run()
                self._run_tests()
                self._post_run()

                self.smtp.quit()
                logger.verbose(
                    "Connection to target ({}) terminated".format(self.target_ip)
                )
        except smtplib.SMTPConnectError as e:
            logger.critical(
                "Error while connecting to target ({})".format(self.target_ip)
            )
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("Connection failed")
        except smtplib.SMTPServerDisconnected as e:
            logger.critical(
                "Target ({}) closed the connection unexpectedly".format(self.target_ip)
            )
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("Connection to target lost")
        except ConnectionRefusedError as e:
            logger.critical("Target ({}) refused the connection".format(self.target_ip))
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("Connection refused")

        logger.summary("{} finished successfully".format(self._suite_name))


class SmtpTestSuite(SmtpGenericTestSuite):
    """Provide tests for a mail setup, simulating mails from another server."""

    def __init__(self, target_ip=None):
        super().__init__(target_ip=target_ip)

        self._suite_name = "SMTP Suite"

    def _run_tests(self):
        logger.info("Start sending of mails...")

        logger.info("All mails sent successfully.")


class SmtpStarttlsTestSuite(SmtpTestSuite):
    """Replicate ``SmtpTestSuite`` with a TLS connection."""

    def __init__(self, target_ip=None):
        super().__init__(target_ip=target_ip)

        self._suite_name = "SMTP (STARTTLS) Suite"

    def _pre_run(self):
        logger.verbose("Sending command STARTTLS...")

        try:
            self.smtp.starttls()
        except (
            smtplib.SMTPNotSupportedError,
            RuntimeError,
            ValueError,
            smtplib.SMTPResponseException,
        ) as e:
            logger.critical("Could not establish TLS connection using STARTTLS")
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("TLS failure")
        logger.verbose("TLS encryption established")
