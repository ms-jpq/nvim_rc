from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

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