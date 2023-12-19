from asyncio import gather
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from itertools import chain
from os.path import normpath
from pathlib import Path, PurePath
from shlex import join
from shutil import which
from tempfile import NamedTemporaryFile
from typing import Iterable, Iterator, Sequence, Tuple

from pynvim_pp.buffer import Buffer
from pynvim_pp.hold import hold_win
from pynvim_pp.lib import decode, encode
from pynvim_pp.nvim import Nvim
from pynvim_pp.preview import set_preview
from std2.asyncio.subprocess import call
from std2.lex import ParseError, envsubst

from ..config.linter import LinterAttrs, LinterType, linter_specs
from ..consts import DATE_FMT
from ..registry import LANG, NAMESPACE, keymap, rpc


@dataclass(frozen=True)
class BufContext:
    buf: Buffer
    filename: str
    filetype: str
    tabsize: int
    linefeed: str
    lines: Sequence[str]


async def current_ctx() -> Tuple[PurePath, BufContext]:
    cwd = await Nvim.getcwd()
    buf = await Buffer.get_current()
    filename = await buf.get_name()
    filetype = await buf.filetype()
    tabsize = await buf.opts.get(int, "tabstop")
    linefeed = await buf.linefeed()
    lines = await buf.get_lines()

    return cwd, BufContext(
        buf=buf,
        filename=filename or "",
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
def mktemp(path: Path, text: bytes) -> Iterator[Path]:
    prefix, suffix = f"{path.stem}-", f"-{path.suffix}"
    with NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False) as temp:
        temp.write(text)
        temp.close()
        tmp = Path(temp.name)
        try:
            yield tmp
        finally:
            tmp.unlink()


async def set_preview_content(text: str) -> None:
    async with hold_win(win=None):
        await set_preview(syntax="", preview=text.splitlines())


async def _linter_output(
    attr: LinterAttrs, ctx: BufContext, cwd: PurePath, body: bytes, temp: Path
) -> str:
    arg_info = join(chain((attr.bin,), attr.args))

    try:
        args = arg_subst(attr.args, ctx=ctx, tmp_name=normpath(temp))
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
                env=attr.env,
                stdin=stdin,
                cwd=cwd,
                check_returncode=set(),
            )
            if proc.returncode == attr.exit_code:
                heading = LANG("proc succeeded", args=arg_info)
            else:
                heading = LANG("proc failed", code=proc.returncode, args=arg_info)
            print_out = ctx.linefeed.join(
                (
                    heading,
                    decode(proc.stderr),
                    decode(proc.stdout),
                )
            )
            return print_out


async def _run(ctx: BufContext, attrs: Iterable[LinterAttrs], cwd: PurePath) -> None:
    body = encode(ctx.linefeed.join(ctx.lines))
    path = Path(ctx.filename)
    with mktemp(path, text=body) as temp:
        outputs = await gather(
            *(
                _linter_output(attr, ctx=ctx, cwd=cwd, body=body, temp=temp)
                for attr in attrs
            )
        )

    now = datetime.now().strftime(DATE_FMT)
    preview = (ctx.linefeed * 2).join(chain((now,), outputs))
    await set_preview_content(preview)


def _linters_for(filetype: str) -> Iterator[LinterAttrs]:
    for attr in linter_specs:
        for pat in attr.filetypes:
            if fnmatch(filetype, pat=pat):
                yield attr
                break


@rpc(blocking=False)
async def _run_linter() -> None:
    cwd, ctx = await current_ctx()
    linters = tuple(_linters_for(ctx.filetype))
    if not linters:
        await Nvim.write(LANG("missing_linter", filetype=ctx.filetype), error=True)
    else:
        await Nvim.write(LANG("loading..."))
        await _run(ctx, attrs=linters, cwd=cwd)
        await Nvim.write("")


_ = keymap.n("B") << f"<cmd>lua {NAMESPACE}.{_run_linter.method}()<cr>"
