from itertools import chain
from os.path import normcase
from shutil import which
from types import NoneType
from typing import AsyncIterator, Mapping, TypedDict
from uuid import uuid4

from pynvim_pp.buffer import Buffer
from pynvim_pp.float_win import list_floatwins, open_float_win
from pynvim_pp.nvim import Nvim
from pynvim_pp.types import RPCallable
from pynvim_pp.window import Window
from std2 import anext
from std2.pathlib import AnyPath

from ..registery import LANG, NAMESPACE, atomic, autocmd, keymap, rpc

BUF_VAR_NAME = uuid4()


async def _list_marked_bufs() -> AsyncIterator[Buffer]:
    bufs = await Buffer.list(listed=True)
    for buf in bufs:
        if await buf.vars.has(str(BUF_VAR_NAME)):
            yield buf


async def _ensure_marked_buf() -> Buffer:
    if buf := await anext(_list_marked_bufs(), None):
        return buf
    else:
        buf = await Buffer.create(
            listed=True, scratch=True, wipe=False, nofile=False, noswap=True
        )
        await buf.vars.set(str(BUF_VAR_NAME), True)
        return buf


class TermOpts(TypedDict, total=False):
    env: Mapping[str, str]
    on_exit: RPCallable[None]
    on_stdout: RPCallable[None]
    on_stderr: RPCallable[None]


@rpc()
async def _term_open(prog: AnyPath, *args: AnyPath, opts: TermOpts = {}) -> None:
    buf = await _ensure_marked_buf()
    buf_type = await buf.opts.get(str, "buftype")
    is_term_buf = buf_type == "terminal"
    await open_float_win(
        BUF_VAR_NAME, margin=0, relsize=0.95, buf=buf, border="rounded"
    )
    if not is_term_buf:
        cmds = tuple(map(str, chain((which(prog),), args)))
        await Nvim.fn.termopen(NoneType, cmds, opts)

    await Nvim.api.command(NoneType, "startinsert")


@rpc()
async def open_term(*args: AnyPath, opts: TermOpts = {}) -> None:
    argv = args or (await Nvim.fn.getenv(str, "SHELL"),)
    prog, *_ = argv

    if not which(prog):
        await Nvim.write(LANG("invaild command: ", cmd=normcase(prog)), error=True)
    else:
        if float_wins := frozenset([win async for win in list_floatwins(BUF_VAR_NAME)]):
            for win in float_wins:
                await win.close()

        await _term_open(*argv, opts=opts)


atomic.command(f"command! -nargs=* FCmd lua {NAMESPACE}.{open_term.name}(<f-args>)")


@rpc()
async def toggle_floating(*args: str) -> None:
    curr_win = await Window.get_current()
    float_wins = frozenset([win async for win in list_floatwins(BUF_VAR_NAME)])
    if curr_win in float_wins:
        for win in float_wins:
            await win.close()
    else:
        argv = args or (await Nvim.fn.getenv(str, "SHELL"),)
        await _term_open(*argv)


_ = keymap.n("<leader>u") << f"<cmd>lua {NAMESPACE}.{toggle_floating.name}()<cr>"


@rpc()
async def _on_resized() -> None:
    if float_wins := frozenset([win async for win in list_floatwins(BUF_VAR_NAME)]):
        for win in float_wins:
            await win.close()
        await toggle_floating()


_ = autocmd("VimResized") << f"lua {NAMESPACE}.{_on_resized.name}()"
