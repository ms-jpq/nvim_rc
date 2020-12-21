#!/usr/bin/env python3

from asyncio import run
from asyncio.events import new_event_loop, set_event_loop
from concurrent.futures import Future
from sys import stderr
from threading import Thread
from traceback import print_exc
from typing import Any

from pynvim import attach
from pynvim.api.nvim import Nvim

from python.server import NOTIF_Q, RPC_Q, server


def srv(nvim: Nvim, notif_q: NOTIF_Q, req_q: RPC_Q) -> None:
    loop = new_event_loop()
    set_event_loop(loop)
    try:
        run(server(nvim, notif_q=notif_q, req_q=req_q))
    except Exception:
        print_exc()


def main() -> None:
    notif_q, req_q = NOTIF_Q(), RPC_Q()

    with attach("stdio") as nvim:
        try:
            th = Thread(target=srv, args=(nvim, notif_q, req_q))

            def on_notif(event: str, *args: Any) -> None:
                notif_q.put((event, args))

            def on_req(event: str, *args: Any) -> Any:
                fut = Future[Any]()
                req_q.put((fut, (event, args)))
                return fut.result()

            def on_setup() -> None:
                th.start()

            def on_err(error: str) -> None:
                print(error, file=stderr)

            nvim.run_loop(
                err_cb=on_err,
                setup_cb=on_setup,
                notification_cb=on_notif,
                request_cb=on_req,
            )
        finally:
            th.join()


main()
