"""Provide a minimal SMTP server for testing."""

# Python imports
import contextlib
import os
import sys
import tempfile
import time

# external imports
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox


class SmtpServer:
    """A minimal SMTP server to be used during the test suite."""

    def __init__(self, hostname="", port=8025, server_hostname=None):
        # Setup the SMTP server
        self.resources = contextlib.ExitStack()
        tempdir = self.resources.enter_context(tempfile.TemporaryDirectory())
        self.maildir_path = os.path.join(tempdir, "maildir")
        self.controller = Controller(
            Mailbox(self.maildir_path),
            hostname=hostname,
            port=port,
            server_hostname=server_hostname,
        )

        self.controller.start()
        self.resources.callback(self.controller.stop)

    def _stop(self):
        self.resources.close()


if __name__ == "__main__":
    print("Launching a minimal SMTP server at port 25")

    try:
        server = SmtpServer(port=25)
        print("Server started, waiting for keyboard interrupt (Ctrl+C)")
        while True:
            time.sleep(1)
    except PermissionError as e:
        print("Got a PermissionError. Most likely you tried to use a privileged port.")
        print(e)
        print("Try using a high port (>1024) or run as root")
        try:
            server._stop()
        except NameError:
            pass
        sys.exit(1)
    except KeyboardInterrupt:
        server._stop()
        print("Server stopped.")
        sys.exit(0)
