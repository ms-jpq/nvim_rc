from os import environ
from typing import Iterator, Sequence, Tuple
from urllib.parse import urlparse
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.common import NvimError
from pynvim.api.window import Window

from ..nvim.float_win import FloatWin, open_float_win
from ..registery import keymap, rpc, autocmd

BUF_VAR_NAME = f"terminal_buf_{uuid4().hex}"


def _list_marked_bufs(nvim: Nvim) -> Iterator[Buffer]:
    bufs: Sequence[Buffer] = nvim.api.list_bufs()
    for buf in bufs:
        try:
            nvim.api.buf_get_var(buf, BUF_VAR_NAME)
        except NvimError:
            pass
        else:
            yield buf


def _ensure_marked_buf(nvim: Nvim) -> Buffer:
    buf = next(_list_marked_bufs(nvim), None)
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
        for buf in _list_marked_bufs(nvim):
            nvim.command(f"bwipeout! {buf.number}")


@rpc(blocking=True)
def _open_floating(nvim: Nvim, *args: str) -> FloatWin:
    buf = _ensure_marked_buf(nvim)
    filename: str = nvim.api.buf_get_name(buf)
    is_term_buf = urlparse(filename).scheme == "term"
    open_float_win(nvim, margin=0, relsize=0.95, buf=buf)
    if not is_term_buf:
        cmds = args or (environ["SHELL"],)
        nvim.funcs.termopen(cmds, {"on_exit": _on_exit.remote_name})


@rpc(blocking=True)
def toggle_floating(nvim: Nvim, *args: str) -> None:
    pass


keymap.n("<leader>u") << f"<cmd>lua {toggle_floating.remote_name}()<cr>"


@rpc(blocking=True)
def _kill_term_wins(nvim: Nvim, win_id: int) -> None:
    pass


autocmd("WinClosed") << f"lua {_kill_term_wins.remote_name()}(vim.fn.expand('<afile>'))"