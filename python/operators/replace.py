from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_set_lines,
    cur_buf,
    cur_window,
    str_col_pos,
    win_get_cursor,
)
from pynvim_pp.operators import VisualTypes, operator_marks, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _go_replace(nvim: Nvim, visual: VisualTypes = None) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        (row1, c1), (row2, c2) = operator_marks(nvim, buf=buf, visual_type=visual)
        col1 = str_col_pos(nvim, buf=buf, row=row1, col=c1)
        col2 = str_col_pos(nvim, buf=buf, row=row1, col=c2)

        lines = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)
        head = lines[0][:col1]
        body: str = nvim.funcs.getreg("*")
        tail = lines[-1][col2 + 1 :]

        new_lines = (head + body + tail).splitlines()
        line = new_lines.pop()
        if line:
            new_lines.append(line)

        buf_set_lines(nvim, buf=buf, lo=row1, hi=row2 + 1, lines=new_lines)


keymap.n("gr") << f"<cmd>set opfunc={_go_replace.name}<cr>g@"
keymap.v("gr") << f"<esc><cmd>lua {_go_replace.name}()<cr>"


@rpc(blocking=True)
def _go_replace_line(nvim: Nvim) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        win = cur_window(nvim)
        row, _ = win_get_cursor(nvim, win=win)
        body: str = nvim.funcs.getreg("*")
        new_lines = body.splitlines()

        line = new_lines.pop()
        if line:
            new_lines.append(line)

        buf_set_lines(nvim, buf=buf, lo=row, hi=row + 1, lines=new_lines)


keymap.n("grr") << f"<cmd>lua {_go_replace_line.name}()<cr>"
