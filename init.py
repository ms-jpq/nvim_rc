#!/usr/bin/env python3

from os import environ, pathsep
from sys import path

from python.consts import PATH_PREPEND, RT_DIR

path.append(RT_DIR)
environ["PATH"] = pathsep.join((*PATH_PREPEND, environ["PATH"]))


from argparse import ArgumentParser, Namespace

from pynvim import attach

from python.client import Client
from python.nvim.client import run_client


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--server-socket", default=None)
    parser.add_argument("--headless", action="store_true", default=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nvim = None

    if args.server_socket:
        nvim = attach("socket", path=args.server_socket)
    elif args.headless:
        nvim = attach("child", argv=())

    if nvim:
        run_client(nvim, client=Client(headless=args.headless))
    else:
        exit(69)


main()
