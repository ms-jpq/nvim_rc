#!/usr/bin/env python3

from sys import path

from python.consts import RT_DIR

path.append(RT_DIR)

from argparse import ArgumentParser, Namespace
from asyncio import run
from asyncio.queues import Queue
from asyncio.tasks import create_task, gather
from os import linesep
from sys import stderr
from typing import Awaitable, Iterator, Sequence, Tuple

from std2.asyncio.subprocess import ProcReturn, call

from python.components.pkgs import p_name
from python.consts import NPM_DIR, PIP_DIR, TOP_LEVEL, VIM_DIR


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--git", nargs="*", default=())
    parser.add_argument("--pip", nargs="*", default=())
    parser.add_argument("--npm", nargs="*", default=())
    parser.add_argument("--bash", nargs="*", default=())
    return parser.parse_args()


async def pip(queue: Queue[Tuple[str, ProcReturn]], pkgs: Sequence[str]) -> None:
    if pkgs:
        p = await call(
            "pip3",
            "install",
            "--upgrade",
            "--target",
            str(PIP_DIR),
            "--",
            *pkgs,
            cwd=str(PIP_DIR),
        )
        await queue.put(("", p))


async def npm(queue: Queue[Tuple[str, ProcReturn]], pkgs: Sequence[str]) -> None:
    if pkgs:
        p1 = await call("npm", "init", "--yes", cwd=str(NPM_DIR))
        await queue.put(("", p1))
        if p1.code == 0:
            p2 = await call(
                "npm", "install", "--upgrade", "--", *pkgs, cwd=str(NPM_DIR)
            )
            await queue.put(("", p2))


async def git(queue: Queue[Tuple[str, ProcReturn]], pkgs: Sequence[str]) -> None:
    def it() -> Iterator[Awaitable[None]]:
        for pkg in pkgs:

            async def cont(pkg: str) -> None:
                location = VIM_DIR / p_name(pkg)
                if location.is_dir():
                    p = await call(
                        "git", "pull", "--recurse-submodules", cwd=str(location)
                    )
                    await queue.put((pkg, p))
                else:
                    p = await call(
                        "git",
                        "clone",
                        "--depth=1",
                        "--recurse-submodules",
                        "--shallow-submodules",
                        pkg,
                        str(location),
                    )
                    await queue.put((pkg, p))

            yield cont(pkg)

    await gather(*it())


async def bash(queue: Queue[Tuple[str, ProcReturn]], pkgs: Sequence[str]) -> None:
    def it() -> Iterator[Awaitable[None]]:
        for pkg in pkgs:

            async def cont(pkg: str) -> None:
                stdin = f"set -x{linesep}{pkg}".encode()
                p = await call("bash", stdin=stdin, cwd=str(TOP_LEVEL))
                await queue.put((pkg, p))

            if pkg:
                yield cont(pkg)

    await gather(*it())


async def stdout(queue: Queue[Tuple[str, ProcReturn]]) -> None:
    while True:
        debug, proc = await queue.get()
        if proc.code == 0:
            print(debug)
            print("✅ 👉", proc.prog, *proc.args)
            print(proc.out.decode())
        else:
            print(debug, file=stderr)
            print(
                f"⛔️ - {proc.code} 👉",
                proc.prog,
                *proc.args,
                file=stderr,
            )
            print(proc.err, file=stderr)
        queue.task_done()


async def main() -> None:
    args = parse_args()
    for path in (NPM_DIR, PIP_DIR, VIM_DIR):
        path.mkdir(parents=True, exist_ok=True)

    queue = Queue[Tuple[str, ProcReturn]]()
    tasks = gather(
        pip(queue, pkgs=args.pip),
        npm(queue, pkgs=args.npm),
        git(queue, pkgs=args.git),
        bash(queue, pkgs=args.bash),
    )
    create_task(stdout(queue))
    await tasks
    await queue.join()


run(main())
