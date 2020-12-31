from os import linesep

from pynvim import Nvim

from ._registery import ____
from .components.install import headless_install_and_quit, maybe_install
from .nvim.client import BasicClient
from .nvim.lib import async_call, write
from .registery import drain


class Client(BasicClient):
    def __init__(self, headless: bool) -> None:
        super().__init__()
        self._headless = headless

    async def wait(self, nvim: Nvim) -> int:
        def init() -> None:
            atomic, specs = drain(nvim)
            self._handlers.update(specs)
            atomic.commit(nvim)
            # write(nvim, *atomic, sep=linesep, error=True)
            maybe_install(nvim)

        await async_call(nvim, init)
        if self._headless:
            return await headless_install_and_quit()
        else:
            return await super().wait(nvim)
