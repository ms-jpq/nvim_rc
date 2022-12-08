from os import environ
from pathlib import PurePath
from time import time
from types import NoneType
from typing import Any, Sequence

from pynvim_pp.logging import suppress_and_log
from pynvim_pp.nvim import conn
from pynvim_pp.rpc import MsgType
from pynvim_pp.types import Method
from std2.locale import si_prefixed_smol

from ._registery import ____
from .components.install import maybe_install
from .registery import drain

assert ____ or 1


async def _default(msg: MsgType, method: Method, params: Sequence[Any]) -> None:
    with suppress_and_log():
        assert False, (msg, method, params)


async def init(socket: PurePath) -> None:
    async with conn(socket, default=_default) as client:
        print("connected", flush=True)
        atomic, handlers = drain()
        for handler in handlers.values():
            client.register(handler)
        await atomic.commit(NoneType)
        print("registered", flush=True)

        await maybe_install()

        if "NVIM_DEBUG" in environ:
            t1 = int(environ["_VIM_START_TIME"])
            t2 = time()
            span = si_prefixed_smol(t2 - t1)
            print(f"{span}s", flush=True)
