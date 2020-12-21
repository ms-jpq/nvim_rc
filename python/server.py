from python.nvim.lib import async_call
from typing import Any, Sequence, Tuple

from forechan import Chan, go
from pynvim import Nvim

from .registery import finalize


async def server(nvim: Nvim, ch: Chan[Tuple[str, Sequence[Any]]]) -> None:
    async def poll(ch: Chan) -> None:
        for event in ch:

            def cont() -> None:
                nvim.api.out_write(f"{event}\n")

            await async_call(nvim, cont)

    await go(poll)

    await finalize(nvim)
