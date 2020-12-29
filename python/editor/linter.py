from os import linesep
from shutil import which
from typing import Iterable, Iterator, Optional, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from std2.asyncio.subprocess import call

from ..config.linter import LinterAttrs, LinterType, linter_specs
from ..nvim.lib import async_call, write
from ..nvim.preview import set_preview
from ..registery import keymap, rpc


def arg_subst(args: Iterable[str], filename: str) -> Iterator[str]:
    for arg in args:
        if arg == "%":
            yield filename
        elif arg == "%%":
            yield "%"
        else:
            yield arg


async def _run(
    nvim: Nvim,
    buf: Buffer,
    bin: str,
    attr: LinterAttrs,
) -> None:
    def cont() -> Tuple[str, str, Optional[bytes]]:
        cwd = nvim.funcs.getcwd()
        filename: str = nvim.api.buf_get_name(buf)
        body = (
            linesep.join(nvim.api.buf_get_lines(buf, 0, -1, True)).encode()
            if attr.type == LinterType.stream
            else None
        )
        return cwd, filename, body

    cwd, filename, body = await async_call(nvim, cont)
    args = arg_subst(attr.args, filename=filename)
    proc = await call(bin, *args, stdin=body, cwd=cwd)
    if proc.code == attr.exit_code:
        await write(nvim, f"✅ 👉 {bin}")
    else:
        await async_call(nvim, set_preview, nvim, proc.out.decode() + proc.err)


@rpc()
async def run_linter(nvim: Nvim) -> None:
    def cont() -> Tuple[Buffer, str]:
        buf: Buffer = nvim.api.get_current_buf()
        filetype: str = nvim.api.buf_get_option(buf, "filetype")
        return buf, filetype

    buf, filetype = await async_call(nvim, cont)
    for bin, attr in linter_specs.items():
        if filetype in attr.filetypes:
            if which(bin):
                await _run(nvim, buf=buf, bin=bin, attr=attr)
            else:
                await write(nvim, f"⁉️: 莫有 {bin}", error=True)
            break
    else:
        await write(nvim, f"⁉️: 莫有 {filetype} 的 linter", error=True)


keymap.n("M") << "<cmd>" + run_linter.call_line() + "<cr>"
