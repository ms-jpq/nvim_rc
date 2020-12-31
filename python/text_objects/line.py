from string import whitespace
from typing import Iterable, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window

from ..registery import keymap, rpc


def _p_inside(line: str) -> Tuple[int, int]:
    ws = {*whitespace}
    chars = tuple(enumerate(line, start=1))

    def p(it: Iterable[Tuple[int, str]]) -> int:
        for idx, char in it:
            if char in ws:
                pass
            else:
                return idx
        else:
            return 0

    return p(chars), p(reversed(chars))


def _p_around(line: str) -> Tuple[int, int]:
    return 1 if line else 0, len(line)


@rpc(blocking=True)
def _line(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, _ = nvim.api.win_get_cursor(win)
    line: str = nvim.api.get_current_line()
    lhs, rhs = (_p_inside if is_inside else _p_around)(line)

    nvim.funcs.setpos("'<", (buf.number, row, lhs, 0))
    nvim.funcs.setpos("'>", (buf.number, row, rhs, 0))
    nvim.command("norm! `<v`>")


keymap.o("il") << f"<cmd>lua {_line.remote_name}(true)<cr>"
keymap.o("al") << f"<cmd>lua {_line.remote_name}(false)<cr>"
keymap.v("il") << f"<esc><cmd>lua {_line.remote_name}(true)<cr>"
keymap.v("al") << f"<esc><cmd>lua {_line.remote_name}(false)<cr>"
