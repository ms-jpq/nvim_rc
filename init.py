#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from asyncio import run

from pynvim import attach

from python.server import server


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("socket_address")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nvim = attach("socket", path=args.socket_address)
    run(server(nvim))


main()
