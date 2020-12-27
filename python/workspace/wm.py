from pynvim.api.buffer import Buffer
from pynvim.api.nvim import Nvim
from pynvim.api.window import Window
from python.nvim.atomic import Atomic

from ..registery import keymap, rpc, settings

# hide background buffers
settings["hidden"] = True
# reuse buf
settings["switchbuf"] += ("useopen", "usetab")

# modern split direction
settings["splitright"] = True
settings["splitbelow"] = True


@rpc()
def new_window(nvim: Nvim, vertical: bool) -> None:
    with Atomic() as (a, ns):
        a.command("vnew" if vertical else "new")
        ns.win = a.get_current_win()
        ns.buf = a.create_buf(False, True)
    nvim.api.win_set_buf(ns.win, ns.buf)


keymap.n("<leader>=", unique=True) << "<cmd>" + new_window.call_line("true") + "<cr>"
keymap.n("<leader>-", unique=True) << "<cmd>" + new_window.call_line("false") + "<cr>"
