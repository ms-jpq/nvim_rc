#!/usr/bin/env python3

from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from queue import SimpleQueue
from sys import stderr
from threading import Thread
from typing import Any, Awaitable, Callable, Sequence, Tuple

from forechan import chan
from pynvim import attach

from python.server import server


def main() -> None:
    q = SimpleQueue[Callable[[], None]]()
    ch = chan(Tuple[str, Sequence[Any]])

    def poll() -> None:
        while True:
            f = q.get()
            f()

    th = Thread(target=poll, daemon=True)
    with attach("stdio") as nvim:
        loop: AbstractEventLoop = nvim.loop

        def submit(co: Awaitable[None]) -> None:
            def run() -> None:
                fut = run_coroutine_threadsafe(co, loop)
                fut.result()

            q.put(run)

        def on_req(event: str, *args: Any) -> None:
            nvim.api.err_write("No Blocking Calls Allowed\n")

        def on_notif(event: str, *args: Any) -> None:
            submit(ch.send((event, args)))

        def on_setup() -> None:
            submit(server(nvim, ch=ch))

        def on_err(error: Exception) -> None:
            print(error, file=stderr)

        th.start()
        nvim.run_loop(
            err_cb=on_err,
            setup_cb=on_setup,
            request_cb=on_req,
            notification_cb=on_notif,
        )


main()
