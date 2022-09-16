"""Provide a minimal (local) mailserver.

The test suite provides some test cases, that require the
*system under test* (SUT) to generate messages to the sending MTA (bounce
messages, non-delivery notifications).

This module is meant to receive these messages.
"""

# Python imports
import atexit
import contextlib
import logging

# external imports
from aiosmtpd.handlers import Mailbox
from aiosmtpd.smtp import (
    SMTP as aiosmtpdSMTP,
    Envelope as aiosmtpdEnvelope,
    Session as aiosmtpdSession,
)

# get a module-level logger
logger = logging.getLogger(__name__)

# create an ExitStack to clean up resources
LOCAL_MTA_RESOURCES = contextlib.ExitStack()


@atexit.register
def cleanup_local_mta_resources() -> None:
    logger.debug("Cleaning resources")
    LOCAL_MTA_RESOURCES.close()


class LocalMtaHandler(Mailbox):
    async def handle_RCPT(
        self,
        server: aiosmtpdSMTP,
        session: aiosmtpdSession,
        envelope: aiosmtpdEnvelope,
        address: str,
        rcpt_options: list[str],
    ) -> str:
        logger.debug("Got a mail: %s", address)
        return "250 OK"
