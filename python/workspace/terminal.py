from itertools import chain
from os import environ
from os.path import normcase
from shutil import which
from typing import Iterator, Mapping, Optional, TypedDict, cast
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.api import (
    buf_get_option,
    buf_get_var,
    buf_set_var,
    create_buf,
    cur_win,
    list_bufs,
    win_close,
)
from pynvim_pp.float_win import list_floatwins, open_float_win
from pynvim_pp.lib import write
from pynvim_pp.rpc import RpcCallable
from std2.pathlib import AnyPath

from ..registery import LANG, NAMESPACE, atomic, autocmd, keymap, rpc

BUF_VAR_NAME = f"terminal_buf_{uuid4().hex}"


def _list_marked_bufs(nvim: Nvim) -> Iterator[Buffer]:
    for buf in list_bufs(nvim, listed=True):
        flag = cast(Optional[bool], buf_get_var(nvim, buf=buf, key=BUF_VAR_NAME))
        if flag:
            yield buf


def _ensure_marked_buf(nvim: Nvim) -> Buffer:
    buf = next(_list_marked_bufs(nvim), None)
    if buf is not None:
        return buf
    else:
        buf = create_buf(
            nvim, listed=True, scratch=True, wipe=False, nofile=False, noswap=True
        )
        buf_set_var(nvim, buf=buf, key=BUF_VAR_NAME, val=True)
        return buf


class TermOpts(TypedDict, total=False):
    env: Mapping[str, str]
    on_exit: RpcCallable[None]
    on_stdout: RpcCallable[None]
    on_stderr: RpcCallable[None]


@rpc(blocking=True)
def _term_open(nvim: Nvim, prog: AnyPath, *args: AnyPath, opts: TermOpts = {}) -> None:
    buf = _ensure_marked_buf(nvim)
    buf_type: str = buf_get_option(nvim, buf=buf, key="buftype")
    is_term_buf = buf_type == "terminal"
    open_float_win(nvim, margin=0, relsize=0.95, buf=buf, border="rounded")
    if not is_term_buf:
        cmds = tuple(map(str, chain((which(prog),), args)))
        nvim.funcs.termopen(cmds, opts)
    nvim.command("startinsert")


@rpc(blocking=True)
def open_term(nvim: Nvim, *args: AnyPath, opts: TermOpts = {}) -> None:
    for win in list_floatwins(nvim):
        win_close(nvim, win=win)
    argv = args or (environ["SHELL"],)
    prog, *_ = argv
    if not which(prog):

        write(nvim, LANG("invaild command: ", cmd=normcase(prog)), error=True)
    else:
        _term_open(nvim, *argv, opts=opts)


atomic.command(f"command! -nargs=* FTerm lua {NAMESPACE}.{open_term.name}(<f-args>)")


@rpc(blocking=True)
def toggle_floating(nvim: Nvim, *args: str) -> None:
    curr_win = cur_win(nvim)
    float_wins = frozenset(list_floatwins(nvim))
    if curr_win in float_wins:
        for win in float_wins:
            win_close(nvim, win=win)
    else:
        argv = args or (environ["SHELL"],)
        _term_open(nvim, *argv)


keymap.n("<leader>u") << f"<cmd>lua {NAMESPACE}.{toggle_floating.name}()<cr>"


@rpc(blocking=True)
def _on_resized(nvim: Nvim) -> None:
    wins = tuple(list_floatwins(nvim))
    if wins:
        for win in wins:
            win_close(nvim, win=win)
        toggle_floating(nvim)


autocmd("VimResized") << f"lua {NAMESPACE}.{_on_resized.name}()"
