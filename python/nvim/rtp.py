from locale import strxfrm
from pathlib import Path
from typing import Iterable, Iterator

from pynvim import Nvim

from ..nvim.atomic import Atomic


def _walk(path: Path) -> Iterator[Path]:
    for p in path.iterdir():
        if p.is_dir():
            yield from _walk(p)
        elif p.is_file():
            yield p


def rtp_packages(nvim: Nvim, plugins: Iterable[Path]) -> Atomic:
    atomic = Atomic()
    head, *tail = nvim.list_runtime_paths()
    rtp = ",".join((head, *(map(str, plugins)), *tail))
    atomic.command(f"set runtimepath={rtp}")

    for path in plugins:
        plug = path / "plugin"
        if plug.exists():
            scripts = (str(s) for s in _walk(plug) if s.suffix == ".vim")
            for script in sorted(scripts, key=strxfrm):
                atomic.command(f"source {script}")

    return atomic
