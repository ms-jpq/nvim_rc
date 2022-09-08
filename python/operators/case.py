from itertools import chain
from typing import Iterator

from pynvim_pp.lib import decode, encode
from pynvim_pp.window import Window

from ..registery import NAMESPACE, keymap, rpc

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
async def _toggle_case() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, col = await win.get_cursor()

    if await buf.modifiable():
        line, *_ = await buf.get_lines(lo=row, hi=row + 1)
        bline = encode(line)
        before, after = bline[:col], bline[col:]
        if after:
            cur, *post = after
            pt = decode(bytes((cur,)))
            swapped = _swap_case(pt)
            new = decode(before) + swapped + decode(bytes(post))
            pos = len(before) + len(encode(swapped))
            await buf.set_lines(lo=row, hi=row + 1, lines=(new,))
            await win.set_cursor(row=row, col=pos)


_ = keymap.n("~") << f"<cmd>lua {NAMESPACE}.{_toggle_case.name}()<cr>"
