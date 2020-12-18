from pynvim import Nvim, command, plugin


@plugin
class Main:
    def __init__(self, nvim: Nvim) -> None:
        pass

    @command("Plan10Start", nargs="*")
    def start(self) -> None:
        pass
