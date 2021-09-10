from itertools import chain
from typing import Iterator

from pynvim.api import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_set_lines,
    cur_win,
    win_get_buf,
    win_get_cursor,
    win_set_cursor,
)
from pynvim_pp.lib import decode, encode
from pynvim_pp.operators import writable

from ..registery import keymap, rpc

_PAIRS = {"-": "_"}


def _swap_case(chars: str) -> str:
    pairs = {
        k: v for k, v in chain(_PAIRS.items(), ((v, k) for k, v in _PAIRS.items()))
    }

    def cont() -> Iterator[str]:
        for char in chars:
            if char in pairs:
                yield pairs[char]
            else:
                yield char.swapcase()

    return "".join(cont())


@rpc(blocking=True)
def _toggle_case(nvim: Nvim) -> None:
    win = cur_win(nvim)
    row, col = win_get_cursor(nvim, win=win)
    buf = win_get_buf(nvim, win=win)
    if writable(nvim, buf=buf):
        line, *_ = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
        bline = encode(line)
        before, after = bline[:col], bline[col:]
        if after:
            cur, *post = after
            pt = decode(bytes((cur,)))
            swapped = _swap_case(pt)
            new = decode(before) + swapped + decode(bytes(post))
            pos = len(before) + len(encode(swapped))
            buf_set_lines(nvim, buf=buf, lo=row, hi=row + 1, lines=(new,))
            win_set_cursor(nvim, win=win, row=row, col=pos)


keymap.n("~") << f"<cmd>lua {_toggle_case.name}()<cr>"
