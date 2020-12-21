#!/usr/bin/env python3

from asyncio import run
from asyncio.events import new_event_loop, set_event_loop
from sys import stderr
from threading import Thread
from traceback import print_exc
from typing import Any

from pynvim import attach

from python.server import RPC_Q, server


def main() -> None:
    notif_q, req_q = RPC_Q(), RPC_Q()

    with attach("stdio") as nvim:

        def srv() -> None:
            loop = new_event_loop()
            set_event_loop(loop)
            try:
                run(server(nvim, notif_q=notif_q, req_q=req_q))
            except Exception:
                print_exc()

        th = Thread(target=srv, daemon=True)

        def on_notif(event: str, *args: Any) -> None:
            notif_q.put((event, args))

        def on_req(event: str, *args: Any) -> None:
            req_q.put((event, args))

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


main()
