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


KMFunction = Callable[[Nvim], None]
KMAFunction = Callable[[Nvim], Awaitable[None]]
KeymapFunction = Union[KMFunction, KMAFunction]


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
                await cast(KMAFunction, rhs)(nvim)

            kmf = new_arhs if iscoroutinefunction(rhs) else new_rhs
            for mode in self._modes:
                self._parent._conf[(mode, lhs)] = kmf
            return kmf

        return decor


class KeyMap:
    def __init__(self) -> None:
        self._finalized = False
        self._conf: MutableMapping[
            Tuple[KeyModes, str], Union[str, KeymapFunction]
        ] = {}

    def __getattr__(self, modes: str) -> KM:
        for mode in modes:
            if mode not in KeyModes:
                raise AttributeError()
        else:
            return KM(modes=tuple(map(KeyModes, modes)), parent=self)

    def finalize(self, nvim: Nvim) -> None:
        if self._finalized:
            raise RuntimeError()
        else:
            self._finalized = True
            for (mode, lhs), rhs in self._conf.items():
                pass
