########################
IP Address Configuration
########################


****
Why?
****

As outlined in :ref:`Mail in a Nutshell`, sending and receiving mails is
heavily interconnected with the *Domain Name System*. The MTA will perform a
DNS request to get the responsible mailserver of a domain (the ``MX`` record)
and another DNS request to get the server's IP address (the ``A`` or ``AAAA``
record).

The recipient's MTA might verify the sender's identity by doing a reverse
lookup of the sender MTA's IP address (its ``PTR`` record).

Additionally, the spam filtering services might use other information that is
provided by DNS, e.g. the
`Sender Policy Framework <https://en.wikipedia.org/wiki/Sender_Policy_Framework>`_
(SPF) and the
`Domain-based Message Authentication, Reporting and Conformance protocol <https://en.wikipedia.org/wiki/DMARC>`_
(DMARC).

If the server has multiple IP addresses, it must be ensured that the MTA uses
the correct one, while connecting to other MTAs.


****
How?
****

*Postfix* already provides the required configuration items to ensure the
desired behaviour.

**mailsrv** exposes them through :source:`configs/settings.env.template`.


Method 1
========

This method will make *Postfix* **listen** to all available interfaces, while
ensuring to use a specific interface/IP while **connecting** to other MTAs.

In ``settings.env``:

- set ``MAILSRV_POSTFIX_INTERFACES=all``
- use ``MAILSRV_BIND_IPV4`` or ``MAILSRV_BIND_IPV6`` to specifiy the desired
  (outgoing) IP address (depending on the usage of IPv4 and/or IPv6)


Method 2
========

This method will make *Postfix* **listen** to specific interfaces/IPs, while
ensuring to use a specific interface/IPs while **connecting** to other MTAs at
the same time.

In ``settings.env``:

- set ``MAILSRV_POSTFIX_INTERFACES`` to the desired interface/IP. You might
  want to add ``[::1],127.0.0.1`` to include the local loopback.
- use ``MAILSRV_BIND_IPV4`` or ``MAILSRV_BIND_IPV6`` to specifiy the desired
  (outgoing) IP address (depending on the usage of IPv4 and/or IPv6)

.. note::
   This method is used for the repository's test configurations.
