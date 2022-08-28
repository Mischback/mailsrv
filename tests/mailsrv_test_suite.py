"""Test suite to check the general setup of a mail server."""

# Python imports
import argparse
import sys

if __name__ == "__main__":

    # setup the argument parser
    parser = argparse.ArgumentParser(
        description="Run some tests against a mail server."
    )

    args = parser.parse_args()

    sys.exit(0)
