from asyncio import gather
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from os import close, linesep
from pathlib import Path
from shutil import which
from tempfile import mkstemp
from typing import Iterable, Iterator, MutableSequence, Sequence, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.api import buf_filetype, buf_get_lines, buf_get_option, buf_name, cur_buf, get_cwd
from pynvim_pp.hold import hold_win_pos
from pynvim_pp.lib import async_call, awrite
from pynvim_pp.preview import set_preview
from std2.asyncio.subprocess import call

from ..config.linter import LinterAttrs, LinterType, linter_specs
from ..consts import DATE_FMT
from ..registery import LANG, keymap, rpc


@dataclass(frozen=True)
class BufContext:
    buf: Buffer
    filename: str
    filetype: str
    tabsize: int
    lines: Sequence[str]


def current_ctx(nvim: Nvim) -> Tuple[str, BufContext]:
    cwd = get_cwd(nvim)
    buf = cur_buf(nvim)
    filename = buf_name(nvim, buf=buf)
    filetype = buf_filetype(nvim, buf=buf)
    tabsize: int = buf_get_option(nvim, buf=buf, key="tabstop")
    lines: Sequence[str] = buf_get_lines(nvim, buf=buf, lo=0, hi=-1)
    return cwd, BufContext(
        buf=buf, filename=filename, filetype=filetype, tabsize=tabsize, lines=lines
    )


class ParseError(Exception):
    ...


def arg_subst(args: Iterable[str], ctx: BufContext, filename: str) -> Iterator[str]:
    def var_sub(arg: str, name: str) -> str:
        if name == "filename":
            return filename
        elif name == "filetype":
            return ctx.filetype
        elif name == "tabsize":
            return str(ctx.tabsize)
        else:
            raise ParseError(arg)

    def subst(arg: str) -> Iterator[str]:
        it = iter(arg)
        for c in it:
            if c == "$":
                nc = next(it, "")
                if nc == "$":
                    yield nc
                elif nc == "{":
                    chars: MutableSequence[str] = []
                    for c in it:
                        if c == "}":
                            name = "".join(chars)
                            yield var_sub(arg, name=name)
                            break
                        else:
                            chars.append(c)
                    else:
                        raise ParseError(arg)
                else:
                    raise ParseError(arg)
            else:
                yield c

    for arg in args:
        yield "".join(subst(arg))


@contextmanager
def make_temp(path: Path) -> Iterator[Path]:
    fd, temp = mkstemp(prefix=path.stem, suffix=path.suffix, dir=path.parent)
    close(fd)
    new_path = Path(temp)
    try:
        yield new_path
    finally:
        new_path.unlink(missing_ok=True)


async def set_preview_content(nvim: Nvim, text: str) -> None:
    def cont() -> None:
        with hold_win_pos(nvim):
            set_preview(nvim, preview=text)

    await async_call(nvim, cont)


async def _linter_output(
    attr: LinterAttrs, ctx: BufContext, cwd: str, body: bytes, temp: Path
) -> str:
    arg_info = f"{attr.bin} {' '.join(attr.args)}"

    try:
        args = arg_subst(attr.args, ctx=ctx, filename=str(temp))
    except ParseError:
        return LANG("grammar error", text=arg_info)
    else:
        if not which(attr.bin):
            return LANG("missing", thing=attr.bin)
        else:
            stdin = body if attr.type is LinterType.stream else None
            proc = await call(attr.bin, *args, stdin=stdin, cwd=cwd)
            if proc.code == attr.exit_code:
                heading = LANG("proc succeeded", args=arg_info)
            else:
                heading = LANG("proc failed", code=proc.code, args=arg_info)
            print_out = linesep.join((heading, proc.out.decode(), proc.err))
            return print_out


async def _run(
    nvim: Nvim, ctx: BufContext, attrs: Iterable[LinterAttrs], cwd: str
) -> None:
    body = linesep.join(ctx.lines).encode()
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
    preview = (linesep * 2).join(chain((now,), outputs))
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
        await awrite(nvim, LANG("missing_linter", filetype=ctx.filetype), error=True)
    else:
        await awrite(nvim, LANG("loading..."))
        await _run(nvim, ctx=ctx, attrs=linters, cwd=cwd)
        await awrite(nvim, "")


keymap.n("M") << f"<cmd>lua {_run_linter.name}()<cr>"
