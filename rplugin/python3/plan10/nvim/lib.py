from asyncio.futures import Future
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
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
        return out


def call(nvim: Nvim, fn: Callable[..., T], *args: Any, **kwargs: Any) -> Awaitable[T]:
    fut: Future = Future()

    def cont() -> None:
        try:
            ret = fn()
        except Exception as e:
            fut.set_exception(e)
        else:
            if not fut.cancelled():
                fut.set_result(ret)

    nvim.async_call(cont)
    return fut


class LockBroken(Exception):
    ...


@asynccontextmanager
async def buffer_lock(nvim: Nvim, b1: Optional[Buffer] = None) -> AsyncIterator[Buffer]:
    def cont() -> Tuple[Buffer, int]:
        b = nvim.api.get_current_buf() if b1 is None else b1
        c2 = nvim.api.buf_get_var(b, "changetick")
        return b, c2

    b1, c1 = await call(nvim, cont)
    try:
        yield b1
    finally:
        b2, c2 = await call(
            nvim, atomic(nvim, ("get_current_buf",), ("buf_get_var", b1, "changetick"))
        )
        if not (b2 == b1 and c2 == c1):
            raise LockBroken()


@asynccontextmanager
async def window_lock(nvim: Nvim, w1: Optional[Window] = None) -> AsyncIterator[None]:
    if w1 is None:
        w1 = await call(nvim, nvim.get_current_win)
    try:
        yield cast(Window, w1)
    finally:
        w2: Window = await call(nvim, nvim.get_current_win)
        if w2 != w1:
            raise LockBroken()
