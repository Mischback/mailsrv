# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Milestone: Crawl - 2022-11-28

See [Milestone: Crawl](https://github.com/Mischback/mailsrv/milestone/1?closed=1)
for the actual implementation steps.

### Added

- basic setup of ``Postfix`` and ``Dovecot`` completed
  - *Postfix* is working as MTA
  - *Dovecot* is working as LDA and IMAP/POP server
- installation script is working
- basic documentation is set up using ``Sphinx``
- repository is set up for ``dependabot`` and using ``GitHub Actions`` for CI
- basic implementation of a test suite using ``Python`` to verify that the
  setup of *Postfix* and *Dovecot* is working

<!--
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->
