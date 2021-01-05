from typing import Iterable, Iterator, Sequence, Tuple
from uuid import uuid4

from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim.api.common import NvimError
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


autocmd("FileType") << f"lua {_detect_tabs.name}()"


# smart indentation level
settings["autoindent"] = True
settings["smarttab"] = True


# remove trailing whitespace
BUF_VAR_NAME = f"buf_last_trimmed_{uuid4().hex}"


def _set_trimmed(nvim: Nvim, buf: Buffer) -> None:
    win: Window = nvim.api.get_current_win()
    row, col = nvim.api.win_get_cursor(win)
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)
    new_lines = [
        line[:col] + line[col:].rstrip() if r == row else line.rstrip()
        for r, line in enumerate(lines, start=1)
    ]

    while new_lines:
        line = new_lines.pop()
        if line or len(new_lines) < row:
            new_lines.append(line)
            break

    if new_lines != lines:
        nvim.api.buf_set_lines(buf, 0, -1, True, new_lines)
        nvim.api.win_set_cursor(win, (row, col))


@rpc(blocking=True)
def _trailing_ws(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not writable(nvim, buf=buf):
        return
    else:
        try:
            prev = nvim.api.buf_get_var(buf, BUF_VAR_NAME)
        except NvimError:
            pass
        else:
            tick = nvim.api.buf_get_changedtick(buf)
            if tick > prev:
                _set_trimmed(nvim, buf=buf)
                nvim.api.buf_set_var(buf, BUF_VAR_NAME, tick)


# autocmd(
#     "CursorHold", modifiers=("*", "undojoin", "|")
# ) << f"lua {_trailing_ws.name}()"
