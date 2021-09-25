from dataclasses import asdict
from operator import attrgetter
from pathlib import Path, PurePosixPath
from textwrap import dedent, indent
from urllib.parse import urlsplit

from pynvim.api.nvim import Nvim
from pynvim_pp.atomic import Atomic
from pynvim_pp.keymap import Keymap

from ..config.pkgs import pkg_specs
from ..consts import VIM_DIR


def p_name(uri: str) -> Path:
    return VIM_DIR / PurePosixPath(urlsplit(uri).path).name


def inst(nvim: Nvim) -> Atomic:
    pkgs = {
        path: spec
        for path, spec in ((p_name(spec.git.uri), spec) for spec in pkg_specs)
        if path.exists()
    }

    atomic1 = Atomic()
    keymap = Keymap()

    for spec in pkgs.values():
        for key in spec.keys:
            for lhs, rhs in key.maps.items():
                attrgetter(key.modes)(keymap)(lhs, **asdict(key.opts)) << rhs

        for lhs, rhs in spec.vals.items():
            atomic1.set_var(lhs, rhs)

    atomic2 = Atomic()
    atomic2.command("packloadall")

    for spec in pkgs.values():
        if spec.lua:
            body = indent(spec.lua, " " * 2)
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
        if spec.viml:
            lua = f"""
            (function(viml)
            local _, err = pcall(vim.cmd, viml)
            if err then
              vim.api.nvim_err_writeln(err)
            end
            end)(...)
            """
            atomic2.exec_lua(dedent(lua), (spec.viml,))

    return atomic1 + keymap.drain(buf=None) + atomic2
