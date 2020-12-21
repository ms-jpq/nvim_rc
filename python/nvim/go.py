from asyncio.tasks import create_task
from os import linesep
from sys import stderr
from traceback import format_exc
from typing import Awaitable, TypeVar

T = TypeVar("T")


async def go(aw: Awaitable[T]) -> Awaitable[T]:
    async def wrapper() -> T:
        try:
            return await aw
        except Exception:
            print(format_exc(), sep=linesep, file=stderr)

    return create_task(wrapper())
