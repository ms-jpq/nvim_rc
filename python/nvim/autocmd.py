from pynvim import Nvim
from typing import MutableSequence


class AutoCMD:
    def __init__(self) -> None:
        self._autocmds: MutableSequence = []

    async def finalize(nvim: Nvim) -> None:
        pass


