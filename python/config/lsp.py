from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, FrozenSet, Mapping, Optional, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_LSP
from .install import InstallSpec


class RPFallback(Enum):
    cwd = auto()
    home = auto()
    parent = auto()


@dataclass(frozen=True)
class RootPattern:
    fallback: RPFallback = RPFallback.cwd
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
