from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class InstallSpec:
    pip: Sequence[str] = ()
    npm: Sequence[str] = ()
    bash: str = ""
