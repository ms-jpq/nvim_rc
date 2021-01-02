from contextlib import contextmanager
from itertools import repeat
from os import linesep
from pathlib import Path
from shutil import which
from typing import Iterable, Iterator
from uuid import uuid4

from pynvim import Nvim
from pynvim_pp.lib import async_call, write
from std2.aitertools import aiterify
from std2.asyncio.subprocess import call

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..registery import keymap, rpc
from .linter import BufContext, arg_subst, current_ctx, set_preview_content


@contextmanager
def _mktemp(path: Path) -> Iterator[Path]:
    new_name = lambda: path.with_name(f"{uuid4().hex}_{path.name}")
    new_path = next(name for name in iter(new_name, None) if not name.exists())
    new_path.touch()
    try:
        yield new_path
    finally:
        new_path.unlink(missing_ok=True)


async def _fmt_output(attr: FmtAttrs, cwd: str, temp: Path) -> str:
    args = arg_subst(attr.args, filename=str(temp))
    if not which(attr.bin):
        return f"⁉️: 莫有 {attr.bin}"
    else:
        stdin = temp.read_bytes() if attr.type == FmtType.stream else None
        proc = await call(attr.bin, *args, stdin=stdin, cwd=cwd)
        if attr.type == FmtType.stream:
            temp.write_bytes(proc.out)

        if proc.code == attr.exit_code:
            return ""
        else:
            arg_info = f"{attr.bin} {' '.join(attr.args)}"
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
                _fmt_output(attr, cwd=cwd, temp=temp) for attr in attrs
            )
        ]
        errors = "".join(repeat(linesep, times=2)).join(errs)
        if errors:
            await set_preview_content(nvim, text=errors)
        else:
            nice = f"✅ 美化成功 👉 {' -> '.join(attr.bin for attr in attrs)}{linesep}"
            lines = temp.read_text().splitlines()

            def cont() -> None:
                nvim.api.buf_set_lines(ctx.buf, 0, -1, True, lines)
                nvim.out_write(nice)

            await async_call(nvim, cont)


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
        await _run(nvim, ctx=ctx, attrs=linters, cwd=cwd)


keymap.n("gq", nowait=True) << f"<cmd>lua {run_fmt.remote_name}()<cr>"
