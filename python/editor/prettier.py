from asyncio import gather
from os import linesep
from pathlib import Path
from shutil import which
from tempfile import NamedTemporaryFile
from typing import IO, Iterable, Iterator

from pynvim import Nvim
from pynvim_pp.lib import async_call, write
from std2.aitertools import aiterify
from std2.asyncio.subprocess import call

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..registery import keymap, rpc
from .linter import BufContext, ParseError, arg_subst, current_ctx, set_preview_content


async def _fmt_output(
    attr: FmtAttrs, ctx: BufContext, cwd: str, temp: IO[bytes]
) -> str:
    arg_info = f"{attr.bin} {' '.join(attr.args)}"

    try:
        args = arg_subst(attr.args, ctx=ctx, filename=temp.name)
    except ParseError:
        return f"⛔️ 语法错误 👉 {arg_info}"
    else:
        if not which(attr.bin):
            return f"⁉️: 莫有 {attr.bin}"
        else:
            temp.seek(0)
            stdin = temp.read() if attr.type is FmtType.stream else None
            proc = await call(attr.bin, *args, stdin=stdin, cwd=cwd)
            if attr.type is FmtType.stream:
                temp.seek(0)
                temp.write(proc.out)
                temp.flush()

            if proc.code == attr.exit_code:
                return ""
            else:
                heading = f"⛔️ - {proc.code} 👉 {arg_info}"
                print_out = linesep.join((heading, proc.err))
                return print_out


async def _run(
    nvim: Nvim, ctx: BufContext, attrs: Iterable[FmtAttrs], cwd: str
) -> None:
    path = Path(ctx.filename)
    with NamedTemporaryFile(dir=str(path.parent), suffix=path.suffix) as temp:
        temp.writelines(b.encode() for line in ctx.lines for b in (line, linesep))
        temp.flush()
        errs = [
            err
            async for err in aiterify(
                _fmt_output(attr, ctx=ctx, cwd=cwd, temp=temp) for attr in attrs
            )
            if err
        ]

        errors = (linesep * 2).join(errs)
        if errors:
            await gather(write(nvim, "⛔️ 美化失败"), set_preview_content(nvim, text=errors))
        else:

            def cont() -> None:
                temp.seek(0)
                lines = temp.read().decode().splitlines()
                nvim.api.buf_set_lines(ctx.buf, 0, -1, True, lines)

            nice = f"✅ 美化成功 👉 {' -> '.join(attr.bin for attr in attrs)}"
            await gather(write(nvim, nice), async_call(nvim, cont))


def _fmts_for(filetype: str) -> Iterator[FmtAttrs]:
    for attr in fmt_specs:
        if filetype in attr.filetypes:
            yield attr


@rpc(blocking=False)
async def run_fmt(nvim: Nvim) -> None:
    cwd, ctx = await async_call(nvim, current_ctx, nvim)

    linters = tuple(_fmts_for(ctx.filetype))
    if not linters:
        await write(nvim, f"⁉️: 莫有 {ctx.filetype} 的 linter", error=True)
    else:
        await write(nvim, "⏳⌛⏳…")
        await _run(nvim, ctx=ctx, attrs=linters, cwd=cwd)


keymap.n("gq", nowait=True) << f"<cmd>lua {run_fmt.name}()<cr>"
