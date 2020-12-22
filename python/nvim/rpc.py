from typing import Any, Callable, MutableMapping, Protocol, Union

from pynvim import Nvim


class RPC_FN(Protocol):
    def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


class RPC_AFN(Protocol):
    async def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


RpcFunction = Union[RPC_FN, RPC_AFN]


class RPC:
    def __init__(self) -> None:
        self._finalized = False
        self._handlers: MutableMapping[str, RpcFunction] = {}

    async def __call__(self, uid: str) -> Callable[[RpcFunction], RpcFunction]:
        def decor(rpc_f: RpcFunction) -> RpcFunction:
            self._handlers[uid] = rpc_f
            return rpc_f

        return decor

    async def finalize(self, nvim: Nvim) -> None:
        if self._finalized:
            raise RuntimeError()
        else:
            self._finalized = True
