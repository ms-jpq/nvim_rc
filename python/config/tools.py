from typing import Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_TOOL
from .install import InstallSpec

ToolSpecs = Sequence[InstallSpec]
tool_specs: ToolSpecs = decode(ToolSpecs, safe_load(CONF_TOOL.open()))
