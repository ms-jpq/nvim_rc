from typing import Any, Callable, MutableMapping, Protocol, Union

from pynvim import Nvim


class RPC_FN(Protocol):
    def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


class RPC_AFN(Protocol):
    async def __call__(self, nvim: Nvim, *args: Any) -> None:
        ...


RpcFunction = Union[RPC_FN, RPC_AFN]

_handlers: MutableMapping[str, RpcFunction] = {}


def rpc(uid: str) -> Callable[[RpcFunction], RpcFunction]:
    def decor(rpc_f: RpcFunction) -> RpcFunction:
        _handlers[uid] = rpc_f
        return rpc_f

    return decor


async def finalize(nvim: Nvim) -> None:
    pass
