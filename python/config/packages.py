from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence, Set

from ..nvim.keymap import KeymapOpts


@dataclass(frozen=True)
class KeymapSpec:
    mode: Set[str]
    map: Mapping[str, str]
    opts: KeymapOpts = field(default_factory=KeymapOpts)


@dataclass(frozen=True)
class PackageSpec:
    uri: str
    keys: Sequence[KeymapSpec]
    vals: Mapping[str, Any]
