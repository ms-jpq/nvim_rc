#!/usr/bin/env python3

from sys import path
from os import environ, pathsep
from python.consts import RT_DIR, PATH_PREPEND

path.append(RT_DIR)
environ["PATH"] = pathsep.join((*PATH_PREPEND, environ["PATH"]))


from argparse import ArgumentParser, Namespace

from pynvim import attach

from python.client import Client
from python.nvim.client import run_client


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("server_socket")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nvim = attach("socket", path=args.server_socket)
    run_client(nvim, client=Client())


main()
