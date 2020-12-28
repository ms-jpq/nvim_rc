from dataclasses import dataclass
from typing import Mapping, Sequence

from .install import InstallSpec


@dataclass(frozen=True)
class LspAttrs:
    bin: str
    args: Sequence[str]
    filetypes: Sequence[str]
    install: InstallSpec


LspSpecs = Mapping[str, LspAttrs]