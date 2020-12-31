from os import environ
from typing import Iterator, Sequence, Tuple
from urllib.parse import urlparse
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.common import NvimError
from pynvim.api.window import Window

from ..nvim.float_win import FloatWin, open_float_win
from ..registery import keymap, rpc

BUF_VAR_NAME = f"terminal_buf_{uuid4().hex}"


def _list_term_wins(nvim: Nvim) -> Iterator[Tuple[Window, Buffer]]:
    wins: Sequence[Window] = nvim.api.list_wins()
    for win in wins:
        buf: Buffer = nvim.api.win_get_buf(win)
        try:
            nvim.api.buf_get_var(buf, BUF_VAR_NAME)
        except NvimError:
            pass
        else:
            yield win, buf


def _single_term_buf(nvim: Nvim) -> Buffer:
    _, buf = next(_list_term_wins(nvim), Tuple[None, None])
    if buf is not None:
        return buf
    else:
        buf = nvim.api.create_buf(False, True)
        nvim.api.buf_set_var(buf, BUF_VAR_NAME, True)
        return buf


@rpc(blocking=True)
def _on_exit(nvim: Nvim, args: Tuple[int, int, str]) -> None:
    job_id, code, event_type = args
    if code == 0:
        for _, buf in _list_term_wins(nvim):
            nvim.command(f"bwipeout! {buf.number}")


@rpc(blocking=True)
def _open_floating(nvim: Nvim, *args: str) -> FloatWin:
    buf = _single_term_buf(nvim)
    fw = open_float_win(nvim, margin=0, relsize=0.95, buf=buf)
    filename: str = nvim.api.buf_get_name(fw.buf)
    if urlparse(filename).scheme != "term":
        cmds = args or (environ["SHELL"],)
        nvim.funcs.termopen(cmds, {"on_exit": _on_exit.remote_name})
    return fw


@rpc(blocking=True)
def toggle_floating(nvim: Nvim, *args: str) -> None:
    pass


keymap.n("<leader>u") << f"<cmd>lua {toggle_floating.remote_name}()<cr>"
