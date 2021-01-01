#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

from python.consts import REQUIREMENTS, RT_DIR


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--install-runtime", action="store_true", default=False)
    parser.add_argument("--install-packages", action="store_true", default=False)
    parser.add_argument("--socket", default=None)
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
        cwd=(RT_DIR),
    )
    if proc.returncode:
        exit(proc.returncode)


from sys import path

path.append(RT_DIR)


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
