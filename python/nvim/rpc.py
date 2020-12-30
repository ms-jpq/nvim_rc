from __future__ import annotations

from asyncio.coroutines import iscoroutinefunction
from asyncio.tasks import create_task
from os import linesep
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
        handler: Union[Callable[..., T], Callable[..., Awaitable[T]]],
    ) -> None:
        self.name = name if name else f"{handler.__module__}.{handler.__qualname__}"
        self._rpcf = handler

    def call_line(self, *args: str, blocking: bool = False) -> _ComposableTemplate:
        op = "request" if blocking else "notify"
        _args = ", ".join(args)
        call = f"lua vim.rpc{op}($chan, '{self.name}', {{{_args}}})"
        return _ComposableTemplate(call)

    def __call__(self, nvim: Nvim, *args: Any) -> Union[T, Awaitable[T]]:
        if iscoroutinefunction(self._rpcf):

            async def wrapper() -> T:
                try:
                    return await cast(Awaitable[T], self._rpcf(nvim, *args))
                except Exception as e:
                    fmt = f"ERROR IN RPC FOR: %s - %s{linesep}%s"
                    log.exception(fmt, self.name, args, e)
                    raise

            return create_task(wrapper())
        else:
            return self._rpcf(nvim, *args)


RpcSpec = Tuple[str, RpcCallable[T]]


class RPC:
    def __init__(self) -> None:
        self._handlers: MutableMapping[str, RpcCallable[Any]] = {}

    def __call__(
        self, name: Optional[str] = None
    ) -> Callable[[Callable[..., T]], RpcCallable[T]]:
        def decor(handler: Callable[..., T]) -> RpcCallable[T]:
            wraped = RpcCallable(name=name, handler=handler)
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

    return RpcCallable(name=name, handler=handler)
