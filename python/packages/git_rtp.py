from locale import strxfrm
from typing import Iterable

from pynvim import Nvim
from std2.pathlib import walk
from yaml import load

from ..consts import CONF_PACKAGES, VIM_DIR
from ..nvim.atomic import Atomic
from pathlib import PurePath
from urllib.parse import urlparse


def _p_name(uri: str) -> str:
    url = urlparse(uri).path
    return PurePath(url).name


def packages(nvim: Nvim) -> Atomic:
    conf = load(CONF_PACKAGES.open())
    plugins = tuple(_p_name(c["uri"]) for c in conf)

    atomic = Atomic()
    head, *tail = nvim.list_runtime_paths()
    rtp = ",".join((head, *tail))
    atomic.commit(f"set runtimepath={rtp}")

    for plug in plugins:
        path = VIM_DIR / plug

    return atomic
