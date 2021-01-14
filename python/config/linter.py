from dataclasses import dataclass
from enum import Enum, auto
from typing import AbstractSet, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_LINT
from .install import InstallSpec


class LinterType(Enum):
    stream = auto()
    fs = auto()


@dataclass(frozen=True)
class LinterAttrs:
    bin: str
    type: LinterType
    filetypes: AbstractSet[str]
    args: Sequence[str] = ()
    exit_code: int = 0
    install: InstallSpec = InstallSpec()


LinterSpecs = Sequence[LinterAttrs]
linter_specs: LinterSpecs = decode(LinterSpecs, safe_load(CONF_LINT.open()))
