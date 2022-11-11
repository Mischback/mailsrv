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

# The actual configuration files are placed in this directory.
#
# This directory may be determined while calling a recipe of this ``Makefile``.
# By default, the actual configs will be generated along the corresponding
# sample files.
#
# Please note: The actual configuration files are ignored in order to prevent
# leaking of actual configurations.
CONFIG_DIR ?= $(REPO_ROOT)/configs

# The filename of the settings file.
SETTINGS_ENV_FILE := settings.env

# Generate a list of all ``.sample`` files, stripping the common part of the
# path.
#
# This is used instead of make's built-in ``wildcard``, as it automatically
# supports infinite depth of directories. Portability is probably not an issue
# here, all Linux/Unix boxes should have ``find``.
ALL_SAMPLES := $(shell find $(SAMPLE_DIR) -type f -iname "*.sample" ! -iname "$(SETTINGS_ENV_FILE).sample" -printf "%P\n")

# Generate a list of all required configuration files.
#
# Basically this is a list of all sample files, removing the suffix ``.sample``
# and adding the value of $(CONFIG_DIR) as common prefix.
#
# This allows for some interesting applications:
# - it recreates the existing structure inside of $(SAMPLE_DIR) in $(CONFIG_DIR)
# - without specifying $(CONFIG_DIR) while calling make, this creates all
#   config files beneath their respective sample
# - when explicitly specifying $(CONFIG_DIR), the structure is created in
#   another location, but making them fully compatible.
CONFIGURATION_FILES := $(addprefix $(CONFIG_DIR)/,$(patsubst %.sample, %, $(ALL_SAMPLES)))

# Keep a reference to the actual settings file
CONFIGURATION_ENV_FILE := $(CONFIG_DIR)/$(SETTINGS_ENV_FILE)

# This is a list of all required config files with their final destination.
INSTALLATION_FILES := $(POSTFIX_CONF_DIR)/main.cf \
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
STAMP_SETUP_COMPLETED := $(MAKE_STAMP_DIR)/setup-completed
STAMP_SOFTWARE_READY := $(MAKE_STAMP_DIR)/software-ready
STAMP_POSTFIX_READY := $(MAKE_STAMP_DIR)/postfix-ready
STAMP_DOVECOT_READY := $(MAKE_STAMP_DIR)/dovecot-ready
STAMP_OS_PACKAGES := $(MAKE_STAMP_DIR)/os-packages-installed
STAMP_VMAIL_USER := $(MAKE_STAMP_DIR)/vmail-user-created
STAMP_POSTFIX_CHROOT := $(MAKE_STAMP_DIR)/postfix-chroot-prepared
STAMP_RESTART_AFTER_SETUP := $(MAKE_STAMP_DIR)/restart-after-setup

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

tmp :
	echo $(CONFIGURATION_FILES)
.PHONY : tmp


# ##### INSTALLATION
#
# These recipes are used to perform configuration and installation.

configure : $(CONFIGURATION_FILES) $(STAMP_SOFTWARE_READY)
.PHONY : configure

install : $(STAMP_SETUP_COMPLETED)
.PHONY : install

restart : $(STAMP_RESTART_AFTER_SETUP)
.PHONY : restart


# This recipe places Dovecot's configuration files in the desired directories.
$(DOVECOT_BASE_DIR)/% : $(CONFIG_DIR)/dovecot/%
	$(SCRIPT_SAVE_COPY) $@ $<

# This recipe places Postfix's configuration files in the desired directories.
$(POSTFIX_CONF_DIR)/% : $(CONFIG_DIR)/postfix/%
	$(SCRIPT_SAVE_COPY) $@ $<

# Compile the actual lookup databases.
#
# This uses Postfix's ``postmap`` utility to create / compile the actual lookup
# databases.
$(POSTFIX_CONF_DIR)/%.db : $(POSTFIX_CONF_DIR)/% | $(STAMP_POSTFIX_READY)
	echo "[INFO] Regenerating $@ using postmap"
	$(shell which postmap) $<

# Compile the local alias lookup database.
#
# The local alias database is special, as it is compiled with ``newaliases``
# instead of ``postmap``.
$(POSTFIX_CONF_DIR)/lookup_local_aliases.db : $(POSTFIX_CONF_DIR)/lookup_local_aliases $(POSTFIX_CONF_DIR)/main.cf | $(STAMP_POSTFIX_READY)
	echo "[INFO] Regenerating $@ using newaliases"
	$(shell which newaliases)
	touch $@

