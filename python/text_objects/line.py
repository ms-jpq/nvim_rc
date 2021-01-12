from typing import Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim_pp.operators import set_visual_selection

from ..registery import keymap, rpc


def _p_inside(line: str) -> Tuple[int, int]:
    lhs = len(line) - len(line.lstrip())
    rhs = len(line.rstrip()) - 1
    return lhs, rhs


def _p_around(line: str) -> Tuple[int, int]:
    return 0, len(line)


@rpc(blocking=True)
def _line(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, _ = nvim.api.win_get_cursor(win)
    line: str = nvim.api.get_current_line()
    lhs, rhs = (_p_inside if is_inside else _p_around)(line)

    set_visual_selection(nvim, buf=buf, mark1=(row, lhs), mark2=(row, rhs))
    nvim.command("norm! `<v`>")


keymap.o("il") << f"<cmd>lua {_line.name}(true)<cr>"
keymap.o("al") << f"<cmd>lua {_line.name}(false)<cr>"
keymap.v("il") << f"<esc><cmd>lua {_line.name}(true)<cr>"
keymap.v("al") << f"<esc><cmd>lua {_line.name}(false)<cr>"
