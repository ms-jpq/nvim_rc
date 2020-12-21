from asyncio import gather

from pynvim import Nvim

from .nvim.autocmd import finalize as fa
from .nvim.keymap import finalize as fk
from .nvim.settings import finalize as fs
from .workspace import wm


async def finalize(nvim: Nvim) -> None:
    await gather(fk(nvim), fa(nvim), fs(nvim))
