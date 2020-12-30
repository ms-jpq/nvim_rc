from string import whitespace
from typing import Iterator, Sequence, Set, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window

from ..nvim.operators import p_indent
from ..nvim.settings import Settings
from ..registery import autocmd, rpc, settings

# join only add 1 space
settings["nojoinspaces"] = True

tabsize_d = 2
# how big are tabs ?
settings["tabstop"] = tabsize_d
# spaces remove on deletion
settings["softtabstop"] = tabsize_d
# manual indentation width
settings["shiftwidth"] = tabsize_d


@rpc(blocking=True)
def _detect_tabsize(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    count: int = nvim.api.buf_line_count(buf)
    rows = min(count, 100)
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, rows, True)

    def it() -> Iterator[Tuple[int, int]]:
        for tabsize in range(2, 9):
            indent_lvs = tuple(p_indent(line, tabsize=tabsize) for line in lines)
            divibilty = sum(lv % tabsize == 0 for lv in indent_lvs if lv)
            if divibilty:
                yield divibilty, tabsize

    try:
        _, tabsize = next(reversed(sorted(it())))
    except StopIteration:
        tabsize = tabsize_d

    settings = Settings()
    settings["tabstop"] = tabsize
    settings["softtabstop"] = tabsize
    settings["shiftwidth"] = tabsize
    settings.drain(True).commit(nvim)


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
