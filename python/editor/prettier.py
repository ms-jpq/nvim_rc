from os import linesep
from shutil import which
from subprocess import CalledProcessError
from typing import Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from std2.asyncio.subprocess import call

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..nvim.lib import async_call, write
from ..registery import keymap, rpc
from .linter import arg_subst


async def _run_stream(
    nvim: Nvim,
    buf: Buffer,
    filename: str,
    bin: str,
    attr: FmtAttrs,
    cwd: str,
) -> Nvim:
    def cont() -> str:
        return linesep.join(nvim.api.buf_get_lines(buf, 0, -1, True))

    body = await async_call(nvim, cont)
    args = arg_subst(attr.args, filename=filename)
    proc = await call(
        bin, *args, stdin=body.encode(), cwd=cwd, expected_code=attr.exit_code
    )


async def _run_fs(
    nvim: Nvim,
    buf: Buffer,
    filename: str,
    bin: str,
    attr: FmtAttrs,
    cwd: str,
) -> None:
    args = arg_subst(attr.args, filename=filename)
    proc = await call(bin, *args, cwd=cwd, expected_code=attr.exit_code)


@rpc()
async def run_fmt(nvim: Nvim) -> None:
    def cont() -> Tuple[str, Buffer, str, str]:
        cwd = nvim.funcs.getcwd()
        buf: Buffer = nvim.api.get_current_buf()
        filename: str = nvim.api.buf_get_name(buf)
        filetype: str = nvim.api.buf_get_option(buf, "filetype")
        return cwd, buf, filename, filetype

    cwd, buf, filename, filetype = await async_call(nvim, cont)
    for bin, attr in fmt_specs.items():
        if filetype in attr.filetypes:
            if which(bin):
                try:
                    if attr.type == FmtType.stream:
                        await _run_stream(
                            nvim,
                            buf=buf,
                            filename=filename,
                            bin=bin,
                            attr=attr,
                            cwd=cwd,
                        )
                    elif attr.type == FmtType.fs:
                        await _run_fs(
                            nvim,
                            buf=buf,
                            filename=filename,
                            bin=bin,
                            attr=attr,
                            cwd=cwd,
                        )
                    elif attr.type == FmtType.lsp:
                        raise NotImplementedError()
                    else:
                        assert False
                except CalledProcessError:
                    pass
            else:
                await write(nvim, f"⁉️: 莫有 {bin}", error=True)
            break
    else:
        await write(nvim, f"⁉️: 莫有 {filetype} 的 linter", error=True)


keymap.n("gq", nowait=True) << "<cmd>" + run_fmt.call_line() + "<cr>"
