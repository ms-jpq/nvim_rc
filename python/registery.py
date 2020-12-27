from typing import Sequence, Tuple

from pynvim import Nvim

from python.nvim.atomic import Atomic

from .nvim.autocmd import AutoCMD
from .nvim.keymap import Keymap
from .nvim.rpc import RPC, RpcSpec
from .nvim.settings import Settings

autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


def drain(nvim: Nvim) -> Tuple[Atomic, Sequence[RpcSpec]]:
    a0 = Atomic()
    a0.set_var("mapleader", " ")
    a0.set_var("maplocalleader", " ")

    a1, s1 = autocmd.drain(nvim.channel_id)
    a2 = keymap.drain(nvim.channel_id, None)
    s2 = rpc.drain()
    a3 = settings.drain(False)
    return a0 + a1 + a2 + a3, tuple((*s1, *s2))
