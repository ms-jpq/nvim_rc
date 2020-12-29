from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional, Sequence

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
    filetypes: Sequence[str]
    args: Sequence[str] = ()
    exit_code: int = 0
    install: Optional[InstallSpec] = None


LinterSpecs = Mapping[str, LinterAttrs]
linter_specs: LinterSpecs = decode(LinterSpecs, safe_load(CONF_LINT.open()))
