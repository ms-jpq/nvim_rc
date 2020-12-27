from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Iterable,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

from .atomic import Atomic
from .rpc import RpcCallable, RpcSpec

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
        self._autocmds: MutableMapping[str, Tuple[_AuParams, RpcCallable[Any]]] = {}

    def __call__(
        self,
        event: str,
        *events: str,
        name: Optional[str] = None,
        filters: Iterable[str] = ("*",),
        modifiers: Iterable[str] = (),
        args: Iterable[str] = (),
        blocking: bool = False,
    ) -> Callable[[Callable[..., T]], RpcCallable[T]]:
        param = _AuParams(
            blocking=blocking,
            events=tuple((event, *events)),
            filters=filters,
            modifiers=modifiers,
            args=args,
        )

        def decor(handler: Callable[..., T]) -> RpcCallable[T]:
            wrapped = RpcCallable(name=name, handler=handler)
            self._autocmds[wrapped.name] = (param, wrapped)
            return wrapped

        return decor

    def drain(self, chan: int) -> Tuple[Atomic, Sequence[RpcSpec]]:
        atomic = Atomic()
        specs: MutableSequence[RpcSpec] = []
        while self._autocmds:
            name, (param, func) = self._autocmds.popitem()
            events = ",".join(param.events)
            filters = " ".join(param.filters)
            modifiers = " ".join(param.modifiers)
            call = func.call_line(*param.args, blocking=param.blocking).substitute(
                chan=chan
            )
            atomic.command(f"augroup ch_{chan}.{name}")
            atomic.command("autocmd!")
            atomic.command(f"autocmd {events} {filters} {modifiers} {call}")
            atomic.command("augroup END")
            specs.append((name, func))

        return atomic, specs
