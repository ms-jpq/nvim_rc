from typing import Sequence

from pynvim.api.nvim import Buffer, Nvim
from pynvim_pp.highlight import HLgroup, highlight

from ..registery import autocmd, rpc, settings

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


@rpc(blocking=True)
def _hl_cursor(nvim: Nvim) -> None:
    highlight(HLgroup("CursorLine", guibg="#f2d9fa")).commit(nvim)


@rpc(blocking=True)
def _dehl_cursor(nvim: Nvim) -> None:
    highlight(HLgroup("CursorLine", guibg="#f1f4f6")).commit(nvim)


autocmd("InsertEnter") << f"lua {_hl_cursor.remote_name}()"
autocmd("InsertLeave") << f"lua {_dehl_cursor.remote_name}()"


# highlight yank
@rpc(blocking=True)
def _hl_yank(nvim: Nvim) -> None:
    nvim.lua.vim.highlight.on_yank({})


autocmd("TextYankPost") << f"lua {_hl_yank.remote_name}()"


# remove welcome message
settings["shortmess"] += "I"
# welcome screen
@rpc(blocking=True)
def _welcome_screen(nvim: Nvim) -> None:
    bufs: Sequence[Buffer] = nvim.api.list_bufs()
    for buf in bufs:
        name = nvim.api.buf_get_name(buf)
        if not name:
            nvim.api.buf_set_option(name, "buftype", "nofile")


autocmd("VimEnter") << f"lua {_welcome_screen.remote_name}()"
