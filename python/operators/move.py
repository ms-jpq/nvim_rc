from pynvim.api.nvim import Nvim
from pynvim_pp.api import buf_line_count, cur_win, win_get_buf, win_get_cursor
from pynvim_pp.operators import operator_marks, set_visual_selection, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _norm_mv(nvim: Nvim, up: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    row, _ = win_get_cursor(nvim, win=win)
    lines = buf_line_count(nvim, buf=buf)

    if not writable(nvim, buf=buf):
        return
    else:
        if up:
            if row:
                nvim.command(f"move -2")
        else:
            if row < lines - 1:
                nvim.command(f"move +1")


keymap.n("<m-up>") << f"<cmd>lua {_norm_mv.name}(true)<cr>"
keymap.n("<m-down>") << f"<cmd>lua {_norm_mv.name}(false)<cr>"


@rpc(blocking=True)
def _visual_mv(nvim: Nvim, up: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=None)
    lines = buf_line_count(nvim, buf=buf)

    if not writable(nvim, buf=buf):
        return
    else:
        if up:
            if row1 <= 0:
                nvim.command("norm! gv")
            else:
                nvim.command(f"{row1+1},{row2+1}move {row1-1}")
                set_visual_selection(
                    nvim,
                    win=win,
                    mode="v",
                    mark1=(row1 - 1, col1),
                    mark2=(row2 - 1, col2),
                    reverse=True
                )

        else:
            if row2 >= lines - 1:
                nvim.command("norm! gv")
            else:
                nvim.command(f"{row1+1},{row2+1}move {row2 +2}")
                set_visual_selection(
                    nvim,
                    win=win,
                    mode="v",
                    mark1=(row1 + 1, col1),
                    mark2=(row2 + 1, col2),
                )


keymap.v("<m-up>") << rf"<c-\><c-n><cmd>lua {_visual_mv.name}(true)<cr>"
keymap.v("<m-down>") << rf"<c-\><c-n><cmd>lua {_visual_mv.name}(false)<cr>"
