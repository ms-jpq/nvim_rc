from pynvim.api import Buffer, Window
from pynvim.api.nvim import Nvim

from ..nvim.operators import operator_marks, set_visual_selection
from ..registery import keymap, rpc


@rpc(blocking=True)
def _normal_up(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not nvim.api.buf_get_option(buf, "modifiable"):
        return
    else:
        win: Window = nvim.api.get_current_win()
        row, col = nvim.api.win_get_cursor(win)
        if row <= 1:
            return
        else:
            row = row - 1
            curr = nvim.api.buf_get_lines(buf, row, row + 1, True)
            nxt = nvim.api.buf_get_lines(buf, row - 1, row, True)
            new = tuple((*curr, *nxt))
            nvim.api.buf_set_lines(buf, row - 1, row + 1, True, new)
            nvim.api.win_set_cursor(win, (row, col))


@rpc(blocking=True)
def _normal_down(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not nvim.api.buf_get_option(buf, "modifiable"):
        return
    else:
        win: Window = nvim.api.get_current_win()
        row, col = nvim.api.win_get_cursor(win)
        count = nvim.api.buf_line_count(buf)
        if row >= count:
            return
        else:
            row = row - 1
            curr = nvim.api.buf_get_lines(buf, row, row + 1, True)
            nxt = nvim.api.buf_get_lines(buf, row + 1, row + 2, True)
            new = tuple((*nxt, *curr))
            nvim.api.buf_set_lines(buf, row, row + 2, True, new)
            nvim.api.win_set_cursor(win, (row + 2, col))


keymap.n("<m-up>") << f"<cmd>lua {_normal_up.remote_name}()<cr>"
keymap.n("<m-down>") << f"<cmd>lua {_normal_down.remote_name}()<cr>"


def _reselect_visual(nvim: Nvim) -> None:
    nvim.command("norm! gv")


@rpc(blocking=True)
def _visual_up(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not nvim.api.buf_get_option(buf, "modifiable"):
        return
    else:
        (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=None)
        if row1 <= 1:
            _reselect_visual(nvim)
        else:
            row1, row2 = row1 - 1, row2 - 1
            curr = nvim.api.buf_get_lines(0, row1, row2 + 1, True)
            nxt = nvim.api.buf_get_lines(0, row1 - 1, row1, True)
            new = tuple((*curr, *nxt))
            nvim.api.buf_set_lines(buf, row1 - 1, row2 + 1, True, new)
            set_visual_selection(
                nvim, buf=buf, mark1=(row1 - 1, col1), mark2=(row2 + 1, col2)
            )
            _reselect_visual(nvim)


@rpc(blocking=True)
def _visual_down(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    if not nvim.api.buf_get_option(buf, "modifiable"):
        return
    else:
        (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=None)
        count = nvim.api.buf_line_count(buf)
        if row2 >= count:
            _reselect_visual(nvim)
        else:
            row1, row2 = row1 - 1, row2 - 1
            curr = nvim.api.buf_get_lines(buf, row1, row2 + 1, True)
            nxt = nvim.api.buf_get_lines(buf, row2 + 1, row2 + 2, True)
            new = tuple((*nxt, *curr))
            nvim.api.buf_set_lines(buf, row1, row2 + 2, True, new)
            set_visual_selection(
                nvim, buf=buf, mark1=(row1 + 2, col1), mark2=(row2 + 2, col2)
            )
            _reselect_visual(nvim)


keymap.v("<m-up>") << f"<esc><cmd>lua {_visual_up.remote_name}()<cr>"
keymap.v("<m-down>") << f"<esc><cmd>lua {_visual_down.remote_name}()<cr>"
