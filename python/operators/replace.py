from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_linefeed,
    buf_set_lines,
    cur_buf,
    cur_win,
    win_get_buf,
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
        linefeed = buf_linefeed(nvim, buf=buf)
        (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=visual)

        lines = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)
        head = lines[0].encode()[:col1].decode()
        body: str = nvim.funcs.getreg("*")
        tail = lines[-1].encode()[col2 + 1 :].decode()

        new_lines = (head + body + tail).split(linefeed)
        buf_set_lines(nvim, buf=buf, lo=row1, hi=row2 + 1, lines=new_lines)


keymap.n("gr") << f"<cmd>set opfunc={_go_replace.name}<cr>g@"
keymap.v("gr") << rf"<c-\><c-n><cmd>lua {_go_replace.name}()<cr>"


@rpc(blocking=True)
def _go_replace_line(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    if not writable(nvim, buf=buf):
        return
    else:
        linefeed = buf_linefeed(nvim, buf=buf)
        row, _ = win_get_cursor(nvim, win=win)
        body: str = nvim.funcs.getreg("*")
        new_lines = body.split(linefeed)
        buf_set_lines(nvim, buf=buf, lo=row, hi=row + 1, lines=new_lines)


keymap.n("grr") << f"<cmd>lua {_go_replace_line.name}()<cr>"
