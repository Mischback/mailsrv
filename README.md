![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/Mischback/mailsrv/CI%20Default%20Branch/development?label=Actions&logo=github)
![GitHub License](https://img.shields.io/github/license/mischback/mailsrv)

[![Python style: black](https://img.shields.io/badge/Python%20style-black-000000?logo=Python&logoColor=white)](https://github.com/psf/black)
[![Shell style: shellcheck](https://img.shields.io/badge/Shell%20style-shellcheck-blue?logo=GNU%20Bash&logoColor=white)](https://github.com/koalaman/shellcheck)

[![Milestone Crawl](https://img.shields.io/github/milestones/progress/mischback/mailsrv/1?style=flat&color=%2333cc33)](https://github.com/Mischback/mailsrv/milestone/1)
[![Milestone Walk](https://img.shields.io/github/milestones/progress/mischback/mailsrv/2?style=flat&color=%23ffcc33)](https://github.com/Mischback/mailsrv/milestone/2)
[![Milestone Run](https://img.shields.io/github/milestones/progress/mischback/mailsrv/3?style=flat&color=%23999)](https://github.com/Mischback/mailsrv/milestone/3)
[![Milestone Fly](https://img.shields.io/github/milestones/progress/mischback/mailsrv/4?style=flat&color=%23999)](https://github.com/Mischback/mailsrv/milestone/4)

# mailsrv

This is a mail server setup using [Postfix](http://www.postfix.org/) as
**Mail Transport Agent** (MTA) and [Dovecot](https://www.dovecot.org/) as
**Mail Delivery Agent** (MDA) and IMAP/POP3 server.


## Disclaimer

This is my personal setup, which is based on *Christoph Haas'*
[ISPmail tutorial](https://workaround.org/bullseye/), though it deviates in
some aspects.

You may freely use the content of this repository (it's *MIT* licensed), but
be aware that you will have to adjust some aspects. I highly recommend working
through the [tutorial](https://workaround.org/bullseye/) to get a deeper
understanding of what is going on.
