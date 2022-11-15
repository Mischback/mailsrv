############
Coding Style
############

The following sections describe the style conventions for all source code
inside of the repository.

They should be considered *guidelines*, you're free to do whatever you desire.
However, some of them are actually checked during CI, causing builds to fail.

If you activated ``pre-commit`` as per
:ref:`Getting Started <mailsrv-dev-doc-setup-getting-started-label>`, you
should be good to go!


*************
Shell Scripts
*************

- Shell scripts tend to get out of control, so keep them small, simple and
  controllable.
- `shellcheck <https://github.com/koalaman/shellcheck>`_ is used in
  ``pre-commit`` and during CI.
- Make sure to include *inline comments*.


******************
Python Source Code
******************

- The Python source code is formatted using
  `black <https://github.com/psf/black>`_; this basically means: You should not
  need to care about code formatting.
- Provide documentation for your code.
  `flake8 <https://github.com/PyCQA/flake8>`_ is configured to highlight
  missing documentation.


*************
Documentation
*************

Documentation is generated using
`Sphinx <https://github.com/sphinx-doc/sphinx>`_ and meant to be published on
`Read the Docs <https://readthedocs.org/>`_.

The configuration for ``Sphinx`` is provided in :source:`docs/source/conf.py`.

Additionnal Available ``Sphinx`` Roles
======================================

Besides ``Sphinx``'s
`pre-defined roles of the Python domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#python-roles>`_,
the following additional ``roles`` are provided through
:source:`docs/source/conf.py`:

``:commit:``
  Reference a commit of the
  `project's repo <https://github.com/Mischback/mailsrv>`_, e.g.::

    :commit:`e9f9f6947ce6334a6a9ccce5fc880d1ab5fb9a13`

  will generate a hyperlink like this
  :commit:`e9f9f6947ce6334a6a9ccce5fc880d1ab5fb9a13`.

  It is recommended to manually shorten the created link like this::

    :commit:`e9f9f6 <e9f9f6947ce6334a6a9ccce5fc880d1ab5fb9a13>`

  resulting in :commit:`e9f9f6 <e9f9f6947ce6334a6a9ccce5fc880d1ab5fb9a13>`.

``:issue:``
  Reference an issue in the
  `project's repo <https://github.com/Mischback/mailsrv>`_ by number,
  e.g.::

    :issue:`23`

  will generate a hyperlink like this: :issue:`23`.

``:source:``
  Reference a file or directory in the
  `project's repo <https://github.com/Mischback/mailsrv>`_, e.g.::

    :source:`docs/source/conf.py`

  will generate a hyperlink like this: :source:`docs/source/conf.py`.

  .. note::
    The file will be looked up in the repository's *default branch*, which is
    ``development``.

    Linking to directories works aswell, e.g. :source:`docs/source`.


*******************
Git Commit Messages
*******************

- highly recommended article:
  `How to write a Git Commit Message <https://cbea.ms/git-commit/>`_
- **tl;dr**:

  - Separate subject from body with one blank line
  - Limit the subject line to 50 characters
  - Capitalize the subject line
  - Do not end the subject line with a period
  - Use the imperative mood in the subject line
  - Wrap the body at around 72 characters
  - Use the body to explain *what* and *why* vs. *how*

- As a general guideline: the commit subject line should finish this sentence:

  | *If applied, this commmit will* **[your subject line here]**
