from os import environ
from typing import Sequence
from urllib.parse import urlparse
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.common import NvimError

from ..nvim.float_win import open_float_win
from ..registery import keymap, rpc

BUF_VAR_NAME = f"buf_cursor_pos_{uuid4().hex}"


def _single_term_buf(nvim: Nvim) -> Buffer:
    bufs: Sequence[Buffer] = nvim.api.list_bufs()
    for buf in bufs:
        try:
            nvim.api.buf_get_var(buf, BUF_VAR_NAME)
        except NvimError:
            pass
        else:
            return buf
    else:
        buf = nvim.api.create_buf(False, True)
        nvim.api.buf_set_var(buf, BUF_VAR_NAME, BUF_VAR_NAME)
        return buf


@rpc(blocking=True)
def on_exit(nvim: Nvim, *args: str) -> None:
    raise Exception()


@rpc(blocking=True)
def open_floating(nvim: Nvim, *args: str) -> None:
    buf = _single_term_buf(nvim)
    fw = open_float_win(nvim, margin=0, relsize=0.95, buf=buf)
    filename: str = nvim.api.buf_get_name(fw.buf)
    if urlparse(filename).scheme != "term":
        cmds = args or (environ["SHELL"],)
        nvim.funcs.termopen(cmds, {"on_exit": f"v:lua.{on_exit.lua_name}"})
    nvim.command("startinsert")


keymap.n("<leader>u") << f"<cmd>lua {open_floating.lua_name}()<cr>"
