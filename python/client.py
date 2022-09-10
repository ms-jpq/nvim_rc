from os import environ
from time import time
from types import NoneType

from pynvim_pp.types import RPClient
from std2.locale import si_prefixed_smol

from ._registery import ____
from .components.install import maybe_install
from .registery import drain

assert ____ or 1


async def init(client: RPClient) -> None:
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
