from asyncio import gather
from asyncio.coroutines import iscoroutinefunction
from concurrent.futures import Future
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Iterable,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Union,
    cast,
)

from pynvim import Nvim

from .lib import async_call, create_task
from .logging import log

RPC_MSG = Tuple[Optional[Future[Any]], Tuple[str, Sequence[Any]]]


class RPC_FN(Protocol):
    def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


class RPC_AFN(Protocol):
    async def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


RPC_FUNCTION = Union[RPC_FN, RPC_AFN]
RPC_SPEC = Tuple[str, RPC_FUNCTION]


class RPC:
    def __init__(self) -> None:
        self._handlers: MutableMapping[str, RPC_FUNCTION] = {}

    def __call__(self, name: str) -> Callable[[RPC_FUNCTION], RPC_FUNCTION]:
        def decor(rpc_f: RPC_FUNCTION) -> RPC_FUNCTION:
            self._handlers[name] = rpc_f
            return rpc_f

        return decor

    def drain(self) -> Iterable[RPC_SPEC]:
        while self._handlers:
            name, hldr = self._handlers.popitem()
            yield name, hldr


def _nil_handler(name: str) -> RPC_FN:
    def handler(nvim: Nvim, *args: Any) -> None:
        log.warn("MISSING RPC HANDLER FOR: %s - %s", name, args)

    return handler


async def _invoke_handler(nvim: Nvim, hldr: RPC_FUNCTION, *args: Any) -> Any:
    if iscoroutinefunction(hldr):
        return await cast(RPC_AFN, hldr)(nvim, *args)
    else:
        return await async_call(nvim, hldr, nvim, *args)


async def rpc_agent(
    specs: AsyncIterable[RPC_SPEC],
    rpcs: AsyncIterable[RPC_MSG],
) -> None:
    handlers: MutableMapping[str, RPC_FUNCTION] = {}

    async def poll_spec() -> None:
        async for name, hldr in specs:
            handlers[name] = hldr

    async def poll_rpc() -> None:
        async for fut, (name, args) in rpcs:
            hldr = handlers.get(name, _nil_handler(name))
            try:
                ret = await _invoke_handler(hldr, *args)
            except Exception as e:
                log.exception("ERROR IN RPC FOR: %s - %s", name, args)
                if fut and not fut.cancelled():
                    fut.set_exception(e)
            else:
                if fut and not fut.cancelled():
                    fut.set_result(ret)

    await gather(create_task(poll_spec()), create_task(poll_rpc()))
