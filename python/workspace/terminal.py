from os import environ
from typing import Iterator, Mapping, Optional, TypedDict
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.api import (
    buf_get_option,
    buf_get_var,
    buf_set_var,
    create_buf, cur_window,
    list_bufs,
    win_close,
)
from pynvim_pp.float_win import list_floatwins, open_float_win
from pynvim_pp.rpc import RpcCallable

from ..registery import autocmd, keymap, rpc

BUF_VAR_NAME = f"terminal_buf_{uuid4().hex}"


def _list_marked_bufs(nvim: Nvim) -> Iterator[Buffer]:
    for buf in list_bufs(nvim):
        flag: Optional[bool] = buf_get_var(nvim, buf=buf, key=BUF_VAR_NAME)
        if flag:
            yield buf


def _ensure_marked_buf(nvim: Nvim) -> Buffer:
    buf = next(_list_marked_bufs(nvim), None)
    if buf is not None:
        return buf
    else:
        buf = create_buf(nvim, listed=True, scratch=True, wipe=False, nofile=False)
        buf_set_var(nvim, buf=buf, key=BUF_VAR_NAME, val=True)
        return buf


class TermOpts(TypedDict, total=False):
    env: Optional[Mapping[str, str]]
    on_exit: Optional[RpcCallable[None]]
    on_stdout: Optional[RpcCallable[None]]
    on_stderr: Optional[RpcCallable[None]]


@rpc(blocking=True)
def _term_open(nvim: Nvim, *args: str, opts: TermOpts = {}) -> None:
    buf = _ensure_marked_buf(nvim)
    buf_type: str = buf_get_option(nvim, buf=buf, key="buftype")
    is_term_buf = buf_type == "terminal"
    open_float_win(nvim, margin=0, relsize=0.95, buf=buf)
    if not is_term_buf:
        cmds = args or (environ["SHELL"],)
        nvim.funcs.termopen(cmds, opts)
    nvim.command("startinsert")


def close_term(nvim: Nvim) -> None:
    for win in list_floatwins(nvim):
        win_close(nvim, win=win)


@rpc(blocking=True)
def open_term(nvim: Nvim, prog: str, *args: str, opts: TermOpts = {}) -> None:
    close_term(nvim)
    _term_open(nvim, prog, *args, opts=opts)


@rpc(blocking=True)
def toggle_floating(nvim: Nvim, *args: str) -> None:
    curr_win = cur_window(nvim)
    float_wins = frozenset(list_floatwins(nvim))
    if curr_win in float_wins:
        for win in float_wins:
            win_close(nvim, win=win)
    else:
        _term_open(nvim, *args)


keymap.n("<leader>u") << f"<cmd>lua {toggle_floating.name}()<cr>"


@rpc(blocking=True)
def _kill_term_wins(nvim: Nvim, win_id: str) -> None:
    wins = tuple(list_floatwins(nvim))
    fw_ids = frozenset(nvim.funcs.win_getid(win.number) for win in wins)
    if int(win_id) in fw_ids:
        for win in wins:
            win_close(nvim, win=win)


autocmd("WinClosed") << f"lua {_kill_term_wins.name}(vim.fn.expand('<afile>'))"
