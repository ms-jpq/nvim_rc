from os import environ
from time import time

from pynvim import Nvim
from pynvim_pp.client import BasicClient
from pynvim_pp.lib import threadsafe_call
from std2.locale import si_prefixed_smol

from ._registery import ____
from .components.install import maybe_install
from .registery import drain


class Client(BasicClient):
    def wait(self, nvim: Nvim) -> int:
        def init() -> None:
            atomic, specs = drain(nvim)
            self._handlers.update(specs)
            atomic.commit(nvim)
            maybe_install(nvim)

        threadsafe_call(nvim, init)
        if "NVIM_DEBUG" in environ:
            t1 = int(environ["_VIM_START_TIME"])
            t2 = time()
            span = si_prefixed_smol(t2 - t1)
            print(f"{span}s", flush=True)
        return super().wait(nvim)
