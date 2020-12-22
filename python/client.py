from asyncio.queues import Queue
from asyncio.tasks import create_task, gather
from typing import AsyncIterable, AsyncIterator, TypeVar

from pynvim import Nvim

from .nvim.client import RPC_MSG
from .nvim.lib import async_call, write
from .nvim.rpc import RPC_SPEC, rpc_agent
from .registery import drain

T = TypeVar("T")


async def to_iter(queue: Queue[T]) -> AsyncIterator[T]:
    while True:
        yield await queue.get()


async def client(nvim: Nvim, rpcs: AsyncIterable[RPC_MSG]) -> None:
    spec_q = Queue[RPC_SPEC]()
    instructons, specs = drain(nvim)

    await write(nvim, instructons)

    await rpc_agent(specs=to_iter(spec_q), rpcs=rpcs)
