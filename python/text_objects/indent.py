from typing import Iterable

from pynvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_get_option,
    cur_window,
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


def _p_around(init_lv: int, tabsize: int, lines: Iterable[str]) -> int:
    pass


@rpc(blocking=True)
def _indent(nvim: Nvim, is_inside: bool) -> None:
    win = cur_window(nvim)
    buf = win_get_buf(nvim, win)
    row, _ = win_get_cursor(nvim, win)
    tabsize: int = buf_get_option(nvim, buf=buf, key="tabstop")

    lines = buf_get_lines(nvim, buf=buf, lo=0, hi=-1)
    before, curr, after = lines[:row], lines[row], lines[row + 1 :]
    init_lv = p_indent(curr, tabsize=tabsize)

    if is_inside:
        top = row - _p_inside(init_lv, tabsize=tabsize, lines=reversed(before))
        btm = row + _p_inside(init_lv, tabsize=tabsize, lines=after)
    else:
        top = row - _p_around(init_lv, tabsize=tabsize, lines=reversed(before))
        btm = row + _p_around(init_lv, tabsize=tabsize, lines=after)

    set_visual_selection(nvim, buf=buf, mark1=(top, 0), mark2=(btm, 0))
    nvim.command("norm! `<V`>")


keymap.o("ii") << f"<cmd>lua {_indent.name}(true)<cr>"
keymap.o("ai") << f"<cmd>lua {_indent.name}(false)<cr>"
keymap.v("ii") << f"<esc><cmd>lua {_indent.name}(true)<cr>"
keymap.v("ai") << f"<esc><cmd>lua {_indent.name}(false)<cr>"
