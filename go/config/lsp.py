from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cache
from typing import AbstractSet, Any, Mapping, Optional, Sequence

from std2.pickle.decoder import new_decoder

from ..consts import CONF_LSP
from .install import HasInstall, InstallSpec, load


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
class LspAttrs(HasInstall):
    args: Optional[Sequence[str]] = None
    filetypes: AbstractSet[str] = frozenset()
    root: Optional[RootPattern] = None
    init_options: Mapping[str, Any] = field(default_factory=dict)
    settings: Mapping[str, Any] = field(default_factory=dict)
    install: InstallSpec = InstallSpec()


LspSpecs = Mapping[str, LspAttrs]


@cache
def lsp_specs() -> LspSpecs:
    p = new_decoder[LspSpecs](LspSpecs)
    conf = load(CONF_LSP)
    return p(conf)
