from asyncio import gather
from dataclasses import dataclass
from datetime import datetime
from os import linesep
from shutil import which
from typing import Iterable, Iterator, MutableSequence, Sequence, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.hold import hold_win_pos
from pynvim_pp.lib import async_call, write
from pynvim_pp.preview import set_preview
from std2.asyncio.subprocess import call

from ..config.linter import LinterAttrs, LinterType, linter_specs
from ..consts import DATE_FMT
from ..registery import keymap, rpc


@dataclass(frozen=True)
class BufContext:
    buf: Buffer
    filename: str
    filetype: str
    tabsize: int
    lines: Sequence[str]


def current_ctx(nvim: Nvim) -> Tuple[str, BufContext]:
    cwd = nvim.funcs.getcwd()
    buf: Buffer = nvim.api.get_current_buf()
    filename: str = nvim.api.buf_get_name(buf)
    filetype: str = nvim.api.buf_get_option(buf, "filetype")
    tabsize: int = nvim.api.buf_get_option(buf, "tabstop")
    lines: Sequence[str] = nvim.api.buf_get_lines(buf, 0, -1, True)
    return cwd, BufContext(
        buf=buf, filename=filename, filetype=filetype, tabsize=tabsize, lines=lines
    )


class ParseError(Exception):
    ...


def arg_subst(args: Iterable[str], ctx: BufContext) -> Iterator[str]:
    def var_sub(arg: str, name: str) -> str:
        if name == "filename":
            yield ctx.filename
        elif name == "filetype":
            yield ctx.filetype
        elif name == "tabsize":
            yield str(ctx.tabsize)
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


async def set_preview_content(nvim: Nvim, text: str) -> None:
    def cont() -> None:
        with hold_win_pos(nvim):
            set_preview(nvim, preview=text)

    await async_call(nvim, cont)


async def _linter_output(
    attr: LinterAttrs, ctx: BufContext, cwd: str, body: bytes
) -> str:
    args = arg_subst(attr.args, ctx=ctx)
    if not which(attr.bin):
        return f"⁉️: 莫有 {attr.bin}"
    else:
        stdin = body if attr.type is LinterType.stream else None
        proc = await call(attr.bin, *args, stdin=stdin, cwd=cwd)
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
        *(_linter_output(attr, ctx=ctx, cwd=cwd, body=body) for attr in attrs)
    )
    now = datetime.now().strftime(DATE_FMT)
    preview = (linesep * 2).join((now, *outputs))
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


keymap.n("M") << f"<cmd>lua {_run_linter.name}()<cr>"
