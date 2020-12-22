from __future__ import annotations

from enum import Enum
from typing import Iterable, Iterator, MutableMapping, Tuple, Union, cast

from .lib import AtomicInstruction


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
    def __init__(self) -> None:
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

    def drain(self, typ: SettingType) -> Iterator[AtomicInstruction]:
        while self._conf:
            key, (op, val) = self._conf.popitem()
            yield "command", (f"{typ.value} {key}{op.value}{val}",)
