#!/usr/bin/env python3

from sys import path

from python.consts import RT_DIR

path.append(RT_DIR)


from pynvim import attach

from python.client import Client
from python.nvim.client import run_client


def main() -> None:
    nvim = attach("stdio")
    run_client(nvim, client=Client())


main()
