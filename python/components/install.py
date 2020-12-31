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


def install(nvim: Nvim) -> None:
    toggle_floating(
        nvim,
        INSTALL_PROG,
        "--git",
        *_git(),
        "--pip",
        *_pip(),
        "--npm",
        *_npm(),
        "--bash",
        *_bash(),
    )


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
            install(nvim)
            UPDATE_LOG.write_text(now.isoformat())
