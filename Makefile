# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# ### SETTINGS

# Postfix's directory (Debian's default ``/etc/postfix``)
# Postfix will assume its ``master.cf`` and ``main.cf`` in this directory.
POSTFIX_CONF_DIR := /etc/postfix

# Dovecot's directory (Debian's default ``/etc/dovecot``)
# Actually more relevant is the ``conf.d`` directory inside of ``/etc/dovecot``,
# as it will contain the actual configuration files.
DOVECOT_BASE_DIR := /etc/dovecot
DOVECOT_CONF_DIR := $(DOVECOT_BASE_DIR)/conf.d

# Keep a reference to the actual settings file
SETTINGS_ENV_FILE := $(CONFIG_DIR)/settings.env


# ### INTERNAL SETTINGS / CONSTANTS

# Find the location of this Makefile, which should also be the repository root,
# which is the root for all path's.
MAKE_FILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# This directory contains all the scripts
SCRIPT_DIR := $(MAKE_FILE_DIR)util/scripts

# This directory contains all the configs
CONFIG_DIR := $(MAKE_FILE_DIR)configs

# This is a list of all required config files with their final destination.
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
                $(POSTFIX_CONF_DIR)/lookup_vmailboxes.db \
                $(DOVECOT_BASE_DIR)/vmail_users \
                $(DOVECOT_CONF_DIR)/10-auth.conf \
                $(DOVECOT_CONF_DIR)/10-mail.conf \
                $(DOVECOT_CONF_DIR)/10-master.conf \
                $(DOVECOT_CONF_DIR)/10-ssl.conf \
                $(DOVECOT_CONF_DIR)/15-lda.conf \
                $(DOVECOT_CONF_DIR)/90-quota.conf \
                $(DOVECOT_BASE_DIR)/quota-warning.sh \
                $(DOVECOT_CONF_DIR)/auth-passwdfile.conf.ext

# The name of the actual setup scripts
SCRIPT_OS_PACKAGES := $(SCRIPT_DIR)/install-packages.sh
SCRIPT_VMAIL_USER := $(SCRIPT_DIR)/create-vmail-user.sh
SCRIPT_CONFIG_FROM_TEMPLATE := $(SCRIPT_DIR)/apply-env-to-template.sh
SCRIPT_SAVE_COPY := $(SCRIPT_DIR)/save-copy.sh
SCRIPT_POSTFIX_CHROOT := $(SCRIPT_DIR)/prepare-postfix-chroot.sh

# make's internal stamps
# These are artificial files to track the status of commands / operations /
# recipes, that do not directly result in output files.
MAKE_STAMP_DIR := $(MAKE_FILE_DIR).make-stamps
STAMP_OS_PACKAGES := $(MAKE_STAMP_DIR)/os-packages-installed
STAMP_VMAIL_USER := $(MAKE_STAMP_DIR)/vmail-user-created
STAMP_POSTFIX_CHROOT := $(MAKE_STAMP_DIR)/postfix-chroot-prepared

# Python virtual environments
#
# Python is used as additional tooling in this repository. Most of the utility
# is run through ``tox``, as of now it is sufficient to create a dedicated
# (Python) virtual environment for ``tox``.
#
# ``tox``'s configuration is included in ``pyproject.toml``.
TOX_VENV_DIR := $(MAKE_FILE_DIR).tox-venv
TOX_VENV_CREATED := $(TOX_VENV_DIR)/pyvenv.cfg
TOX_VENV_INSTALLED := $(TOX_VENV_DIR)/packages.txt
TOX_CMD := $(TOX_VENV_DIR)/bin/tox

# ``pre-commit`` is used to run several code-quality tools automatically.
#
# ``pre-commit`` is run through ``tox`` aswell, see ``tox``'s ``util``
# environment.
PRE_COMMIT_READY := .git/hooks/pre-commit

# ``make``-specific settings
.SILENT :
.DELETE_ON_ERROR :
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


