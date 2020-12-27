from dataclasses import dataclass
from typing import Mapping, Sequence

from python.config.packages import InstallSpec


@dataclass(frozen=True)
class LspAttrs:
    bin: str
    args: Sequence[str]
    filetypes: Sequence[str]
    install: InstallSpec


LspSpec = Mapping[str, LspAttrs]