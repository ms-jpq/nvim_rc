from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import AbstractSet, Optional, Sequence

from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import CONF_LINT
from .install import HasInstall, InstallSpec


class LinterType(Enum):
    stream = auto()
    fs = auto()


@dataclass(frozen=True)
class LinterAttrs(HasInstall):
    type: LinterType
    filetypes: AbstractSet[str]
    args: Sequence[str] = ()
    env: Optional[Mapping[str, str]] = None
    exit_code: int = 0
    install = InstallSpec()


LinterSpecs = Sequence[LinterAttrs]
linter_specs = new_decoder[LinterSpecs](LinterSpecs)(safe_load(CONF_LINT.open()))
