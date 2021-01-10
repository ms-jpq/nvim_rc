from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ScriptSpec:
    interpreter: str = "bash"
    env: Mapping[str, str] = field(default_factory=dict)
    body: str = ""


@dataclass(frozen=True)
class InstallSpec:
    pip: Sequence[str] = ()
    npm: Sequence[str] = ()
    go: Sequence[str] = ()
    script: ScriptSpec = ScriptSpec()
