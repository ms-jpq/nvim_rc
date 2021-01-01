#!/usr/bin/env python3

from sys import path

from python.consts import RT_DIR

path.append(RT_DIR)


from argparse import ArgumentParser, Namespace

from pynvim import attach
from pynvim_pp.client import run_client

from python.client import Client


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("socket", default=None)
    parser.add_argument("--headless", action="store_true", default=False)
    return parser.parse_args()


def run_headless() -> int:
    return 1


def main() -> None:
    args = parse_args()
    if args.headless:
        code = run_headless()
    else:
        nvim = attach("socket", path=args.socket)
        code = run_client(nvim, client=Client(headless=False))
    exit(code)


main()
