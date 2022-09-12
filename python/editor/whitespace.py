from asyncio import gather
from types import NoneType
from typing import Iterable, Iterator, Tuple

from pynvim_pp.atomic import Atomic
from pynvim_pp.buffer import Buffer
from pynvim_pp.lib import decode, encode
from pynvim_pp.operators import p_indent
from pynvim_pp.window import Window

from ..registery import NAMESPACE, autocmd, rpc, settings

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


async def _set_tabsize(buf: Buffer, lines: Iterable[str]) -> None:
    def it() -> Iterator[Tuple[int, int]]:
        for tabsize in range(2, 9):
            indent_lvs = tuple(
                p_indent(line, tabsize=tabsize) for line in lines if lines
            )
            divibilty = sum(lv % tabsize == 0 for lv in indent_lvs if lv)
            if divibilty:
                yield divibilty, tabsize

    _, tabsize = next(iter(sorted(it(), reverse=True)), (-1, tabsize_d))

    atomic = Atomic()
    for option in _TAB_OPTIONS:
        atomic.buf_set_option(buf, option, tabsize)
    await atomic.commit(NoneType)


async def _set_usetab(buf: Buffer, lines: Iterable[str]) -> None:
    first_chars = tuple(next(iter(line), "") for line in lines if lines)
    if first_chars.count("\t") > first_chars.count(" "):
        await buf.opts.set("expandtab", val=False)


async def detect_tabs(buf: Buffer) -> None:
    count = await buf.line_count()
    rows = min(count, 100)
    lines = await buf.get_lines(lo=0, hi=rows)
    await gather(_set_tabsize(buf, lines=lines), _set_usetab(buf, lines=lines))


@rpc()
async def _detect_tabs() -> None:
    buf = await Buffer.get_current()
    await detect_tabs(buf=buf)


_ = autocmd("FileType") << f"lua {NAMESPACE}.{_detect_tabs.method}()"


# smart indentation level
settings["smarttab"] = True


async def _set_trimmed(win: Window, buf: Buffer) -> None:
    row, col = await win.get_cursor()
    lines = await buf.get_lines(lo=0, hi=-1)
    new_lines = [
        decode(encode(line)[:col]) + decode(encode(line)[col:]).rstrip()
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
        atomic = Atomic()
        atomic.buf_set_lines(buf, 0, -1, True, lines)
        atomic.win_set_cursor(win, (row + 1, col))
        await atomic.commit(NoneType)


async def trailing_ws() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    if not await buf.modifiable():
        return
    else:
        await _set_trimmed(win, buf=buf)
