from typing import Iterable, Iterator, Sequence, Tuple

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
            indent_lvs = tuple(
                p_indent(line, tabsize=tabsize) for line in lines if lines
            )
            divibilty = sum(lv % tabsize == 0 for lv in indent_lvs if lv)
            if divibilty:
                yield divibilty, tabsize

    _, tabsize = next(iter(sorted(it(), reverse=True)), (-1, tabsize_d))
    for option in _TAB_OPTIONS:
        nvim.api.buf_set_option(buf, option, tabsize)


def _set_usetab(nvim: Nvim, buf: Buffer, lines: Iterable[str]) -> None:
    first_chars = tuple(next(iter(line), "") for line in lines if lines)
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


# remove trailing whitespace
@rpc(blocking=True)
def _trailing_ws(nvim: Nvim) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, col = nvim.api.win_get_cursor(win)
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)
    new_lines = enumerate((line.rstrip() for line in lines), start=1)

    def it() -> Iterator[str]:
        trimmable = True
        for r, line in reversed(tuple(new_lines)):
            trimmable = trimmable and (not line) and r > row
            if r == row:
                yield line + (" " * (col - len(line)))
            elif not trimmable:
                yield line

    nvim.api.buf_set_lines(buf, 0, -1, True, tuple(it()))
    nvim.api.win_set_cursor(win, (row, col))


autocmd(
    "BufWritePre", modifiers=("*", "undojoin", "|")
) << f"lua {_trailing_ws.remote_name}()"
