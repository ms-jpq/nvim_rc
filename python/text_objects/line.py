from typing import Iterable, Tuple
from ..registery import keymap, rpc
from string import whitespace

from pynvim import Nvim
from pynvim.api import Buffer, Window


def _p_inside(line: str) -> Tuple[int, int]:
    ws = {*whitespace}
    chars = tuple(enumerate(line, start=1))

    def p(it: Iterable[Tuple[int, str]], default: int) -> int:
        for idx, char in it:
            if char in ws:
                pass
            else:
                return idx
        else:
            return default

    return p(chars, 0), p(reversed(chars), len(chars))


def _p_around(line: str) -> Tuple[int, int]:
    return 1, len(line)


@rpc(blocking=True)
def _line(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, _ = nvim.api.win_get_cursor(win)
    line: str = nvim.api.get_current_line()
    lhs, rhs = (_p_inside if is_inside else _p_around)(line)

    nvim.funcs.setpos("'<", (buf.number, row, lhs, 0))
    nvim.funcs.setpos("'>", (buf.number, row, rhs, 0))
    nvim.command("norm! `<V`>")


keymap.o("il") << "<cmd>" + _line.call_line("true") + "<cr>"
keymap.o("al") << "<cmd>" + _line.call_line("false") + "<cr>"
keymap.v("il") << "<esc><cmd>" + _line.call_line("true") + "<cr>"
keymap.v("al") << "<esc><cmd>" + _line.call_line("false") + "<cr>"
