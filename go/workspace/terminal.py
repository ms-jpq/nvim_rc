from collections.abc import AsyncIterator, Mapping, Sequence
from itertools import chain
from os import environ
from os.path import normcase, normpath
from typing import TypedDict
from uuid import uuid4

from pynvim_pp.buffer import Buffer
from pynvim_pp.float_win import list_floatwins, open_float_win
from pynvim_pp.nvim import Nvim
from pynvim_pp.rpc_types import RPCallable
from pynvim_pp.types import NoneType
from pynvim_pp.window import Window
from std2 import anext
from std2.asyncio.subprocess import call
from std2.pathlib import AnyPath
from std2.platform import OS, os

from ..config.install import which
from ..registry import LANG, NAMESPACE, atomic, autocmd, keymap, rpc

_BUF_VAR_NAME = uuid4()


class TermOpts(TypedDict, total=False):
    env: Mapping[str, str]
    on_exit: RPCallable[None]
    on_stdout: RPCallable[None]
    on_stderr: RPCallable[None]


if "TMUX" in environ:

    @rpc()
    async def open_term(*args: AnyPath) -> None:
        if tmux := which("tmux"):
            cwd = await Nvim.getcwd()
            await call(
                tmux,
                "display-popup",
                "-EE",
                "-d",
                cwd,
                "-w",
                "95%",
                "-h",
                "90%",
                "--",
                *args,
                check_returncode=set(),
            )
        else:
            await Nvim.write(LANG("cannot tmux"))

    atomic.command(
        f"command! -nargs=* FCmd lua {NAMESPACE}.{open_term.method}(<f-args>)"
    )
    _ = keymap.n("<leader>u") << f"<cmd>lua {NAMESPACE}.{open_term.method}()<cr>"

else:

    async def _list_marked_bufs() -> AsyncIterator[Buffer]:
        bufs = await Buffer.list(listed=True)
        for buf in bufs:
            if await buf.vars.has(str(_BUF_VAR_NAME)):
                yield buf

    async def _ensure_marked_buf() -> Buffer:
        if buf := await anext(_list_marked_bufs(), None):
            return buf
        else:
            buf = await Buffer.create(
                listed=True, scratch=True, wipe=False, nofile=False, noswap=True
            )
            await buf.vars.set(str(_BUF_VAR_NAME), True)
            return buf

    async def _sh() -> Sequence[str]:
        if os == OS.windows:
            sh = "bash.exe"
        else:
            sh = await Nvim.fn.getenv(str, "SHELL")

        return (sh,)

    @rpc()
    async def _term_open(prog: AnyPath, *args: AnyPath, opts: TermOpts = {}) -> None:
        buf = await _ensure_marked_buf()
        buf_type = await buf.opts.get(str, "buftype")
        is_term_buf = buf_type == "terminal"
        await open_float_win(
            _BUF_VAR_NAME, margin=0, relsize=0.95, buf=buf, border="rounded"
        )
        if not is_term_buf:
            cmds = tuple(map(str, chain((which(normpath(prog)),), args)))
            await Nvim.fn.termopen(NoneType, cmds, opts)

        await Nvim.api.command(NoneType, "startinsert")

    @rpc()
    async def open_term(*args: AnyPath, opts: TermOpts = {}) -> None:
        argv = args or await _sh()
        prog, *_ = argv

        if not which(normpath(prog)):
            await Nvim.write(LANG("invalid command: ", cmd=normcase(prog)), error=True)
        else:
            if float_wins := frozenset(
                [win async for win in list_floatwins(_BUF_VAR_NAME)]
            ):
                for win in float_wins:
                    await win.close()

            await _term_open(*argv, opts=opts)

    @rpc()
    async def _toggle_floating(*args: str) -> None:
        curr_win = await Window.get_current()
        float_wins = frozenset([win async for win in list_floatwins(_BUF_VAR_NAME)])
        if curr_win in float_wins:
            for win in float_wins:
                await win.close()
        else:
            argv = args or await _sh()
            await _term_open(*argv)

    _ = keymap.n("<leader>u") << f"<cmd>lua {NAMESPACE}.{_toggle_floating.method}()<cr>"

    @rpc()
    async def _on_resized() -> None:
        if float_wins := frozenset(
            [win async for win in list_floatwins(_BUF_VAR_NAME)]
        ):
            for win in float_wins:
                await win.close()
            await _toggle_floating()

    _ = autocmd("VimResized") << f"lua {NAMESPACE}.{_on_resized.method}()"

atomic.command(f"command! -nargs=* FCmd lua {NAMESPACE}.{open_term.method}(<f-args>)")
