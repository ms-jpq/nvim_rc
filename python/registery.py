from asyncio import gather

from pynvim import Nvim

from .nvim.autocmd import AutoCMD
from .nvim.keymap import KeyMap
from .nvim.settings import Settings

autocmd = AutoCMD()

keymap = KeyMap()
settings = Settings()

async def finalize(nvim: Nvim) -> None:
    pass
    # await gather(fk(nvim), fa(nvim), fs(nvim))
