from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from pynvim_pp.keymap import KeymapOpts
from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import CONF_PKGS


@dataclass(frozen=True)
class GitPkgSpec:
    uri: str
    branch: Optional[str] = None
    call: Sequence[str] = ()


@dataclass(frozen=True)
class KeymapSpec:
    modes: str
    maps: Mapping[str, str]
    opts: KeymapOpts = KeymapOpts()


@dataclass(frozen=True)
class PkgAttrs:
    git: GitPkgSpec
    keys: Sequence[KeymapSpec] = ()
    vals: Mapping[str, Any] = field(default_factory=dict)
    lua: str = ""
    viml: str = ""


PkgSpecs = Sequence[PkgAttrs]
pkg_specs = new_decoder[PkgSpecs](PkgSpecs)(safe_load(CONF_PKGS.open()))