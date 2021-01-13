from typing import Tuple

from pynvim import Nvim
from pynvim_pp.api import buf_get_lines, cur_window, win_get_buf, win_get_cursor
from pynvim_pp.operators import set_visual_selection

from ..registery import keymap, rpc


def _p_inside(line: str) -> Tuple[int, int]:
    encoded = line.encode()
    lhs = len(encoded) - len(encoded.lstrip())
    rhs = len(encoded.rstrip()) - 1
    return lhs, rhs


def _p_around(line: str) -> Tuple[int, int]:
    return 0, len(line.encode()) - 1


@rpc(blocking=True)
def _line(nvim: Nvim, is_inside: bool) -> None:
    win = cur_window(nvim)
    buf = win_get_buf(nvim, win=win)
    row, _ = win_get_cursor(nvim, win=win)
    lines = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
    line = next(iter(lines))
    lhs, rhs = (_p_inside if is_inside else _p_around)(line)

    set_visual_selection(nvim, buf=buf, mark1=(row, lhs), mark2=(row, rhs))
    nvim.command("norm! `<v`>")


keymap.o("il") << f"<cmd>lua {_line.name}(true)<cr>"
keymap.o("al") << f"<cmd>lua {_line.name}(false)<cr>"
keymap.v("il") << f"<esc><cmd>lua {_line.name}(true)<cr>"
keymap.v("al") << f"<esc><cmd>lua {_line.name}(false)<cr>"
