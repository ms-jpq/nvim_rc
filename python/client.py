from asyncio.queues import Queue
from asyncio.tasks import gather
from typing import AsyncIterable, AsyncIterator, TypeVar

from pynvim import Nvim

from ._registery import __
from .nvim.client import RpcMsg
from .nvim.lib import async_call, write
from .nvim.rpc import RpcSpec, rpc_agent
from .registery import drain

T = TypeVar("T")


async def _to_iter(queue: Queue[T]) -> AsyncIterator[T]:
    while True:
        yield await queue.get()


async def client(nvim: Nvim, rpcs: AsyncIterable[RpcMsg]) -> None:
    spec_q = Queue[RpcSpec]()
    atomic, specs = drain(nvim)
    await gather(
        async_call(
            nvim,
            atomic.execute,
            nvim,
        ),
        *(spec_q.put(spec) for spec in specs)
    )

    await write(nvim, *atomic, sep="\n")
    await rpc_agent(nvim, specs=_to_iter(spec_q), rpcs=rpcs)
