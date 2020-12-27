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

# move between windows
keymap.n("<c-left>") << "<cmd>wincmd h<cr>"
keymap.n("<c-right>") << "<cmd>wincmd l<cr>"
keymap.n("<c-up>") << "<cmd>wincmd k<cr>"
keymap.n("<c-down>") << "<cmd>wincmd j<cr>"

# swap windows
keymap.n("<leader>'") << "<cmd>wincmd r<cr>"
keymap.n("<leader>;") << "<cmd>wincmd R<cr>"

# move windows
keymap.n("<s-left>") << "<cmd>wincmd H<cr>"
keymap.n("<s-right>") << "<cmd>wincmd L<cr>"
keymap.n("<s-up>") << "<cmd>wincmd K<cr>"
keymap.n("<s-down>") << "<cmd>wincmd J<cr>"


@rpc()
def new_window(nvim: Nvim, vertical: bool) -> None:
    with Atomic() as (a, ns):
        a.command("vnew" if vertical else "new")
        ns.win = a.get_current_win()
        ns.buf = a.create_buf(False, True)
    a.commit(nvim)
    nvim.api.win_set_buf(ns.win, ns.buf)


keymap.n("<leader>=", unique=True) << "<cmd>" + new_window.call_line("true") + "<cr>"
keymap.n("<leader>-", unique=True) << "<cmd>" + new_window.call_line("false") + "<cr>"
