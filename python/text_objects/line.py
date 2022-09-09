from typing import Tuple

from pynvim_pp.lib import encode
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.window import Window

from ..registery import NAMESPACE, keymap, rpc


def _p_inside(line: str) -> Tuple[int, int]:
    lhs = len(encode(line)) - len(encode(line.lstrip()))
    rhs = len(encode(line.rstrip()))
    return lhs, rhs


def _p_around(line: str) -> Tuple[int, int]:
    return 0, len(encode(line))


@rpc()
async def _line(is_inside: bool) -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, _ = await win.get_cursor()
    lines = await buf.get_lines(lo=row, hi=row + 1)
    line = next(iter(lines))
    lhs, rhs = (_p_inside if is_inside else _p_around)(line)

    await set_visual_selection(win, mode="v", mark1=(row, lhs), mark2=(row, rhs))


_ = keymap.o("il") << f"<cmd>lua {NAMESPACE}.{_line.name}(true)<cr>"
_ = keymap.o("al") << f"<cmd>lua {NAMESPACE}.{_line.name}(false)<cr>"
_ = keymap.v("il") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_line.name}(true)<cr>"
_ = keymap.v("al") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_line.name}(false)<cr>"
