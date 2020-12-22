from abc import abstractmethod
from asyncio import get_running_loop, run
from concurrent.futures import Future
from logging import WARN
from queue import SimpleQueue
from threading import Thread
from typing import Any, AsyncIterator, Protocol, TypeVar

from pynvim import Nvim

from .logging import log, nvim_handler

T = TypeVar("T")

from .rpc import ARPC_MSG, RPC_MSG


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


def run_client(nvim: Nvim, client: Client, log_level: int = WARN) -> None:
    arpc_q, rpc_q = SimpleQueue[ARPC_MSG](), SimpleQueue[RPC_MSG]()

    def on_err(error: str) -> None:
        log.error("%s", error)

    def on_arpc(event: str, *args: Any) -> None:
        arpc_q.put((event, args))

    def on_rpc(event: str, *args: Any) -> Any:
        fut = Future[Any]()
        rpc_q.put((fut, (event, args)))
        return fut.result()

    async def main() -> None:
        try:
            await client(nvim, arpcs=_transq(arpc_q), rpcs=_transq(rpc_q))
        except Exception as e:
            log.exception("%s", e)

    def forever() -> None:
        nvim.run_loop(
            err_cb=on_err,
            notification_cb=on_arpc,
            request_cb=on_rpc,
        )

    th1 = Thread(target=run, args=(main(),))
    th2 = Thread(target=forever, daemon=True)

    log.addHandler(nvim_handler(nvim))
    log.setLevel(log_level)
    th2.start()
    th1.start()
    th1.join()
