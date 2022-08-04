from pynvim import Nvim
from pynvim_pp.api import buf_get_lines, cur_win, win_get_buf, win_get_cursor
from pynvim_pp.lib import decode, encode
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.text_object import gen_split

from ..registery import NAMESPACE, keymap, rpc

UNIFIYING_CHARS = frozenset(("_", "-"))


@rpc(blocking=True)
def _word(nvim: Nvim, is_inside: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    row, col = win_get_cursor(nvim, win=win)
    line, *_ = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)

    bline = encode(line)
    lhs, rhs = decode(bline[:col]), decode(bline[col:])
    ctx = gen_split(lhs, rhs, unifying_chars=UNIFIYING_CHARS)

    if not (ctx.word_lhs + ctx.word_rhs):
        words_lhs, words_rhs = ctx.syms_lhs, ctx.syms_rhs
    else:
        words_lhs, words_rhs = ctx.word_lhs, ctx.word_rhs

    c_lhs = max(col - len(encode(words_lhs)), 0)
    c_rhs = max(col + len(encode(words_rhs)) - 2, 0)

    if is_inside:
        mark1 = (row, c_lhs)
        mark2 = (row, c_rhs)
    else:
        mark1 = (row, max(0, c_lhs - 1))
        mark2 = (row, min(len(bline), c_rhs + 1))

    set_visual_selection(nvim, win=win, mode="v", mark1=mark1, mark2=mark2)


_ = keymap.o("iw") << f"<cmd>lua {NAMESPACE}.{_word.name}(true)<cr>"
_ = keymap.o("aw") << f"<cmd>lua {NAMESPACE}.{_word.name}(false)<cr>"
_ = keymap.v("iw") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_word.name}(true)<cr>"
_ = keymap.v("aw") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_word.name}(false)<cr>"
