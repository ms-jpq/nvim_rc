from os import linesep

from pynvim import Nvim
from pynvim_pp.client import BasicClient
from pynvim_pp.lib import threadsafe_call, write

from ._registery import ____
from .components.install import maybe_install
from .registery import drain



class Client(BasicClient):
    def wait(self, nvim: Nvim) -> int:
        def init() -> None:
            atomic, specs = drain(nvim)
            self._handlers.update(specs)
            atomic.commit(nvim)
            # write(nvim, *atomic, sep=linesep, error=True)
            maybe_install(nvim)

        threadsafe_call(nvim, init)
        return super().wait(nvim)
