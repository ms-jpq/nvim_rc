from dataclasses import dataclass, field
from typing import FrozenSet, Mapping, Sequence


@dataclass(frozen=True)
class ScriptSpec:
    interpreter: str = "bash"
    required: FrozenSet[str] = frozenset()
    env: Mapping[str, str] = field(default_factory=dict)
    body: str = ""


@dataclass(frozen=True)
class InstallSpec:
    pip: Sequence[str] = ()
    npm: Sequence[str] = ()
    go: Sequence[str] = ()
    script: ScriptSpec = ScriptSpec()
