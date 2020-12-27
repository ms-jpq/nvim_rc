from contextlib import contextmanager
from typing import Iterator, Optional, cast

from pynvim import Nvim
from pynvim.api import Buffer, Window
from .atomic import Atomic


class LockBroken(Exception):
    ...


@contextmanager
def buffer_lock(nvim: Nvim, b1: Optional[Buffer] = None) -> Iterator[Buffer]:
    if b1 is None:
        b1 = nvim.api.get_current_buf()
    c1 = nvim.api.buf_get_var(b1, "changetick")
    try:
        yield b1
    finally:
        with Atomic() as (a, ns):
            ns.b2 = a.get_current_buf()
            ns.c2 = a.buf_get_var(b1, "changetick")
        a.commit(nvim)

        if not (ns.b2 == b1 and ns.c2 == c1):
            raise LockBroken()


@contextmanager
def window_lock(nvim: Nvim, w1: Optional[Window] = None) -> Iterator[Window]:
    if w1 is None:
        w1 = nvim.api.get_current_win()
    try:
        yield cast(Window, w1)
    finally:
        w2: Window = nvim.api.get_current_win()
        if w2 != w1:
            raise LockBroken()
