from datetime import datetime, timezone
from os import linesep

from pynvim.api.nvim import Nvim

from ..config.fmt import fmt_specs
from ..config.install import InstallSpec
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import pkg_specs
from ..consts import CONFIG_LOG, INSTALL_PROG
from ..workspace.terminal import toggle_floating


def install(nvim: Nvim) -> None:
    toggle_floating(nvim, INSTALL_PROG)


def maybe_install(nvim: Nvim) -> None:
    before = (
        datetime.fromisoformat(CONFIG_LOG.read_text())
        if CONFIG_LOG.exists()
        else datetime(year=1949, month=9, day=21, tzinfo=timezone.utc)
    )
    now = datetime.now(tz=timezone.utc)
    diff = now - before
    if diff.days > 7:
        ans = nvim.funcs.confirm("🤖「ゴゴゴゴ」？", f"&Yes{linesep}&No", 2)
        if ans == 1:
            install(nvim)
            CONFIG_LOG.write_text(now.isoformat())
