from pynvim.api.nvim import Nvim, Window, Buffer
from ..registery import keymap, autocmd
from uuid import uuid4

# # normalize Y
keymap.n("Y") << "y$"

# fix cursor pos moving 1 back
BUF_VAR_NAME = f"buf_cursor_pos_{uuid4().hex}"


@autocmd("InsertEnter", "CursorMovedI", "TextChangedP")
def record_pos(nvim: Nvim) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    _, col = nvim.api.win_get_cursor(win)
    nvim.api.buf_set_var(buf, BUF_VAR_NAME, col)


@autocmd("InsertLeave")
def restore_pos(nvim: Nvim) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, col = nvim.api.win_get_cursor(win)
    pos = nvim.api.buf_get_var(buf, BUF_VAR_NAME)
    if col != pos:
        nvim.api.win_set_cursor(0, (row, pos))
