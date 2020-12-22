from __future__ import annotations

from enum import Enum
from typing import AsyncIterator, Iterable, Iterator, MutableMapping, Tuple, Union, cast

from pynvim import Nvim

from .lib import AtomicInstruction, atomic


class SettingType(Enum):
    system = "set"
    local = "setlocal"


class _OP(Enum):
    exact = ""
    equals = "="
    plus = "+="
    minus = "-="


class _Setting:
    def __init__(self, name: str, parent: Settings) -> None:
        self.name, self._parent = name, parent

    def __iadd__(self, vals: Iterable[str]) -> _Setting:
        self._parent._conf[self.name] = (_OP.plus, ",".join(vals))
        return self

    def __isub__(self, vals: Iterable[str]) -> _Setting:
        self._parent._conf[self.name] = (_OP.minus, ",".join(vals))
        return self


class Settings:
    def __init__(self, s_type: SettingType = SettingType.system) -> None:
        self._finalized = False
        self._type = s_type
        self._conf: MutableMapping[str, Tuple[_OP, str]] = {}

    def __getitem__(self, key: str) -> _Setting:
        return _Setting(name=key, parent=self)

    def __setitem__(self, key: str, val: Union[_Setting, str, bool]) -> None:
        if type(val) is _Setting:
            pass
        elif type(val) is str:
            self._conf[key] = (_OP.equals, cast(str, val))
        elif type(val) is bool:
            self._conf[key] = (_OP.exact, "")
        else:
            raise TypeError()

    def drain(self) -> Iterator[AtomicInstruction]:
        while self._conf:
            key, (op, val) = self._conf.popitem()
            yield "command", (f"{self._type.value} {key}{op.value}{val}",)
