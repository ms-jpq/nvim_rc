from asyncio import create_task
from contextlib import asynccontextmanager, suppress
from functools import cache
from itertools import count
from math import inf
from os import environ, linesep
from pathlib import PurePath
from shutil import which
from subprocess import CalledProcessError
from typing import AsyncIterator, Iterator, Mapping, Optional, Sequence, Tuple
from uuid import uuid4

from pynvim_pp.buffer import Buffer, ExtMark, ExtMarker
from pynvim_pp.lib import decode, encode
from pynvim_pp.logging import suppress_and_log
from pynvim_pp.nvim import Nvim
from pynvim_pp.operators import operator_marks
from pynvim_pp.types import NoneType
from pynvim_pp.window import Window
from std2.asyncio.subprocess import call

from ..consts import TOP_LEVEL
from ..registry import LANG, NAMESPACE, keymap, rpc

_REPL_SCRIPTS = TOP_LEVEL / "repl"

_SEP = "\x1f"

_NS = uuid4()
_HNS = uuid4()
_TMUX_NS = f"NVIM-#{_NS}"

_TEXT_HL = "Normal"
_LINE_HL = "Cursor"


@rpc()
async def _marks_clear(visual: bool) -> None:
    ns = await Nvim.create_namespace(_NS)
    buf = await Buffer.get_current()
    if visual:
        (lo, _), (hi, _) = await operator_marks(buf, visual_type=None)
        await buf.clear_namespace(ns, lo=lo, hi=hi + 1)
    else:
        await buf.clear_namespace(ns)
        await buf.vars.set(str(_NS), val=None)


_ = keymap.n("<leader>E") << f"<cmd>lua {NAMESPACE}.{_marks_clear.method}(false)<cr>"
_ = (
    keymap.v("<leader>E")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_marks_clear.method}(true)<cr>"
)


@rpc()
async def _mark_set(visual: bool) -> None:
    ns = await Nvim.create_namespace(_NS)
    win = await Window.get_current()
    buf = await win.get_buf()

    marks = await buf.get_extmarks(ns)
    indices = {mark.marker for mark in marks}
    gen = map(ExtMarker, (i for i in count(1) if i not in indices))
    lcs, rcs = (await buf.commentstr()) or ("", "")
    cs = lcs + LANG("repl") + rcs

    def mk(r: int) -> ExtMark:
        return ExtMark(
            buf=buf,
            marker=next(gen),
            begin=(r, 0),
            end=None,
            meta={
                "virt_text": ((cs, _TEXT_HL),),
                "virt_text_pos": "right_align",
                "hl_mode": "combine",
                "line_hl_group": _LINE_HL,
            },
        )

    if visual:
        (lo, _), (hi, _) = await operator_marks(buf, visual_type=None)

        def cont() -> Iterator[ExtMarker]:
            for mark in marks:
                r, _ = mark.begin
                if r <= hi and r >= lo:
                    yield mark.marker

        existing = tuple(cont())
        if existing:
            await buf.del_extmarks(ns, markers=existing)
        else:
            m1, m2 = mk(lo), mk(hi)
            await buf.set_extmarks(ns, extmarks=(m1, m2))

    else:
        row, _ = await win.get_cursor()
        for mark in marks:
            r, _ = mark.begin
            if r == row:
                await buf.del_extmarks(ns, markers=(mark.marker,))
                break
        else:
            mark = mk(row)
            await buf.set_extmarks(ns, extmarks=(mark,))


_ = keymap.n("<leader>e") << f"<cmd>lua {NAMESPACE}.{_mark_set.method}(false)<cr>"
_ = (
    keymap.v("<leader>e")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_mark_set.method}(true)<cr>"
)


