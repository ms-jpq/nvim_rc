from typing import Sequence

from pynvim.api import Buffer, Window
from pynvim.api.nvim import Nvim
from pynvim_pp.grapheme import break_into, join
from pynvim_pp.operators import VisualTypes, operator_marks, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _go_replace(nvim: Nvim, visual: VisualTypes = None) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not writable(nvim, buf=buf):
        return
    else:
        (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=visual)
        row1, row2 = row1 - 1, row2 - 1

        lines: Sequence[str] = nvim.api.buf_get_lines(buf, row1, row2 + 1, True)
        head = join(tuple(break_into(lines[0]))[:col1])
        body: str = nvim.funcs.getreg("*")
        tail = join(tuple(break_into(lines[-1]))[col2 + 1 :])

        new_lines = (head + body + tail).splitlines()
        line = new_lines.pop()
        if line:
            new_lines.append(line)

        nvim.api.buf_set_lines(buf, row1, row2 + 1, True, new_lines)


keymap.n("gr") << f"<cmd>set opfunc={_go_replace.name}<cr>g@"
keymap.v("gr") << f"<esc><cmd>lua {_go_replace.name}()<cr>"


@rpc(blocking=True)
def _go_replace_line(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not writable(nvim, buf=buf):
        return
    else:
        win: Window = nvim.api.get_current_win()
        row, _ = nvim.api.win_get_cursor(win)
        row = row - 1
        body: str = nvim.funcs.getreg("*")
        new_lines = body.splitlines()
        line = new_lines.pop()
        if line:
            new_lines.append(line)
        nvim.api.buf_set_lines(buf, row, row + 1, True, new_lines)


keymap.n("grr") << f"<cmd>lua {_go_replace_line.name}()<cr>"
