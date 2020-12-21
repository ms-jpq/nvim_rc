from pynvim import Nvim

from .nvim.keymap import finalize as kf
from .workspace import wm


async def finalize(nvim: Nvim) -> None:
    await kf(nvim)
