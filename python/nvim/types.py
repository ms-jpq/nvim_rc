from abc import abstractmethod
from concurrent.futures import Future
from queue import SimpleQueue
from typing import Any, Protocol, Sequence, Tuple

from pynvim import Nvim

NOTIF_MSG = Tuple[str, Sequence[Any]]
NOTIF_Q = SimpleQueue[NOTIF_MSG]

RPC_MSG = Tuple[Future[Any], NOTIF_MSG]
RPC_Q = SimpleQueue[RPC_MSG]


class Client(Protocol):
    @abstractmethod
    async def __call__(self, nvim: Nvim, notif_q: NOTIF_Q, rpc_q: RPC_Q) -> None:
        ...
