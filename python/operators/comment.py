from typing import Sequence, Tuple

from pynvim import Nvim
from pynvim.api.nvim import Buffer, Nvim
from pynvim_pp.api import (
    buf_get_lines,
    buf_get_option,
    buf_set_lines,
    cur_buf,
    cur_win,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.operators import VisualTypes, operator_marks, writable

from ..registery import keymap, rpc


def _parse_comment_str(nvim: Nvim, buf: Buffer) -> Tuple[str, str]:
    comment_str: str = buf_get_option(nvim, buf=buf, key="commentstring")
    lhs, _, rhs = comment_str.partition(comment_str)
    return lhs, rhs


def _toggle_comment(lhs: str, rhs: str, lines: Sequence[str]) -> Sequence[str]:
    is_commented = tuple(line.startswith(lhs) and line.endswith(rhs) for line in lines)
    if all(is_commented):
        return tuple(line[lhs:rhs] for line in lines)
    elif any(is_commented):
        return tuple(
            f"{lhs}{line}{rhs}" if commented else line
            for commented, line in zip(is_commented, lines)
        )
    else:
        return tuple(f"{lhs}{line}{rhs}" for line in lines)


@rpc(blocking=True)
def _comment(nvim: Nvim, visual: VisualTypes = None) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        (row1, _), (row2, _) = operator_marks(nvim, buf=buf, visual_type=visual)
        lines = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)
        lhs, rhs = _parse_comment_str(nvim, buf=buf)
        new_lines = _toggle_comment(lhs, rhs, lines=lines)
        buf_set_lines(nvim, buf=buf, lo=row1, hi=row2 + 1, lines=new_lines)


keymap.n("gc") << f"<cmd>set opfunc={_comment.name}<cr>g@"
keymap.v("gc") << f"<esc><cmd>lua {_comment.name}()<cr>"


@rpc(blocking=True)
def _comment_line(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    if not writable(nvim, buf=buf):
        return
    else:
        row, _ = win_get_cursor(nvim, win=win)
        lines = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
        lhs, rhs = _parse_comment_str(nvim, buf=buf)
        new_lines = _toggle_comment(lhs, rhs, lines=lines)
        buf_set_lines(nvim, buf=buf, lo=row, hi=row + 1, lines=new_lines)


keymap.n("grr") << f"<cmd>lua {_comment_line.name}()<cr>"
