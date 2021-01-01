from asyncio.tasks import as_completed
from datetime import datetime, timezone
from os import linesep
from sys import stderr
from typing import Awaitable, Iterator, Sequence, Tuple

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


SortOfMonoid = Sequence[Tuple[str, ProcReturn]]


def _git() -> Iterator[Awaitable[SortOfMonoid]]:
    for pkg in _git_specs():

        async def cont(pkg: str) -> SortOfMonoid:
            location = VIM_DIR / p_name(pkg)
            if location.is_dir():
                p = await call("git", "pull", "--recurse-submodules", cwd=str(location))
                return ((pkg, p),)
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
                return ((pkg, p),)

        yield cont(pkg)


def _pip() -> Iterator[Awaitable[SortOfMonoid]]:
    async def cont() -> SortOfMonoid:
        p = await call(
            "pip3",
            "install",
            "--upgrade",
            "--target",
            str(PIP_DIR),
            "--",
            *_pip_specs(),
            cwd=str(PIP_DIR),
        )
        return (("", p),)

    yield cont()


def _npm() -> Iterator[Awaitable[SortOfMonoid]]:
    async def cont() -> SortOfMonoid:
        p1 = await call("npm", "init", "--yes", cwd=str(NPM_DIR))
        if p1.code:
            return (("", p1),)
        else:
            p2 = await call(
                "npm", "install", "--upgrade", "--", *_npm_specs(), cwd=str(NPM_DIR)
            )
            return ("", p1), ("", p2)

    yield cont()


def _bash() -> Iterator[Awaitable[SortOfMonoid]]:
    for pkg in _bash_specs():

        async def cont(pkg: str) -> SortOfMonoid:
            stdin = f"set -x{linesep}{pkg}".encode()
            p = await call("bash", stdin=stdin, cwd=str(TOP_LEVEL))
            return ((pkg, p),)

        if pkg:
            yield cont(pkg)


async def install() -> None:
    tasks = as_completed((*_git(), *_pip(), *_npm(), *_bash()))
    for fut in tasks:
        for debug, proc in await fut:
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
