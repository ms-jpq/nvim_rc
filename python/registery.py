from os import environ, pathsep
from typing import Sequence, Tuple

from pynvim import Nvim

from .consts import BINS
from .nvim.atomic import Atomic
from .nvim.autocmd import AutoCMD
from .nvim.keymap import Keymap
from .nvim.rpc import RPC, RpcSpec
from .nvim.rtp import rtp_packages
from .nvim.settings import Settings
from .packages.vim import plugins

for bin in BINS:
    bin.mkdir(parents=True, exist_ok=True)
environ["PATH"] = pathsep.join((*(map(str, BINS)), *environ["PATH"].split(pathsep)))


atomic = Atomic()
autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


_atomic = Atomic()
_atomic.call_function("setenv", ("PATH", environ["PATH"]))
_atomic.set_var("mapleader", " ")
_atomic.set_var("maplocalleader", " ")


def drain(nvim: Nvim) -> Tuple[Atomic, Sequence[RpcSpec]]:
    a0 = rtp_packages(nvim, plugins=plugins)
    a1, s1 = autocmd.drain(nvim.channel_id)
    a2 = keymap.drain(nvim.channel_id, None)
    s2 = rpc.drain()
    a3 = settings.drain(False)
    return _atomic + a0 + a1 + a2 + a3 + atomic, tuple((*s1, *s2))
