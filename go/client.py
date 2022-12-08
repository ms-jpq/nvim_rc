from contextlib import AbstractAsyncContextManager
from os import environ
from pathlib import PurePath
from time import time
from types import NoneType
from typing import Any, Literal, Sequence, Union

from pynvim_pp.logging import suppress_and_log
from pynvim_pp.nvim import conn
from pynvim_pp.rpc import MsgType
from pynvim_pp.types import Method
from std2.contextlib import nullacontext
from std2.locale import si_prefixed_smol
from std2.platform import OS, os
from std2.sys import suicide

from ._registery import ____
from .components.install import maybe_install
from .registery import drain

assert ____ or 1


def _suicide(ppid: int) -> AbstractAsyncContextManager:
    if os is OS.windows:
        return nullacontext(None)
    else:
        return suicide(ppid)


async def _default(msg: MsgType, method: Method, params: Sequence[Any]) -> None:
    with suppress_and_log():
        assert False, (msg, method, params)


async def init(
    socket: Union[PurePath, tuple[Literal["localhost"], int]], ppid: int
) -> None:
    async with _suicide(ppid):
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
                print(f"{span}s", flush=True)