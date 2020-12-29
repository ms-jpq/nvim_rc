from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional, Sequence

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
    filetypes: Sequence[str]
    args: Sequence[str] = ()
    install: Optional[InstallSpec] = None


FmtSpecs = Mapping[str, FmtAttrs]
fmt_specs: FmtSpecs = decode(FmtSpecs, safe_load(CONF_FMT.open()))
