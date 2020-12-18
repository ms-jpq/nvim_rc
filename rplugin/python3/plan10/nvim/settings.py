from __future__ import annotations

from enum import Enum, auto
from typing import Iterable, Mapping, Tuple

from pynvim import Nvim


class _OP(Enum):
    equals = auto()
    plus = auto()
    minus = auto()


class Setting:
    def __init__(self, name: str, parent: Settings) -> None:
        self.name, self._parent = name, parent

    def __iadd__(self, vals: Iterable[str]) -> None:
        self._parent._conf[self.name] = (_OP.plus, ",".join(vals))

    def __isub__(self, vals: Iterable[str]) -> None:
        self._parent._conf[self.name] = (_OP.minus, ",".join(vals))


class Settings:
    _conf: Mapping[str, Tuple[_OP, str]] = {}

    def __getitem__(self, key: str) -> Setting:
        return Setting(name=key, parent=self)

    def __setitem__(self, key: str, val: str) -> None:
        self._conf[key] = (_OP.equals, val)


settings = Settings()
