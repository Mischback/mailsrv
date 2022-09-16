#!/usr/bin/env python3

"""Provide a wrapper around the (local) make recipe ``local/mypy``.

``mypy`` should be run through pre-commit, however, as the actual dependencies
are only available in a virtual environment, pre-commit's ``mypy`` hook has
no access to them.

The project includes a dedicated ``tox`` environment for typechecking, that
installs ``mypy`` together with the actual dependencies. To use this ``tox``
environment through ``pre-commit``, pre-commit actually calls this script which
translates it into a ``make`` command that executes the ``tox`` environment.
"""

# Python imports
import subprocess
import sys

if __name__ == "__main__":
    files_args = sys.argv[1:]

    files = "mypy_files={}".format(" ".join(files_args))

    tmp = subprocess.run(
        ["make", "local/mypy", files],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if tmp.returncode == 0:
        sys.exit(0)

    # FIXME: Only provide the actual output of ``mypy``
    print(tmp.stdout)

    sys.exit(tmp.returncode)
