from asyncio import gather, wrap_future
from concurrent.futures import Future
from operator import attrgetter
from os import environ
from time import time
from typing import Any, Sequence

from pynvim_pp.logging import log, suppress_and_log
from pynvim_pp.nvim import Nvim, conn
from pynvim_pp.rpc_types import Method, MsgType, ServerAddr
from pynvim_pp.types import NoneType
from std2.locale import si_prefixed_smol

from ._registry import ____
from .components.install import maybe_install
from .components.rtp import inst_later
from .registry import NAMESPACE, autocmd, drain, rpc
from .workspace.session import restore

assert ____ or 1


async def _default(msg: MsgType, method: Method, params: Sequence[Any]) -> None:
    with suppress_and_log():
        assert False, (msg, method, params)


@rpc()
async def _once() -> None:
    atomic = inst_later()
    await atomic.commit(NoneType)


_ = (
    autocmd("CursorHold", modifiers=("*", "++once"))
    << f"lua {NAMESPACE}.{_once.method}()"
)


async def init(socket: ServerAddr) -> None:
    die: Future = Future()

    async def cont() -> None:
        async with conn(die, socket=socket, default=_default) as client:
            atomic, handlers = drain()
            for handler in handlers.values():
                client.register(handler)
            await atomic.commit(NoneType)

            await maybe_install()
            await attrgetter(restore.method)(attrgetter(NAMESPACE)(Nvim.lua))(NoneType)

            if "NVIM_DEBUG" in environ:
                t1 = int(environ["_VIM_START_TIME"])
                t2 = time()
                span = si_prefixed_smol(t2 - t1)
                log.warn("%s", f"{span}s")

    await gather(wrap_future(die), cont())
