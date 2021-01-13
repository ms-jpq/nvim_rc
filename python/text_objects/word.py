from pynvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    cur_window,
    str_col_pos,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.text_object import gen_split

from ..registery import keymap, rpc

UNIFIYING_CHARS = frozenset(("_", "-"))


@rpc(blocking=True)
def _word(nvim: Nvim, is_inside: bool) -> None:
    win = cur_window(nvim)
    buf = win_get_buf(nvim, win=win)

    row, c = win_get_cursor(nvim, win=win)
    lines = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
    line = next(iter(lines))

    col = str_col_pos(nvim, buf=buf, row=row, col=c)
    # position under cursor
    col = col + 1
    lhs, rhs = line[:col], line[col:]
    # undo col + 1
    offset = len(next(reversed(lhs), "").encode())

    ctx = gen_split(lhs, rhs, unifying_chars=UNIFIYING_CHARS)
    if not (ctx.word_lhs + ctx.word_rhs):
        words_lhs, words_rhs = ctx.syms_lhs, ctx.syms_rhs
    else:
        words_lhs, words_rhs = ctx.word_lhs, ctx.word_rhs

    lhs = c + offset - len(words_lhs.encode())
    rhs = c + offset + len(words_rhs.encode()) - 1

    if is_inside:
        mark1 = (row, lhs)
        mark2 = (row, rhs)
    else:
        mark1 = (row, lhs - 1)
        mark2 = (row, rhs + 1)

    set_visual_selection(nvim, buf=buf, mark1=mark1, mark2=mark2)
    nvim.command("norm! `<v`>")


keymap.o("iw") << f"<cmd>lua {_word.name}(true)<cr>"
keymap.o("aw") << f"<cmd>lua {_word.name}(false)<cr>"
keymap.v("iw") << f"<esc><cmd>lua {_word.name}(true)<cr>"
keymap.v("aw") << f"<esc><cmd>lua {_word.name}(false)<cr>"
