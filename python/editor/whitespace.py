from typing import Iterable, Iterator, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim_pp.api import (
    buf_get_lines,
    buf_line_count,
    buf_set_lines,
    buf_set_option,
    cur_buf,
    cur_win,
    win_get_buf,
    win_get_cursor,
    win_set_cursor,
)
from pynvim_pp.operators import p_indent, writable

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
        buf_set_option(nvim, buf=buf, key=option, val=tabsize)


def _set_usetab(nvim: Nvim, buf: Buffer, lines: Iterable[str]) -> None:
    first_chars = tuple(next(iter(line), "") for line in lines if lines)
    if first_chars.count("\t") > first_chars.count(" "):
        buf_set_option(nvim, buf=buf, key="expandtab", val=False)


@rpc(blocking=True)
def _detect_tabs(nvim: Nvim) -> None:
    buf = cur_buf(nvim)
    count = buf_line_count(nvim, buf=buf)
    rows = min(count, 100)
    lines = buf_get_lines(nvim, buf=buf, lo=0, hi=rows)
    _set_tabsize(nvim, buf=buf, lines=lines)
    _set_usetab(nvim, buf=buf, lines=lines)


autocmd("FileType") << f"lua {_detect_tabs.name}()"


# smart indentation level
settings["autoindent"] = True
settings["smarttab"] = True


def _set_trimmed(nvim: Nvim, win: Window, buf: Buffer) -> None:
    row, col = win_get_cursor(nvim, win=win)
    lines = buf_get_lines(nvim, buf=buf, lo=0, hi=-1)
    new_lines = [
        line.encode()[:col].decode() + line.encode()[col:].decode().rstrip()
        if r == row
        else line.rstrip()
        for r, line in enumerate(lines)
    ]

    while new_lines:
        line = new_lines.pop()
        if line or len(new_lines) <= row:
            new_lines.append(line)
            break
    if len(new_lines) < len(lines):
        new_lines.append("")

    if new_lines != lines:
        buf_set_lines(nvim, buf=buf, lo=0, hi=-1, lines=new_lines)
        win_set_cursor(nvim, win=win, row=row, col=col)


def trailing_ws(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    if not writable(nvim, buf=buf):
        return
    else:
        _set_trimmed(nvim, win=win, buf=buf)

