from typing import Sequence, Tuple

from pynvim import Nvim
from pynvim_pp.atomic import Atomic
from pynvim_pp.autocmd import AutoCMD
from pynvim_pp.keymap import Keymap
from pynvim_pp.rpc import RPC, RpcSpec
from pynvim_pp.settings import Settings

from .components.localization import load
from .components.rtp import inst
from .consts import PATH

NAMESPACE = "__init__"

LANG = load(code=None)
atomic = Atomic()
autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC(NAMESPACE)
settings = Settings()


def drain(nvim: Nvim) -> Tuple[Atomic, Sequence[RpcSpec]]:
    _atomic = Atomic()
    _atomic.call_function("setenv", ("PATH", PATH))
    _atomic.set_var("mapleader", " ")
    _atomic.set_var("maplocalleader", " ")

    a0 = inst(nvim)
    a1 = settings.drain()
    a2, s0 = rpc.drain(nvim.channel_id)
    a3 = keymap.drain(buf=None)
    a4 = autocmd.drain()
    return _atomic + a0 + a1 + a2 + a3 + a4 + atomic, s0
