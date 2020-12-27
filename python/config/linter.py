from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from python.config.packages import InstallSpec


class LinterType(Enum):
    stream = "stream"
    fs = "fs"


@dataclass(frozen=True)
class LinterAttrs:
    type: LinterType
    args: Sequence[str]
    filetypes: Sequence[str]
    install: InstallSpec


LinterSpec = Mapping[str, LinterAttrs]