from dataclasses import dataclass, field
from typing import AbstractSet, Mapping, Sequence


@dataclass(frozen=True)
class ScriptSpec:
    file: str = ""
    required: AbstractSet[str] = frozenset()
    env: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InstallSpec:
    pip: Sequence[str] = ()
    npm: Sequence[str] = ()
    go: Sequence[str] = ()
    script: ScriptSpec = ScriptSpec()
