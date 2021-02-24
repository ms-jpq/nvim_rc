from pynvim.api.nvim import Nvim
from pynvim_pp.highlight import HLgroup, highlight

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


@rpc(blocking=True)
def _hl_cursor(nvim: Nvim) -> None:
    highlight(HLgroup("CursorLine", guibg="#f2d9fa")).commit(nvim)


@rpc(blocking=True)
def _dehl_cursor(nvim: Nvim) -> None:
    highlight(HLgroup("CursorLine", guibg="#f1f4f6")).commit(nvim)


autocmd("InsertEnter") << f"lua {_hl_cursor.name}()"
autocmd("InsertLeave") << f"lua {_dehl_cursor.name}()"


# highlight yank
@rpc(blocking=True)
def _hl_yank(nvim: Nvim) -> None:
    nvim.lua.vim.highlight.on_yank({"higroup": "IncSearch"})


atomic.command("highlight HighlightedyankRegion cterm=reverse gui=reverse")
autocmd("TextYankPost") << f"lua {_hl_yank.name}()"
