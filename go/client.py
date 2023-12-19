from contextlib import AbstractAsyncContextManager
from os import environ
from time import time
from typing import Any, Sequence

from pynvim_pp.logging import log, suppress_and_log
from pynvim_pp.nvim import conn
from pynvim_pp.rpc_types import Method, MsgType, ServerAddr
from pynvim_pp.types import NoneType
from std2.contextlib import nullacontext
from std2.locale import si_prefixed_smol
from std2.platform import OS, os
from std2.sys import autodie

from ._registry import ____
from .components.install import maybe_install
from .registry import drain

assert ____ or 1


def _autodie(ppid: int) -> AbstractAsyncContextManager[None]:
    if os is OS.windows:
        return nullacontext(None)
    else:
        return autodie(ppid)


async def _default(msg: MsgType, method: Method, params: Sequence[Any]) -> None:
    with suppress_and_log():
        assert False, (msg, method, params)


async def init(socket: ServerAddr, ppid: int) -> None:
    async with _autodie(ppid):
        async with conn(socket, default=_default) as client:
            atomic, handlers = drain()
            for handler in handlers.values():
                client.register(handler)
            await atomic.commit(NoneType)

            await maybe_install()

            if "NVIM_DEBUG" in environ:
                t1 = int(environ["_VIM_START_TIME"])
                t2 = time()
                span = si_prefixed_smol(t2 - t1)
                log.warn("%s", f"{span}s")
