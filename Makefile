# SPDX-License-Identifier: MIT

# ### INTERNAL SETTINGS / CONSTANTS

# Python virtual environments
UTIL_VENV_DIR := .util-venv
UTIL_VENV_CREATED := $(UTIL_VENV_DIR)/pyvenv.cfg
UTIL_VENV_INSTALLED := $(UTIL_VENV_DIR)/packages.txt

PRE_COMMIT_READY := .git/hooks/pre-commit



# ``make``-specific settings
.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


util/black :
	$(MAKE) util/pre-commit pre-commit_id="black" pre-commit_files="--all-files"
.PHONY : util/black

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
	python -m venv $(UTIL_VENV_DIR)

# Install the required packages in the utility virtual environments
$(UTIL_VENV_INSTALLED) : $(UTIL_VENV_CREATED) requirements/util.txt
	$(UTIL_VENV_DIR)/bin/pip install -r requirements/util.txt
	$(UTIL_VENV_DIR)/bin/pip freeze > $(UTIL_VENV_INSTALLED)
