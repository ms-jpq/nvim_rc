from collections import deque
from collections.abc import Sequence

from pynvim_pp.lib import encode
from pynvim_pp.operators import p_indent, set_visual_selection
from pynvim_pp.window import Window

from ..registry import NAMESPACE, keymap, rpc


def _p_inside(init_lv: int, tabsize: int, lines: Sequence[str]) -> int:
    n = 0
    for n, line in enumerate(lines, start=1):
        lv = p_indent(line, tabsize=tabsize)
        if line and lv < init_lv:
            return n - 1
    else:
        return n


@rpc()
async def _indent() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, _ = await win.get_cursor()

    tabsize = await buf.opts.get(int, "tabstop")

    lines = await buf.get_lines(lo=0, hi=-1)
    before, curr, after = lines[:row], lines[row], lines[row + 1 :]
    init_lv = p_indent(curr, tabsize=tabsize)

    top = row - _p_inside(init_lv, tabsize=tabsize, lines=tuple(reversed(before)))
    btm = min(len(lines) - 1, row + _p_inside(init_lv, tabsize=tabsize, lines=after))

    lines = deque(await buf.get_lines(lo=top, hi=btm + 1))
    while lines:
        if line := lines.popleft():
            lines.appendleft(line)
            break
        else:
            top += 1

    while lines:
        if line := lines.pop():
            lines.append(line)
            break
        else:
            btm -= 1

    if lines:
        *_, btm_line = lines
        mark1, mark2 = (top, 0), (btm, len(encode(btm_line)))
    else:
        mark1, mark2 = (row, 0), (row, len(encode(curr)))

    await set_visual_selection(win, mode="V", mark1=mark1, mark2=mark2)


_ = keymap.o("ii") << f"<cmd>lua {NAMESPACE}.{_indent.method}()<cr>"
_ = keymap.v("ii") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_indent.method}()<cr>"
