from typing import Sequence, Tuple

from pynvim import Nvim

from python.nvim.atomic import Atomic

from .nvim.autocmd import AutoCMD
from .nvim.keymap import Keymap
from .nvim.rpc import RPC, RpcSpec
from .nvim.settings import Settings

atomic = Atomic()
autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


atomic.set_var("mapleader", " ")
atomic.set_var("maplocalleader", " ")


def drain(nvim: Nvim) -> Tuple[Atomic, Sequence[RpcSpec]]:

    a1, s1 = autocmd.drain(nvim.channel_id)
    a2 = keymap.drain(nvim.channel_id, None)
    s2 = rpc.drain()
    a3 = settings.drain(False)
    return atomic + a1 + a2 + a3, tuple((*s1, *s2))
