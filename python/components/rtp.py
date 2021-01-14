from dataclasses import asdict
from operator import attrgetter
from pathlib import Path
from urllib.parse import urlparse

from pynvim.api.nvim import Nvim
from pynvim_pp.atomic import Atomic
from pynvim_pp.keymap import Keymap
from pynvim_pp.rtp import rtp_packages

from ..config.pkgs import pkg_specs
from ..consts import VIM_DIR


def p_name(uri: str) -> Path:
    return VIM_DIR / Path(urlparse(uri).path).name


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

    atomic2 = rtp_packages(nvim, plugins=pkgs)

    for spec in pkgs.values():
        if spec.lua:
            atomic2.exec_lua(spec.lua, ())
        if spec.viml:
            atomic2.exec(spec.viml, False)

    return atomic1 + keymap.drain(buf=None) + atomic2
