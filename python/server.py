from queue import SimpleQueue
from typing import Any, Sequence, Tuple

from forechan import Chan, chan
from pynvim import Nvim

from python.nvim.lib import async_call

from .nvim.go import go
from .registery import finalize

RPC_Q = SimpleQueue[Tuple[str, Sequence[Any]]]


async def server(nvim: Nvim, notif_q: RPC_Q, req_q: RPC_Q) -> None:
    async def poll() -> None:
        async for event in chan():

            def cont() -> None:
                nvim.api.out_write(f"{event}\n")

            await async_call(nvim, cont)

    await go(poll())

    await finalize(nvim)
