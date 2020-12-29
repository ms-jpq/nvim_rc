#!/usr/bin/env python3

from asyncio.tasks import gather
from sys import path
from typing import AsyncIterator, Awaitable, Iterable, Iterator

from python.consts import RT_DIR

path.append(str(RT_DIR))

from argparse import ArgumentParser, Namespace
from asyncio import run, as_completed

from std2.asyncio.subprocess import ProcReturn, call

from python.components.pkgs import p_name
from python.consts import NPM_DIR, PIP_DIR, VIM_DIR

from asyncio.queues import Queue


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--npm", nargs="*", default=())
    parser.add_argument("--pip", nargs="*", default=())
    parser.add_argument("--git", nargs="*", default=())
    parser.add_argument("--bash", nargs="*", default=())
    return parser.parse_args()


async def pip(queue: Queue[ProcReturn], pkgs: Iterable[str]) -> None:
    p = await call(
        "pip3", "install", "--upgrade", "--target", str(PIP_DIR), "--", *pkgs
    )
    await queue.put(p)


async def npm(queue: Queue[ProcReturn], pkgs: Iterable[str]) -> None:
    p1 = await call("npm", "init", "--yes", cwd=str(NPM_DIR))
    await queue.put(p1)
    p2 = await call("npm", "install", "--upgrade", "--", *pkgs, cwd=str(NPM_DIR))
    await queue.put(p2)


async def git(queue: Queue[ProcReturn], pkgs: Iterable[str]) -> None:
    def it() -> Iterator[Awaitable[ProcReturn]]:
        for pkg in pkgs:

            async def cont() -> None:
                location = VIM_DIR / p_name(pkg)
                if location.is_dir():
                    p = await call("git", "pull", cwd=str(location))
                else:
                    p = await call("git", "clone", "--depth=1", pkg, str(location))
                await queue.put(p)

            yield cont()

    await gather(*it())


async def bash(queue: Queue[ProcReturn], pkgs: Iterable[str]) -> None:
    def it() -> Iterator[Awaitable[ProcReturn]]:
        for pkg in pkgs:

            async def cont() -> None:
                p = await call("bash", stdin=pkg.encode())
                await queue.put(p)

            yield cont()

    await gather(*it())


async def main() -> None:
    args = parse_args()
    queue = Queue[ProcReturn]()


run(main())
