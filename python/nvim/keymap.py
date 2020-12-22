from __future__ import annotations

from enum import Enum
from typing import Callable, Iterable, MutableMapping, Tuple, Union


from .rpc import RPC_FUNCTION


class _KeyModes(Enum):
    n = "n"
    o = "o"
    v = "v"
    t = "t"


class _KM:
    def __init__(self, modes: Iterable[_KeyModes], parent: KeyMap) -> None:
        self._modes, self._parent = modes, parent

    def __setattr__(self, name: str, value: str) -> None:
        for mode in self._modes:
            self._parent._mappings[(mode, name)] = value

    def __call__(self, lhs: str) -> Callable[[RPC_FUNCTION], RPC_FUNCTION]:
        def decor(rhs: RPC_FUNCTION) -> RPC_FUNCTION:
            return rhs

        return decor


class KeyMap:
    def __init__(self) -> None:
        self._finalized = False
        self._mappings: MutableMapping[
            Tuple[_KeyModes, str], Union[str, RPC_FUNCTION]
        ] = {}

    def __getattr__(self, modes: str) -> _KM:
        for mode in modes:
            if mode not in _KeyModes:
                raise AttributeError()
        else:
            return _KM(modes=tuple(map(_KeyModes, modes)), parent=self)

    def drain(self) -> None:
        if self._finalized:
            raise RuntimeError()
        else:
            self._finalized = True
            for (mode, lhs), rhs in self._mappings.items():
                pass
