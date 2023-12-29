from collections.abc import Iterable
from dataclasses import asdict
from operator import attrgetter
from pathlib import Path
from textwrap import dedent, indent

from pynvim_pp.atomic import Atomic
from pynvim_pp.keymap import Keymap
from std2.urllib import uri_path

from ..config.pkgs import PkgAttrs, pkg_specs
from ..consts import VIM_DIR


def p_name(opt: bool, uri: str) -> Path:
    return VIM_DIR / {True: "opt", False: "start"}[opt] / uri_path(uri).name


def _inst(packages: Iterable[PkgAttrs], cmds: Iterable[str]) -> Atomic:
    pkgs = {
        path: spec
        for path, spec in (
            (p_name(spec.opt, uri=spec.git.uri), spec) for spec in packages
        )
        if path.exists()
    }

    atomic1 = Atomic()
    keymap = Keymap()

    for spec in pkgs.values():
        for key in spec.keys:
            for lhs, rhs in key.maps.items():
                _ = attrgetter(key.modes)(keymap)(lhs, **asdict(key.opts)) << rhs

        for lhs, rhs in spec.vals.items():
            atomic1.set_var(lhs, rhs)

    atomic2 = Atomic()
    for cmd in cmds:
        atomic2.command(cmd)

    for spec in pkgs.values():
        if code := spec.lua:
            body = indent(code, " " * 2)
            lua = f"""
            (function()
            local _, err = pcall(function()
            {body}
            end)
            if err then
              vim.api.nvim_err_writeln(err)
            end
            end)()
            """
            atomic2.exec_lua(dedent(lua), ())

        if code := spec.viml:
            lua = """
            (function(viml)
            local _, err = pcall(vim.cmd, viml)
            if err then
              vim.api.nvim_err_writeln(err)
            end
            end)(...)
            """
            atomic2.exec_lua(dedent(lua), (code,))

    return atomic1 + keymap.drain(buf=None) + atomic2


def inst() -> Atomic:
    pkgs = (spec for spec in pkg_specs if not spec.opt)
    return _inst(pkgs, cmds=("packloadall",))


def inst_later() -> Atomic:
    pkgs = tuple(spec for spec in pkg_specs if spec.opt)
    cmds = (f"packadd {uri_path(pkg.git.uri).name}" for pkg in pkgs)
    return _inst(pkgs, cmds=cmds)
