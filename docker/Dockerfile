FROM ubuntu:latest


# Requirements
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install --no-install-recommends --yes -- \
    software-properties-common gpg-agent \
    git python3 python3-venv python3-pip build-essential && \
    add-apt-repository ppa:neovim-ppa/unstable && \
    apt-get update && \
    apt-get install --no-install-recommends --yes -- neovim && \
    rm -rf -- /var/lib/apt/lists/*


# Dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends --yes -- \
    nodejs \
    npm \
    clang \
    golang-go && \
    rm -rf -- /var/lib/apt/lists/*


# INSTALL
COPY . /root/.config/nvim
ENV TERM=xterm-256color
WORKDIR "/root"
RUN ./.config/nvim/install.sh


# Cleanup
RUN apt-get autoremove --yes && \
    apt-get clean
