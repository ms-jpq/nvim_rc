from __future__ import annotations

from asyncio.coroutines import iscoroutinefunction
from enum import Enum
from typing import Awaitable, Callable, Iterable, MutableMapping, Tuple, Union, cast

from pynvim import Nvim


class KeyModes(Enum):
    n = "n"
    o = "o"
    v = "v"
    t = "t"


KeymapFunction = Callable[[Nvim], Union[Awaitable[None], None]]


class KM:
    def __init__(self, modes: Iterable[KeyModes], parent: KeyMap) -> None:
        self._modes, self._parent = modes, parent

    def __setattr__(self, name: str, value: str) -> None:
        for mode in self._modes:
            self._parent._conf[(mode, name)] = value

    def __call__(self, lhs: str) -> Callable[[KeymapFunction], KeymapFunction]:
        def decor(rhs: KeymapFunction) -> KeymapFunction:
            def new_rhs(nvim: Nvim) -> None:
                nvim.async_call(rhs, nvim)

            async def new_arhs(nvim: Nvim) -> None:
                await cast(Callable[[Nvim], Awaitable[None]], rhs)(nvim)

            new = new_arhs if iscoroutinefunction(rhs) else new_rhs
            for mode in self._modes:
                self._parent._conf[(mode, lhs)] = new
            return new

        return decor


class KeyMap:
    _conf: MutableMapping[Tuple[KeyModes, str], Union[str, KeymapFunction]] = {}

    def __getattr__(self, modes: str) -> KM:
        for mode in modes:
            if mode not in KeyModes:
                raise AttributeError()
        else:
            return KM(modes=tuple(map(KeyModes, modes)), parent=self)


keymap = KeyMap()


async def finalize(nvim: Nvim) -> None:
    for (mode, lhs), rhs in keymap._conf.items():
        pass
