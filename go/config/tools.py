from dataclasses import dataclass
from functools import cache
from typing import AbstractSet, Sequence

from std2.pickle.decoder import new_decoder

from ..consts import CONF_TOOL
from .install import ScriptSpec, load


@dataclass(frozen=True)
class ToolSpecs:
    pip: AbstractSet[str] = frozenset()
    gem: AbstractSet[str] = frozenset()
    npm: AbstractSet[str] = frozenset()
    script: Sequence[ScriptSpec] = ()


@cache
def tool_specs() -> ToolSpecs:
    p = new_decoder[ToolSpecs](ToolSpecs)
    conf = load(CONF_TOOL)
    return p(conf)