async def _pane(tmux: PurePath, buf: Buffer) -> Optional[str]:
    pane_id = environ.get("TMUX_PANE")

    try:
        p1 = await call(tmux, "display-message", "-p", "-F", "#{window_id}")
        p2 = await call(
            tmux,
            "list-panes",
            "-a",
            "-F",
            _SEP.join(
                (
                    "#{pane_id}",
                    "#{window_id}",
                    "#{window_active}",
                    "#{session_name} -> #{window_index} -> #{pane_index}",
                )
            ),
        )
    except CalledProcessError as e:
        await Nvim.write(e, e.stderr, e.stdout)
        return None
    else:
        win_id = decode(p1.stdout).strip()

        def c1() -> Iterator[tuple[bool, bool, int, str, str]]:
            for idx, line in enumerate(decode(p2.stdout).splitlines()):
                p_id, w_id, w_active, show = line.split(_SEP, maxsplit=3)
                local, active = w_id == win_id, int(w_active)

                def cont() -> Iterator[str]:
                    yield show
                    if local:
                        yield "✱"
                    elif active:
                        yield "◉"

                if p_id != pane_id:
                    line = " ".join(cont())
                    yield not active, not local, idx, p_id, line

        def c2() -> Iterator[Tuple[str, str]]:
            for idx, (_, _, _, p_id, line) in enumerate(sorted(c1()), start=1):
                yield f"({idx}) {line}", p_id

    if pane := await Nvim.input_list({k: v for k, v in c2()}):
        await buf.vars.set(str(_NS), val=pane)
        return pane
    else:
        return None


async def _tmux_send(buf: Buffer, text: bytes) -> None:
    if tmux := which("tmux"):
        mux = PurePath(tmux)
        if pane := await buf.vars.get(str, str(_NS)) or await _pane(mux, buf=buf):
            try:
                await call(mux, "load-buffer", "-b", _TMUX_NS, "--", "-", stdin=text)
                await call(
                    mux,
                    "paste-buffer",
                    "-r",
                    "-p",
                    "-t",
                    pane,
                    "-b",
                    _TMUX_NS,
                )
                await call(
                    mux, "load-buffer", "-b", _TMUX_NS, "--", "-", stdin=encode(linesep)
                )
                await call(mux, "paste-buffer", "-d", "-r", "-b", _TMUX_NS, "-t", pane)
            except CalledProcessError as e:
                await Nvim.write(e, e.stderr, e.stdout)
                with suppress(CalledProcessError):
                    await call(mux, "delete-buffer", "-b", _TMUX_NS)


@asynccontextmanager
async def _highlight(
    buf: Buffer, begin: int, lines: Sequence[str]
) -> AsyncIterator[None]:
    hns = await Nvim.create_namespace(_HNS)
    *_, line = lines or ("",)
    end_c = len(encode(line))
    await Nvim.lua.vim.highlight.range(
        NoneType,
        buf,
        hns,
        "HighlightedyankRegion",
        (begin, 0),
        (max(0, begin + len(lines) - 1), end_c),
        {"inclusive": False},
    )

    yield None

    await buf.clear_namespace(hns)


@cache
def _scripts() -> Mapping[str, PurePath]:
    return {
        "" if path.stem == path.name else path.stem: path
        for path in _REPL_SCRIPTS.iterdir()
    }


async def _process(filetype: str, lines: Sequence[str]) -> Optional[bytes]:
    text = encode(linesep.join(lines))
    if script := _scripts().get(filetype) or _scripts().get("_"):
        try:
            proc = await call(script, stdin=text)
        except CalledProcessError as e:
            await Nvim.write(e, e.stderr, e.stdout)
            return None
        else:
            return proc.stdout
    else:
        return text


@rpc()
async def _eval(visual: bool) -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    filetype = await buf.filetype()

    if visual:
        (begin, _), (end, _) = await operator_marks(buf, visual_type=None)
    else:
        ns = await Nvim.create_namespace(_NS)
        row, _ = await win.get_cursor()
        marks = await buf.get_extmarks(ns)
        begin, end = 0, None
        for mark in marks:
            r, _ = mark.begin
            if r < row:
                begin = max(begin, r)
            else:
                end = int(min(end or inf, r))

    lo, hi = max(0, begin), -1 if end is None else min(await buf.line_count(), end + 1)
    lines = await buf.get_lines(lo=lo, hi=hi)

    async def cont() -> None:
        with suppress_and_log():
            if text := await _process(filetype, lines=lines):
                async with _highlight(buf, begin=begin, lines=lines):
                    await _tmux_send(buf, text=text)

    create_task(cont())


_ = keymap.n("<leader>g") << f"<cmd>lua {NAMESPACE}.{_eval.method}(false)<cr>"
_ = keymap.v("<leader>g") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_eval.method}(true)<cr>"
