from asyncio.tasks import gather
from queue import SimpleQueue
from typing import TypeVar

from forechan import Chan, chan
from pynvim import Nvim
from std2.asyncio import run_in_executor

from python.nvim.lib import async_call

from .lib.go import go
from .nvim.client import NOTIF_MSG, NOTIF_Q, RPC_MSG, RPC_Q
from .registery import finalize

NOTIF_CH = Chan[NOTIF_MSG]

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


async def client(nvim: Nvim, notif_q: NOTIF_Q, rpc_q: RPC_Q) -> None:
    async def poll_notif() -> None:
        async for event, args in await transq(notif_q):

            def cont() -> None:
                nvim.api.out_write(f"{event} - {args}\n")

            await async_call(nvim, cont)

    async def poll_rpc() -> None:
        async for fut, (event, args) in await transq(rpc_q):

            def cont() -> None:
                nvim.api.out_write(f"{event}\n")

            await async_call(nvim, cont)
            fut.set_result(None)

    await gather(go(poll_notif()), go(poll_rpc()))
    await finalize(nvim)
