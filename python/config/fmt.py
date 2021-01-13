from dataclasses import dataclass
from enum import Enum, auto
from typing import FrozenSet, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_FMT
from .install import InstallSpec


class FmtType(Enum):
    stream = auto()
    fs = auto()
    lsp = auto()


@dataclass(frozen=True)
class FmtAttrs:
    bin: str
    type: FmtType
    filetypes: FrozenSet[str]
    args: Sequence[str] = ()
    exit_code: int = 0
    install: InstallSpec = InstallSpec()


FmtSpecs = Sequence[FmtAttrs]
fmt_specs: FmtSpecs = decode(FmtSpecs, safe_load(CONF_FMT.open()))
