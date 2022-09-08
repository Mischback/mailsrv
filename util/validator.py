#!/usr/bin/env python3
"""Run the validation suite."""


# Python imports
import argparse
import sys

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Check and validate the interdependent configuration files of the mail setup"
    )

    arg_parser.add_argument(
        "dovecot_userdb_file", action="store", help="Dovecot's passwd-like userdb file"
    )
    arg_parser.add_argument(
        "postfix_vmailbox_file", action="store", help="Postfix's virtual mailbox file"
    )

    args = arg_parser.parse_args()

    print(args)

    sys.exit(0)
