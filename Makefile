# SPDX-License-Identifier: MIT

# ### INTERNAL SETTINGS / CONSTANTS

# Python virtual environments
UTIL_VENV_DIR := .util-venv
UTIL_VENV_CREATED := $(UTIL_VENV_DIR)/pyvenv.cfg
UTIL_VENV_INSTALLED := $(UTIL_VENV_DIR)/packages.txt

TEST_VENV_DIR := .test-venv
TEST_VENV_CREATED := $(TEST_VENV_DIR)/pyvenv.cfg
TEST_VENV_INSTALLED := $(TEST_VENV_DIR)/packages.txt

PRE_COMMIT_READY := .git/hooks/pre-commit



# ``make``-specific settings
.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


tests/venv : $(TEST_VENV_INSTALLED)
.PHONY : tests/venv


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
	$(UTIL_VENV_DIR)/bin/pre-commit run $(pre-commit_files) $(pre-commit_id)
.PHONY : util/pre-commit



# Internal utility stuff to make the actual commands work

# Install the pre-commit hooks
$(PRE_COMMIT_READY) : $(UTIL_VENV_INSTALLED)
	$(UTIL_VENV_DIR)/bin/pre-commit install

# Create the utility virtual environment
$(UTIL_VENV_CREATED) :
	/usr/bin/env python3 -m venv $(UTIL_VENV_DIR)

# Install the required packages in the utility virtual environment
$(UTIL_VENV_INSTALLED) : $(UTIL_VENV_CREATED) requirements/util.txt
	$(UTIL_VENV_DIR)/bin/pip install -r requirements/util.txt
	$(UTIL_VENV_DIR)/bin/pip freeze > $(UTIL_VENV_INSTALLED)

# Create the virtual environment for the test suite
$(TEST_VENV_CREATED) :
	/usr/bin/env python3 -m venv $(TEST_VENV_DIR)

# Install the required packages in the test suite virtual environment
$(TEST_VENV_INSTALLED) : $(TEST_VENV_CREATED) requirements/test_suite.txt
	$(TEST_VENV_DIR)/bin/pip install -r requirements/test_suite.txt
	$(TEST_VENV_DIR)/bin/pip freeze > $(TEST_VENV_INSTALLED)
