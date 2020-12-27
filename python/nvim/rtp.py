from locale import strxfrm
from pathlib import Path
from typing import Iterable

from pynvim import Nvim
from std2.pathlib import walk

from ..nvim.atomic import Atomic


def rtp_packages(nvim: Nvim, plugins: Iterable[Path]) -> Atomic:
    atomic = Atomic()
    head, *tail = nvim.list_runtime_paths()
    rtp = ",".join((head, *(map(str, plugins)), *tail))
    atomic.command(f"set runtimepath={rtp}")

    for path in plugins:
        plug = path / "plugin"
        if plug.exists():
            scripts = (str(s) for s in walk(plug) if s.suffix == ".vim")
            for script in sorted(scripts, key=strxfrm):
                atomic.command(f"source {script}")

    return atomic
