#!/usr/bin/env python3

from asyncio import create_task

from pynvim import Nvim, attach


async def test(nvim: Nvim):
    ...


def main() -> None:
    with attach("stdio") as nvim:

        def req_cb(*args, **kwds) -> None:
            pass

        def notif_cb(*args, **kwds) -> None:
            create_task(test())
            nvim.api.out_write(str(nvim.loop) + "\n")

        nvim.run_loop(req_cb, notif_cb)


main()
