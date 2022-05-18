FROM ubuntu:latest


# Requirements
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install --no-install-recommends --yes -- \
    software-properties-common \
    git python3 python3-venv python3-pip && \
    # add-apt-repository ppa:neovim-ppa/stable && \
    apt-get update && \
    apt-get install --no-install-recommends --yes -- neovim && \
    rm -rf -- /var/lib/apt/lists/*


# Dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends --yes -- \
    nodejs \
    npm \
    golang-go && \
    rm -rf -- /var/lib/apt/lists/*


# INSTALL
COPY . /root/.config/nvim
ENV TERM=xterm-256color
WORKDIR "/root"
RUN ./.config/nvim/init.py deps


# Cleanup
RUN apt-get autoremove --yes && \
    apt-get clean
