from typing import Sequence, Tuple

from pynvim import Nvim

from .nvim.autocmd import AutoCMD
from .nvim.keymap import Keymap
from .nvim.lib import AtomicInstruction
from .nvim.rpc import RPC, RPC_SPEC
from .nvim.settings import Settings

autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


def drain(nvim: Nvim) -> Tuple[Sequence[AtomicInstruction], Sequence[RPC_SPEC]]:
    i1, s1 = autocmd.drain(nvim.channel_id)
    i2, s2 = keymap.drain(nvim.channel_id, None)
    s3 = rpc.drain()
    i4 = settings.drain(False)
    return tuple((*i1, *i2, *i4)), tuple((*s1, *s2, *s3))
