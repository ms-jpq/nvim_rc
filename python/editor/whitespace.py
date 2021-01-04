from string import whitespace
from typing import Iterable, Iterator, Sequence, Set, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim_pp.operators import p_indent

from ..registery import autocmd, rpc, settings

# join only add 1 space
settings["nojoinspaces"] = True


# how big are tabs ?
# spaces remove on deletion
# manual indentation width
_TAB_OPTIONS = ("tabstop", "softtabstop", "shiftwidth")
tabsize_d = 2
for option in _TAB_OPTIONS:
    settings[option] = tabsize_d

# insert spaces instead of tabs
settings["expandtab"] = True


def _set_tabsize(nvim: Nvim, buf: Buffer, lines: Iterable[str]) -> None:
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

    for option in _TAB_OPTIONS:
        nvim.api.buf_set_option(buf, option, tabsize)


def _set_usetab(nvim: Nvim, buf: Buffer, lines: Iterable[str]) -> None:
    first_chars = tuple(next(iter(line), "") for line in lines)
    if first_chars.count("\t") > first_chars.count(" "):
        nvim.api.buf_set_option(buf, "expandtab", False)


@rpc(blocking=True)
def _detect_tabs(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    count: int = nvim.api.buf_line_count(buf)
    rows = min(count, 100)
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, rows, True)
    _set_tabsize(nvim, buf=buf, lines=lines)
    _set_usetab(nvim, buf=buf, lines=lines)


autocmd("FileType") << f"lua {_detect_tabs.remote_name}()"


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
