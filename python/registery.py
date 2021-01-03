from os import environ, pathsep
from typing import Sequence, Tuple

from pynvim import Nvim
from pynvim_pp.atomic import Atomic
from pynvim_pp.autocmd import AutoCMD
from pynvim_pp.keymap import Keymap
from pynvim_pp.rpc import RPC, RpcSpec
from pynvim_pp.settings import Settings

from .components.rtp import inst
from .consts import PATH_PREPEND, PIP_DIR

atomic = Atomic()
autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


def drain(nvim: Nvim) -> Tuple[Atomic, Sequence[RpcSpec]]:
    PATH = environ["PATH"] = pathsep.join((*PATH_PREPEND, environ["PATH"]))
    PYTHONPATH = environ["PYTHONPATH"] = (
        pathsep.join((str(PIP_DIR), environ["PYTHONPATH"]))
        if "PYTHONPATH" in environ
        else str(PIP_DIR)
    )

    _atomic = Atomic()
    _atomic.call_function("setenv", ("PATH", PATH))
    _atomic.call_function("setenv", ("PYTHONPATH", PYTHONPATH))
    _atomic.set_var("mapleader", " ")
    _atomic.set_var("maplocalleader", " ")

    a0 = inst(nvim)
    a1 = autocmd.drain()
    a2 = keymap.drain(buf=None)
    a3, s0 = rpc.drain(nvim.channel_id)
    a4 = settings.drain()
    return _atomic + a0 + a1 + a2 + a3 + a4 + atomic, s0
