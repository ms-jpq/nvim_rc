from abc import abstractmethod
from asyncio import get_running_loop, run
from concurrent.futures import Future
from queue import SimpleQueue
from threading import Thread
from typing import Any, AsyncIterator, Protocol, Sequence, Tuple, TypeVar

from pynvim import Nvim, attach

from .logging import log

T = TypeVar("T")

ARPC_MSG = Tuple[str, Sequence[Any]]
RPC_MSG = Tuple[Future[Any], ARPC_MSG]


class Client(Protocol):
    @abstractmethod
    async def __call__(
        self, nvim: Nvim, arpcs: AsyncIterator[ARPC_MSG], rpcs: AsyncIterator[RPC_MSG]
    ) -> None:
        ...


async def _transq(simple: SimpleQueue[T]) -> AsyncIterator[T]:
    loop = get_running_loop()
    while True:
        yield await loop.run_in_executor(None, simple.get)


def run_client(client: Client) -> None:
    with attach("stdio") as nvim:

        arpc_q, rpc_q = SimpleQueue[ARPC_MSG](), SimpleQueue[RPC_MSG]()
        aw = client(nvim, arpcs=_transq(arpc_q), rpcs=_transq(rpc_q))

        try:
            th = Thread(target=run, args=(aw,))

            def on_arpc(event: str, *args: Any) -> None:
                arpc_q.put((event, args))

            def on_rpc(event: str, *args: Any) -> Any:
                fut = Future[Any]()
                rpc_q.put((fut, (event, args)))
                return fut.result()

            def on_start() -> None:
                th.start()

            def on_err(error: str) -> None:
                log.error("%s", error)

            nvim.run_loop(
                err_cb=on_err,
                setup_cb=on_start,
                notification_cb=on_arpc,
                request_cb=on_rpc,
            )
        finally:
            th.join()
