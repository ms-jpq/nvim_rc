#!/usr/bin/env python3

from sys import path

from python.consts import RT_DIR

path.append(str(RT_DIR))

from argparse import ArgumentParser, Namespace
from asyncio import run
from asyncio.queues import Queue
from asyncio.tasks import create_task, gather
from sys import stderr
from typing import AsyncIterable, Awaitable, Iterator, Sequence

from std2.asyncio.queue import to_iter
from std2.asyncio.subprocess import ProcReturn, call

from python.components.pkgs import p_name
from python.consts import NPM_DIR, PIP_DIR, VIM_DIR


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--pip", nargs="*", default=())
    parser.add_argument("--npm", nargs="*", default=())
    parser.add_argument("--git", nargs="*", default=())
    parser.add_argument("--bash", nargs="*", default=())
    return parser.parse_args()


async def pip(queue: Queue[ProcReturn], pkgs: Sequence[str]) -> None:
    if pkgs:
        p = await call(
            "pip3", "install", "--upgrade", "--target", str(PIP_DIR), "--", *pkgs
        )
        await queue.put(p)


async def npm(queue: Queue[ProcReturn], pkgs: Sequence[str]) -> None:
    p1 = await call("npm", "init", "--yes", cwd=str(NPM_DIR))
    await queue.put(p1)
    if p1.code == 0 and pkgs:
        p2 = await call("npm", "install", "--upgrade", "--", *pkgs, cwd=str(NPM_DIR))
        await queue.put(p2)


async def git(queue: Queue[ProcReturn], pkgs: Sequence[str]) -> None:
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


async def bash(queue: Queue[ProcReturn], pkgs: Sequence[str]) -> None:
    def it() -> Iterator[Awaitable[ProcReturn]]:
        for pkg in pkgs:

            async def cont() -> None:
                p = await call("bash", stdin=pkg.encode())
                await queue.put(p)

            yield cont()

    await gather(*it())


async def stdout(ait: AsyncIterable[ProcReturn]) -> None:
    async for proc in ait:
        if proc.code == 0:
            print("Success |>", proc.prog, *proc.args)
            print(proc.out.decode())
        else:
            print(
                f"Failure - Exit Code {proc.code} |>",
                proc.prog,
                *proc.args,
                file=stderr,
            )
            print(proc.err, file=stderr)


async def main() -> None:
    args = parse_args()
    queue = Queue[ProcReturn]()
    tasks = gather(
        pip(queue, pkgs=args.pip),
        npm(queue, pkgs=args.npm),
        git(queue, pkgs=args.git),
        bash(queue, pkgs=args.bash),
    )
    create_task(stdout(to_iter(queue)))
    await tasks


run(main())
