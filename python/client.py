from pynvim import Nvim

from ._registery import ____
from .nvim.client import BasicClient
from .nvim.lib import async_call
from .registery import drain


class Client(BasicClient):
    async def wait(self, nvim: Nvim) -> None:
        def init() -> None:
            atomic, specs = drain(nvim)
            self._handlers.update(specs)
            atomic.commit(nvim)

        await async_call(nvim, init)
        await super().wait(nvim)
