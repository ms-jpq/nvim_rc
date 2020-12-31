from string import whitespace
from typing import Iterable, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window

from ..registery import keymap, rpc


@rpc(blocking=True)
def _word(nvim: Nvim, is_inside: bool) -> None:
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.get_current_buf()
    row, col = nvim.api.win_get_cursor(win)
    line: str = nvim.api.get_current_line()

    nvim.command("norm! `<v`>")


keymap.o("iw") << f"<cmd>lua {_word.remote_name}(true)<cr>"
keymap.o("aw") << f"<cmd>lua {_word.remote_name}(false)<cr>"
keymap.v("iw") << f"<esc><cmd>lua {_word.remote_name}(true)<cr>"
keymap.v("aw") << f"<esc><cmd>lua {_word.remote_name}(false)<cr>"
