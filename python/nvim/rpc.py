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
    TypeVar,
    Union,
    cast,
)

from pynvim import Nvim

from .lib import async_call, create_task
from .logging import log

T_co = TypeVar("T_co", covariant=True)

RPC_MSG = Tuple[Optional[Future[T_co]], Tuple[str, Sequence[Any]]]


class RPC_FN(Protocol[T_co]):
    def __call__(self, nvim: Nvim, *args: Any) -> T_co:
        ...


class RPC_AFN(Protocol[T_co]):
    async def __call__(self, nvim: Nvim, *args: Any) -> T_co:
        ...


RPC_FUNCTION = Union[RPC_FN[T_co], RPC_AFN[T_co]]
RPC_SPEC = Tuple[str, RPC_FUNCTION[T_co]]


class RPC:
    def __init__(self) -> None:
        self._handlers: MutableMapping[str, RPC_FUNCTION[Any]] = {}

    def __call__(self, name: str) -> Callable[[RPC_FUNCTION[T_co]], RPC_FUNCTION[T_co]]:
        def decor(rpc_f: RPC_FUNCTION[T_co]) -> RPC_FUNCTION[T_co]:
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


async def _invoke_handler(nvim: Nvim, hldr: RPC_FUNCTION[T_co], *args: Any) -> T_co:
    if iscoroutinefunction(hldr):
        return await cast(RPC_AFN[T_co], hldr)(nvim, *args)
    else:
        return await async_call(nvim, cast(RPC_FN[T_co], hldr), nvim, *args)


async def rpc_agent(
    specs: AsyncIterable[RPC_SPEC[Any]],
    rpcs: AsyncIterable[RPC_MSG[Any]],
) -> None:
    handlers: MutableMapping[str, RPC_FUNCTION[Any]] = {}

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
