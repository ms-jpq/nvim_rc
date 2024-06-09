from dataclasses import dataclass
from enum import Enum, auto
from functools import cache
from typing import AbstractSet, Mapping, Optional, Sequence

from std2.pickle.decoder import new_decoder

from ..consts import CONF_FMT
from .install import HasInstall, InstallSpec, load


class FmtType(Enum):
    stream = auto()
    fs = auto()
    lsp = auto()


@dataclass(frozen=True)
class FmtAttrs(HasInstall):
    type: FmtType
    filetypes: AbstractSet[str]
    args: Sequence[str] = ()
    env: Optional[Mapping[str, str]] = None
    exit_code: int = 0
    install: InstallSpec = InstallSpec()


FmtSpecs = Mapping[str, FmtAttrs]


@cache
def fmt_specs() -> FmtSpecs:
    p = new_decoder[FmtSpecs](FmtSpecs)
    conf = load(CONF_FMT)
    return p(conf)
