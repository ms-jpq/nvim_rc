from contextlib import suppress
from fnmatch import fnmatch
from itertools import chain
from os.path import normcase, normpath
from pathlib import Path, PurePath
from shlex import join
from typing import AsyncIterator, Iterable, Iterator, Tuple

from pynvim_pp.lib import decode, encode
from pynvim_pp.nvim import Nvim
from pynvim_pp.rpc_types import NvimError
from pynvim_pp.types import NoneType
from pynvim_pp.window import Window
from std2.aitertools import aiterify
from std2.asyncio.subprocess import call
from std2.lex import ParseError

from ..config.fmt import FmtAttrs, FmtType, fmt_specs
from ..config.install import which
from ..registry import LANG, NAMESPACE, keymap, rpc
from .linter import BufContext, arg_subst, current_ctx, mktemp, set_preview_content
from .whitespace import detect_tabs, trailing_ws

_LSP_NOTIFY = (
    Path(__file__).resolve(strict=True).with_name("lsp_notify.lua").read_text("UTF-8")
)


async def _fmt_output(
    attr: FmtAttrs, ctx: BufContext, cwd: PurePath, temp: Path
) -> str:
    arg_info = join(chain((attr.bin.as_posix(),), attr.args))

    try:
        args = arg_subst(attr.args, ctx=ctx, tmp_name=normcase(temp))
    except ParseError:
        return LANG("grammar error", text=arg_info)
    else:
        if not which(attr.bin):
            return LANG("missing", thing=normpath(attr.bin))
        else:
            stdin = temp.read_bytes() if attr.type is FmtType.stream else None
            try:
                proc = await call(
                    "env",
                    "--",
                    attr.bin,
                    *args,
                    env=attr.env,
                    stdin=stdin,
                    cwd=cwd,
                    check_returncode=set(),
                )
            except OSError as e:
                heading = LANG("proc failed", code=-e.errno, args=arg_info)
                print_out = ctx.linefeed.join((heading, str(e)))
                return print_out
            else:
                if attr.type is FmtType.stream:
                    temp.write_bytes(proc.stdout)

                if proc.returncode == attr.exit_code:
                    return ""
                else:
                    heading = LANG("proc failed", code=proc.returncode, args=arg_info)
                    print_out = ctx.linefeed.join((heading, decode(proc.stderr)))
                    return print_out


async def _run(ctx: BufContext, attrs: Iterable[FmtAttrs], cwd: PurePath) -> None:
    body = encode(ctx.linefeed.join(ctx.lines))
    path = Path(ctx.filename)
    with mktemp(path, text=body) as temp:
        errs = [
            err
            async for err in aiterify(
                _fmt_output(attr, ctx=ctx, cwd=cwd, temp=temp) for attr in attrs
            )
            if err
        ]
        if errors := (ctx.linefeed * 2).join(errs):
            await ctx.buf.opts.set("modifiable", True)
            await set_preview_content(errors)
            await Nvim.write(LANG("prettier failed"))

        else:

            async def it() -> AsyncIterator[Tuple[Window, Tuple[int, int]]]:
                wins = await Window.list()
                for win in wins:
                    buf = await win.get_buf()
                    if buf == ctx.buf:
                        row, col = await win.get_cursor()
                        yield win, (row, col)

            saved = {win: pos async for win, pos in it()}

            if lines := temp.read_text().splitlines():
                if line := lines.pop():
                    lines.append(line)

            await ctx.buf.opts.set("modifiable", True)
            await ctx.buf.set_lines(lo=0, hi=-1, lines=lines)

            for win, (row, col) in saved.items():
                new_row = min(row, len(lines) - 1)
                with suppress(NvimError):
                    await win.set_cursor(row=new_row, col=col)

            await detect_tabs(ctx.buf)

            prettiers = LANG("step join sep").join(normpath(attr.bin) for attr in attrs)
            nice = LANG("prettier succeeded", prettiers=prettiers)
            await Nvim.write(nice)


def _fmts_for(filetype: str) -> Iterator[FmtAttrs]:
    for attr in fmt_specs():
        for pat in attr.filetypes:
            if fnmatch(filetype, pat=pat):
                yield attr
                break


@rpc(blocking=False)
async def run_fmt() -> None:
    cwd, ctx = await current_ctx()

    prettiers = tuple(_fmts_for(ctx.filetype))
    if not prettiers:
        await trailing_ws()
        await Nvim.write(LANG("basic prettier", filetype=ctx.filetype))
    else:
        await Nvim.write(LANG("loading..."))

        await ctx.buf.opts.set("modifiable", False)
        await _run(ctx, attrs=prettiers, cwd=cwd)

    await Nvim.api.execute_lua(NoneType, _LSP_NOTIFY, (ctx.linefeed,))


_ = keymap.n("gq", nowait=True) << f"<cmd>lua {NAMESPACE}.{run_fmt.method}()<cr>"
