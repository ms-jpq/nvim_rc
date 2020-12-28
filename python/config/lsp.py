from dataclasses import dataclass
from typing import Mapping, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_LSP
from .install import InstallSpec


@dataclass(frozen=True)
class LspAttrs:
    bin: str
    args: Sequence[str]
    filetypes: Sequence[str]
    install: InstallSpec


LspSpecs = Mapping[str, LspAttrs]
lsp_specs: LspSpecs = decode(LspSpecs, safe_load(CONF_LSP.open()))
