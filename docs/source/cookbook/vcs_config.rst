################################
Version-controlled Configuration
################################

**mailsrv** creates the actual configuration files from templates and copies
them to the required locations (i.e. ``/etc/postfix`` and
``/etc/dovecot/conf.d``).

However, it may be desired to keep the actual running configuration under
version control. This makes updates really easy and enables the administrator
to see any changes quickly.

.. note::
   **mailsrv**'s installation process will always create backups of existing
   configuration files. Administrators can use ``diff`` to see changes between
   old and current configuration.

Without any special consideration, ``make configure`` creates the configuration
files in **mailsrv**'s directory structure, right beside the respective
template. The repository's :source:`.gitignore` prohibits the generated
configuration files from being tracked in **mailsrv**'s repository.

The :source:`Makefile` allows the administrator to specify a location for the
intermediate configuration files.

   .. code-block:: console

      make configure CONFIG_DIR=~/mailsrv-config

This will create a directory ``mailsrv-config`` in the user's *home* directory,
which may be used in a version control system (e.g. ``git``).

   .. code-block:: console

      make install CONFIG_DIR=~/mailsrv-config

will then use these configuration files for the installation.
