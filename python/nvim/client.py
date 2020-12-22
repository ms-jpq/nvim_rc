from abc import abstractmethod
from asyncio import new_event_loop, run, set_event_loop
from concurrent.futures import Future
from queue import SimpleQueue
from threading import Thread
from typing import Any, Protocol, Sequence, Tuple

from pynvim import Nvim, attach

from .logging import log

NOTIF_MSG = Tuple[str, Sequence[Any]]
NOTIF_Q = SimpleQueue[NOTIF_MSG]

RPC_MSG = Tuple[Future[Any], NOTIF_MSG]
RPC_Q = SimpleQueue[RPC_MSG]


class Client(Protocol):
    @abstractmethod
    async def __call__(self, nvim: Nvim, notif_q: NOTIF_Q, rpc_q: RPC_Q) -> None:
        ...


def run_client(client: Client) -> None:
    notif_q, rpc_q = NOTIF_Q(), RPC_Q()

    def loop2() -> None:
        loop = new_event_loop()
        loop.set_exception_handler()
        set_event_loop(loop)
        run(client(nvim, notif_q=notif_q, rpc_q=rpc_q))

    with attach("stdio") as nvim:
        try:
            th = Thread(target=loop2)

            def on_notif(event: str, *args: Any) -> None:
                notif_q.put((event, args))

            def on_req(event: str, *args: Any) -> Any:
                fut = Future[Any]()
                rpc_q.put((fut, (event, args)))
                return fut.result()

            def on_setup() -> None:
                th.start()

            def on_err(error: str) -> None:
                log.error("%s", error)

            nvim.run_loop(
                err_cb=on_err,
                setup_cb=on_setup,
                notification_cb=on_notif,
                request_cb=on_req,
            )
        finally:
            th.join()