# ### RECIPES

# ##### These recipes perform the actual setup of the **mailsrv**.

# Actually perform the complete setup of the mailsrv. This command is to be
# used to trigger everything else.
install : $(STAMP_OS_PACKAGES) $(STAMP_POSTFIX_CHROOT) $(STAMP_VMAIL_USER) $(CONFIG_FILES)
.PHONY : install

# Create Dovecot's required configuration files from the provided samples.
#
# This recipe creates:
#   - ``10-auth.conf``
#   - ``auth-passwdfile.conf.ext``
#
# The configuration files are placed directly in Dovecot's configuration
# directory (by default: ``/etc/dovecot/conf.d``).
$(DOVECOT_CONF_DIR)/% : $(CONFIG_DIR)/dovecot/conf.d/%.sample $(SETTINGS_ENV_FILE)
	$(SCRIPT_CONFIG_FROM_TEMPLATE) $@ $< $(SETTINGS_ENV_FILE)

# Create Dovecot's additional configuration files from the provided samples.
#
# This recipe creates:
#   - ``vmail_users``
#
# The configuration files are placed directly in Dovecot's base directory (by
# default ``/etc/dovecot``).
$(DOVECOT_BASE_DIR)/% : $(CONFIG_DIR)/dovecot/%.sample
	$(SCRIPT_SAVE_COPY) $@ $<

# Create Postfix's required configuration files from the provided samples.
#
# This recipe creates:
#   - ``main.cf``
#   - ``master.cf``
#
# The configuration files are placed directly in Postfix's main directory (by
# default: ``/etc/postfix``).
$(POSTFIX_CONF_DIR)/%.cf : $(CONFIG_DIR)/postfix/%.cf.sample $(SETTINGS_ENV_FILE)
	$(SCRIPT_CONFIG_FROM_TEMPLATE) $@ $< $(SETTINGS_ENV_FILE)

# Create Postfix's lookup tables.
#
# This recipe creates:
#   - ``lookup_sender2login``
#   - ``lookup_valiases``
#   - ``lookup_vdomains``
#   - ``lookup_vmailboxes``
#
# The configuration files are placed directly in Postfix's main directory (by
# default: ``/etc/postfix``).
$(POSTFIX_CONF_DIR)/% : $(CONFIG_DIR)/postfix/%.sample
	$(SCRIPT_SAVE_COPY) $@ $<

# Compile the actual lookup databases.
#
# This uses Postfix's ``postmap`` utility to create / compile the actual lookup
# databases.
$(POSTFIX_CONF_DIR)/%.db : $(POSTFIX_CONF_DIR)/%
	echo "[INFO] Regenerating $@ using postmap"
	$(shell which postmap) $<

# Compile the local alias lookup database.
#
# The local alias database is special, as it is compiled with ``newaliases``
# instead of ``postmap``.
$(POSTFIX_CONF_DIR)/lookup_local_aliases.db : $(POSTFIX_CONF_DIR)/lookup_local_aliases $(POSTFIX_CONF_DIR)/main.cf
	echo "[INFO] Regenerating $@ using newaliases"
	$(shell which newaliases)

# Generate the actual setting file from the sample.
#
# This will overwrite existing settings, if there is a more recent ``.sample``.
# This should not be a problem, as the existing file is backed up.
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

# Prepare Postfix's ``chroot`` environment.
#
# As Dovecot's sockets are placed in non-default locations, this has to be run
# once.
$(STAMP_POSTFIX_CHROOT) : $(SCRIPT_POSTFIX_CHROOT) | $(STAMP_OS_PACKAGES)
	$(create_dir)
	$(SCRIPT_POSTFIX_CHROOT)
	touch $@


# ##### Utility commands, i.e. linters
#
# Basically all of them are PHONY targets. ``make`` is (mis-) used as a mere
# task runner here.

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


# ##### Internal utility stuff to make the actual commands work

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
