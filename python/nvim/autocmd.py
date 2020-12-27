from dataclasses import dataclass
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
)

from .lib import AtomicInstruction
from .rpc import RPC_FUNCTION, RPC_SPEC

T = TypeVar("T")


@dataclass(frozen=True)
class _AuParams:
    blocking: bool
    events: Iterable[str]
    filters: Iterable[str]
    modifiers: Iterable[str]
    args: Iterable[str]


class AutoCMD:
    def __init__(self) -> None:
        self._autocmds: MutableMapping[str, Tuple[_AuParams, RPC_FUNCTION[Any]]] = {}

    def __call__(
        self,
        event: str,
        *events: str,
        name: Optional[str] = None,
        filters: Iterable[str] = ("*",),
        modifiers: Iterable[str] = (),
        args: Iterable[str] = (),
        blocking: bool = False,
    ) -> Callable[[Callable[..., T]], RPC_FUNCTION[T]]:
        param = _AuParams(
            blocking=blocking,
            events=tuple((event, *events)),
            filters=filters,
            modifiers=modifiers,
            args=args,
        )

        def decor(handler: Callable[..., T]) -> RPC_FUNCTION[T]:
            wrapped = RPC_FUNCTION(name=name, handler=handler)
            self._autocmds[wrapped.name] = (param, wrapped)
            return wrapped

        return decor

    def drain(
        self, chan: int
    ) -> Tuple[Sequence[AtomicInstruction], Sequence[RPC_SPEC]]:
        def it() -> Iterator[Tuple[Sequence[AtomicInstruction], RPC_SPEC]]:
            while self._autocmds:
                name, (param, func) = self._autocmds.popitem()
                events = ",".join(param.events)
                filters = " ".join(param.filters)
                modifiers = " ".join(param.modifiers)
                call = func.rpc(*param.args, blocking=param.blocking).substitute(
                    chan=chan
                )

                yield (
                    ("command", (f"augroup ch_{chan}_{name}",)),
                    ("command", ("autocmd!",)),
                    ("command", (f"autocmd {events} {filters} {modifiers} {call}",)),
                    ("command", ("augroup END",)),
                ), (name, func)

        try:
            instructions, specs = zip(*it())
        except ValueError:
            instructions, specs = (), ()

        return tuple(i for inst in instructions for i in inst), specs
