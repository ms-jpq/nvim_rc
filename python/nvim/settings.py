from __future__ import annotations

from enum import Enum
from typing import Iterable, Iterator, MutableMapping, Tuple, Union, cast
from .lib import atomic, AtomicInstruction, async_call
from pynvim import Nvim


class _OP(Enum):
    exact = ""
    equals = "="
    plus = "+="
    minus = "-="


class Setting:
    def __init__(self, name: str, parent: Settings) -> None:
        self.name, self._parent = name, parent

    def __iadd__(self, vals: Iterable[str]) -> Setting:
        self._parent._conf[self.name] = (_OP.plus, ",".join(vals))
        return self

    def __isub__(self, vals: Iterable[str]) -> Setting:
        self._parent._conf[self.name] = (_OP.minus, ",".join(vals))
        return self


class Settings:
    _conf: MutableMapping[str, Tuple[_OP, str]] = {}

    def __getitem__(self, key: str) -> Setting:
        return Setting(name=key, parent=self)

    def __setitem__(self, key: str, val: Union[Setting, str, bool]) -> None:
        if type(val) is Setting:
            pass
        elif type(val) is str:
            self._conf[key] = (_OP.equals, cast(str, val))
        elif type(val) is bool:
            self._conf[key] = (_OP.exact, "")
        else:
            raise TypeError()


settings = Settings()


async def finalize(nvim: Nvim) -> None:
    def instructions() -> Iterator[AtomicInstruction]:
        for key, (op, val) in settings._conf.items():
            yield "nvim_command", (f"set {key}{op.value}{val}",)

    await async_call(nvim, atomic, *instructions())