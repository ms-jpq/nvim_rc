from os import environ, linesep, pathsep
from shutil import which
from subprocess import CalledProcessError
from typing import Iterable, Iterator, Optional, Tuple, cast

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from std2.asyncio.subprocess import call

from ..config.linter import LinterAttrs, LinterType, linter_specs
from ..consts import BIN_PATHS
from ..nvim.lib import async_call, write
from ..nvim.preview import set_preview
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


async def _run(nvim: Nvim, buf: Buffer, attr: LinterAttrs, PATH: str) -> None:
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
    try:
        await call(
            attr.bin,
            *args,
            stdin=body,
            cwd=cwd,
            env={"PATH": PATH},
            expected_code=attr.exit_code,
        )
    except CalledProcessError as e:
        heading = f"⛔️ - {e.returncode} 👉 {attr.bin} {' '.join(attr.args)}"
        stdout = cast(bytes, e.stdout).decode()
        err_out = f"{heading}{linesep}{stdout}{linesep}{e.stderr}"
        await async_call(nvim, set_preview, nvim, err_out)
    else:
        await write(nvim, f"✅ 👉 {attr.bin} {' '.join(attr.args)}")


@rpc(blocking=False)
async def _run_linter(nvim: Nvim) -> None:
    PATH = pathsep.join((BIN_PATHS, environ["PATH"]))

    def cont() -> Tuple[Buffer, str]:
        buf: Buffer = nvim.api.get_current_buf()
        filetype: str = nvim.api.buf_get_option(buf, "filetype")
        return buf, filetype

    buf, filetype = await async_call(nvim, cont)
    for attr in linter_specs:
        if filetype in attr.filetypes:
            if which(attr.bin, path=PATH):
                await _run(nvim, buf=buf, attr=attr, PATH=PATH)
            else:
                await write(nvim, f"⁉️: 莫有 {attr.bin}", error=True)
            break
    else:
        await write(nvim, f"⁉️: 莫有 {filetype} 的 linter", error=True)


keymap.n("M") << f"<cmd>lua {_run_linter.lua_name}()<cr>"
