#!/usr/bin/env python3

from python.client import client
from python.nvim.client import run_client

from pynvim import attach


def main() -> None:
    nvim = attach("stdio")
    run_client(nvim, client=client)


main()
