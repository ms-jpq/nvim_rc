from pynvim.api.nvim import Nvim
from pynvim_pp.api import (
    buf_get_lines,
    cur_window,
    win_get_buf,
    win_get_cursor,
    win_set_cursor,
)
from pynvim_pp.lib import async_call, go

from ..registery import autocmd, rpc

_CHAR_PAIRS = {'"': '"', "'": "'", "`": "`", "(": ")", "{": "}", "<": ">"}


@rpc(blocking=True)
def _surround(nvim: Nvim) -> None:
    char: str = nvim.vvars["char"]
    match = _CHAR_PAIRS.get(char)

    if match:
        win = cur_window(nvim)
        buf = win_get_buf(nvim, win=win)
        row, col = win_get_cursor(nvim, win=win)
        lines = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
        line = next(iter(lines))

        def cont() -> None:
            new_col = col + len(char.encode())
            nvim.api.set_vvar("char", char + match)
            set_cur = lambda: win_set_cursor(nvim, win=win, row=row, col=new_col)
            go(async_call(nvim, set_cur))

        if match == char:
            odd_one_out = line.count(char) % 2 != 0
            if odd_one_out:
                cont()
        else:
            rhs = line.encode()[col:].decode()
            count = 0
            for ch in rhs:
                if ch == char:
                    count += 1
                elif ch == match:
                    count -= 1
            if count < 0:
                cont()


autocmd("InsertCharPre") << f"lua {_surround.name}()"
