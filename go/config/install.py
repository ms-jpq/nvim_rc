from dataclasses import dataclass
from pathlib import PurePath
from typing import AbstractSet, Optional


@dataclass(frozen=True)
class ScriptSpec:
    file: Optional[PurePath] = None


@dataclass(frozen=True)
class InstallSpec:
    requires: AbstractSet[str] = frozenset()
    pip: AbstractSet[str] = frozenset()
    gem: AbstractSet[str] = frozenset()
    npm: AbstractSet[str] = frozenset()
    script: ScriptSpec = ScriptSpec()
