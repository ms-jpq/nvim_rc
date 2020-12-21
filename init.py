#!/usr/bin/env python3

from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from queue import SimpleQueue
from threading import Thread
from typing import Awaitable

from pynvim import Nvim, attach


async def uwu(nvim: Nvim) -> None:
    nvim.api.out_write("uwu\n")
    raise Exception("WWW")


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

        def req_cb(*args, **kwds) -> None:
            pass

        def notif_cb(*args, **kwds) -> None:
            nvim.api.out_write(str(nvim.loop) + "\n")
            submit(uwu(nvim))

        th.start()
        nvim.run_loop(req_cb, notif_cb)


main()
