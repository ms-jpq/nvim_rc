from __future__ import annotations

from asyncio.coroutines import iscoroutinefunction
from enum import Enum
from typing import Awaitable, Callable, Iterable, Mapping, Union

from pynvim import Nvim


class KeyModes(Enum):
    n = "n"
    o = "o"
    v = "v"
    t = "t"


KeymapFunction = Callable[[Nvim], Union[Awaitable[None], None]]


class KM:
    def __init__(self, modes: Iterable[str], parent: KeyMap) -> None:
        self._modes, self._parent = modes, parent

    def __setattr__(self, name: str, value: str) -> None:
        ...


class KeyMap:
    _conf: Mapping[str, str] = {}

    def __getattr__(self, keys: str) -> KM:
        for key in keys:
            if key not in KeyModes:
                raise AttributeError()
        else:
            return KM(keys)

    def __call__(self, lhs: str) -> Callable[[KeymapFunction], KeymapFunction]:
        def decor(rhs: KeymapFunction) -> KeymapFunction:
            def new_rhs(nvim: Nvim) -> None:
                nvim.async_call(rhs, nvim)

            async def new_arhs(nvim: Nvim) -> None:
                await rhs(nvim)

            return new_arhs if iscoroutinefunction(rhs) else new_rhs

        return decor


keymap = KeyMap()


async def finalize(nvim: Nvim) -> None:
    for key, val in keymap._conf.items():
        pass
