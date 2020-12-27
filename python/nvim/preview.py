from pynvim import Nvim
from pynvim.api import Buffer, Tabpage, Window
from typing import Sequence


def _open_preview(nvim: Nvim) -> Window:
    tab: Tabpage = nvim.api.get_current_tabpage()
    wins: Sequence[Window] = nvim.api.tabpage_list_wins(tab)
    for win in wins:
        opt = nvim.api.win_get_option(win, "previewwindow")
        if opt:
            nvim.api.set_current_win(win)
            return win
    else:
        nvim.api.command("new")
        win = nvim.api.get_current_win()
        nvim.api.win_set_option(win, "previewwindow", True)
        height = nvim.options.previewheight
        nvim.api.win_set_height(win, height)
        return win


def set_preview(nvim: Nvim, preview: str) -> None:
    win = _open_preview(nvim)
    buf: Buffer = nvim.api.win_get_buf(win)
    nvim.api.buf_set_option(buf, "modifiable", True)
    nvim.api.buf_set_lines(buf, 0, -1, True, preview.splitlines())
    nvim.api.buf_set_option(buf, "modifiable", False)