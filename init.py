#!/usr/bin/env python3

from os import environ, pathsep
from pathlib import Path

REQUIREMENTS = str(Path(__file__).resolve().parent / "vars" / "requirements")
PYTHONPATH = pathsep.join(
    path for path in environ["PYTHONPATH"].split(pathsep) if path != REQUIREMENTS
)
if PYTHONPATH:
    environ["PYTHONPATH"] = PYTHONPATH
else:
    environ.pop("PYTHONPATH")


from pynvim import attach

from python.client import client
from python.nvim.client import run_client


def main() -> None:
    nvim = attach("stdio")
    run_client(nvim, client=client)


main()
