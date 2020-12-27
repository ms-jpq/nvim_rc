from typing import Iterator, Sequence, Tuple

from pynvim import Nvim

from .nvim.autocmd import AutoCMD
from .nvim.keymap import Keymap
from .nvim.lib import AtomicInstruction
from .nvim.rpc import RPC, RpcSpec
from .nvim.settings import Settings

autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


def _map_leader() -> Iterator[AtomicInstruction]:
    yield "set_var", ("mapleader", " ")
    yield "set_var", ("maplocalleader", " ")


def drain(nvim: Nvim) -> Tuple[Sequence[AtomicInstruction], Sequence[RpcSpec]]:
    i1, s1 = autocmd.drain(nvim.channel_id)
    i2 = keymap.drain(nvim.channel_id, None)
    s2 = rpc.drain()
    i4 = settings.drain(False)
    return tuple((*_map_leader(), *i1, *i2, *i4)), tuple((*s1, *s2))
