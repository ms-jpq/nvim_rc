from abc import abstractmethod
from asyncio import get_running_loop, run
from concurrent.futures import Future
from logging import WARN
from os import linesep
from queue import SimpleQueue
from threading import Thread
from typing import Any, AsyncIterable, AsyncIterator, Protocol, Sequence, TypeVar

from pynvim import Nvim

from .logging import log, nvim_handler

T = TypeVar("T")

from .rpc import RPC_MSG


class Client(Protocol):
    @abstractmethod
    async def __call__(self, nvim: Nvim, rpcs: AsyncIterable[RPC_MSG[Any]]) -> None:
        ...


async def _transq(simple: SimpleQueue[T]) -> AsyncIterator[T]:
    loop = get_running_loop()
    while True:
        yield await loop.run_in_executor(None, simple.get)


def on_err(error: str) -> None:
    log.error("%s", error)


def run_client(nvim: Nvim, client: Client, log_level: int = WARN) -> None:
    rpc_q = SimpleQueue[RPC_MSG[Any]]()

    def on_arpc(event: str, args: Sequence[Any]) -> None:
        rpc_q.put((None, (event, args)))

    def on_rpc(name: str, args: Sequence[Any]) -> Any:
        fut = Future[Any]()
        rpc_q.put((fut, (name, args)))
        try:
            return fut.result()
        except Exception as e:
            fmt = f"ERROR IN RPC FOR: %s - %s{linesep}%s"
            log.exception(fmt, name, args, e)
            return None

    async def main() -> None:
        try:
            await client(nvim, rpcs=_transq(rpc_q))
        except Exception:
            log.exception("")

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
