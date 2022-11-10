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


# ### INTERNAL SETTINGS / CONSTANTS

# The absolute path to the repository.
#
# This assumes that this ``Makefile`` is placed in the root of the repository.
# REPO_ROOT does not contain a trailing ``/``
#
# Ref: https://stackoverflow.com/a/324782
# Ref: https://stackoverflow.com/a/2547973
# Ref: https://stackoverflow.com/a/73450593
REPO_ROOT := $(patsubst %/, %, $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

# This directory contains all the scripts
SCRIPT_DIR := $(REPO_ROOT)/util/scripts

# The base directory for all configuration samples.
SAMPLE_DIR := $(REPO_ROOT)/configs

CONFIG_DIR ?= $(REPO_ROOT)

# Keep a reference to the actual settings file
SETTINGS_ENV_FILE := $(CONFIG_DIR)/settings.env

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
MAKE_STAMP_DIR := $(REPO_ROOT)/.make-stamps
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
TOX_VENV_DIR := $(REPO_ROOT)/.tox-venv
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

# ##### DEVELOPMENT

repo :
	echo $(REPO_ROOT)
.PHONY : repo


# ##### INSTALLATION
#
# These recipes are used to perform configuration and installation.


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

util/docs/build/html : $(TOX_VENV_INSTALLED)
	$(TOX_CMD) -q -e docs
.PHONY : util/docs/build/html

util/docs/serve/html : $(TOX_VENV_INSTALLED)
	$(TOX_CMD) -q -e docs-serve
.PHONY : util/docs/serve/html

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
