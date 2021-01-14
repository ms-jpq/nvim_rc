from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, AbstractSet, Mapping, Optional, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_LSP
from .install import InstallSpec


class RPFallback(Enum):
    none = auto()
    cwd = auto()
    home = auto()
    parent = auto()


@dataclass(frozen=True)
class RootPattern:
    fallback: RPFallback = RPFallback.cwd
    exact: AbstractSet[str] = frozenset()
    glob: Sequence[str] = ()


@dataclass(frozen=True)
class LspAttrs:
    server: str
    bin: str
    args: Optional[Sequence[str]] = None
    filetypes: AbstractSet[str] = frozenset()
    root: Optional[RootPattern] = None
    init_options: Mapping[str, Any] = field(default_factory=dict)
    settings: Mapping[str, Any] = field(default_factory=dict)
    install: InstallSpec = InstallSpec()


LspSpecs = Sequence[LspAttrs]
lsp_specs: LspSpecs = decode(LspSpecs, safe_load(CONF_LSP.open()))
