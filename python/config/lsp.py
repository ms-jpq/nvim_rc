from dataclasses import dataclass, field
from typing import Any, FrozenSet, Mapping, Optional, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_LSP
from .install import InstallSpec


@dataclass(frozen=True)
class RootPattern:
    exact: FrozenSet[str] = frozenset()
    glob: Sequence[str] = ()


@dataclass(frozen=True)
class LspAttrs:
    server: str
    bin: str
    filetypes: FrozenSet[str]
    args: Sequence[str] = ()
    config: Mapping[str, Any] = field(default_factory=dict)
    root: Optional[RootPattern] = None
    install: InstallSpec = InstallSpec()


LspSpecs = Sequence[LspAttrs]
lsp_specs: LspSpecs = decode(LspSpecs, safe_load(CONF_LSP.open()))
