"""Test cases for SMTP.

These tests are meant to test the smtp functions of a server.
"""
# Python imports
import logging
import os
import smtplib
import time
from collections import defaultdict
from functools import total_ordering

# app imports
from test_suite.exceptions import MailsrvTestSuiteException
from test_suite.fixture_mail import GENERIC_VALID_MAIL
from test_suite.log import add_level

# get a module-level logger
logger = logging.getLogger(__name__)

# Add the VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


def combine_smtp_suite_results(result1, result2):
    """Merge two dictionaries with identical keys."""
    result_keys = [k for k in result1.keys()]
    result_merged = {k: result1[k] + result2[k] for k in result_keys}

    return result_merged


@total_ordering
class SmtpTestProtocol:
    """Data class to store the results of running a test suite."""

    def __init__(self, sent=None, rejected=None, accepted=None):
        if sent is None:
            self._mails_sent = list()
        else:
            self._mails_sent = sent

        if rejected is None:
            self._mails_rejected = list()
        else:
            self._mails_rejected = rejected

        if accepted is None:
            self._mails_accepted = defaultdict(list)
        else:
            self._mails_accepted = accepted

    def mail_sent(self, subject):
        """Add the subject of a mail to the list of sent mails."""
        self._mails_sent.append(subject)

    def mail_rejected(self, subject):
        """Add the subject of a mail to the list of rejected mails."""
        self._mails_rejected.append(subject)

    def mail_accepted(self, recipient, subject):
        """Add the subject of a mail to the list of accepted mails."""
        self._mails_accepted[recipient].append(subject)

    def __bool__(self):
        """Return ``True`` if there were some mails sent."""
        return self._mails_sent.len() != 0

    def __eq__(self, other):
        """Check equality with ``other`` object."""
        # see https://stackoverflow.com/a/2909119
        # see https://stackoverflow.com/a/8796908
        # see https://stackoverflow.com/a/44575926
        if isinstance(other, SmtpTestProtocol):
            return self.__key() == other.__key()
        return NotImplemented

    def __lt__(self, other):
        """Comparing these objects does not make sense semantically."""  # noqa: D401
        # see https://stackoverflow.com/a/44575926
        return NotImplemented

    def __hash__(self):
        """Provide a unique representation of the instance."""
        # see https://stackoverflow.com/a/2909119
        return hash(self.__key())

    def __repr__(self):
        """Provide an instance's `representation`."""
        # see https://stackoverflow.com/a/12448200
        return "<SmtpTestProtocol(sent={}, rejected={}, accepted={})>".format(
            self._mails_sent.__repr__(),
            self._mails_rejected.__repr__(),
            self._mails_accepted.__repr__(),
        )

    def __str__(self):
        """Provide a string representation."""
        return "Mails sent: {} ({} rejected)".format(
            self._mails_sent.len(), self._mails_rejected.len()
        )

    def __key(self):
        """Provide internal representation of the instance."""
        # see https://stackoverflow.com/a/2909119
        return (self._mails_sent, self._mails_rejected, self._mails_accepted)


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
        suite_name="Generic Suite",
        local_hostname="mail.another-host.test",
        mail_count_offset=0,
    ):
        self.target_ip = target_ip
        self.target_port = target_port
        self.suite_name = suite_name
        self.local_hostname = local_hostname
        # ``__init__()``'s parameter is called ``_offset``, but this attribute
        # will only be incremented at the end of ``_sendmail()``, so in order
        # to let the numbering start with *1*, this has to be added here.
        self._mail_counter = mail_count_offset + 1
        self._protocol = SmtpTestProtocol()

    def _pre_connect(self):
        pass

    def _pre_run(self):
        pass

    def _post_run(self):
        pass

    def _run_tests(self):
        raise NotImplementedError("Has to be implemented in real test suite")

    def _generate_subject(self):
        return "{} {}".format(self._mail_counter, hash(time.time()))

    def _increment_mail_counter(self):
        self._mail_counter += 1

    def _sendmail(
        self, from_addr, to_addrs, msg_template, mail_options=(), rcpt_options=()
    ):
        # Prepare the actual mail for sending:
        # 1) RCPT TO:
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
            header_to = to_addrs
        else:
            # to_addrs is already a list
            header_to = ", ".join(to_addrs)

        # 2) Generate the subject
        header_subject = self._generate_subject()

        # 3) Actualle generate the message from the template
        # TODO: Actually name the parameters in ``tests/test_suite/fixture_mail.py``
        msg = msg_template.format(
            mail_from=from_addr,
            rcpt_to=header_to,
            subject=header_subject,
        )

        logger.debug(
            "sendmail(): {}, {}, {:16.16}, {}, {}".format(
                from_addr, to_addrs, msg, mail_options, rcpt_options
            )
        )

        self._increment_mail_counter()
        self._protocol.mail_sent(header_subject)

        try:
            # actually send the mail
            resp = self.smtp.sendmail(
                from_addr, to_addrs, msg, mail_options, rcpt_options
            )
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused):
            self._protocol.mail_rejected(header_subject)
            raise

        for addr in to_addrs:
            if addr not in resp:
                self._protocol.mail_accepted(addr, header_subject)

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
                logger.verbose(
                    "Connection to target ({}) established".format(self.target_ip)
                )

                self._pre_run()
                self._run_tests()
                self._post_run()

                self.smtp.quit()
                logger.verbose(
                    "Connection to target ({}) terminated".format(self.target_ip)
                )
        except smtplib.SMTPException as e:
            logger.critical("SMTP exception: '{}'".format(e))
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("SMTP exception")
        except ConnectionRefusedError as e:
            logger.critical("Target ({}) refused the connection".format(self.target_ip))
            logger.debug(e, exc_info=1)
            raise self.SmtpOperationalError("Connection refused")

        logger.summary("{} finished successfully".format(self._suite_name))


