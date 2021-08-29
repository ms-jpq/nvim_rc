from typing import Iterable

from pynvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_get_option,
    cur_win,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.operators import p_indent, set_visual_selection

from ..registery import keymap, rpc


def _p_inside(init_lv: int, tabsize: int, lines: Iterable[str]) -> int:
    n = 0
    for n, line in enumerate(lines):
        lv = p_indent(line, tabsize=tabsize)
        if line and lv < init_lv:
            return n
    else:
        return n + 1 if n else 0


@rpc(blocking=True)
def _indent(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win)
    row, _ = win_get_cursor(nvim, win)
    tabsize: int = buf_get_option(nvim, buf=buf, key="tabstop")

    lines = buf_get_lines(nvim, buf=buf, lo=0, hi=-1)
    before, curr, after = lines[:row], lines[row], lines[row + 1 :]
    init_lv = p_indent(curr, tabsize=tabsize)

    top = row - _p_inside(init_lv, tabsize=tabsize, lines=reversed(before))
    btm = row + _p_inside(init_lv, tabsize=tabsize, lines=after)

    set_visual_selection(nvim, win=win, mode="V", mark1=(top, 0), mark2=(btm, 0))


keymap.o("ii") << f"<cmd>lua {_indent.name}()<cr>"
keymap.v("ii") << rf"<c-\><c-n><cmd>lua {_indent.name}()<cr>"
