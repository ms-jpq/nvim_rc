from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from os import getcwd
from os.path import normpath
from pathlib import Path, PurePath
from shutil import which as _which
from sys import stderr
from typing import AbstractSet, Any, Optional, Protocol

from std2.graphlib import merge
from std2.pathlib import AnyPath
from std2.pickle.decoder import new_decoder
from std2.platform import OS, os
from yaml import safe_load

from ..consts import CONF_SAFE


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


_Safe = AbstractSet[PurePath]

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


def load(path: Path) -> Any:
    dir = Path(getcwd()) / ".nvim"

    def paths() -> Iterator[Path]:
        if not CONF_SAFE.is_file():
            CONF_SAFE.touch()
        with CONF_SAFE.open() as fd:
            safe = safe_load(fd)

        p = new_decoder[_Safe](_Safe)
        loadable = p(safe or ())

        yield path
        for ps in (dir / path.name,):
            if ps.is_file():
                if ps in loadable:
                    yield ps
                else:
                    print("!", [ps], file=stderr)

    def cont() -> Iterator[Any]:
        for path in paths():
            with path.open() as fd:
                yield safe_load(fd)

    return merge(*cont())
