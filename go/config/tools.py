from dataclasses import dataclass
from typing import AbstractSet, Sequence

from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import CONF_TOOL
from .install import ScriptSpec


@dataclass(frozen=True)
class ToolSpecs:
    pip: AbstractSet[str] = frozenset()
    gem: AbstractSet[str] = frozenset()
    npm: AbstractSet[str] = frozenset()
    script: Sequence[ScriptSpec] = ()


tool_specs = new_decoder[ToolSpecs](ToolSpecs)(safe_load(CONF_TOOL.open()))
