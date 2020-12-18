from sys import path

from .consts import SUB_MODULES

path.extend(SUB_MODULES)

from typing import Any, Sequence

from pynvim import Nvim, command, function, plugin


@plugin
class Main:
    def __init__(self, nvim: Nvim) -> None:
        pass

    @command("Plan10Start", nargs="*")
    def start(self) -> None:
        pass

    @function("_Plan10Comm")
    def comm(self, args: Sequence[Any]) -> None:
        pass
