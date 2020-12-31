from datetime import datetime, timezone
from os import linesep
from typing import Iterator

from pynvim.api.nvim import Nvim

from ..config.fmt import fmt_specs
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import pkg_specs
from ..consts import UPDATE_LOG, INSTALL_PROG
from ..workspace.terminal import toggle_floating
from subprocess import run


def _pip() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.pip
    for i_spec in linter_specs:
        yield from i_spec.install.pip
    for f_spec in fmt_specs:
        yield from f_spec.install.pip


def _npm() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.npm
    for i_spec in linter_specs:
        yield from i_spec.install.npm
    for f_spec in fmt_specs:
        yield from f_spec.install.npm


def _bash() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield l_spec.install.bash
    for i_spec in linter_specs:
        yield i_spec.install.bash
    for f_spec in fmt_specs:
        yield f_spec.install.bash


def _git() -> Iterator[str]:
    for spec in pkg_specs:
        yield spec.uri


def _install_args() -> Iterator[str]:
    yield INSTALL_PROG
    yield "--git"
    yield from _git()
    yield "--pip"
    yield from _pip()
    yield "--npm"
    yield from _npm()
    yield "--bash"
    yield from _bash()


def _install_with_ui(nvim: Nvim) -> None:
    toggle_floating(nvim, *_install_args())


def headless_install_and_quit() -> None:
    p = run(tuple(_install_args()))
    exit(p.returncode)


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
            _install_with_ui(nvim)
            UPDATE_LOG.write_text(now.isoformat())
