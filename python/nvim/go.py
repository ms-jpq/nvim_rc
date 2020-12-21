from asyncio.tasks import create_task
from traceback import print_exc
from typing import Awaitable, TypeVar

T = TypeVar("T")


async def go(aw: Awaitable[T]) -> Awaitable[T]:
    async def wrapper() -> T:
        try:
            return await aw
        except Exception:
            print_exc()
            raise

    return create_task(wrapper())
