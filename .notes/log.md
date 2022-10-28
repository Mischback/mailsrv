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
