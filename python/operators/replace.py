from typing import Tuple

from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_linefeed,
    buf_set_lines,
    buf_set_text,
    cur_buf,
    cur_win,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.operators import VisualTypes, operator_marks, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _go_replace(nvim: Nvim, args: Tuple[Tuple[VisualTypes]]) -> None:
    (visual,), *_ = args
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        linefeed = buf_linefeed(nvim, buf=buf)
        (r1, c1), (r2, c2) = operator_marks(nvim, buf=buf, visual_type=visual)
        line, *_ = buf_get_Lines(nvim, buf=buf, lo=r1, hi=r2 + 1)
        begin, end = (r1, c1), (r2, min(len(line.encode("UTF-8")), c2 + 1))
        text: str = nvim.funcs.getreg("*")
        buf_set_text(nvim, buf=buf, begin=begin, end=end, text=text.split(linefeed))


keymap.n("gr") << f"<cmd>set opfunc={_go_replace.name}<cr>g@"
keymap.v("gr") << rf"<c-\><c-n><cmd>lua {_go_replace.name}{{{{vim.NIL}}}}<cr>"


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
