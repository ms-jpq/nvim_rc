FROM ubuntu:latest


# Requirements
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install --no-install-recommends --yes -- \
    software-properties-common gpg-agent \
    make git curl jq python3-venv && \
    add-apt-repository ppa:neovim-ppa/unstable && \
    apt-get update && \
    apt-get install --no-install-recommends --yes -- neovim && \
    rm -v --recursive --force -- /var/lib/apt/lists/*


# Dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends --yes -- \
    clang \
    golang-go && \
    rm -v --recursive --force -- /var/lib/apt/lists/*


# INSTALL
COPY . /root/.config/nvim
ENV TERM=xterm-256color
WORKDIR /root
RUN make --directory ./.config/nvim install


# Cleanup
RUN apt-get autoremove --yes && \
    apt-get clean
