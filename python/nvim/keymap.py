from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from pynvim.api import Buffer
from python.nvim.lib import AtomicInstruction

from .rpc import RPC_FUNCTION, RPC_SPEC, lua_rpc_literal

T = TypeVar("T")


@dataclass(frozen=True)
class _KeymapOpts:
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
        blocking: bool,
        modes: Iterable[_KeyModes],
        options: _KeymapOpts,
        parent: Keymap,
    ) -> None:
        self._lhs, self._modes = lhs, modes
        self._blk = blocking
        self._opts, self._parent = options, parent

    def __lshift__(self, rhs: str) -> None:
        for mode in self._modes:
            self._parent._mappings[(mode, self._lhs)] = (self._blk, self._opts, rhs)

    def __call__(self, rhs: RPC_FUNCTION[T]) -> RPC_FUNCTION[T]:
        for mode in self._modes:
            self._parent._mappings[(mode, self._lhs)] = (self._blk, self._opts, rhs)
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
            noremap=noremap,
            silent=silent,
            nowait=nowait,
            unique=unique,
        )

        return _K(
            lhs=lhs,
            blocking=blocking,
            modes=self._modes,
            options=opts,
            parent=self._parent,
        )


class Keymap:
    def __init__(self) -> None:
        self._mappings: MutableMapping[
            Tuple[_KeyModes, str],
            Tuple[bool, _KeymapOpts, Union[str, RPC_FUNCTION[Any]]],
        ] = {}

    def __getattr__(self, modes: str) -> _KM:
        for mode in modes:
            if mode not in _KeyModes:
                raise AttributeError()
        else:
            return _KM(modes=tuple(map(_KeyModes, modes)), parent=self)

    def drain(
        self, chan: int, buf: Optional[Buffer]
    ) -> Tuple[Sequence[AtomicInstruction], Sequence[RPC_SPEC]]:
        def it() -> Iterator[Tuple[AtomicInstruction, Optional[RPC_SPEC]]]:
            while self._mappings:
                (mode, lhs), (blocking, opts, rhs) = self._mappings.popitem()
                if type(rhs) is str and buf is None:
                    yield ("set_keymap", (mode, lhs, rhs, asdict(opts))), None

                elif type(rhs) is str and buf is not None:
                    yield ("buf_set_keymap", (buf, mode, lhs, rhs, asdict(opts))), None

                elif callable(rhs) and buf is None:
                    name = cast(Callable, rhs).__name__
                    lua = lua_rpc_literal(chan, blocking=blocking, name=name)
                    yield ("set_keymap", (mode, lhs, lua, asdict(opts))), (name, rhs)

                elif callable(rhs) and buf is not None:
                    name = cast(Callable, rhs).__name__
                    lua = lua_rpc_literal(chan, blocking=blocking, name=name)
                    yield ("buf_set_keymap", (buf, mode, lhs, lua, asdict(opts))), (
                        name,
                        rhs,
                    )

                else:
                    assert False

        instructions, specs = zip(*it())
        return instructions, tuple(s for s in specs if s)
