from pynvim import Nvim
from pynvim_pp.api import buf_get_lines, cur_win, win_get_buf, win_get_cursor
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.text_object import gen_split

from ..registery import keymap, rpc

UNIFIYING_CHARS = frozenset(("_", "-"))


@rpc(blocking=True)
def _word(nvim: Nvim, is_inside: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    row, c = win_get_cursor(nvim, win=win)
    lines = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
    line = next(iter(lines))
    bline = line.encode()

    # position under cursor
    c = min(len(bline) - 1, c)
    col = len(bline[:c].decode()) + 1
    lhs, rhs = line[:col], line[col:]
    # undo col + 1
    offset = len(next(reversed(lhs), "").encode())

    ctx = gen_split(lhs, rhs, unifying_chars=UNIFIYING_CHARS)
    if not (ctx.word_lhs + ctx.word_rhs):
        words_lhs, words_rhs = ctx.syms_lhs, ctx.syms_rhs
    else:
        words_lhs, words_rhs = ctx.word_lhs, ctx.word_rhs

    c_lhs = c + offset - len(words_lhs.encode())
    c_rhs = c + offset + len(words_rhs.encode()) - 1

    if is_inside:
        mark1 = (row, c_lhs)
        mark2 = (row, c_rhs)
    else:
        mark1 = (row, c_lhs - 1)
        mark2 = (row, c_rhs + 1)

    set_visual_selection(nvim, win=win, mode="v", mark1=mark1, mark2=mark2)


keymap.o("iw") << f"<cmd>lua {_word.name}(true)<cr>"
keymap.o("aw") << f"<cmd>lua {_word.name}(false)<cr>"
keymap.v("iw") << f"<esc><cmd>lua {_word.name}(true)<cr>"
keymap.v("aw") << f"<esc><cmd>lua {_word.name}(false)<cr>"
