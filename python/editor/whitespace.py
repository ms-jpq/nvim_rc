from string import whitespace
from typing import Iterator, Sequence, Set, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window

from ..nvim.operators import p_indent
from ..registery import autocmd, rpc, settings

# join only add 1 space
settings["nojoinspaces"] = True

tabsize = 2
# how big are tabs ?
settings["tabstop"] = tabsize
# spaces remove on deletion
settings["softtabstop"] = tabsize
# manual indentation width
settings["shiftwidth"] = tabsize


@rpc(blocking=True)
def _detect_tabsize(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    count: int = nvim.api.buf_line_count(buf)
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, min(count, 100), True)

    def it() -> Tuple[int, int]:
        for tabsize in range(2, 9):
            divibilty = sum(
                p_indent(line, tabsize=tabsize) % tabsize == 0 for line in lines
            )
            yield divibilty, tabsize

    _, tabsize = next(reversed(sorted(it())))
    nvim.options["tabstop"] = tabsize
    nvim.options["softtabstop"] = tabsize
    nvim.options["shiftwidth"] = tabsize


autocmd("FileType") << f"lua {_detect_tabsize.lua_name}()"


# insert spaces instead of tabs
settings["expandtab"] = True
# smart indentation level
settings["autoindent"] = True
settings["smarttab"] = True


def _strip_ending(string: str, nono: Set[str]) -> str:
    def it() -> Iterator[str]:
        before_seen = True
        for c in reversed(string):
            if before_seen and c in nono:
                pass
            else:
                before_seen = False
                yield c

    return "".join(it())


# remove trailing whitespace
# @autocmd("BufWritePre",  modifiers=("*", "undojoin", "|"))
@rpc(blocking=True)
def _trailing_ws(nvim: Nvim) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, col = nvim.api.win_get_cursor(win)
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)

    def it() -> Iterator[str]:
        ws = {*whitespace}
        trimmable = True
        new_line = ""
        for r, line in reversed(tuple(enumerate(lines, 1))):
            trimmable = trimmable and r > row
            if trimmable:
                new_line = _strip_ending(line, nono=ws)
                trimmable = trimmable and not new_line
            if trimmable:
                yield new_line if trimmable else line

    nvim.api.buf_set_lines(buf, 0, -1, True, tuple(it()))
    nvim.api.win_set_cursor(win, (row, col))
