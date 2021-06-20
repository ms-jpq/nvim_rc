from pynvim.api.nvim import Nvim
from pynvim_pp.api import cur_win, win_set_option

from ..registery import atomic, autocmd, rpc, settings

# use 256 colours
settings["termguicolors"] = True
# remove welcome message
settings["shortmess"] += "I"
# always show status line
settings["laststatus"] = 2
# always show issues column
settings["signcolumn"] = "yes"
# dont show eob lines
settings["fillchars"] = r"eob:\ "
# always show tabline
settings["showtabline"] = 2
# show line count
settings["number"] = True


# show cursor
settings["cursorline"] = True
# constant cursor styling
settings["guicursor"] = ""

atomic.command("colorscheme zellner")
# light background
settings["background"] = "light"


@rpc(blocking=True)
def _hl_cursor(nvim: Nvim) -> None:
    win = cur_win(nvim)
    win_set_option(nvim, win=win, key="winhighlight", val="CursorLine:Visual")


@rpc(blocking=True)
def _dehl_cursor(nvim: Nvim) -> None:
    win = cur_win(nvim)
    win_set_option(nvim, win=win, key="winhighlight", val="")


autocmd("InsertEnter") << f"lua {_hl_cursor.name}()"
autocmd("InsertLeave") << f"lua {_dehl_cursor.name}()"


# highlight yank
@rpc(blocking=True)
def _hl_yank(nvim: Nvim) -> None:
    nvim.lua.vim.highlight.on_yank({"higroup": "HighlightedyankRegion"})


atomic.command("highlight HighlightedyankRegion cterm=reverse gui=reverse")
autocmd("TextYankPost") << f"lua {_hl_yank.name}()"

