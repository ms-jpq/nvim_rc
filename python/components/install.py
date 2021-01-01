from asyncio import gather
from asyncio.queues import Queue
from asyncio.tasks import create_task
from datetime import datetime, timezone
from os import linesep
from sys import stderr
from typing import Awaitable, Iterator, Tuple

from pynvim.api.nvim import Nvim
from std2.asyncio.subprocess import ProcReturn, call

from ..config.fmt import fmt_specs
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import pkg_specs
from ..consts import INSTALL_SCRIPT, NPM_DIR, PIP_DIR, TOP_LEVEL, UPDATE_LOG, VIM_DIR
from ..workspace.terminal import toggle_floating
from .rtp import p_name


def _git_specs() -> Iterator[str]:
    for spec in pkg_specs:
        yield spec.uri


def _pip_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.pip
    for i_spec in linter_specs:
        yield from i_spec.install.pip
    for f_spec in fmt_specs:
        yield from f_spec.install.pip


def _npm_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.npm
    for i_spec in linter_specs:
        yield from i_spec.install.npm
    for f_spec in fmt_specs:
        yield from f_spec.install.npm


def _bash_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield l_spec.install.bash
    for i_spec in linter_specs:
        yield i_spec.install.bash
    for f_spec in fmt_specs:
        yield f_spec.install.bash


async def _git(queue: Queue[Tuple[str, ProcReturn]]) -> None:
    def it() -> Iterator[Awaitable[None]]:
        for pkg in _git_specs():

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


async def _pip(queue: Queue[Tuple[str, ProcReturn]]) -> None:
    specs = tuple(_pip_specs())
    if specs:
        p = await call(
            "pip3",
            "install",
            "--upgrade",
            "--target",
            str(PIP_DIR),
            "--",
            *specs,
            cwd=str(PIP_DIR),
        )
        await queue.put(("", p))


async def _npm(queue: Queue[Tuple[str, ProcReturn]]) -> None:
    p1 = await call("npm", "init", "--yes", cwd=str(NPM_DIR))
    await queue.put(("", p1))
    if p1.code == 0:
        p2 = await call(
            "npm", "install", "--upgrade", "--", *_npm_specs(), cwd=str(NPM_DIR)
        )
        await queue.put(("", p2))


async def _bash(queue: Queue[Tuple[str, ProcReturn]]) -> None:
    def it() -> Iterator[Awaitable[None]]:
        for pkg in _bash_specs():

            async def cont(pkg: str) -> None:
                stdin = f"set -x{linesep}{pkg}".encode()
                p = await call("bash", stdin=stdin, cwd=str(TOP_LEVEL))
                await queue.put((pkg, p))

            if pkg:
                yield cont(pkg)

    await gather(*it())


async def _stdout(queue: Queue[Tuple[str, ProcReturn]]) -> None:
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


async def install() -> None:
    queue = Queue[Tuple[str, ProcReturn]]()
    create_task(_stdout(queue))
    await gather(
        _git(queue),
        _pip(queue),
        _npm(queue),
        _bash(queue),
    )
    await queue.join()


def maybe_install(nvim: Nvim) -> None:
    before = (
        datetime.fromisoformat(UPDATE_LOG.read_text())
        if UPDATE_LOG.exists()
        else datetime(year=1949, month=9, day=21, tzinfo=timezone.utc)
    )
    now = datetime.now(tz=timezone.utc)
    diff = now - before
    if diff.days > 7:
        ans = nvim.funcs.confirm("🤖「ゴゴゴゴ」？", f"&Yes{linesep}&No", 2)
        if ans == 1:
            toggle_floating(nvim, INSTALL_SCRIPT, "--install-packages")
            UPDATE_LOG.write_text(now.isoformat())
