from os import linesep

from pynvim import Nvim

from ._registery import ____
from .components.install import maybe_install
from .nvim.client import BasicClient
from .nvim.lib import async_call, write
from .registery import drain


class Client(BasicClient):
    async def wait(self, nvim: Nvim) -> None:
        def init() -> None:
            atomic, specs = drain(nvim)
            self._handlers.update(specs)
            atomic.commit(nvim)
            # write(nvim, *atomic, sep=linesep, error=True)
            maybe_install(nvim)

        await async_call(nvim, init)
        await super().wait(nvim)
