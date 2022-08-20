from itertools import count
from math import inf
from os import linesep
from uuid import uuid4

from pynvim import Nvim
from pynvim_pp.api import (
    ExtMark,
    buf_get_extmarks,
    buf_get_lines,
    buf_set_extmarks,
    clear_ns,
    create_ns,
    cur_buf,
    cur_win,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.operators import operator_marks

from ..registery import NAMESPACE, keymap, rpc

_NS = uuid4()
_LS = "LINE BREAK"


@rpc(blocking=True)
def _marks_clear(nvim: Nvim, visual: bool) -> None:
    ns = create_ns(nvim, ns=_NS)
    buf = cur_buf(nvim)
    if visual:
        (lo, _), (hi, _) = operator_marks(nvim, buf=buf, visual_type=None)
        clear_ns(nvim, id=ns, buf=buf, lo=lo, hi=hi)
    else:
        clear_ns(nvim, id=ns, buf=buf)


_ = keymap.n("<leader>E") << f"<cmd>lua {NAMESPACE}.{_marks_clear.name}(false)<cr>"
_ = (
    keymap.v("<leader>E")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_marks_clear.name}(true)<cr>"
)


@rpc(blocking=True)
def _mark_set(nvim: Nvim) -> None:
    ns = create_ns(nvim, ns=_NS)
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    row, _ = win_get_cursor(nvim, win=win)

    marks = tuple(buf_get_extmarks(nvim, id=ns, buf=buf))
    for mark in marks:
        r, _ = mark.begin
        if r == row:
            break
    else:
        indices = {mark.idx for mark in marks}
        idx = next(i for i in count(1) if i not in indices)

        mark = ExtMark(
            idx=idx,
            begin=(row, 0),
            end=(row, 0),
            meta={"virt_lines": (((_LS, "NormalFloat"),),)},
        )
        buf_set_extmarks(nvim, buf=buf, id=ns, marks=(mark,))


_ = keymap.n("<leader>e") << f"<cmd>lua {NAMESPACE}.{_mark_set.name}()<cr>"


@rpc(blocking=True)
def _eval(nvim: Nvim, visual: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    if visual:
        (begin, _), (end, _) = operator_marks(nvim, buf=buf, visual_type=None)
    else:
        ns = create_ns(nvim, ns=_NS)
        row, _ = win_get_cursor(nvim, win=win)
        marks = tuple(buf_get_extmarks(nvim, id=ns, buf=buf))
        begin, end = 0, None
        for mark in marks:
            r, _ = mark.begin
            if r < row:
                begin = max(begin, r)
            else:
                end = min(end or inf, r)

    lines = buf_get_lines(nvim, buf=buf, lo=begin, hi=int(end or -2) + 1)
    text = linesep.join(lines)


_ = keymap.n("<leader>g") << f"<cmd>lua {NAMESPACE}.{_eval.name}(false)<cr>"
_ = keymap.v("<leader>g") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_eval.name}(true)<cr>"
