from __future__ import annotations

from asyncio.coroutines import iscoroutinefunction
from asyncio.tasks import Task
from string import Template
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Iterator,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from pynvim import Nvim
from python.nvim.lib import async_call, go

from .logging import log

T = TypeVar("T")

RpcMsg = Tuple[str, Sequence[Any]]


class _ComposableTemplate(Template):
    def __add__(self, other: Union[str, Template]) -> _ComposableTemplate:
        return _ComposableTemplate(
            self.template
            + (
                cast(str, other)
                if type(other) is str
                else cast(Template, other).template
            )
        )

    def __radd__(self, other: Union[str, Template]) -> _ComposableTemplate:
        return _ComposableTemplate(
            (cast(str, other) if type(other) is str else cast(Template, other).template)
            + self.template
        )


class RpcCallable(Generic[T]):
    def __init__(
        self,
        name: Optional[str],
        blocking: bool,
        handler: Union[Callable[..., T], Callable[..., Awaitable[T]]],
    ) -> None:
        if iscoroutinefunction(handler) and blocking:
            raise ValueError()
        else:
            self.name = name if name else f"{handler.__module__}.{handler.__qualname__}"
            self._blocking = blocking
            self._handler = handler

    def call_line(self, *args: str) -> _ComposableTemplate:
        op = "request" if self._blocking else "notify"
        _args = ", ".join(args)
        call = f"lua vim.rpc{op}($chan, '{self.name}', {{{_args}}})"
        return _ComposableTemplate(call)

    def __call__(self, nvim: Nvim, *args: Any) -> Union[T, Task[T]]:
        if iscoroutinefunction(self._handler):
            aw = cast(Awaitable[T], self._handler(nvim, *args))
            return go(aw)
        elif self._blocking:
            return self._handler(nvim, *args)
        else:
            handler = cast(Callable[[Nvim, Any], T], self._handler)
            aw = async_call(nvim, handler, nvim, *args)
            return go(aw)


RpcSpec = Tuple[str, RpcCallable[T]]


class RPC:
    def __init__(self) -> None:
        self._handlers: MutableMapping[str, RpcCallable[Any]] = {}

    def __call__(
        self,
        blocking: bool,
        name: Optional[str] = None,
    ) -> Callable[[Callable[..., T]], RpcCallable[T]]:
        def decor(handler: Callable[..., T]) -> RpcCallable[T]:
            wraped = RpcCallable(name=name, blocking=blocking, handler=handler)
            self._handlers[wraped.name] = wraped
            return wraped

        return decor

    def drain(self) -> Sequence[RpcSpec]:
        def it() -> Iterator[RpcSpec]:
            while self._handlers:
                name, hldr = self._handlers.popitem()
                yield name, hldr

        return tuple(it())


def nil_handler(name: str) -> RpcCallable:
    def handler(nvim: Nvim, *args: Any) -> None:
        log.warn("MISSING RPC HANDLER FOR: %s - %s", name, args)

    return RpcCallable(name=name, blocking=True, handler=handler)
