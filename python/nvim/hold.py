from contextlib import contextmanager
from typing import Iterator

from pynvim import Nvim
from pynvim.api import Window


@contextmanager
def hold_win_pos(nvim: Nvim, hold: bool) -> Iterator[None]:
    if hold:
        win: Window = nvim.api.get_current_win()
    else:
        win = None
    try:
        yield None
    finally:
        if win is not None:
            nvim.api.set_current_win(win)
