from typing import Optional, cast
from uuid import uuid4

from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_var,
    buf_set_var,
    cur_win,
    win_get_buf,
    win_get_cursor,
    win_set_cursor,
)

from ..registery import NAMESPACE, autocmd, keymap, rpc

# fix cursor pos moving 1 back
_BUF_VAR_NAME = f"buf_cursor_pos_{uuid4().hex}"


@rpc(blocking=True)
def _record_pos(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    _, col = win_get_cursor(nvim, win=win)
    buf_set_var(nvim, buf=buf, key=_BUF_VAR_NAME, val=col)


(
    autocmd("InsertEnter", "CursorMovedI", "TextChangedP")
    << f"lua {NAMESPACE}.{_record_pos.name}()"
)


@rpc(blocking=True)
def _restore_pos(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    row, _ = win_get_cursor(nvim, win=win)
    pos = cast(Optional[int], buf_get_var(nvim, buf=buf, key=_BUF_VAR_NAME))

    if pos is not None:
        win_set_cursor(nvim, win=win, row=row, col=pos)


autocmd("InsertLeave") << f"lua {NAMESPACE}.{_restore_pos.name}()"
