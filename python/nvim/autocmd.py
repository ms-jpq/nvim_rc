from pynvim import Nvim
from typing import MutableSequence


class AutoCMD:
    def __init__(self) -> None:
        self._finalized = False
        self._autocmds: MutableSequence = []

    async def finalize(self, nvim: Nvim) -> None:
        if self._finalized:
            raise RuntimeError()
        else:
            self._finalized = True
