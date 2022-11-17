##################
Mail in a Nutshell
##################


*******************************
Visualization of Sending a Mail
*******************************

#. A user fires up his mail programm of choice (e.g. Thunderbird, Outlook) to
   draft a message and then clicks **send**. ::

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
   address. ::

     -> "Yo, do you know who handles mails for target-domain.test?"
     <- "That would be mail.target-domain.test."
     -> "Very creative! By any change, you got his address?"
     <- "That would be 192.168.100.5."
     -> "Thanks buddy..."
     <- "..."

#. The mail server (again, the MTA) connects to the target server
   ``mail.target-domain.test`` using port ``25`` and submits the message. ::

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
   recipient's mailbox. ::

     -> "Wake up, you lazy waste of bytes!"
     <- "What's up?"
     -> "Here's a message for recipient@target-domain.test. Make sure he receives it!"
     <- "Chill, man, I'll take care of it."

#. The recipient fires up his MUA to check for new mails using IMAP. ::

     -> "Greetings! Do you have any recent messages for my account?"
     <- "Let's see... Send your credentials!"
     -> "Ok, let's just establish an encrypted communication channel."
     <- "Sure."
     -- MAGIC HAPPENS
     -> "My username is recipient@target-domain.test and my password is foobar"
     <- "Seems valid, wait, I'll check your messages... Ah, here you go!"
     -> "Thanks buddy, see you soon!"
     <- "Yeah, whatever..."
