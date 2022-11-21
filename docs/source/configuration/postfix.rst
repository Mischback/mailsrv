#######################
Postfix's Configuration
#######################

*******
main.cf
*******

Postfix's ``main.cf`` is the actual configuration file for Postfix, controlling
all aspects of the service.

.. note::
   The actual configuration file does not require the settings to be in any
   particular order, as Postfix will read the whole file during startup.

   While :source:`configs/postfix/main.cf.sample` have a lax ordering by
   *topic*, this reference provides the configuration in alphabetical order.


append_dot_mydomain
===================

Control if Postfix should append ``.$mydomain`` to addresses without domain
information.

**mailsrv** is only accepting messages with correct addresses, and appending
domain information is expected to be done by the *MUA*.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    append_dot_mydomain = no

- **Postfix Default**:

  - Postfix >= ``3.0``: ``append_dot_mydomain = no``
  - Postfix < ``3.0``: ``append_dot_mydomain = yes``

- **Reference**: https://www.postfix.org/postconf.5.html#append_dot_mydomain


biff
====

``biff`` is used to send *new mail* notifications to (local) users. As
**mailsrv** relies exclusively on virtual mailboxes, this is not required.

Postfix's default value for this setting is ``yes`` for compatibility, but it
can safely be turned off.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    biff = no

- **Postfix Default**: ``biff = yes``
- **Reference**: https://www.postfix.org/postconf.5.html#biff


compatibility_level
===================

Provide some backwards compatible default settings after upgrading Postfix.

This setting is not desired in **mailsrv**.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    compatibility_level = 99

- **Postfix Default**: ``compatibility_level = 0``
- **Reference**: https://www.postfix.org/postconf.5.html#compatibility_level


smptd_banner
============

This is the banner as used by Postfix during *SMTP* sessions. There are some
constraints regarding its value, as specified in
`RFC 5321 Section 4.3.1 <https://datatracker.ietf.org/doc/html/rfc5321#section-4.3.1>`_.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_banner = $myhostname ESMTP $mail_name

- **Postfix Default**: ``smptd_banner = $myhostname ESMTP $mail_name``
- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_banner


smtpd_tls_cert_file
===================

**TLS** does require a (public) certificate and a (private) key to provide the
desired encryption. This is the certificate, which identifies the server.

The setting expects a path to the actual certificate file. **mailsrv** makes
that path configurable using :source:`configs/settings.env.sample`, so the
actual configuration below contains the placeholder that will be replaced
during the configuration phase of **mailsrv**'s setup process.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_cert_file = ${MAILSRV_TLS_CERT}

- **Postfix Default**: ``smtpd_tls_cert_file =`` (empty)
- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_cert_file
- **Related Settings**:

  - :ref:`smtpd_tls_key_file`
  - :ref:`smtpd_tls_security_level`


smtpd_tls_mandatory_ciphers
===========================

This setting controls, which ciphers will be used whenever TLS usage is
mandatory.

The setting actually just determines which list of ciphers is used (``mediu``
in this case). The actual list of ciphers is then provided by
:ref:`tls_medium_cipherlist`.

The configuration value is based on
`Mozilla's recommendation <https://ssl-config.mozilla.org/#server=postfix&version=3.5.13&config=intermediate>`_
for Postfix.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_mandatory_ciphers = medium

- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_mandatory_ciphers
- **Related Settings**:

  - :ref:`tls_medium_cipherlist`
  - :ref:`smtpd_tls_ciphers`


smtpd_tls_mandatory_protocols
=============================

This setting controls, which versions of TLS may be used whenever TLS usage is
mandatory.

Effectively we want to use TLS > v1.2, but providing this setting like this is
only supported by Postfix > v3.6. Instead, we have to exclude the undesired
protocl versions.

The configuration value is based on
`Mozilla's recommendation <https://ssl-config.mozilla.org/#server=postfix&version=3.5.13&config=intermediate>`_
for Postfix.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_mandatory_protocols
- **Related Settings**:

  - :ref:`smtpd_tls_security_level`
  - :ref:`smtpd_tls_protocols`


smtpd_tls_key_file
==================

**TLS** does require a (public) certificate and a (private) key to provide the
desired encryption. This is the key.

The setting expects a path to the actual key file. **mailsrv** makes
that path configurable using :source:`configs/settings.env.sample`, so the
actual configuration below contains the placeholder that will be replaced
during the configuration phase of **mailsrv**'s setup process.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_key_file = ${MAILSRV_TLS_KEY}

- **Postfix Default**: ``smtpd_tls_key_file =`` (empty)
- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_key_file
- **Related Settings**:

  - :ref:`smtpd_tls_cert_file`
  - :ref:`smtpd_tls_security_level`


smtpd_tls_ciphers
=================

This setting controls, which ciphers will be used whenever TLS usage is
optional / opportunistic.

The setting actually just determines which list of ciphers is used (``mediu``
in this case). The actual list of ciphers is then provided by
:ref:`tls_medium_cipherlist`.

The configuration value is based on
`Mozilla's recommendation <https://ssl-config.mozilla.org/#server=postfix&version=3.5.13&config=intermediate>`_
for Postfix.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_ciphers = medium

- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_ciphers
- **Related Settings**:

  - :ref:`tls_medium_cipherlist`
  - :ref:`smtpd_tls_mandatory_ciphers`


smtpd_tls_protocols
===================

This setting controls, which versions of TLS may be used whenever TLS usage is
optional / opportunistic.

Effectively we want to use TLS > v1.2, but providing this setting like this is
only supported by Postfix > v3.6. Instead, we have to exclude the undesired
protocl versions.

The configuration value is based on
`Mozilla's recommendation <https://ssl-config.mozilla.org/#server=postfix&version=3.5.13&config=intermediate>`_
for Postfix.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_protocols
- **Related Settings**:

  - :ref:`smtpd_tls_security_level`
  - :ref:`smtpd_tls_mandatory_protocols`


smtpd_tls_security_level
========================

The parameter controls, whether Postfix offers TLS security for the SMTP
daemon.

The accepted values include ``none``, meaning no TLS use incoming SMTP
connections, ``may``, which offers TLS but let the connecting server choose and
``encrypt``, which makes the usage of TLS mandatory.

.. note::
   Making TLS usage mandatory is the most secure setting, however, it will
   prohibit receiving mails from less secure servers.

This requires the configuration of TLS certificates for Postfix, see the
related settings :ref:`smtpd_tls_cert_file` and :ref:`smtpd_tls_key_file`

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    smtpd_tls_security_level = may

- **Postfix Default**: ``smtpd_tls_security_level =`` (empty)
- **Reference**: https://www.postfix.org/postconf.5.html#smtpd_tls_security_level
- **Related Settings**:

  - :ref:`smtpd_tls_cert_file`
  - :ref:`smtpd_tls_key_file`
  - :ref:`smtpd_tls_mandatory_protocols`
  - :ref:`smtpd_tls_protocols`


tls_medium_cipherlist
=====================

Define which ciphers may be used for TLS.

The configuration value is based on
`Mozilla's recommendation <https://ssl-config.mozilla.org/#server=postfix&version=3.5.13&config=intermediate>`_
for Postfix, ignoring Postfix's recommendation to **not change** this
configuration value.

- **Actual setting** in :source:`configs/postfix/main.cf.sample`:

  .. code-block:: text

    tls_medium_cipherlist = ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384

- **Reference**: https://www.postfix.org/postconf.5.html#tls_medium_cipherlist
- **Related Settings**:

  - :ref:`smtpd_tls_mandatory_protocols`
  - :ref:`smtpd_tls_protocols`


*********
master.cf
*********
