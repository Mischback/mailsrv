##################
mailsrv's settings
##################

**mailsrv** uses a settings file to expose a set of configuration values for
easy configuration by the administrator.

The values in :source:`configs/settings.env.sample` are the applied to the
actual configuration files for Postfix and Dovecot.

.. important::
   :source:`configs/settings.env.sample` does include the actual values with
   their default values, references to Postfix's/Dovecot's official
   documentation and mentions the actual config file, where the setting is
   applied.

   The information is not duplicated here, please refer directly to the file
   and :issue:`38`.

.. note::
   The magic of substituting the actual settings in the configuration files is
   performed during **mailsrv**'s setup process by
   :source:`util/scripts/apply-env-to-template.sh`.
