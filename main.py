#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from typing import Any, Sequence

from pynvim import attach
from asyncio import run


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("socket_address")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()


run(main())