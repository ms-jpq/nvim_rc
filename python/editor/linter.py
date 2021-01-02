from asyncio import gather
from datetime import datetime, timezone
from itertools import repeat
from os import linesep
from shutil import which
from typing import Iterable, Iterator, Sequence, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.lib import async_call, write
from pynvim_pp.preview import set_preview
from std2.asyncio.subprocess import call

from ..config.linter import LinterAttrs, linter_specs
from ..consts import DATE_FMT
from ..registery import keymap, rpc

ESCAPE_CHAR = "%"


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


async def _run(nvim: Nvim, buf: Buffer, attrs: Iterable[LinterAttrs]) -> None:
    def cont() -> Tuple[str, str, bytes]:
        cwd = nvim.funcs.getcwd()
        filename: str = nvim.api.buf_get_name(buf)
        lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)
        body = linesep.join(lines).encode()
        return cwd, filename, body

    cwd, filename, body = await async_call(nvim, cont)
    outputs = await gather(
        *(_linter_output(attr, cwd=cwd, filename=filename, body=body) for attr in attrs)
    )
    now = datetime.now(tz=timezone.utc).strftime(DATE_FMT)
    preview = f"".join(repeat(linesep, times=2)).join((now, *outputs))
    await async_call(nvim, set_preview, nvim, preview)


def _linters_for(filetype: str) -> Iterator[LinterAttrs]:
    for attr in linter_specs:
        if filetype in attr.filetypes:
            yield attr


@rpc(blocking=False)
async def _run_linter(nvim: Nvim) -> None:
    def cont() -> Tuple[Buffer, str]:
        buf: Buffer = nvim.api.get_current_buf()
        filetype: str = nvim.api.buf_get_option(buf, "filetype")
        return buf, filetype

    buf, filetype = await async_call(nvim, cont)
    linters = tuple(_linters_for(filetype))
    if not linters:
        await write(nvim, f"⁉️: 莫有 {filetype} 的 linter", error=True)
    else:
        await _run(nvim, buf=buf, attrs=linters)


keymap.n("M") << f"<cmd>lua {_run_linter.remote_name}()<cr>"
