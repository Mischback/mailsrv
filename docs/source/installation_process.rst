####################
Installation Process
####################


*************
Prerequisites
*************

**mailsrv** takes care of the setup of *Postfix* as MTA and *Dovecot* as LDA
and IMAP/POP server.

.. important::
   **mailsrv** does **not include** a webserver or a DNS server. And
   though **mailsrv** relies on TLS, it does not provide the means to generate
   and maintain certificates.

- **[mandatory]** A working installation of **Debian Stable**:

  .. note::
     As of now, this is **Bullseye**.

  *Working installation* does mean that the system is up and running, has
  network connectivity, including DNS, and you're able to execute commands with
  ``root`` privileges.

- **[mandatory]** Access to your server's DNS setup.

  You must be able to add/modify the DNS records for your server. Most likely
  your hoster provides some sort of interface to modify DNS information. It is
  required to modify the *Forward lookup zone* and **highly** recommended to be
  able to add entries to the *Reverse lookup zone*.

  .. note::
     Running a mail server does require a working DNS setup in order to enable
     other mail servers to send mails to your users.

     **mailsrv** can not
     automatically determine the required DNS configuration, so this step has
     to be done manually.

- **[recommended]** A working TLS setup.

  From a security-centric point of view, the usage of self-signed certificates
  is sufficient. Neither *Postfix* nor *Dovecot* will complain about them.

  However, many (most?) MUAs / email clients will complain, if they can't
  validate the provided certificates.

  You may want to use some service like
  `Let's Encrypt <https://letsencrypt.org/>`_ to generate *"trusted"*
  certificates and maintain them automatically. This is beyond the scope of
  **mailsrv**, but there are plenty of resources available.

  `ACME Client Implementations <https://letsencrypt.org/docs/client-options/>`_
  is the recommended starting point.


.. notes::
   All of the following commands are meant to be executed from the root of the
   repository.


*****************
Step 1: Configure
*****************

Overall Settings
================

Assuming you're starting from scratch (without using **mailsrv** before), just
run

.. code-block:: console

   make configure

to start the configuration process. The command will trigger the installation
of the required packages, create required system users and adjust some paths
and permissions. Also, this will create actual configuration files from the
repository's templates.

.. note::
   You may want to have a look at :ref:`Version-controlled Configuration`.

To adjust **mailsrv**'s configuration, you want to modify the file
``settings.env``. To apply the adjustments to the configuration files, just run

.. code-block:: console

   make configure

again.


Virtual Mail Setup
==================

The next step is the setup of virtual domains, mailboxes and aliases. These
are configured in

- ``postfix/lookup_vdomains``
- ``postfix/lookup_vmailboxes``
- ``postfix/lookup_valiases``

Refer to the documentation in the files.


Virtual Users
=============

All *virtual mailboxes* require an actual account, these will be added in
``dovecot/vmail_users``.

This file **must** contain the usernames in the form of a full mail address,
synchronized with ``postfix/lookup_vmailboxes``. To generate the required
password hashes, you can use *Dovecot*'s built-in ``doveadm pw`` utility (see
`its documentation <https://wiki.dovecot.org/Tools/Doveadm/Pw>`_).


Optional: Validating the virtual setup
======================================

**mailsrv** provides a Python-based script to perform a *basic* validation of
the configuration files.

.. code-block:: console

   ./util/validator.py


***************
Step 2: Install
***************

Everything is prepared, so running

.. code-block:: console

   make install

will copy the configuration files to their final destinations (e.g.
``/etc/postfix/``, ``/etc/dovecot/``).

Congratulation, your server is ready.

.. code-block:: console

   systemctl restart postfix*
   systemctl restart dovecot*
