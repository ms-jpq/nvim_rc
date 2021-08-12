from asyncio import gather
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from os import close
from pathlib import Path
from shlex import join
from shutil import which
from tempfile import mkstemp
from typing import Iterable, Iterator, Sequence, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.api import (
    buf_filetype,
    buf_get_lines,
    buf_get_option,
    buf_linefeed,
    buf_name,
    cur_buf,
    get_cwd,
)
from pynvim_pp.hold import hold_win_pos
from pynvim_pp.lib import async_call, awrite
from pynvim_pp.preview import set_preview
from std2.asyncio.subprocess import call
from std2.lex import ParseError, envsubst

from ..config.linter import LinterAttrs, LinterType, linter_specs
from ..consts import DATE_FMT
from ..registery import LANG, keymap, rpc


@dataclass(frozen=True)
class BufContext:
    buf: Buffer
    filename: str
    filetype: str
    tabsize: int
    linefeed: str
    lines: Sequence[str]


def current_ctx(nvim: Nvim) -> Tuple[str, BufContext]:
    cwd = get_cwd(nvim)
    buf = cur_buf(nvim)
    filename = buf_name(nvim, buf=buf)
    filetype = buf_filetype(nvim, buf=buf)
    tabsize: int = buf_get_option(nvim, buf=buf, key="tabstop")
    linefeed = buf_linefeed(nvim, buf=buf)
    lines: Sequence[str] = buf_get_lines(nvim, buf=buf, lo=0, hi=-1)
    return cwd, BufContext(
        buf=buf,
        filename=filename,
        filetype=filetype,
        tabsize=tabsize,
        linefeed=linefeed,
        lines=lines,
    )


def arg_subst(args: Iterable[str], ctx: BufContext, tmp_name: str) -> Sequence[str]:
    env = {
        "tmpname": tmp_name,
        "filename": ctx.filename,
        "filetype": ctx.filetype,
        "tabsize": str(ctx.tabsize),
    }
    return tuple(envsubst(arg, env=env) for arg in args)


@contextmanager
def make_temp(path: Path) -> Iterator[Path]:
    prefix, suffix = f"{path.stem}_", f"_{path.suffix}"
    fd, temp = mkstemp(prefix=prefix, suffix=suffix)
    close(fd)
    new_path = Path(temp)
    try:
        yield new_path
    finally:
        new_path.unlink(missing_ok=True)


def set_preview_content(nvim: Nvim, text: str) -> None:
    with hold_win_pos(nvim):
        set_preview(nvim, syntax="", preview=text.splitlines())


async def _linter_output(
    attr: LinterAttrs, ctx: BufContext, cwd: str, body: bytes, temp: Path
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
            stdin = body if attr.type is LinterType.stream else None
            proc = await call(
                attr.bin,
                *args,
                stdin=stdin,
                cwd=cwd,
                check_returncode=set(),
            )
            if proc.code == attr.exit_code:
                heading = LANG("proc succeeded", args=arg_info)
            else:
                heading = LANG("proc failed", code=proc.code, args=arg_info)
            print_out = ctx.linefeed.join(
                (heading, proc.err.decode(), proc.out.decode())
            )
            return print_out


async def _run(
    nvim: Nvim, ctx: BufContext, attrs: Iterable[LinterAttrs], cwd: str
) -> None:
    body = ctx.linefeed.join(ctx.lines).encode()
    path = Path(ctx.filename)
    with make_temp(path) as temp:
        temp.write_bytes(body)
        outputs = await gather(
            *(
                _linter_output(attr, ctx=ctx, cwd=cwd, body=body, temp=temp)
                for attr in attrs
            )
        )

    now = datetime.now().strftime(DATE_FMT)
    preview = (ctx.linefeed * 2).join(chain((now,), outputs))
    await async_call(nvim, lambda: set_preview_content(nvim, text=preview))


def _linters_for(filetype: str) -> Iterator[LinterAttrs]:
    for attr in linter_specs:
        if filetype in attr.filetypes:
            yield attr


@rpc(blocking=False)
async def _run_linter(nvim: Nvim) -> None:
    cwd, ctx = await async_call(nvim, current_ctx, nvim)
    linters = tuple(_linters_for(ctx.filetype))
    if not linters:
        await awrite(nvim, LANG("missing_linter", filetype=ctx.filetype), error=True)
    else:
        await awrite(nvim, LANG("loading..."))
        await _run(nvim, ctx=ctx, attrs=linters, cwd=cwd)
        await awrite(nvim, "")


keymap.n("M") << f"<cmd>lua {_run_linter.name}()<cr>"
