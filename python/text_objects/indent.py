from typing import Iterable, Optional, Sequence

from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim_pp.lib import write
from pynvim_pp.operators import p_indent, set_visual_selection

from ..registery import keymap, rpc


def _p_inside(init_lv: int, tabsize: int, lines: Iterable[str]) -> int:
    for n, line in enumerate(lines):
        lv = p_indent(line, tabsize=tabsize)
        if line and lv < init_lv:
            return n
    else:
        return 0


def _p_around(init_lv: int, tabsize: int, lines: Iterable[str]) -> int:
    pass


@rpc(blocking=True)
def _indent(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, _ = nvim.api.win_get_cursor(win)
    tabsize: int = nvim.api.buf_get_option(buf, "tabstop")

    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)
    before, curr, after = lines[: row - 1], lines[row - 1], lines[row:]
    init_lv = p_indent(curr, tabsize=tabsize)

    if is_inside:
        top = row - _p_inside(init_lv, tabsize=tabsize, lines=reversed(before))
        btm = row + _p_inside(init_lv, tabsize=tabsize, lines=after)
    else:
        top = row - _p_around(init_lv, tabsize=tabsize, lines=reversed(before))
        btm = row + _p_around(init_lv, tabsize=tabsize, lines=after)

    write(nvim, top, btm)

    set_visual_selection(nvim, buf=buf, mark1=(top, 1), mark2=(btm, 1))
    nvim.command("norm! `<V`>")


keymap.o("ii") << f"<cmd>lua {_indent.name}(true)<cr>"
keymap.o("ai") << f"<cmd>lua {_indent.name}(false)<cr>"
keymap.v("ii") << f"<esc><cmd>lua {_indent.name}(true)<cr>"
keymap.v("ai") << f"<esc><cmd>lua {_indent.name}(false)<cr>"
