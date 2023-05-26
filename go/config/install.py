from dataclasses import dataclass, field
from pathlib import PurePath
from typing import AbstractSet, Mapping, Optional


@dataclass(frozen=True)
class ScriptSpec:
    file: Optional[PurePath] = None
    required: AbstractSet[str] = frozenset()
    env: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InstallSpec:
    pip: AbstractSet[str] = frozenset()
    gem: AbstractSet[str] = frozenset()
    npm: AbstractSet[str] = frozenset()
    script: ScriptSpec = ScriptSpec()
