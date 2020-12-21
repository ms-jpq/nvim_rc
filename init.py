#!/usr/bin/env python3

from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from queue import SimpleQueue
from threading import Thread
from typing import Any, Awaitable

from pynvim import Nvim, attach

from python.nvim.lib import async_call


async def uwu(nvim: Nvim) -> None:
    def cont() -> None:
        nvim.api.out_write("uwu\n")
        nvim.api.out_write("uwu\n")
        nvim.api.out_write("uwu\n")

    await async_call(nvim, cont)


def main() -> None:
    q = SimpleQueue()

    def poll():
        while True:
            f = q.get()
            f()

    th = Thread(target=poll, daemon=True)
    with attach("stdio") as nvim:
        loop: AbstractEventLoop = nvim.loop

        def submit(co: Awaitable[None]) -> None:
            def run() -> None:
                fut = run_coroutine_threadsafe(co, loop)
                try:
                    fut.result()
                except Exception as e:
                    nvim.async_call(nvim.api.err_write, f"{e}\n")

            q.put(run)

        def on_req(*args: Any) -> None:
            pass

        def on_notif(*args: Any) -> None:
            submit(uwu(nvim))

        th.start()
        nvim.run_loop(request_cb=on_req, notification_cb=on_notif)


main()
