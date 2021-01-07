from asyncio import gather
from contextlib import contextmanager
from os import close, linesep
from pathlib import Path
from shutil import which
from tempfile import mkstemp
from typing import Iterable, Iterator

from pynvim import Nvim
from pynvim_pp.lib import async_call, write
from std2.aitertools import aiterify
from std2.asyncio.subprocess import call

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..registery import keymap, rpc
from .linter import BufContext, ParseError, arg_subst, current_ctx, set_preview_content


@contextmanager
def _mktemp(path: Path) -> Iterator[Path]:
    fd, temp = mkstemp(prefix=path.stem, suffix=path.suffix, dir=path.parent)
    close(fd)
    new_path = Path(temp)
    try:
        yield new_path
    finally:
        new_path.unlink(missing_ok=True)


async def _fmt_output(attr: FmtAttrs, ctx: BufContext, cwd: str, temp: Path) -> str:
    arg_info = f"{attr.bin} {' '.join(attr.args)}"

    try:
        args = arg_subst(attr.args, ctx=ctx, filename=str(temp))
    except ParseError:
        return f"⛔️ 语法错误 👉 {arg_info}"
    else:
        if not which(attr.bin):
            return f"⁉️: 莫有 {attr.bin}"
        else:
            stdin = temp.read_bytes() if attr.type is FmtType.stream else None
            proc = await call(attr.bin, *args, stdin=stdin, cwd=cwd)
            if attr.type is FmtType.stream:
                temp.write_bytes(proc.out)

            if proc.code == attr.exit_code:
                return ""
            else:
                heading = f"⛔️ - {proc.code} 👉 {arg_info}"
                print_out = linesep.join((heading, proc.err))
                return print_out


async def _run(
    nvim: Nvim, ctx: BufContext, attrs: Iterable[FmtAttrs], cwd: str
) -> None:
    body = linesep.join(ctx.lines).encode()
    path = Path(ctx.filename)
    with _mktemp(path) as temp:
        temp.write_bytes(body)
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
                lines = temp.read_text().splitlines()
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
