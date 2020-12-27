from locale import strxfrm
from typing import Iterable

from pynvim import Nvim
from std2.pathlib import walk
from yaml import load

from ..consts import CONF_PACKAGES, VIM_DIR
from ..nvim.atomic import Atomic
from pathlib import PurePath, Path
from urllib.parse import urlparse


def _p_name(uri: str) -> Path:
    url = urlparse(uri).path
    return VIM_DIR / PurePath(url).stem


def packages(nvim: Nvim) -> Atomic:
    conf = load(CONF_PACKAGES.open())
    plugins = tuple(_p_name(c["uri"]) for c in conf)

    atomic = Atomic()
    head, *tail = nvim.list_runtime_paths()
    rtp = ",".join((head, *(map(str, plugins)), *tail))
    atomic.command(f"set runtimepath={rtp}")

    for path in plugins:
        plug = path / "plugin"
        if plug.exists():
            for vim_script in walk(plug):
                if vim_script.suffix == ".vim":
                    atomic.command("source", str(vim_script))

    return atomic
