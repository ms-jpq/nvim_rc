from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Iterable, MutableMapping, Tuple, TypeVar, Union

from .rpc import RPC_FUNCTION

T = TypeVar("T")


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

    def __call__(
        self, lhs: str, blocking: bool = False, silent: bool = True
    ) -> Callable[[RPC_FUNCTION[T]], RPC_FUNCTION[T]]:
        def decor(rhs: RPC_FUNCTION[T]) -> RPC_FUNCTION[T]:
            return rhs

        return decor


class KeyMap:
    def __init__(self) -> None:
        self._mappings: MutableMapping[
            Tuple[_KeyModes, str], Union[str, RPC_FUNCTION[Any]]
        ] = {}

    def __getattr__(self, modes: str) -> _KM:
        for mode in modes:
            if mode not in _KeyModes:
                raise AttributeError()
        else:
            return _KM(modes=tuple(map(_KeyModes, modes)), parent=self)

    def drain(self) -> None:
        for (mode, lhs), rhs in self._mappings.items():
            pass
