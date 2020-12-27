from __future__ import annotations

from asyncio import gather
from asyncio.coroutines import iscoroutinefunction
from concurrent.futures import Future
from os import linesep
from string import Template
from typing import (
    Any,
    AsyncIterable,
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

from .lib import async_call, create_task
from .logging import log

T = TypeVar("T")

RPC_MSG = Tuple[Optional[Future[T]], Tuple[str, Sequence[Any]]]


class ComposableTemplate(Template):
    def __add__(self, other: Union[str, Template]) -> ComposableTemplate:
        return ComposableTemplate(
            self.template
            + (
                cast(str, other)
                if type(other) is str
                else cast(Template, other).template
            )
        )

    def __radd__(self, other: Union[str, Template]) -> ComposableTemplate:
        return ComposableTemplate(
            (cast(str, other) if type(other) is str else cast(Template, other).template)
            + self.template
        )


class RPC_FUNCTION(Generic[T]):
    def __init__(
        self,
        name: Optional[str],
        handler: Union[Callable[..., T], Callable[..., Awaitable[T]]],
    ) -> None:
        self.name = name if name else handler.__qualname__
        self._rpcf = handler

    def rpc(self, *args: str, blocking: bool = False) -> ComposableTemplate:
        op = "request" if blocking else "notify"
        _args = ", ".join(args)
        call = f"lua vim.rpc{op}($chan, '{self.name}', {{{_args}}})"
        return ComposableTemplate(call)

    async def __call__(self, nvim: Nvim, *args: Any) -> T:
        if iscoroutinefunction(self._rpcf):
            return await cast(Callable[..., Awaitable[T]], self._rpcf)(nvim, *args)
        else:
            return await async_call(
                nvim, cast(Callable[..., T], self._rpcf), nvim, *args
            )


RPC_SPEC = Tuple[str, RPC_FUNCTION[T]]


class RPC:
    def __init__(self) -> None:
        self._handlers: MutableMapping[str, RPC_FUNCTION[Any]] = {}

    def __call__(
        self, name: Optional[str] = None
    ) -> Callable[[Callable[..., T]], RPC_FUNCTION[T]]:
        def decor(handler: Callable[..., T]) -> RPC_FUNCTION[T]:
            wraped = RPC_FUNCTION(name=name, handler=handler)
            self._handlers[wraped.name] = wraped
            return wraped

        return decor

    def drain(self) -> Sequence[RPC_SPEC]:
        def it() -> Iterator[RPC_SPEC]:
            while self._handlers:
                name, hldr = self._handlers.popitem()
                yield name, hldr

        return tuple(it())


def _nil_handler(name: str) -> RPC_FUNCTION:
    def handler(nvim: Nvim, *args: Any) -> None:
        log.warn("MISSING RPC HANDLER FOR: %s - %s", name, args)

    return RPC_FUNCTION(name=name, handler=handler)


async def rpc_agent(
    nvim: Nvim,
    specs: AsyncIterable[RPC_SPEC[Any]],
    rpcs: AsyncIterable[RPC_MSG[Any]],
) -> None:
    handlers: MutableMapping[str, RPC_FUNCTION[Any]] = {}

    async def poll_spec() -> None:
        async for name, handler in specs:
            handlers[name] = handler

    async def poll_rpc() -> None:
        async for fut, (name, args) in rpcs:
            handler = handlers.get(name, _nil_handler(name))
            try:
                ret = await handler(nvim, *args)
            except Exception as e:
                if fut and not fut.cancelled():
                    fut.set_exception(e)
                else:
                    fmt = f"ERROR IN RPC FOR: %s - %s{linesep}%s"
                    log.exception(fmt, name, args, e)
            else:
                if fut and not fut.cancelled():
                    fut.set_result(ret)

    await gather(create_task(poll_spec()), create_task(poll_rpc()))
