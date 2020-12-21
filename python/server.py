from pynvim import Nvim

from .registery import finalize


async def server(nvim: Nvim) -> None:
    await finalize(nvim)
