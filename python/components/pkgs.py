from dataclasses import asdict
from operator import attrgetter
from pathlib import Path
from urllib.parse import urlparse

from pynvim.api.nvim import Nvim

from ..config.pkgs import pkg_specs
from ..consts import VIM_DIR
from ..nvim.atomic import Atomic
from ..nvim.keymap import Keymap
from ..nvim.rtp import rtp_packages


def p_name(uri: str) -> Path:
    return VIM_DIR / Path(urlparse(uri).path).name


def inst(nvim: Nvim) -> Atomic:
    pkgs = {
        path: spec
        for path, spec in ((p_name(spec.uri), spec) for spec in pkg_specs)
        if path.exists()
    }

    atomic = rtp_packages(nvim, plugins=pkgs)
    keymap = Keymap()

    for spec in pkgs.values():
        for key in spec.keys:
            for lhs, rhs in key.maps.items():
                attrgetter(key.modes)(keymap)(lhs, **asdict(key.opts)) << rhs

        for lhs, rhs in spec.vals.items():
            atomic.set_var(lhs, rhs)
        if spec.lua:
            atomic.exec_lua(spec.lua, ())
        if spec.viml:
            atomic.exec(spec.viml, False)

    return atomic + keymap.drain(nvim.channel_id, buf=None)
