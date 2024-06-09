from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto
from functools import cache
from typing import AbstractSet, Optional, Sequence

from std2.pickle.decoder import new_decoder

from ..consts import CONF_LINT
from .install import HasInstall, InstallSpec, load


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
    install: InstallSpec = InstallSpec()


LinterSpecs = Mapping[str, LinterAttrs]


@cache
def linter_specs() -> LinterSpecs:
    p = new_decoder[LinterSpecs](LinterSpecs)
    conf = load(CONF_LINT)
    return p(conf)
