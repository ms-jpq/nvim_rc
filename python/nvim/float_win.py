from typing import Tuple
from pynvim import Nvim
from pynvim.api import Window, Buffer
from math import floor
from itertools import repeat, islice
from dataclasses import dataclass


@dataclass(frozen=True)
class FloatWin:
    border_win: Window
    border_buf: Buffer
    win: Window
    buf: Buffer


def _open_float_win(
    nvim: Nvim,
    buf: Buffer,
    width: int,
    height: int,
    pos: Tuple[int, int],
    focusable: bool,
) -> Window:
    row, col = pos
    opts = {
        "relative": "editor",
        "anchor": "NW",
        "style": "minimal",
        "width": width,
        "height": height,
        "row": row,
        "col": col,
        "focusable": focusable,
    }
    win: Window = nvim.api.open_win(buf, True, opts)
    nvim.api.win_set_option(win, "winhighlight", "Normal:Floating")
    return win


def _border_buf(nvim: Nvim, width: int, height: int) -> Buffer:
    assert width >= 2
    assert height >= 2

    buf = nvim.api.create_buf(False, True)
    top = "╭" + "".join(islice(repeat("─"), width - 2)) + "╮"
    mid = "│" + "".join(islice(repeat("─"), width - 2)) + "│"
    btm = "╰" + "".join(islice(repeat("─"), width - 2)) + "╯"

    lines = tuple((top, *islice(repeat(mid), height - 2), btm))
    nvim.api.buf_set_lines(buf, 0, -1, True, lines)
    return buf


def open_float_win(nvim: Nvim, margin: int, relsize: float, buf: Buffer) -> FloatWin:
    assert margin >= 0
    assert 0 < relsize < 1
    t_width, t_height = nvim.options["columns"], nvim.options["lines"]
    width = floor((t_width - margin) * relsize)
    height = floor((t_height - margin) * relsize)
    row, col = (t_height - height) / 2, (t_width - width) / 2

    border_buf = _border_buf(nvim, width=width, height=height)
    border_win = _open_float_win(
        nvim,
        buf=border_buf,
        width=width,
        height=height,
        pos=(row, col),
        focusable=False,
    )
    win = _open_float_win(
        nvim,
        buf=buf,
        width=width - 2,
        height=height - 2,
        pos=(row + 1, col + 1),
        focusable=True,
    )

    return FloatWin(border_win=border_win, border_buf=border_buf, win=win, buf=buf)
