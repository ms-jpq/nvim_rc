from dataclasses import dataclass, field
from functools import cache
from typing import Any, Mapping, Optional, Sequence

from pynvim_pp.keymap import KeymapOpts
from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import CONF_PKGS


@dataclass(frozen=True)
class GitPkgSpec:
    uri: str
    branch: Optional[str] = None
    call: Sequence[Sequence[str]] = ()
    mvp: bool = False


@dataclass(frozen=True)
class KeymapSpec:
    modes: str
    maps: Mapping[str, str]
    opts: KeymapOpts = KeymapOpts()


@dataclass(frozen=True)
class PkgAttrs:
    git: GitPkgSpec
    opt: Optional[bool] = False
    keys: Sequence[KeymapSpec] = ()
    vals: Mapping[str, Any] = field(default_factory=dict)
    lua: str = ""
    lub: str = ""
    viml: str = ""


PkgSpecs = Sequence[PkgAttrs]


@cache
def pkg_specs() -> PkgSpecs:
    p = new_decoder[PkgSpecs](PkgSpecs)
    return p(safe_load(CONF_PKGS.open()))
