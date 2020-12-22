from pynvim.api.buffer import Buffer
from pynvim.api.nvim import Nvim
from pynvim.api.window import Window
from ..registery import settings, keymap

# hide background buffers
settings["hidden"] = True
# reuse buf
settings["switchbuf"] += ("useopen", "usetab")

# modern split direction
settings["splitright"] = True
settings["splitbelow"] = True


def _new_window(nvim: Nvim) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.create_buf(False, True)
    nvim.api.win_set_buf(win, buf)


@keymap.n("<leader>=", unique=True)
def new_window_v(nvim: Nvim) -> None:
    nvim.command("vnew")
    _new_window(nvim)


@keymap.n("<leader>-", unique=True)
def new_window_h(nvim: Nvim) -> None:
    nvim.command("new")
    _new_window(nvim)
