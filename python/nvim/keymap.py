from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, MutableMapping, Tuple, TypeVar, Union

from .rpc import RPC_FUNCTION

T = TypeVar("T")


@dataclass(frozen=True)
class _KeymapOpts:
    blocking: bool
    noremap: bool
    silent: bool
    nowait: bool
    unique: bool


class _KeyModes(Enum):
    n = "n"
    o = "o"
    v = "v"
    t = "t"


class _K:
    def __init__(
        self,
        lhs: str,
        modes: Iterable[_KeyModes],
        options: _KeymapOpts,
        parent: Keymap,
    ) -> None:
        self._lhs, self._modes = lhs, modes
        self._opts, self._parent = options, parent

    def __lshift__(self, rhs: str) -> None:
        for mode in self._modes:
            self._parent._mappings[(mode, self._lhs)] = (self._opts, rhs)

    def __call__(self, rhs: RPC_FUNCTION[T]) -> RPC_FUNCTION[T]:
        for mode in self._modes:
            self._parent._mappings[(mode, self._lhs)] = (self._opts, rhs)
        return rhs


class _KM:
    def __init__(self, modes: Iterable[_KeyModes], parent: Keymap) -> None:
        self._modes, self._parent = modes, parent

    def __call__(
        self,
        lhs: str,
        blocking: bool = False,
        noremap: bool = True,
        silent: bool = True,
        nowait: bool = False,
        unique: bool = False,
    ) -> Callable[[RPC_FUNCTION[T]], RPC_FUNCTION[T]]:
        opts = _KeymapOpts(
            blocking=blocking,
            noremap=noremap,
            silent=silent,
            nowait=nowait,
            unique=unique,
        )

        return _K(lhs=lhs, modes=self._modes, options=opts, parent=self._parent)


class Keymap:
    def __init__(self) -> None:
        self._mappings: MutableMapping[
            Tuple[_KeyModes, str], Tuple[_KeymapOpts, Union[str, RPC_FUNCTION[Any]]]
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
