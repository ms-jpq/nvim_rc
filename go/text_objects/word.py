from pynvim_pp.lib import decode, encode
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.text_object import gen_split
from pynvim_pp.window import Window

from ..registry import NAMESPACE, keymap, rpc

UNIFIYING_CHARS = frozenset(("_", "-"))


@rpc()
async def _word(is_inside: bool) -> None:
    win = await Window.get_current()
    buf = await win.get_buf()

    row, col = await win.get_cursor()
    line, *_ = await buf.get_lines(lo=row, hi=row + 1)

    bline = encode(line)
    lhs, rhs = decode(bline[:col]), decode(bline[col:])
    ctx = gen_split(UNIFIYING_CHARS, lhs=lhs, rhs=rhs)

    if not (ctx.word_lhs + ctx.word_rhs):
        words_lhs, words_rhs = ctx.syms_lhs, ctx.syms_rhs
    else:
        words_lhs, words_rhs = ctx.word_lhs, ctx.word_rhs

    c_lhs = max(col - len(encode(words_lhs)), 0)
    c_rhs = col + len(encode(words_rhs))

    if is_inside:
        mark1 = (row, c_lhs)
        mark2 = (row, c_rhs)
    else:
        mark1 = (row, max(0, c_lhs - 1))
        mark2 = (row, min(len(bline), c_rhs + 1))

    await set_visual_selection(win, mode="v", mark1=mark1, mark2=mark2)


_ = keymap.o("iw") << f"<cmd>lua {NAMESPACE}.{_word.method}(true)<cr>"
_ = keymap.o("aw") << f"<cmd>lua {NAMESPACE}.{_word.method}(false)<cr>"
_ = keymap.v("iw") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_word.method}(true)<cr>"
_ = keymap.v("aw") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_word.method}(false)<cr>"