# Meta stamp to track, if a restart is required
$(STAMP_RESTART_AFTER_SETUP) : $(STAMP_SETUP_COMPLETED)
	echo "[INFO] Restarting services!"
	systemctl restart postfix*
	systemctl restart dovecot*
	$(create_dir)
	touch $@

# Meta stamp to track the overall status of the setup
$(STAMP_SETUP_COMPLETED) : $(INSTALLATION_FILES) $(STAMP_SOFTWARE_READY)
	$(create_dir)
	touch $@

# Meta stamp to track the overall status of the software
$(STAMP_SOFTWARE_READY) : $(STAMP_POSTFIX_READY) $(STAMP_DOVECOT_READY)
	$(create_dir)
	touch $@

# Meta stamp to track the status of Dovecot
$(STAMP_DOVECOT_READY) : $(STAMP_OS_PACKAGES) $(STAMP_VMAIL_USER) $(STAMP_POSTFIX_CHROOT)
	$(create_dir)
	touch $@

# Meta stamp to track the status of Postfix
$(STAMP_POSTFIX_READY) : $(STAMP_OS_PACKAGES) $(STAMP_VMAIL_USER) $(STAMP_POSTFIX_CHROOT)
	$(create_dir)
	touch $@

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

# Generate the actual configuration files from the samples.
#
# This implicit rule is used to generate all configuration files, applying
# variable substitution from $(CONFIGURATION_ENV_FILE).
$(CONFIG_DIR)/% : $(SAMPLE_DIR)/%.sample $(CONFIGURATION_ENV_FILE) | $(STAMP_SOFTWARE_READY)
	$(create_dir)
	$(SCRIPT_CONFIG_FROM_TEMPLATE) $@ $< $(CONFIGURATION_ENV_FILE)

# Generate the actual setting file from the sample.
#
# This will overwrite existing settings, if there is a more recent ``.sample``.
# This should not be a problem, as the existing file is backed up.
$(CONFIGURATION_ENV_FILE) : $(SAMPLE_DIR)/$(SETTINGS_ENV_FILE).sample
	$(create_dir)
	$(SCRIPT_SAVE_COPY) $@ $<


# ##### Utility commands, i.e. linters
#
# Basically all of them are PHONY targets. ``make`` is (mis-) used as a mere
# task runner here.

# This is an artificial recipe run the linters.
#
# It is called in GitHub Actions workflow, but it **would** be preferable to
# just run ``make util/pre-commit`` to run all linters.
# However, because of #33 this is currently not possible.
#
# FIXME: https://github.com/Mischback/mailsrv/issues/33
util/ci/linting : util/linter/black util/linter/isort util/linter/flake8 util/linter/shellcheck util/linter/doc8
	$(MAKE) util/pre-commit pre-commit_id="check-executables-have-shebangs" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="check-json" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="check-toml" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="check-yaml" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="check-vcs-permalinks" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="requirements-txt-fixer" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="end-of-file-fixer" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="trailing-whitespace" pre-commit_files="--all-files"
	$(MAKE) util/pre-commit pre-commit_id="mixed-line-ending" pre-commit_files="--all-files"
.PHONY : util/ci/linting

# FIXME: https://github.com/Mischback/mailsrv/issues/33
mypy_files ?= ""
util/local/mypy :
	$(TOX_CMD) -e typechecking -- mypy $(mypy_files)
.PHONY : util/local/mypy

util/linter/black :
	$(MAKE) util/pre-commit pre-commit_id="black" pre-commit_files="--all-files"
.PHONY : util/linter/black

util/linter/doc8 :
	$(MAKE) util/pre-commit pre-commit_id="doc8" pre-commit_files="--all-files"
.PHONY : util/linter/doc8

util/linter/isort :
	$(MAKE) util/pre-commit pre-commit_id="isort" pre-commit_files="--all-files"
.PHONY : util/linter/isort

util/linter/flake8 :
	$(MAKE) util/pre-commit pre-commit_id="flake8" pre-commit_files="--all-files"
.PHONY : util/linter/flake8

# FIXME: https://github.com/Mischback/mailsrv/issues/33
util/linter/mypy :
	$(MAKE) util/pre-commit pre-commit_id="mypy" pre-commit_files="--all-files"
.PHONY : util/linter/mypy

util/linter/shellcheck :
	$(MAKE) util/pre-commit pre-commit_id="shellcheck" pre-commit_files="--all-files"
.PHONY : util/linter/shellcheck

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
