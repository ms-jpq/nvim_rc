#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from sys import path

from python.consts import REQUIREMENTS, RT_DIR

RT_DIR.mkdir(parents=True, exist_ok=True)
path.append(str(RT_DIR))


def parse_args() -> Namespace:
    parser = ArgumentParser()

    run = parser.add_mutually_exclusive_group()
    run.add_argument("--socket", default=None)

    deps = parser.add_mutually_exclusive_group()
    deps.add_argument("--install-runtime", action="store_true", default=False)
    deps.add_argument("--install-packages", action="store_true", default=False)

    return parser.parse_args()


args = parse_args()


if args.install_runtime:

    from subprocess import run

    proc = run(
        (
            "pip3",
            "install",
            "--upgrade",
            "--target",
            str(RT_DIR),
            "--requirement",
            REQUIREMENTS,
        ),
        cwd=str(RT_DIR),
    )
    if proc.returncode:
        exit(proc.returncode)


if args.install_packages:

    from asyncio import run as arun

    from python.components.install import install

    code = arun(install())
    if code:
        exit(code)


if args.socket:
    from pynvim import attach
    from pynvim_pp.client import run_client

    from python.client import Client

    nvim = attach("socket", path=args.socket)
    code = run_client(nvim, client=Client())
    exit(code)
