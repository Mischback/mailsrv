# This Dockerfile is **ONLY MEANT** for CI testing! Do **NOT** use in production!

# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

# During CI, the setup should be tested automatically. As the test does require
# a network setup, consisting of several mail servers and a working DNS setup,
# the servers are built using Dockerfiles.
#
# These Dockerfiles **ARE NOT MEANT** for production usage!
#
# Running several services alongside each other in one container is just plain
# wrong. It does work, but defies the purpose of containers.

# As the whole setup is meant to be used on Debian Stable, base the image
# on Debian's official *stable* **slim** image.
#
# As of now, this is still **bullseye**.
FROM debian:bullseye-slim

# STAGE 01: Prepare the image for our repository.
#
# The image will take care of setting up our mail service setup using the
# installation process of the repository.
# a) This does (kind of) test, if the setup process is working;
# b) is done for convenience.
#
# However, a Docker Debian image does not provide the built-in tools that a
# *real* installation does, so we need to take care of that.

# Make the frontend "noninteractive"
ARG DEBIAN_FRONTEND=noninteractive

# Install packages to prepare the base system
#
# ATTENTION: Do **not** remove ``apt``'s lists, as they will be re-used during
#            the repository's setup process!
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y make

CMD ["bash", "-c", "which make"]
