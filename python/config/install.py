from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True)
class BashSpec:
    env: Mapping[str, str] = field(default_factory=dict)
    script: str = ""


@dataclass(frozen=True)
class InstallSpec:
    pip: Sequence[str] = ()
    npm: Sequence[str] = ()
    bash: BashSpec = BashSpec()
