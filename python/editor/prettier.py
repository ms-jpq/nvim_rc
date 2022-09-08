from contextlib import suppress
from fnmatch import fnmatch
from itertools import chain
from pathlib import Path, PurePath
from shlex import join
from shutil import which
from typing import AsyncIterator, Iterable, Iterator, Tuple

from pynvim_pp.lib import decode, encode
from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NvimError
from pynvim_pp.window import Window
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


async def _run(ctx: BufContext, attrs: Iterable[FmtAttrs], cwd: PurePath) -> None:
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
            await set_preview_content(errors)
            await Nvim.write(LANG("prettier failed"))

        else:

            async def it() -> AsyncIterator[Tuple[Window, Tuple[int, int]]]:
                wins = await Window.list()
                for win in wins:
                    buf = await win.get_buf()
                    if buf == ctx.buf:
                        row, col = await win.get_cursor()
                        yield win, (row, col)

            saved = {win: pos async for win, pos in it()}

            lines = temp.read_text().split(ctx.linefeed)
            if lines:
                l = lines.pop()
                if l:
                    lines.append(l)

            await ctx.buf.set_lines(lo=0, hi=-1, lines=lines)

            for win, (row, col) in saved.items():
                new_row = min(row, len(lines) - 1)
                with suppress(NvimError):
                    await win.set_cursor(row=new_row, col=col)

            await detect_tabs(ctx.buf)

            prettiers = LANG("step join sep").join(attr.bin for attr in attrs)
            nice = LANG("prettier succeeded", prettiers=prettiers)
            await Nvim.write(nice)


def _fmts_for(filetype: str) -> Iterator[FmtAttrs]:
    for attr in fmt_specs:
        for pat in attr.filetypes:
            if fnmatch(filetype, pat=pat):
                yield attr
                break


@rpc(blocking=False)
async def run_fmt() -> None:
    cwd, ctx = await current_ctx()

    prettiers = tuple(_fmts_for(ctx.filetype))
    if not prettiers:
        await trailing_ws()
        await Nvim.write(LANG("missing prettier", filetype=ctx.filetype), error=True)
    else:
        await Nvim.write(LANG("loading..."))
        await _run(ctx, attrs=prettiers, cwd=cwd)


_ = keymap.n("gq", nowait=True) << f"<cmd>lua {NAMESPACE}.{run_fmt.name}()<cr>"
