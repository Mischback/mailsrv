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

.. important::
   :source:`configs/postfix/main.cf.template` does include the actual settings
   aswell as documentation of each setting with its references.

   It is not duplicated here, please see :issue:`38`.


*********
master.cf
*********

Postfix's ``master.cf`` defines which (sub) services of Postfix are launched.

.. important::
   :source:`configs/postfix/master.cf.template` does include the actual settings.

   :issue:`38` will consider this file aswell. See :issue:`17` aswell, as this
   will likely adjust Postfix's service configuration.
