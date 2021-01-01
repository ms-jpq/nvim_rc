FROM ubuntu:latest


# Requirements
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
    apt upgrade -y && \
    apt install -y \
    software-properties-common \
    git python3 python3-pip nodejs && \
    add-apt-repository ppa:neovim-ppa/stable && \
    apt update && \
    apt install neovim


# INSTALL
COPY . /root/.config/nvim
ENV TERM=xterm-256color
WORKDIR "/root"
RUN ./.config/nvim/init.py --install-runtime --install-packages


# Cleanup
RUN apt autoremove -y && \
    apt clean
