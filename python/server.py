from typing import Any, Sequence, Tuple

from forechan import Chan
from pynvim import Nvim

from python.nvim.lib import async_call

from .nvim.go import go
from .registery import finalize

RPC_CH = Chan[Tuple[str, Sequence[Any]]]


async def server(nvim: Nvim, notif_ch: RPC_CH) -> None:
    async def poll() -> None:
        async for event in notif_ch:

            def cont() -> None:
                nvim.api.out_write(f"{event}\n")

            await async_call(nvim, cont)

    await go(poll())

    await finalize(nvim)
