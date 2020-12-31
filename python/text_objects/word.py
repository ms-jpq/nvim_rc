from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.text_object import gen_lhs_rhs

from ..registery import keymap, rpc

UNIFIYING_CHARS = {"_", "-"}


@rpc(blocking=True)
def _word(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, col = nvim.api.win_get_cursor(win)
    line: str = nvim.api.get_current_line()

    # position under cursor
    col = col + 1
    (words_lhs, words_rhs), (sym_lhs, sym_rhs) = gen_lhs_rhs(
        line, col=col, unifying_chars=UNIFIYING_CHARS
    )
    if not (words_lhs + words_rhs):
        words_lhs, words_rhs = sym_lhs, sym_rhs
    lhs, rhs = col - len(words_lhs), col + len(words_rhs) - 1

    if is_inside:
        mark1 = (row, lhs)
        mark2 = (row, rhs)
    else:
        mark1 = (row, lhs - 1)
        mark2 = (row, rhs + 1)

    set_visual_selection(nvim, buf=buf, mark1=mark1, mark2=mark2)
    nvim.command("norm! `<v`>")


keymap.o("iw") << f"<cmd>lua {_word.remote_name}(true)<cr>"
keymap.o("aw") << f"<cmd>lua {_word.remote_name}(false)<cr>"
keymap.v("iw") << f"<esc><cmd>lua {_word.remote_name}(true)<cr>"
keymap.v("aw") << f"<esc><cmd>lua {_word.remote_name}(false)<cr>"
