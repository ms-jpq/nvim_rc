from dataclasses import dataclass
from enum import Enum, auto
from typing import AbstractSet, Sequence, Mapping, Optional

from std2.pickle.decoder import new_decoder
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
    filetypes: AbstractSet[str]
    args: Sequence[str] = ()
    env: Optional[Mapping[str, str]] = None
    exit_code: int = 0
    install: InstallSpec = InstallSpec()


FmtSpecs = Sequence[FmtAttrs]
fmt_specs = new_decoder[FmtSpecs](FmtSpecs)(safe_load(CONF_FMT.open()))
