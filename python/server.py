from queue import SimpleQueue
from typing import Any, Sequence, Tuple, TypeVar

from forechan import Chan, chan
from pynvim import Nvim
from std2.asyncio import run_in_executor
from python.nvim.lib import async_call

from .nvim.go import go
from .registery import finalize

RPC_MSG = Tuple[str, Sequence[Any]]
RPC_Q = SimpleQueue[RPC_MSG]
RPC_CH = Chan[RPC_MSG]


T = TypeVar("T")


async def transq(simple: SimpleQueue[T]) -> Chan[T]:
    out: Chan[T] = chan()

    async def cont() -> None:
        async with out:
            while True:
                msg = await run_in_executor(simple.get)
                await out.send(msg)

    await go(cont())
    return out


async def server(nvim: Nvim, notif_q: RPC_Q, req_q: RPC_Q) -> None:
    async def poll() -> None:
        async for event in await transq(notif_q):

            def cont() -> None:
                nvim.api.out_write(f"{event}\n")

            await async_call(nvim, cont)

    await go(poll())
    await finalize(nvim)
