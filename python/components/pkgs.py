from dataclasses import asdict
from operator import attrgetter
from pathlib import Path, PurePath
from urllib.parse import urlparse

from pynvim.api.nvim import Nvim

from ..config.pkgs import pkg_specs
from ..consts import VIM_DIR
from ..nvim.atomic import Atomic
from ..nvim.keymap import Keymap
from ..nvim.rtp import rtp_packages


def p_name(uri: str) -> Path:
    url = urlparse(uri).path
    return VIM_DIR / PurePath(url).stem


def inst(nvim: Nvim) -> Atomic:
    plugins = (
        path for path in (p_name(spec.uri) for spec in pkg_specs) if path.exists()
    )

    atomic = rtp_packages(nvim, plugins=plugins)
    keymap = Keymap()

    for spec in pkg_specs:
        for key in spec.keys:
            for lhs, rhs in key.maps.items():
                attrgetter(key.modes)(keymap)(lhs, **asdict(key.opts)) << rhs

        for lhs, rhs in spec.vals.items():
            atomic.set_var(lhs, rhs)

        atomic.exec_lua(spec.lua, ())

    return atomic + keymap.drain(nvim.channel_id, buf=None)
