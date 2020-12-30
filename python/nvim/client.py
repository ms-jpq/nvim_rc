from abc import abstractmethod
from asyncio import get_running_loop
from asyncio.tasks import run_coroutine_threadsafe
from concurrent.futures import Future
from logging import WARN
from os import linesep
from queue import SimpleQueue
from threading import Thread
from typing import Any, AsyncIterable, AsyncIterator, Protocol, Sequence, TypeVar

from pynvim import Nvim

from .logging import log, nvim_handler

T = TypeVar("T")

from .rpc import RpcMsg


class Client(Protocol):
    @abstractmethod
    async def __call__(self, nvim: Nvim, rpcs: AsyncIterable[RpcMsg[Any]]) -> None:
        ...


async def _transq(simple: SimpleQueue[T]) -> AsyncIterator[T]:
    loop = get_running_loop()
    while True:
        yield await loop.run_in_executor(None, simple.get)


def _on_err(error: str) -> None:
    log.error("%s", error)


def run_client(nvim: Nvim, client: Client, log_level: int = WARN) -> None:
    rpc_q = SimpleQueue[RpcMsg[Any]]()

    def on_arpc(name: str, args: Sequence[Sequence[Any]]) -> None:
        rpc_q.put_nowait((None, (name, args[0])))

    def on_rpc(name: str, args: Sequence[Sequence[Any]]) -> Any:
        fut = Future[Any]()
        rpc_q.put_nowait((None, (name, args[0])))
        try:
            return fut.result()
        except Exception as e:
            fmt = f"ERROR IN RPC FOR: %s - %s{linesep}%s"
            log.exception(fmt, name, args, e)
            raise

    def main() -> None:
        try:
            fut = run_coroutine_threadsafe(
                client(nvim, rpcs=_transq(rpc_q)), loop=nvim.loop
            )
            fut.result()
        except Exception as e:
            log.exception(e)

    def forever() -> None:
        nvim.run_loop(
            err_cb=_on_err,
            notification_cb=on_arpc,
            request_cb=on_rpc,
        )

    th1 = Thread(target=main)
    th2 = Thread(target=forever, daemon=True)

    log.addHandler(nvim_handler(nvim))
    log.setLevel(log_level)
    th2.start()
    th1.start()
    th1.join()
