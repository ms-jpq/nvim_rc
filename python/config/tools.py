from dataclasses import dataclass
from typing import Sequence

from std2.pickle import new_decoder
from yaml import safe_load

from ..consts import CONF_TOOL
from .install import ScriptSpec


@dataclass(frozen=True)
class ToolSpecs:
    pip: Sequence[str] = ()
    npm: Sequence[str] = ()
    go: Sequence[str] = ()
    script: Sequence[ScriptSpec] = ()


tool_specs = new_decoder[ToolSpecs](ToolSpecs)(safe_load(CONF_TOOL.open()))
