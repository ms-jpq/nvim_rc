from asyncio.tasks import create_task, gather
from typing import AsyncIterable

from pynvim import Nvim

from .nvim.client import RPC_MSG
from .nvim.lib import async_call
from .registery import finalize
from .nvim.rpc import rpc_agent


async def client(nvim: Nvim, rpcs: AsyncIterable[RPC_MSG]) -> None:

    await finalize(nvim)

    # await rpc_agent