from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_line_count,
    buf_set_lines,
    cur_win,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.operators import operator_marks, set_visual_selection, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _norm_mv(nvim: Nvim, up: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    if not writable(nvim, buf=buf):
        return
    else:
        row, _ = win_get_cursor(nvim, win=win)
        lines = buf_line_count(nvim, buf=buf)
        if up:
            nvim.command(f"{row},{row}move{row+1}")
            nvim.command("norm! k")
        else:
            if row < lines - 1:
                nvim.command(f"{row+1},{row+1}move{row+2}")


keymap.n("<m-up>") << f"<cmd>lua {_norm_mv.name}(true)<cr>"
keymap.n("<m-down>") << f"<cmd>lua {_norm_mv.name}(false)<cr>"


def _reselect_visual(nvim: Nvim) -> None:
    nvim.command("norm! gv")


@rpc(blocking=True)
def _visual_up(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    if not writable(nvim, buf=buf):
        return
    else:
        (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=None)
        if row1 <= 0:
            _reselect_visual(nvim)
        else:
            curr = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)
            nxt = buf_get_lines(nvim, buf=buf, lo=row1 - 1, hi=row1)
            new = tuple((*curr, *nxt))
            buf_set_lines(nvim, buf=buf, lo=row1 - 1, hi=row2 + 1, lines=new)
            set_visual_selection(
                nvim, win=win, mode="v", mark1=(row1 - 1, col1), mark2=(row2 - 1, col2)
            )


@rpc(blocking=True)
def _visual_down(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    if not writable(nvim, buf=buf):
        return
    else:
        (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=None)
        count = buf_line_count(nvim, buf=buf)
        if row2 >= count - 1:
            _reselect_visual(nvim)
        else:
            curr = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)
            nxt = buf_get_lines(nvim, buf=buf, lo=row2 + 1, hi=row2 + 2)
            new = tuple((*nxt, *curr))
            buf_set_lines(nvim, buf=buf, lo=row1, hi=row2 + 2, lines=new)
            set_visual_selection(
                nvim, win=win, mode="v", mark1=(row1 + 1, col1), mark2=(row2 + 1, col2)
            )


keymap.v("<m-up>") << rf"<c-\><c-n><cmd>lua {_visual_up.name}()<cr>"
keymap.v("<m-down>") << rf"<c-\><c-n><cmd>lua {_visual_down.name}()<cr>"
