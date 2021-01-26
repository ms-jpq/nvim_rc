FROM ubuntu:latest


# Requirements
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    git python3 python3-venv && \
    add-apt-repository ppa:neovim-ppa/stable && \
    apt-get update && \
    apt-get install -y neovim && \
    rm -rf /var/lib/apt/lists/*


# Dependencies
RUN apt-get update && \
    apt-get install -y \
    nodejs npm golang-go perl && \
    rm -rf /var/lib/apt/lists/*


# INSTALL
COPY . /root/.config/nvim
ENV TERM=xterm-256color
WORKDIR "/root"
RUN ./.config/nvim/init.py deps


# Cleanup
RUN apt-get autoremove -y && \
    apt-get clean
