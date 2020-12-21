#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os.path import dirname, join, realpath
from time import sleep

from pynvim import Host, attach

MAIN = join(dirname(realpath(__file__)), "python")


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("socket_address")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with attach("socket", path=args.socket_address) as nvim:
        host = Host(nvim)
        host.start((MAIN,))


main()
