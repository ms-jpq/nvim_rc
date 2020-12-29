from pathlib import Path, PurePath
from urllib.parse import urlparse

from pynvim.api.nvim import Nvim

from ..config.pkgs import pkg_specs
from ..consts import VIM_DIR
from ..nvim.atomic import Atomic
from ..nvim.rtp import rtp_packages


def _p_name(uri: str) -> Path:
    url = urlparse(uri).path
    return VIM_DIR / PurePath(url).stem


def inst(nvim: Nvim) -> Atomic:
    plugins = (
        path for path in (_p_name(spec.uri) for spec in pkg_specs) if path.exists()
    )
    atomic = rtp_packages(nvim, plugins=plugins)

    return atomic
