from pynvim import Nvim

from .nvim.autocmd import AutoCMD
from .nvim.keymap import Keymap
from .nvim.rpc import RPC
from .nvim.settings import Settings

autocmd = AutoCMD()
keymap = Keymap()
rpc = RPC()
settings = Settings()


async def finalize(nvim: Nvim) -> None:
    pass
    # await gather(fk(nvim), fa(nvim), fs(nvim))
