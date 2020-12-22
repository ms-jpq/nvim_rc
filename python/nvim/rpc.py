from concurrent.futures import Future
from typing import (
    Any,
    Callable,
    Iterable,
    MutableMapping,
    Protocol,
    Sequence,
    Tuple,
    Union,
)

from pynvim import Nvim

ARPC_MSG = Tuple[str, Sequence[Any]]
RPC_MSG = Tuple[Future[Any], ARPC_MSG]


class RPC_FN(Protocol):
    def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


class RPC_AFN(Protocol):
    async def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


RPC_Function = Union[RPC_FN, RPC_AFN]


class RPC:
    def __init__(self) -> None:
        self._rpc_handlers: MutableMapping[str, Tuple[bool, RPC_Function]] = {}

    def __call__(
        self, name: str, blocking: bool = False
    ) -> Callable[[RPC_Function], RPC_Function]:
        def decor(rpc_f: RPC_Function) -> RPC_Function:
            self._rpc_handlers[name] = rpc_f
            return rpc_f

        return decor

    def drain(self) -> Iterable[str, Tuple[bool, RPC_Function]]:
        while self._rpc_handlers:
            yield self._rpc_handlers.popitem()
