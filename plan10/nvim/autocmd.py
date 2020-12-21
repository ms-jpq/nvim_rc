from pynvim import Nvim
from typing import MutableSequence

_autocmds: MutableSequence = []


def autocmd() -> None:
    pass


async def finalize(nvim: Nvim) -> None:
    pass