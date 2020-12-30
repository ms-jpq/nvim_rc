from typing import Any, Mapping, Sequence

from pynvim.api.nvim import Buffer, Nvim

from ..nvim.highlight import HLgroup, highlight
from ..registery import atomic, autocmd, settings

# use 256 colours
settings["termguicolors"] = True
# always show status line
settings["laststatus"] = 2
# always show issues column
settings["signcolumn"] = "yes"
# dont show eob lines
settings["fillchars"] = "eob:\ "
# always show tabline
settings["showtabline"] = 2
# show line count
settings["number"] = True


# show cursor
settings["cursorline"] = True
# constant cursor styling
settings["guicursor"] = ""


@autocmd("InsertEnter", blocking=True)
def hl_cursor(nvim: Nvim) -> None:
    highlight(HLgroup("CursorLine", guibg="#f2d9fa")).commit(nvim)


@autocmd("InsertLeave", blocking=True)
def dehl_cursor(nvim: Nvim) -> None:
    highlight(HLgroup("CursorLine", guibg="#f1f4f6")).commit(nvim)


# highlight yank
@autocmd("TextYankPost", blocking=True)
def hl_yank(nvim: Nvim) -> None:
    nvim.lua.vim.highlight.on_yank({})


# remove welcome message
settings["shortmess"] += "I"
# welcome screen
@autocmd("VimEnter", blocking=True)
def welcome_screen(nvim: Nvim) -> None:
    bufs: Sequence[Buffer] = nvim.api.list_bufs()
    for buf in bufs:
        name = nvim.api.buf_get_name(buf)
        if not name:
            nvim.api.buf_set_option(name, "buftype", "nofile")


# light theme
settings["background"] = "light"
atomic.command("colorscheme edge")
