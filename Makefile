# SPDX-License-Identifier: MIT

# ### INTERNAL SETTINGS / CONSTANTS

# Python virtual environments
UTIL_VENV_DIR := .util-venv
UTIL_VENV_CREATED := $(UTIL_VENV_DIR)/pyvenv.cfg
UTIL_VENV_INSTALLED := $(UTIL_VENV_DIR)/packages.txt

TOX_VENV_DIR := .tox-venv
TOX_VENV_CREATED := $(TOX_VENV_DIR)/pyvenv.cfg
TOX_VENV_INSTALLED := $(TOX_VENV_DIR)/packages.txt
TOX_CMD := $(TOX_VENV_DIR)/bin/tox

PRE_COMMIT_READY := .git/hooks/pre-commit



# ``make``-specific settings
.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


mypy_files ?= ""
local/mypy :
	$(TOX_CMD) -e typechecking -- mypy $(mypy_files)
.PHONY : local/mypy

util/black :
	$(MAKE) util/pre-commit pre-commit_id="black" pre-commit_files="--all-files"
.PHONY : util/black

util/isort :
	$(MAKE) util/pre-commit pre-commit_id="isort" pre-commit_files="--all-files"
.PHONY : util/isort

util/flake8 :
	$(MAKE) util/pre-commit pre-commit_id="flake8" pre-commit_files="--all-files"
.PHONY : util/isort

util/mypy :
	$(MAKE) util/pre-commit pre-commit_id="mypy" pre-commit_files="--all-files"
.PHONY : util/mypy

pre-commit_id ?= ""
pre-commit_files ?= ""
util/pre-commit : $(PRE_COMMIT_READY)
	$(TOX_CMD) -e util -- pre-commit run $(pre-commit_files) $(pre-commit_id)
.PHONY : util/pre-commit

util/docs/build/html : $(TOX_VENV_INSTALLED)
	$(TOX_CMD) -q -e docs
.PHONY : util/docs/build/html

util/docs/serve/html : $(TOX_VENV_INSTALLED)
	$(TOX_CMD) -q -e docs-serve
.PHONY : util/docs/serve/html


# Internal utility stuff to make the actual commands work

# Install the pre-commit hooks
$(PRE_COMMIT_READY) : | $(TOX_VENV_INSTALLED)
	$(TOX_CMD) -e util -- pre-commit install

# Create the virtual environment for the test suite
$(TOX_VENV_CREATED) :
	/usr/bin/env python3 -m venv $(TOX_VENV_DIR)

# Install the required packages in the test suite virtual environment
$(TOX_VENV_INSTALLED) : $(TOX_VENV_CREATED) requirements/tox.txt
	$(TOX_VENV_DIR)/bin/pip install -r requirements/tox.txt
	$(TOX_VENV_DIR)/bin/pip freeze > $@
