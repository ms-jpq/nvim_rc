from typing import Tuple, Set

from pynvim import Nvim
from pynvim.api import Buffer, Window
from ..nvim.operators import set_visual_selection
from ..registery import keymap, rpc


UNIFIYING_CHARS = {"_", "-"}


def _is_word(c: str, unifying_chars: Set[str]) -> bool:
    return c.isalnum() or c in unifying_chars


def _gen_lhs_rhs(
    line: str, col: int, unifying_chars: Set[str]
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    enumd = tuple(enumerate(line))
    before, after = reversed(enumd[:col]), iter(enumd[col:])
    (word_lhs, word_rhs), (sym_lhs, sym_rhs) = (-1, -1), (-1, -1)

    encountered_sym = False
    for idx, char in before:
        is_w = _is_word(char, unifying_chars=unifying_chars)
        if encountered_sym:
            if is_w:
                break
            else:
                sym_lhs = idx
        else:
            if is_w:
                word_lhs = idx
            else:
                sym_lhs = idx
                encountered_sym = True

    encountered_sym = False
    for idx, char in after:
        is_w = _is_word(char, unifying_chars=unifying_chars)
        if encountered_sym:
            if is_w:
                break
            else:
                sym_rhs = idx
        else:
            if is_w:
                word_rhs = idx
            else:
                sym_rhs = idx
                encountered_sym = True

    return (word_lhs, word_rhs), (sym_lhs, sym_rhs)


@rpc(blocking=True)
def _word(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, col = nvim.api.win_get_cursor(win)
    line: str = nvim.api.get_current_line()

    # apperant position
    col = col + 1
    (word_lhs, word_rhs), (sym_lhs, sym_rhs) = _gen_lhs_rhs(
        line, col=col, unifying_chars=UNIFIYING_CHARS
    )

    if is_inside:
        mark1 = (row, word_lhs)
        mark2 = (row, word_rhs)
    else:
        mark1 = (row, sym_lhs)
        mark2 = (row, sym_rhs)

    set_visual_selection(nvim, buf=buf, mark1=mark1, mark2=mark2)
    nvim.command("norm! `<v`>")


keymap.o("iw") << f"<cmd>lua {_word.remote_name}(true)<cr>"
keymap.o("aw") << f"<cmd>lua {_word.remote_name}(false)<cr>"
keymap.v("iw") << f"<esc><cmd>lua {_word.remote_name}(true)<cr>"
keymap.v("aw") << f"<esc><cmd>lua {_word.remote_name}(false)<cr>"