class SmtpTestSuite(SmtpGenericTestSuite):
    """Provide tests for a mail setup, simulating mails from another server."""

    def __init__(self, target_ip=None, mail_count_offset=0):
        super().__init__(
            target_ip=target_ip,
            suite_name="SMTP Suite",
            mail_count_offset=mail_count_offset,
        )

        # provide some specific things
        self.default_sender = os.getenv(
            "MAILSRV_TEST_SMTP_SENDER", "sender@another-host.test"
        )
        self.default_recipient = os.getenv(
            "MAILSRV_TEST_SMTP_RECIPIENT_1", "user_one@sut.test"
        )
        self.alternate_recipient = os.getenv(
            "MAILSRV_TEST_SMTP_RECIPIENT_2", "user_two@sut.test"
        )

    def test_single_mailbox(self):
        """Send a mail to a valid single mailbox.

        This mail is expected to get delivered / to be accepted.
        """
        logger.verbose("Mail to a single mailbox")
        logger.debug("test_single_mailbox()")

        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            self.default_recipient,
        )

        try:
            if (
                self._sendmail(self.default_sender, self.default_recipient, message)
                != {}
            ):
                raise self.SmtpTestSuiteError("Mail to a valid mailbox got rejected")
        except smtplib.SMTPRecipientsRefused:
            raise self.SmtpTestSuiteError("Mail to a valid mailbox got rejected")

        logger.verbose("Test completed successfully")

    def test_simple_alias(self):
        """Send a mail to an alias.

        This mail is expected to get delivered / to be accepted.
        """
        logger.verbose("Mail to an alias")
        logger.debug("test_simple_alias()")

        rcpt = os.getenv("MAILSRV_TEST_SMTP_ALIAS_1", "alias_one@sut.test")
        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            rcpt,
        )

        try:
            if self._sendmail(self.default_sender, rcpt, message) != {}:
                raise self.SmtpTestSuiteError("Mail to a valid alias got rejected")
        except smtplib.SMTPRecipientsRefused:
            raise self.SmtpTestSuiteError("Mail to a valid alias got rejected")

        logger.verbose("Test completed successfully")

    def test_multiple_recipients(self):
        """Send a mail to multiple recipients.

        This mail is expected to get delivered / to be accepted.
        """
        logger.verbose("Mail to multiple recipients")
        logger.debug("test_multiple_recipients()")

        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            "{}, {}".format(self.default_recipient, self.alternate_recipient),
        )

        try:
            if (
                self._sendmail(
                    self.default_sender,
                    [self.default_recipient, self.alternate_recipient],
                    message,
                )
                != {}
            ):
                raise self.SmtpTestSuiteError(
                    "Mail to multiple recipients got rejected"
                )
        except smtplib.SMTPRecipientsRefused:
            raise self.SmtpTestSuiteError("Mail to multiple recipients got rejected")

        logger.verbose("Test completed successfully")

    def test_list_alias(self):
        """Send a mail to an alias, that is actually a list.

        This mail is expected to get delivered / to be accepted.
        """
        logger.verbose("Mail to an alias (list)")
        logger.debug("test_list_alias()")

        rcpt = os.getenv("MAILSRV_TEST_SMTP_ALIAS_LIST", "alias_list@sut.test")
        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            rcpt,
        )

        try:
            if self._sendmail(self.default_sender, rcpt, message) != {}:
                raise self.SmtpTestSuiteError(
                    "Mail to a valid alias (list) got rejected"
                )
        except smtplib.SMTPRecipientsRefused:
            raise self.SmtpTestSuiteError("Mail to a valid alias (list) got rejected")

        logger.verbose("Test completed successfully")

    def test_nonexistent_mailbox(self):
        """Send a mail to a invalid single mailbox.

        This mail is expected to be rejected.
        """
        logger.verbose("Mail to a nonexistent mailbox")
        logger.debug("test_nonexistent_mailbox()")

        rcpt = os.getenv(
            "MAILSRV_TEST_SMTP_RECIPIENT_NONEXISTENT", "idontevenexist@sut.test"
        )
        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            rcpt,
        )

        try:
            if self._sendmail(self.default_sender, rcpt, message) == {}:
                raise self.SmtpTestSuiteError("Mail to an invalid mailbox got accepted")
        except smtplib.SMTPRecipientsRefused:
            logger.debug("sendmail() raised SMTPRecipientsRefused as expected!")

        logger.verbose("Test completed successfully")

    def test_relay_mail(self):
        """Send a mail to a mail address, the SUT is not responsible for.

        This mail is expected to get delivered / to be accepted.
        """
        logger.verbose("Mail to a relay host's mailbox")
        logger.debug("test_relay_mail()")

        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            self.default_sender,
        )

        try:
            if self._sendmail(self.default_sender, self.default_sender, message) == {}:
                raise self.SmtpTestSuiteError(
                    "Mail to a relay host's mailbox got accepted"
                )
        except smtplib.SMTPRecipientsRefused:
            logger.debug("sendmail() raised SMTPRecipientsRefused as expected!")

        logger.verbose("Test completed successfully")

    def test_corrupt_alias(self):
        """Send a mail to a valid alias that points to a non-existent mailbox.

        This mail is expected to get delivered / to be accepted, but a BOUNCE
        message will be created.

        This test is considered "Passing" if the mail is accepted by the SUT.
        In order to verify the actual behaviour of the SUT, the BOUNCE message
        has to be checked.
        """
        logger.verbose("Mail to a corrupted alias")
        logger.debug("test_corrupt_alias()")

        rcpt = os.getenv("MAILSRV_TEST_SMTP_ALIAS_INVALID", "alias_invalid@sut.test")
        subject = self.get_subject(self._test_counter)
        message = GENERIC_VALID_MAIL.format(
            subject,
            self.default_sender,
            rcpt,
        )

        try:
            if self._sendmail(self.default_sender, rcpt, message) != {}:
                raise self.SmtpTestSuiteError(
                    "Mail to a corrupt, though valid, alias got rejected"
                )
        except smtplib.SMTPRecipientsRefused:
            raise self.SmtpTestSuiteError(
                "Mail to a corrupt, though valid, alias got rejected"
            )

        logger.verbose("Test completed successfully")

    def _run_tests(self):
        logger.info("Start sending of mails...")

        self.test_single_mailbox()
        self.test_simple_alias()
        self.test_multiple_recipients()
        self.test_list_alias()
        self.test_nonexistent_mailbox()
        self.test_relay_mail()
        self.test_corrupt_alias()

        logger.info("All mails sent successfully.")
        logger.debug(self.result)


class SmtpStarttlsTestSuite(SmtpTestSuite):
    """Replicate ``SmtpTestSuite`` with a TLS connection."""

    def __init__(self, target_ip=None, mail_count_offset=0):
        super().__init__(
            target_ip=target_ip,
            suite_name="SMTP (STARTTLS) Suite",
            mail_count_offset=mail_count_offset,
        )

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
