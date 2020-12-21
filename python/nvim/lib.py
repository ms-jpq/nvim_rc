from contextlib import contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    cast,
)

from pynvim import Nvim
from pynvim.api import Buffer, Window

T = TypeVar("T")


def atomic(nvim: Nvim, *instructions: Tuple[str, Sequence[Any]]) -> Sequence[Any]:
    inst = tuple((f"nvim_{instruction}", args) for instruction, args in instructions)
    out, err = nvim.api.call_atomic(inst)
    if err:
        idx, err_type, err_msg = err
        raise err_type(instructions[idx][0], err_msg)
    else:
        return cast(Sequence[Any], out)


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
        b2, c2 = atomic(
            nvim, ("get_current_buf", ()), ("buf_get_var", (b1, "changetick"))
        )
        if not (b2 == b1 and c2 == c1):
            raise LockBroken()


@contextmanager
def window_lock(nvim: Nvim, w1: Optional[Window] = None) -> Iterator[Window]:
    if w1 is None:
        w1 = nvim.get_current_win()
    try:
        yield cast(Window, w1)
    finally:
        w2: Window = nvim.get_current_win()
        if w2 != w1:
            raise LockBroken()
