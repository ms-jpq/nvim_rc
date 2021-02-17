from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_line_count,
    buf_set_lines,
    cur_buf,
    cur_win,
    win_get_buf,
    win_get_cursor,
    win_set_cursor,
)
from pynvim_pp.operators import operator_marks, set_visual_selection, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _normal_up(nvim: Nvim) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        win = cur_win(nvim)
        row, col = win_get_cursor(nvim, win=win)
        if row <= 0:
            return
        else:
            curr = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
            nxt = buf_get_lines(nvim, buf=buf, lo=row - 1, hi=row)
            new = tuple((*curr, *nxt))
            buf_set_lines(nvim, buf=buf, lo=row - 1, hi=row + 1, lines=new)
            win_set_cursor(nvim, win=win, row=row - 1, col=col)


@rpc(blocking=True)
def _normal_down(nvim: Nvim) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        win = cur_win(nvim)
        row, col = win_get_cursor(nvim, win=win)
        count = buf_line_count(nvim, buf=buf)
        if row >= count - 1:
            return
        else:
            curr = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
            nxt = buf_get_lines(nvim, buf=buf, lo=row + 1, hi=row + 2)
            new = tuple((*nxt, *curr))
            buf_set_lines(nvim, buf=buf, lo=row, hi=row + 2, lines=new)
            win_set_cursor(nvim, win=win, row=row + 1, col=col)


keymap.n("<m-up>") << f"<cmd>lua {_normal_up.name}()<cr>"
keymap.n("<m-down>") << f"<cmd>lua {_normal_down.name}()<cr>"


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


keymap.v("<m-up>") << f"<esc><cmd>lua {_visual_up.name}()<cr>"
keymap.v("<m-down>") << f"<esc><cmd>lua {_visual_down.name}()<cr>"
