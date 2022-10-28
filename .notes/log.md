# Setup Log

This log is meant to be used as a reference while (re-) building this mail
server setup.


### Notation

- commands are given in backticks like this ``$ git commit -a``
- commands starting with ``#`` are executed as ``root`` user (or with root
  privileges, i.e. using ``sudo``)
- commands starting with ``$`` may be executed as *normal user*
- for readability, files are referenced in backticks


## Log

- ``# DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends postfix/stable``
- Get configuration files for ``Postfix``:
  - ``/etc/postfix/master.cf``
  - ``/etc/postfix/main.cf``
  - ``/etc/postfix/local_aliases``
  - ``/etc/postfix/sender_login_map``
  - ``/etc/postfix/virtual_aliases``
  - ``/etc/postfix/virtual_domains``
  - ``/etc/postfix/virtual_mailboxes``
- Create a dedicated user and group for virtual mails
  - ``# groupadd -g 5000 vmail``
  - ``# mkdir -p /var/vmail``
  - ``# useradd -g vmail -u 5000 -d /var/vmail vmail``
  - ``# chsh -s /usr/sbin/nologin vmail``
  - ``# chown -R vmail:vmail /var/vmail``
- ``# DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends dovecot-core/stable dovecot-lmtpd/stable dovecot-pop3d/stable dovecot-imapd/stable``
- Get configuration files for ``Dovecot``:
  - ``/etc/dovecot/conf.d/10-auth.conf``
