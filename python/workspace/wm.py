from pynvim.api.buffer import Buffer
from pynvim.api.nvim import Nvim
from pynvim.api.window import Window
from ..registery import settings, keymap, rpc

# hide background buffers
settings["hidden"] = True
# reuse buf
settings["switchbuf"] += ("useopen", "usetab")

# modern split direction
settings["splitright"] = True
settings["splitbelow"] = True


@rpc()
def new_window(nvim: Nvim, vertical: bool) -> None:
    nvim.command("vnew" if vertical else "new")
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.create_buf(False, True)
    nvim.api.win_set_buf(win, buf)


keymap.n("<leader>=", unique=True) << "cmd" + new_window.call_line("true") + "<cr>"
keymap.n("<leader>-", unique=True) << "<cmd>" + new_window.call_line("false") + "<cr>"