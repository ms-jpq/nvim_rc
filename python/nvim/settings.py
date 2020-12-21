from __future__ import annotations

from enum import Enum
from typing import Iterable, MutableMapping, Tuple, Union, cast

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

    def __setitem__(self, key: str, val: Union[str, bool]) -> None:
        self._conf[key] = (
            (_OP.equals, cast(str, val)) if type(val) is str else (_OP.exact, "")
        )


settings = Settings()


async def finalize(nvim: Nvim) -> None:
    for key, (op, val) in settings._conf.items():
        print("set " + key + op.value + val)
