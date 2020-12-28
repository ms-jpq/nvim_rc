from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from std2.pickle import decode
from yaml import safe_load

from ..consts import CONF_LINT
from .install import InstallSpec


class LinterType(Enum):
    stream = "stream"
    fs = "fs"


@dataclass(frozen=True)
class LinterAttrs:
    type: LinterType
    args: Sequence[str]
    filetypes: Sequence[str]
    install: InstallSpec


LinterSpecs = Mapping[str, LinterAttrs]
linter_specs = decode(LinterSpecs, safe_load(CONF_LINT.open()))
