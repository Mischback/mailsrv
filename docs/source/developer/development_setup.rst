.. _mailsrv-dev-doc-setup-label:

#################
Development Setup
#################

This section is targeted at development of **mailsrv** itsself.


.. _mailsrv-dev-doc-setup-getting-started-label:

***************
Getting Started
***************

#. clone the repository::

   $ git clone https://github.com/Mischback/mailsrv.git
   $ cd mailsrv

#. activate pre-commit hooks for code quality::

   $ make util/pre-commit

Congratulations! You're up and ready for development! If you're interested in
the juicy details of this setup, see
:ref:`the high level repo description <mailsrv-dev-doc-setup-desc-label>`
below.


.. _mailsrv-dev-doc-setup-desc-label:

************
Description
************

Repository Layout
=================

::

  mailsrv/
    .github/                 # utility files for GitHub, including workflows
    configs/                 # the actual configuration samples
    docs/                    # documentation sources for Sphinx
    requirements/            # requirments files to be used with pip
    util/                    # utility scripts
    .editorconfig            # configuration for supporting editors
    .flake8                  # configuration for flake8
    .gitignore               # ...
    .pre-commit-config.yaml  # configuration of pre-commit
    CHANGELOG.md             # ...
    LICENSE                  # MIT, actually
    Makefile                 # configuration for make
    pyproject.toml           # configuration for most of the tools
    README.md                # ...


Tools in Use
============

- **GNU make** (`make's official homepage <https://www.gnu.org/software/make/>`_):
  ``make`` is used for two different purposes in this project. On the one hand
  it drives the setup process by creating the actual configuration files, takes
  care of packet installation and other setup tasks. On the other hand ``make``
  is (mis-) used as a task runner, facilitating common development tasks.

  See the dedicated
  :ref:`section about the Makefile <mailsrv-dev-doc-setup-desc-makefile-label>`
  for more details.
- **tox** (`tox@GitHub <https://github.com/tox-dev/tox>`_): Actually all tools are run
  from within ``tox``, see :ref:`mailsrv-dev-doc-setup-desc-tox-env-label` for
  a detailled description of the provided environments and how they relate to
  given development tasks. Configuration is included in
  :source:`pyproject.toml` (as of now, ``tox`` does not fully support the
  ``pyproject.toml`` format and read its configuration from a string that
  in fact is in ``ini`` style).
- **pre-commit** (`pre-commit@GitHub <https://github.com/pre-commit/pre-commit>`_):
  Several code quality tools are run by ``pre-commit``. If activated as
  described in :ref:`mailsrv-dev-doc-setup-getting-started-label`, these tools
  are run on every commit, maintaining a high quality codebase.

  - **black** (`black@GitHub <https://github.com/psf/black>`_): Python code
    formatter. No configuration is provided, meaning the code formatting is
    handed over fully to ``black``.
  - **isort** (`isort@GitHub <https://github.com/PyCQA/isort>`_): Sort imports
    in Python source code. Configuration is included in
    :source:`pyproject.toml`.
  - **mypy** (`mypy@GitHub <https://github.com/python/mypy>`_): Perform static
    typechecking of Python source code.
  - **flake8** (`flake8@GitHub <https://github.com/PyCQA/flake8>`_): Python
    linter. Configuration is provided by :source:`.flake8`. The following
    plugins are run:

      - flake8-bugbear (`flake8-bugbear@GitHub <https://github.com/PyCQA/flake8-bugbear>`_)
      - flake8-comprehensions (`flake8-comprehensions@GitHub <https://github.com/adamchainz/flake8-comprehensions>`_)
      - flake8-docstrings (`flake8-docstrings@GitHub <https://github.com/PyCQA/flake8-docstrings>`_)
      - flake8-logging-format (`flake8-logging-format@GitHub <https://github.com/globality-corp/flake8-logging-format>`_)

  - **shellcheck** (`shellcheck@GitHub <https://github.com/koalaman/shellcheck>`_):
    Linter for shell scripts. Please note that the actual *pre-commit* hook is
    provided by `this alternative repo <https://github.com/shellcheck-py/shellcheck-py>`_
  - **doc8** (`doc8@GitHub <https://github.com/PyCQA/doc8>`_): Style checker for rST
    source files. No configuration is provided.

  The whole ``pre-commit`` configuration can be found in
  :source:`.pre-commit-config.yaml`. It includes some more *hooks* that are not
  Python-specific.

- **Sphinx** (`Sphinx@GitHub <https://github.com/sphinx-doc/sphinx>`_): The
  documentation is intended to be published on
  `Read the Docs <https://readthedocs.org/>`_, which uses ``Sphinx``.
  Configuration is provided in :source:`docs/source/conf.py`.

  .. warning::
    The documentation uses `Graphviz <https://graphviz.org/>`_ to provide
    visualizations. ``Sphinx`` runs the corresponding plugin, but it requires
    an installation of ``graphviz`` on the system.

    If you want to build the documentation locally, you will have to install
    the respective ``graphviz`` package.


.. _mailsrv-dev-doc-setup-desc-makefile-label:

Makefile
========

``make`` is used for two different purposes in this project.


Driving the Setup
-----------------

The installation and configuration process is driven by ``make``. There is a
set of recipes to create the required configuration files, run certain scripts
to install packages, add OS users/groups and creating required directories and
finally place the actual configurations in the required locations.


Task Runner
-----------

This is actually pretty straight forward. There are some common and repititive
development-related tasks, like *running linters* or *building the
documentation*.

Technically, these tasks are implemented using ``pre-commit``, ``tox`` or
local scripts.

There are some recipes in the :source:`Makefile` (or *targets*) that simply
call the respective commands or scripts (implemented as ``.PHONY`` targets).
``make`` is mis-used here, because it offers an easy way to provide a common
interface to different tools, including ``bash``/``zsh`` completion.

These recipes are backed-up by recipes that provide the required setup, e.g.
by setting up ``tox`` to run the environments.


.. _mailsrv-dev-doc-setup-desc-tox-env-label:

``tox`` Environments
====================

``tox``'s configuration is included in :source:`pyproject.toml`.

As this project is not Python-centric, ``tox`` is **not** used to automate the
unit testing but rather as a tool to manage different Python virtual
environments, that are used as utility runners during development.


``testenv:util``
----------------

This environment runs ``pre-commit`` itsself. The actual hooks are managed by
``pre-commit``.

Packages are installed from :source:`requirements/util.txt`.


``testenv:docs``
------------------

Locally build and view the app's documentation using ``sphinx``.

Packages are installed from :source:`requirements/documentation.txt`.


``testenv:docs-serve``
------------------------

Just an extension of ``testenv:sphinx`` that launches Python's built-in
``http.server`` in the output directory.

*Has to be provided as its own environment, because it should change into the
build directory. Internally,* ``testenv:docs`` *is reused completely.*
