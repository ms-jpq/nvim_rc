from pynvim.api.nvim import Nvim
from pynvim_pp.api import cur_win, win_set_option

from ..registery import atomic, autocmd, rpc, settings

# use 256 colours
settings["termguicolors"] = True

# remove welcome message
settings["shortmess"] += "I"
# always show status line
settings["laststatus"] = 2
# always show tabline
settings["showtabline"] = 2


# always show issues column
settings["signcolumn"] = "yes"
# show line count
settings["number"] = True
# dont show eob lines
settings["fillchars"] = r"eob:\ "


# keep wrapped text indent
settings["breakindent"] = True
# settings["showbreak"] = "↳"

# show cursor
settings["cursorline"] = True
# constant cursor styling
settings["guicursor"] = ""

# completion menu transparency
settings["pumblend"] = 5
# light background
settings["background"] = "light"


@rpc(blocking=True)
def _ins_cursor(nvim: Nvim) -> None:
    win = cur_win(nvim)
    win_set_option(nvim, win=win, key="cursorline", val=False)


@rpc(blocking=True)
def _norm_cursor(nvim: Nvim) -> None:
    win = cur_win(nvim)
    win_set_option(nvim, win=win, key="cursorline", val=True)


autocmd("InsertEnter") << f"lua {_ins_cursor.name}()"
autocmd("InsertLeave") << f"lua {_norm_cursor.name}()"


# highlight yank
@rpc(blocking=True)
def _hl_yank(nvim: Nvim) -> None:
    nvim.lua.vim.highlight.on_yank({"higroup": "HighlightedyankRegion"})


atomic.command("highlight HighlightedyankRegion cterm=reverse gui=reverse")
autocmd("TextYankPost") << f"lua {_hl_yank.name}()"
