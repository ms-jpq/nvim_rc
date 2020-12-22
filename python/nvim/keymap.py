from __future__ import annotations

from dataclasses import asdict, dataclass
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

from .lib import AtomicInstruction
from .rpc import RPC_FUNCTION, RPC_SPEC, lua_rpc_literal

T = TypeVar("T")


@dataclass(frozen=True)
class _KeymapOpts:
    noremap: bool
    silent: bool
    expr: bool
    nowait: bool
    unique: bool


_KEY_MODES = {"n", "o", "v", "i", "c", "t"}


class _K:
    def __init__(
        self,
        lhs: str,
        blocking: bool,
        modes: Iterable[str],
        options: _KeymapOpts,
        parent: Keymap,
    ) -> None:
        self._lhs, self._modes = lhs, modes
        self._blk = blocking
        self._opts, self._parent = options, parent

    def __lshift__(self, rhs: Optional[str]) -> None:
        for mode in self._modes:
            self._parent._mappings[(mode, self._lhs)] = (self._blk, self._opts, rhs)

    def __call__(self, rhs: Callable[..., T]) -> RPC_FUNCTION[T]:
        for mode in self._modes:
            self._parent._mappings[(mode, self._lhs)] = (self._blk, self._opts, rhs)
        return rhs


class _KM:
    def __init__(self, modes: Iterable[str], parent: Keymap) -> None:
        self._modes, self._parent = modes, parent

    def __call__(
        self,
        lhs: str,
        blocking: bool = False,
        noremap: bool = True,
        silent: bool = True,
        expr: bool = False,
        nowait: bool = False,
        unique: bool = False,
    ) -> Callable[[Callable[..., T]], RPC_FUNCTION[T]]:
        opts = _KeymapOpts(
            noremap=noremap,
            silent=silent,
            expr=expr,
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
            Tuple[str, str],
            Tuple[bool, _KeymapOpts, Union[str, None, RPC_FUNCTION[Any]]],
        ] = {}

    def __getattr__(self, modes: str) -> _KM:
        for mode in modes:
            if mode not in _KEY_MODES:
                raise AttributeError()
        else:
            return _KM(modes=modes, parent=self)

    def drain(
        self, chan: int, buf: Optional[Buffer]
    ) -> Tuple[Sequence[AtomicInstruction], Sequence[RPC_SPEC]]:
        def it() -> Iterator[Tuple[AtomicInstruction, Optional[RPC_SPEC]]]:
            while self._mappings:
                (mode, lhs), (blocking, opts, rhs) = self._mappings.popitem()
                if (rhs is None or type(rhs) is str) and buf is None:
                    yield ("set_keymap", (mode, lhs, rhs, asdict(opts))), None

                elif (rhs is None or type(rhs) is str) and buf is not None:
                    yield ("buf_set_keymap", (buf, mode, lhs, rhs, asdict(opts))), None

                elif callable(rhs) and buf is None:
                    name = cast(Callable, rhs).__name__
                    lua = lua_rpc_literal(chan, blocking=blocking, name=name)
                    call = f"<cmd>{lua}<cr>"
                    yield ("set_keymap", (mode, lhs, call, asdict(opts))), (name, rhs)

                elif callable(rhs) and buf is not None:
                    name = cast(Callable, rhs).__name__
                    lua = lua_rpc_literal(chan, blocking=blocking, name=name)
                    call = f"<cmd>{lua}<cr>"
                    yield ("buf_set_keymap", (buf, mode, lhs, call, asdict(opts))), (
                        name,
                        rhs,
                    )

                else:
                    assert False

        try:
            instructions, specs = zip(*it())
        except ValueError:
            instructions, specs = (), ()

        return instructions, tuple(s for s in specs if s)
