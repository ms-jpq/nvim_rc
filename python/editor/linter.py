from asyncio import gather
from dataclasses import dataclass
from datetime import datetime
from itertools import repeat
from os import linesep
from shutil import which
from typing import Iterable, Iterator, Sequence, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.hold import hold_win_pos
from pynvim_pp.lib import async_call, write
from pynvim_pp.preview import set_preview
from std2.asyncio.subprocess import call

from ..config.linter import LinterAttrs, linter_specs
from ..consts import DATE_FMT
from ..registery import keymap, rpc

ESCAPE_CHAR = "%"


@dataclass(frozen=True)
class BufContext:
    buf: Buffer
    filename: str
    filetype: str
    lines: Sequence[str]


def current_ctx(nvim: Nvim) -> Tuple[str, BufContext]:
    cwd = nvim.funcs.getcwd()
    buf: Buffer = nvim.api.get_current_buf()
    filename: str = nvim.api.buf_get_name(buf)
    filetype: str = nvim.api.buf_get_option(buf, "filetype")
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)
    return cwd, BufContext(buf=buf, filename=filename, filetype=filetype, lines=lines)


def arg_subst(args: Iterable[str], filename: str) -> Iterator[str]:
    for arg in args:

        def it() -> Iterator[str]:
            chars = iter(arg)
            for char in chars:
                if char == ESCAPE_CHAR:
                    nchar = next(chars, "")
                    if nchar == ESCAPE_CHAR:
                        yield ESCAPE_CHAR
                    else:
                        yield filename
                        yield nchar
                else:
                    yield char

        yield "".join(it())


async def set_preview_content(nvim: Nvim, text: str) -> None:
    def cont() -> None:
        with hold_win_pos(nvim):
            set_preview(nvim, preview=text)

    await async_call(nvim, cont)


async def _linter_output(
    attr: LinterAttrs, cwd: str, filename: str, body: bytes
) -> str:
    args = arg_subst(attr.args, filename=filename)
    if not which(attr.bin):
        return f"⁉️: 莫有 {attr.bin}"
    else:
        proc = await call(attr.bin, *args, stdin=body, cwd=cwd)
        arg_info = f"{attr.bin} {' '.join(attr.args)}"
        if proc.code == attr.exit_code:
            heading = f"✅ 👉 {arg_info}"
        else:
            heading = f"⛔️ - {proc.code} 👉 {arg_info}"
        print_out = linesep.join((heading, proc.out.decode(), proc.err))
        return print_out


async def _run(
    nvim: Nvim, ctx: BufContext, attrs: Iterable[LinterAttrs], cwd: str
) -> None:
    body = linesep.join(ctx.lines).encode()
    outputs = await gather(
        *(
            _linter_output(attr, cwd=cwd, filename=ctx.filename, body=body)
            for attr in attrs
        )
    )
    now = datetime.now().strftime(DATE_FMT)
    preview = f"".join(repeat(linesep, times=2)).join((now, *outputs))
    await set_preview_content(nvim, text=preview)


def _linters_for(filetype: str) -> Iterator[LinterAttrs]:
    for attr in linter_specs:
        if filetype in attr.filetypes:
            yield attr


@rpc(blocking=False)
async def _run_linter(nvim: Nvim) -> None:
    cwd, ctx = await async_call(nvim, current_ctx, nvim)
    linters = tuple(_linters_for(ctx.filetype))
    if not linters:
        await write(nvim, f"⁉️: 莫有 {ctx.filetype} 的 linter", error=True)
    else:
        await _run(nvim, ctx=ctx, attrs=linters, cwd=cwd)


keymap.n("M") << f"<cmd>lua {_run_linter.remote_name}()<cr>"
