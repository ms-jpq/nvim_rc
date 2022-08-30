from contextlib import suppress
from fnmatch import fnmatch
from itertools import chain
from pathlib import Path, PurePath
from shlex import join
from shutil import which
from typing import Iterable, Iterator, Tuple

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim.api.window import Window
from pynvim_pp.api import (
    buf_set_lines,
    list_wins,
    win_get_buf,
    win_get_cursor,
    win_set_cursor,
)
from pynvim_pp.lib import async_call, awrite, decode, encode, write
from std2.aitertools import aiterify
from std2.asyncio.subprocess import call
from std2.lex import ParseError

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..registery import LANG, NAMESPACE, keymap, rpc
from .linter import BufContext, arg_subst, current_ctx, make_temp, set_preview_content
from .whitespace import detect_tabs, trailing_ws


async def _fmt_output(
    attr: FmtAttrs, ctx: BufContext, cwd: PurePath, temp: Path
) -> str:
    arg_info = join(chain((attr.bin,), attr.args))

    try:
        args = arg_subst(attr.args, ctx=ctx, tmp_name=str(temp))
    except ParseError:
        return LANG("grammar error", text=arg_info)
    else:
        if not which(attr.bin):
            return LANG("missing", thing=attr.bin)
        else:
            stdin = temp.read_bytes() if attr.type is FmtType.stream else None
            proc = await call(
                attr.bin,
                *args,
                stdin=stdin,
                cwd=cwd,
                check_returncode=set(),
            )
            if attr.type is FmtType.stream:
                temp.write_bytes(proc.stdout)

            if proc.returncode == attr.exit_code:
                return ""
            else:
                heading = LANG("proc failed", code=proc.returncode, args=arg_info)
                print_out = ctx.linefeed.join((heading, decode(proc.stderr)))
                return print_out


async def _run(
    nvim: Nvim, ctx: BufContext, attrs: Iterable[FmtAttrs], cwd: PurePath
) -> None:
    body = encode(ctx.linefeed.join(ctx.lines))
    path = Path(ctx.filename)
    with make_temp(path) as temp:
        temp.write_bytes(body)
        errs = [
            err
            async for err in aiterify(
                _fmt_output(attr, ctx=ctx, cwd=cwd, temp=temp) for attr in attrs
            )
            if err
        ]
        errors = (ctx.linefeed * 2).join(errs)
        if errors:

            def c1() -> None:
                set_preview_content(nvim, text=errors)
                write(nvim, LANG("prettier failed"))

            await async_call(nvim, c1)

        else:

            def c2() -> None:
                def it() -> Iterator[Tuple[Window, Tuple[int, int]]]:
                    wins = list_wins(nvim)
                    for win in wins:
                        buf = win_get_buf(nvim, win=win)
                        if buf == ctx.buf:
                            row, col = win_get_cursor(nvim, win)
                            yield win, (row, col)

                saved = {win: pos for win, pos in it()}

                lines = temp.read_text().split(ctx.linefeed)
                if lines:
                    l = lines.pop()
                    if l:
                        lines.append(l)
                buf_set_lines(nvim, buf=ctx.buf, lo=0, hi=-1, lines=lines)

                for win, (row, col) in saved.items():
                    new_row = min(row, len(lines) - 1)
                    with suppress(NvimError):
                        win_set_cursor(nvim, win=win, row=new_row, col=col)
                detect_tabs(nvim, buf=ctx.buf)

                prettiers = LANG("step join sep").join(attr.bin for attr in attrs)
                nice = LANG("prettier succeeded", prettiers=prettiers)
                write(nvim, nice)

            await async_call(nvim, c2)


def _fmts_for(filetype: str) -> Iterator[FmtAttrs]:
    for attr in fmt_specs:
        for pat in attr.filetypes:
            if fnmatch(filetype, pat=pat):
                yield attr
                break


@rpc(blocking=False)
async def run_fmt(nvim: Nvim) -> None:
    cwd, ctx = await async_call(nvim, current_ctx, nvim)

    prettiers = tuple(_fmts_for(ctx.filetype))
    if not prettiers:
        await async_call(nvim, trailing_ws, nvim)
        await awrite(nvim, LANG("missing prettier", filetype=ctx.filetype), error=True)
    else:
        await awrite(nvim, LANG("loading..."))
        await _run(nvim, ctx=ctx, attrs=prettiers, cwd=cwd)


keymap.n("gq", nowait=True) << f"<cmd>lua {NAMESPACE}.{run_fmt.name}()<cr>"
