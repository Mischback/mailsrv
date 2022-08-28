# SPDX-License-Identifier: MIT

# ### INTERNAL SETTINGS / CONSTANTS

# Python virtual environments
UTIL_VENV_DIR := .util-venv
UTIL_VENV_CREATED := $(UTIL_VENV_DIR)/pyvenv.cfg
UTIL_VENV_INSTALLED := $(UTIL_VENV_DIR/)/packages.txt



# ``make``-specific settings
.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


util/pre-commit/install : $(UTIL_VENV_INSTALLED)
	$(UTIL_VENV_DIR)/bin/pre-commit install
.PHONY : util/pre-commit/install


$(UTIL_VENV_CREATED) :
	python -m venv $(UTIL_VENV_DIR)

$(UTIL_VENV_INSTALLED) : $(UTIL_VENV_CREATED)
	$(UTIL_VENV_DIR)/bin/pip install -r requirements/util.txt

