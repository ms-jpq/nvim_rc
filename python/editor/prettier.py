from os import environ, linesep, pathsep
from shutil import which
from subprocess import CalledProcessError
from typing import Tuple, cast

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from std2.asyncio.subprocess import call

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..consts import BIN_PATHS
from ..nvim.lib import async_call, write
from ..nvim.preview import set_preview
from ..registery import keymap, rpc
from .linter import arg_subst


async def _run_stream(
    nvim: Nvim,
    buf: Buffer,
    filename: str,
    bin: str,
    attr: FmtAttrs,
    cwd: str,
    PATH: str,
) -> Nvim:
    def c1() -> str:
        return linesep.join(nvim.api.buf_get_lines(buf, 0, -1, True))

    body = await async_call(nvim, c1)
    args = arg_subst(attr.args, filename=filename)
    proc = await call(
        bin,
        *args,
        stdin=body.encode(),
        cwd=cwd,
        env={"PATH": PATH},
        expected_code=attr.exit_code,
    )
    lines = proc.out.decode().splitlines()

    def c2() -> None:
        nvim.api.buf_set_lines(buf, 0, -1, True, lines)

    await async_call(nvim, c2)


async def _run_fs(
    nvim: Nvim,
    buf: Buffer,
    filename: str,
    bin: str,
    attr: FmtAttrs,
    cwd: str,
    PATH: str,
) -> None:
    args = arg_subst(attr.args, filename=filename)
    await call(bin, *args, cwd=cwd, env={"PATH": PATH}, expected_code=attr.exit_code)
    await async_call(nvim, nvim.command, "checktime")


_progs = {FmtType.stream: _run_stream, FmtType.fs: _run_fs}


@rpc()
async def run_fmt(nvim: Nvim) -> None:
    PATH = pathsep.join((BIN_PATHS, environ["PATH"]))

    def cont() -> Tuple[str, Buffer, str, str]:
        cwd = nvim.funcs.getcwd()
        buf: Buffer = nvim.api.get_current_buf()
        filename: str = nvim.api.buf_get_name(buf)
        filetype: str = nvim.api.buf_get_option(buf, "filetype")
        return cwd, buf, filename, filetype

    cwd, buf, filename, filetype = await async_call(nvim, cont)
    for bin, attr in fmt_specs.items():
        if filetype in attr.filetypes:
            if which(bin, path=PATH):
                run = _progs.get(attr.type)
                if not run:
                    raise NotImplementedError()
                else:
                    try:
                        await run(
                            nvim,
                            buf=buf,
                            filename=filename,
                            bin=bin,
                            attr=attr,
                            cwd=cwd,
                            PATH=PATH,
                        )
                    except CalledProcessError as e:
                        heading = f"⛔️ - {e.returncode} 👉 {bin} {' '.join(attr.args)}"
                        stdout = cast(bytes, e.stdout).decode()
                        err_out = f"{heading}{linesep}{stdout}{linesep}{e.stderr}"
                        await async_call(nvim, set_preview, nvim, err_out)
                    else:
                        await write(nvim, f"✅ 👉 {bin}")
            else:
                await write(nvim, f"⁉️: 莫有 {bin}", error=True)
            break
    else:
        await write(nvim, f"⁉️: 莫有 {filetype} 的 prettier", error=True)


keymap.n("gq", nowait=True) << "<cmd>" + run_fmt.call_line() + "<cr>"
