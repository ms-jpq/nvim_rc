from pynvim import Nvim
from typing import MutableSequence

_handlers: MutableSequence = []


def rpc() -> None:
    pass


async def finalize(nvim: Nvim) -> None:
    pass