from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_FMT
from .install import InstallSpec


class FmtType(Enum):
    stream = "stream"
    fs = "fs"
    lsp = "lsp"


@dataclass(frozen=True)
class FmtAttrs:
    type: FmtType
    args: Sequence[str]
    filetypes: Sequence[str]
    install: InstallSpec


FmtSpecs = Mapping[str, FmtAttrs]
fmt_specs = decode(FmtSpecs, safe_load(CONF_FMT.open()))
