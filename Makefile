# SPDX-License-Identifier: MIT

# ### INTERNAL SETTINGS / CONSTANTS


# Postfix's directory (Debian's default ``/etc/postfix``)
# Postfix will assume its ``master.cf`` and ``main.cf`` in this directory.
POSTFIX_CONF_DIR := /etc/postfix

# Find the location of this Makefile, which should also be the repository root,
# which is the root for all path's.
MAKE_FILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# This directory contains all the scripts
SCRIPT_DIR := $(MAKE_FILE_DIR)util/scripts

# This directory contains all the configs
CONFIG_DIR := $(MAKE_FILE_DIR)configs

SETTINGS_ENV_FILE := $(CONFIG_DIR)/settings.env

# This is a list of all required config files with their final destination.
# FIXME: Provide the list of required config files!
# TODO: Will need adjustment while building up the sequence of recipes!
CONFIG_FILES := $(POSTFIX_CONF_DIR)/main.cf \
                $(POSTFIX_CONF_DIR)/master.cf \
                $(POSTFIX_CONF_DIR)/lookup_local_aliases \
                $(POSTFIX_CONF_DIR)/lookup_local_aliases.db \
                $(POSTFIX_CONF_DIR)/lookup_sender2login \
                $(POSTFIX_CONF_DIR)/lookup_sender2login.db \
                $(POSTFIX_CONF_DIR)/lookup_valiases \
                $(POSTFIX_CONF_DIR)/lookup_valiases.db \
                $(POSTFIX_CONF_DIR)/lookup_vdomains \
                $(POSTFIX_CONF_DIR)/lookup_vdomains.db \
                $(POSTFIX_CONF_DIR)/lookup_vmailboxes \
                $(POSTFIX_CONF_DIR)/lookup_vmailboxes \
                $(POSTFIX_CONF_DIR)/lookup_vmailboxes.db

# The name of the actual setup scripts
SCRIPT_OS_PACKAGES := $(SCRIPT_DIR)/install-packages.sh
SCRIPT_VMAIL_USER := $(SCRIPT_DIR)/create-vmail-user.sh
SCRIPT_CONFIG_FROM_TEMPLATE := $(SCRIPT_DIR)/apply-env-to-template.sh
SCRIPT_LINK_CONFIG := $(SCRIPT_DIR)/create-symlink.sh
SCRIPT_SAVE_COPY := $(SCRIPT_DIR)/save-copy.sh

# make's internal stamps
# These are artificial files to track the status of commands / operations /
# recipes, that do not directly result in output files.
MAKE_STAMP_DIR := $(MAKE_FILE_DIR).make-stamps
STAMP_OS_PACKAGES := $(MAKE_STAMP_DIR)/os-packages-installed
STAMP_VMAIL_USER := $(MAKE_STAMP_DIR)/vmail-user-created

# Python virtual environments
# FIXME: These are currently unused... Do we need them?!
UTIL_VENV_DIR := $(MAKE_FILE_DIR).util-venv
UTIL_VENV_CREATED := $(UTIL_VENV_DIR)/pyvenv.cfg
UTIL_VENV_INSTALLED := $(UTIL_VENV_DIR)/packages.txt

TOX_VENV_DIR := $(MAKE_FILE_DIR).tox-venv
TOX_VENV_CREATED := $(TOX_VENV_DIR)/pyvenv.cfg
TOX_VENV_INSTALLED := $(TOX_VENV_DIR)/packages.txt
TOX_CMD := $(TOX_VENV_DIR)/bin/tox

PRE_COMMIT_READY := .git/hooks/pre-commit



# ``make``-specific settings
# FIXME: Make it silent again!
#.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


# These recipes perform the actual setup of mailsrv

# Actually perform the complete setup of the mailsrv. This command is to be
# used to trigger everything else.
install : $(STAMP_OS_PACKAGES) $(STAMP_VMAIL_USER) $(CONFIG_FILES)
.PHONY : install

# Create Postfix's required configuration files from the provided samples.
#
# This recipe creates ``main.cf`` and ``master.cf``.
#
# The configuration files are placed in Postfix's main directory (by default:
# ``/etc/postfix``) directly.
$(POSTFIX_CONF_DIR)/%.cf : $(CONFIG_DIR)/postfix/%.cf.sample $(SETTINGS_ENV_FILE)
	$(SCRIPT_CONFIG_FROM_TEMPLATE) $@ $< $(SETTINGS_ENV_FILE)

# Create Postfix's lookup tables.
#
# This recipe creates ``lookup_sender2login``, ``lookup_valiases``,
# ``lookup_vdomains`` and ``lookup_vmailboxes``.
#
# The configuration files are placed in Postfix's main directory (by default:
# ``/etc/postfix``) directly.
$(POSTFIX_CONF_DIR)/% : $(CONFIG_DIR)/postfix/%.sample
	$(SCRIPT_SAVE_COPY) $@ $<

# Compile the actual lookup databases.
#
# This uses Postfix's ``postmap`` utility to create / compile the actual lookup
# databases.
$(POSTFIX_CONF_DIR)/%.db : $(POSTFIX_CONF_DIR)/%
	$(shell which postmap) $<

# Generate the actual setting file from the sample
# TODO: Is this recipe really relevant? It is added during development of the
#       sample settings file.
$(SETTINGS_ENV_FILE) : $(SETTINGS_ENV_FILE).sample
	$(SCRIPT_SAVE_COPY) $@ $<

# Installation of the required packages (from the repositories)
$(STAMP_OS_PACKAGES) : $(SCRIPT_OS_PACKAGES)
	$(create_dir)
	$(SCRIPT_OS_PACKAGES)
	touch $@

# Create the required system user and group and create the mailbox directory
$(STAMP_VMAIL_USER) : $(SCRIPT_VMAIL_USER)
	$(create_dir)
	$(SCRIPT_VMAIL_USER)
	touch $@


# Utility commands, i.e. linters

mypy_files ?= ""
util/local/mypy :
	$(TOX_CMD) -e typechecking -- mypy $(mypy_files)
.PHONY : util/local/mypy

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


# Internal utility stuff to make the actual commands work

# Install the pre-commit hooks
$(PRE_COMMIT_READY) : | $(TOX_VENV_INSTALLED)
	$(TOX_CMD) -e util -- pre-commit install

# Create the virtual environment for running tox
$(TOX_VENV_CREATED) :
	/usr/bin/env python3 -m venv $(TOX_VENV_DIR)

# Install the required packages in tox's virtual environment
$(TOX_VENV_INSTALLED) : $(TOX_VENV_CREATED) requirements/tox.txt
	$(TOX_VENV_DIR)/bin/pip install -r requirements/tox.txt
	$(TOX_VENV_DIR)/bin/pip freeze > $@

# Utility function to create required directories on the fly
create_dir = @mkdir -p $(@D)
