from typing import Any, Awaitable, Callable, MutableMapping, Union

from pynvim import Nvim

RPC_FN = Callable[[Nvim, *Any], None]
RPC_AFN = Callable[[Nvim, *Any], Awaitable[None]]
RpcFunction = Union[RPC_FN, RPC_AFN]

_handlers: MutableMapping[RpcFunction] = []


def rpc(uid: str) -> Callable[[RpcFunction], RpcFunction]:
    def decor(rpc_f: RpcFunction) -> RpcFunction:
        _handlers[uid] = rpc_f
        return rpc_f

    return decor


async def finalize(nvim: Nvim) -> None:
    pass
