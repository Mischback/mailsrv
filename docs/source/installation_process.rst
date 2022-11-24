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
