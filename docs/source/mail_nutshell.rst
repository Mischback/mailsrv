##################
Mail in a Nutshell
##################


****************************
Sending Mail - non-technical
****************************

#. A user fires up his mail programm of choice (e.g. Thunderbird, Outlook) to
   draft a message and then clicks **send**.

   .. code-block:: text

     -> "Hey, mail server, sorry to disturb your idle time... I have a message in need of transfer!"
     <- "Terrific! Can you prove your identity?"
     -> "Yeah, just a second... Oh, my username is..."
     <- "Hold on, hold on! You don't want to send these over an unencrypted connection!"
     -> "Sorry, forgot about that! Let's resume this chat encrypted."
     -- MAGIC HAPPENS
     <- "Great, now, what are your credentials again?"
     -> "My username is "frood" and my password is "narf"."
     <- "Welcome back! Now, let's see that message..."
     -> "I want to send it from sender@the-domain.test..."
     <- "Got ya! Let me just verify that you are allowed to use that address... Ok!"
     -> "The message is meant for recipient@target-domain.test..."
     <- "Got it! So, what's the actual message?"
     -> sends a wall of text
     <- "Great. I will transfer your message as soon as possible!"
     -> "Thank you, mail server! Bye!"
     <- "Yeah, whatever..."

#. The mail server (or more specifically: the Mail Transfer Agent (MTA))
   determines the address of the server which handles mails for the recipient
   address.

   .. code-block:: text

     -> "Yo, do you know who handles mails for target-domain.test?"
     <- "That would be mail.target-domain.test."
     -> "Very creative! By any change, you got his address?"
     <- "That would be 192.168.100.5."
     -> "Thanks buddy..."
     <- "..."

#. The mail server (again, the MTA) connects to the target server
   ``mail.target-domain.test`` using port ``25`` and submits the message.

   .. code-block:: text


     -> "Yo yo yo, it's me, mail.the-domain.test. I've got a message for one of your users."
     <- "Do you care to take encrypted?"
     -> "Nah, disregard. Not worth the effort. Will you accept the message?"
     <- "Sure thing. Wait, let me just look up the recipient... Ok, got him... Shoot!"
     -> "Here you go!"
     -> delivers the message
     <- "Got it!"
     -> "K, thx, bye!"
     <- "C ya!"

#. The MTA hands the message to the MDA (or LDA), who will add it to the
   recipient's mailbox.

   .. code-block:: text

     -> "Wake up, you lazy waste of bytes!"
     <- "What's up?"
     -> "Here's a message for recipient@target-domain.test. Make sure he receives it!"
     <- "Chill, man, I'll take care of it."

#. The recipient fires up his MUA to check for new mails using IMAP.

   .. code-block:: text

     -> "Greetings! Do you have any recent messages for my account?"
     <- "Let's see... Send your credentials!"
     -> "Ok, let's just establish an encrypted communication channel."
     <- "Sure."
     -- MAGIC HAPPENS
     -> "My username is recipient@target-domain.test and my password is foobar"
     <- "Seems valid, wait, I'll check your messages... Ah, here you go!"
     -> "Thanks buddy, see you soon!"
     <- "Yeah, whatever..."


************************
Sending Mail - technical
************************

Ok, let's get serious.

There's no *mail server* in the sense of having one service, that does handle
all required functions of *sending*, *receiving* and *retrieving* mails.

A complete setup consists of several components, which are interdependent and
are required to work together to provide the required functionality:

- The **Mail Transfer Agent**
  (`MTA <https://en.wikipedia.org/wiki/Message_transfer_agent>`_) handles
  communication with other servers, meaning handling all communication with
  other MTAs: It will receive messages for its recipients and pass messages for
  external addressees along.

  MTAs use the *Simple Mail Transfer Protocol*
  (`SMTP <https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol>`_) for
  communications. This is one of the oldest protocols of the internet,
  originally standardized in
  `RFC 772 <https://datatracker.ietf.org/doc/html/rfc772>`_ with its latest
  core version `RFC 5321 <https://datatracker.ietf.org/doc/html/rfc5321>`_.
  Today, there is a whole ecosystem of RFCs around SMTP, defining various
  protocol extensions, additional implementation details and addons.

  **mailsrv** uses `Postfix <https://www.postfix.org/>`_ in the MTA role.

- The **Mail Delivery Agent**
  (`MDA <https://en.wikipedia.org/wiki/Message_delivery_agent>`_) adds received
  messages to the users' mailboxes.

  **mailsrv** uses `Dovecot <https://www.dovecot.org/>`_ in the MDA role.

- **Mail User Agents** (`MUA <https://en.wikipedia.org/wiki/Email_client>`_)
  are used to read and write mails at the user's machine.

  Historically, users would read/write mails directly on the server. This
  architecture is obsolete nowadays. Users will access their mailboxes
  remotely, using protocols like *Internet Message Access Protocol*
  (`IMAP <https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_) or
  the older *Post Office Protocol*
  (`POP <https://en.wikipedia.org/wiki/Post_Office_Protocol>`_) to retrieve
  messages from their mailboxes.

  In order to sent mails, the MUA will contact a *Mail Submission Agent*
  (`MSA <https://en.wikipedia.org/wiki/Message_submission_agent>`_) on the
  corresponding server (see below).

  The *MUA* is not part of **mailsrv**'s setup, but there are lots of email
  clients to choose from, e.g. Thunderbird or Outlook.

  However, **mailsrv** provides access to mailboxes with IMAP and POP, using
  services implemented by `Dovecot <https://www.dovecot.org/>`_.

- The **Mail Submission Agent**
  (`MSA <https://en.wikipedia.org/wiki/Message_submission_agent>`_) will accept
  users' mails and process them, which means the *MTA* will deliver them to
  other servers as required.

  Technically, *mail submission* uses *SMTP* aswell on the communication
  protocol level, but its specification was moved to
  `RFC 6409 <https://datatracker.ietf.org/doc/html/rfc6409>`_.

  **mailsrv** uses `Postfix <https://www.postfix.org/>`_ in the MSA role.


Security Considerations
=======================

Let's face it, it's 2022 and the internet is no longer the nice playground it
was. Security and privacy are issues that do apply to mail aswell.

While *SMTP*, *POP* and *IMAP* were developed as clear-text protocols, their
communication must be secured today.

State of the art cryptography is available with **Transport Layer Security**
(`TLS <https://en.wikipedia.org/wiki/Transport_Layer_Security>`_) and
**mailsrv** makes heavy use of it.

While the default setup does provide the non-secure variants of SMTP, POP and
IMAP on their default ports, relevant parts of the setup do only work on
secured connections, using
`STARTTLS <https://en.wikipedia.org/wiki/Opportunistic_TLS>`_.

However, the *TLS* setup is not part of **mailsrv**. You will have to provide
the required certificates yourself.

.. TODO: Add reference to the related settings!
.. TODO: Add reference to the cookbook recipe for TLS
