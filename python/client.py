from asyncio.queues import Queue
from asyncio.tasks import gather
from typing import AsyncIterable, AsyncIterator, TypeVar

from pynvim import Nvim

from ._registery import __
from .nvim.client import RpcMsg
from .nvim.lib import async_call, atomic, write
from .nvim.rpc import RpcSpec, rpc_agent
from .registery import drain

T = TypeVar("T")


async def to_iter(queue: Queue[T]) -> AsyncIterator[T]:
    while True:
        yield await queue.get()


async def client(nvim: Nvim, rpcs: AsyncIterable[RpcMsg]) -> None:
    spec_q = Queue[RpcSpec]()
    instructons, specs = drain(nvim)
    await gather(
        async_call(nvim, atomic, nvim, *instructons),
        *(spec_q.put(spec) for spec in specs)
    )

    await write(nvim, *instructons, sep="\n")
    await rpc_agent(nvim, specs=to_iter(spec_q), rpcs=rpcs)
