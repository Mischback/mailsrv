##########
References
##########

This page lists lots of references. Most of them were actually used while
implementing **mailsrv**, some were providing background information and others
included information that was tested but not included in the actual setup.

.. important::
   The primary and most notable source for the setup is *Christoph Haas'*
   `ISPmail guide for Debian "Bullseye" <https://workaround.org/bullseye/>`_.

   **mailsrv** does deviate in quite some aspects, but the tutorial is the very
   base. I'm standing on the shoulders of giants here.


**********************
Official Documentation
**********************

- `Postfix <https://www.postfix.org/>`_ is the *Mail Transfer Agent*
  (`MTA <https://en.wikipedia.org/wiki/Message_transfer_agent>`_) in this setup.

  `Postfix's documentation <https://www.postfix.org/documentation.html>`_
  includes an actual configuration reference in
  `manpage format <https://www.postfix.org/postconf.5.html>`_ aswell as
  topic-specific guides.

  .. note::
     The Postfix-related configuration files of **mailsrv** do provide direct
     links to actual configuration values.

- `Dovecot <https://www.dovecot.org/>`_ is used as *Mail Delivery Agent*
  (`MDA <https://en.wikipedia.org/wiki/Message_delivery_agent>`_) and provides
  access to the mailboxes with
  `IMAP <https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_ and
  `POP3 <https://en.wikipedia.org/wiki/Post_Office_Protocol>`_.

  `Dovecot's documentation <https://doc.dovecot.org/>`_ includes an actual
  `configuration reference <https://doc.dovecot.org/settings/core/>`_ aswell as
  topic-specific guides.

  .. note::
     The Dovecot-related configuration files of **mailsrv** do provide direct
     links to actual configuration values.

  Dovecot's documentation seems a little bit unorganized, but is heavily linked
  between the pages. It's easy to get distracted, but on the other hand you can
  get fairly comprehensive information.


******
Guides
******

- `ISPmail guide for Debian "Bullseye" <https://workaround.org/bullseye/>`_ -
  Easily one of the best guides on *how to build your own mailserver*. It
  includes an easy to follow step-by-step guide to setup the required software
  in order to build a working private mail server, including spam protection
  measures, webmail interface and TLS security.

  **mailsrv** is heavily based on this tutorial, though it deviates in some
  points.

  The really cool thing about the guide is the fact, that beside creating a
  working mail server, you'll learn a lot about the included protocols like
  SMTP, IMAP, DNS and how they work together.

  Even if you use **mailsrv** out-of-the-box, this is a highly recommended read
  for a deeper understanding of the setup.

- `Mailserver mit Dovecot, Postfix, MySQL und Rspamd unter Debian 10 Buster <https://thomas-leister.de/mailserver-debian-buster/>`_
  is another detailed tutorial for a mail setup, only available in German
  (there is an
  `English version <https://thomas-leister.de/en/mailserver-debian-stretch/>`_,
  based on Debian 9 Stretch).

  It provides details on the required DNS setup, even including
  `unbound <https://www.nlnetlabs.nl/projects/unbound/about/>`_ as a local DNS
  resolver.

  Additionally, there is a section about *TLS policies* which might be
  included in future releases.
