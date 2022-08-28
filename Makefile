# SPDX-License-Identifier: MIT

# ### INTERNAL SETTINGS / CONSTANTS

# Python virtual environments
UTIL_VENV_DIR := .util-venv
UTIL_VENV_CREATED := $(UTIL_VENV_DIR)/pyvenv.cfg
UTIL_VENV_INSTALLED := $(UTIL_VENV_DIR)/packages.txt



# ``make``-specific settings
.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


util/pre-commit/install : $(UTIL_VENV_INSTALLED)
	$(UTIL_VENV_DIR)/bin/pre-commit install
.PHONY : util/pre-commit/install

# Internal utility stuff to make the actual commands work

# Create the utility virtual environment
$(UTIL_VENV_CREATED) :
	python -m venv $(UTIL_VENV_DIR)

# Install the required packages in the utility virtual environments
$(UTIL_VENV_INSTALLED) : $(UTIL_VENV_CREATED) requirements/util.txt
	$(UTIL_VENV_DIR)/bin/pip install -r requirements/util.txt
	$(UTIL_VENV_DIR)/bin/pip freeze > $(UTIL_VENV_INSTALLED)
