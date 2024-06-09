from dataclasses import dataclass
from functools import cache
from os.path import normpath
from pathlib import PurePath
from shutil import which as _which
from typing import AbstractSet, Optional, Protocol, Any

from std2.configparser import hydrate
from std2.graphlib import merge
from std2.pathlib import AnyPath
from std2.platform import OS, os


@dataclass(frozen=True)
class ScriptSpec:
    file: Optional[PurePath] = None


@dataclass(frozen=True)
class InstallSpec:
    requires: AbstractSet[PurePath] = frozenset()
    pip: AbstractSet[str] = frozenset()
    gem: AbstractSet[str] = frozenset()
    npm: AbstractSet[str] = frozenset()
    script: ScriptSpec = ScriptSpec()


class _HasInstall(Protocol):
    install: InstallSpec


@dataclass(frozen=True)
class HasInstall(_HasInstall):
    bin: PurePath


_DIE = {"/usr/bin/ruby", "/usr/bin/gem", "/usr/bin/java"}


@cache
def which(src: AnyPath) -> Optional[PurePath]:
    if dst := _which(normpath(src)):
        if os is OS.macos and dst in _DIE:
            return None
        else:
            return PurePath(dst)
    else:
        return None


def load(path: PurePath) -> Any:
    pass
