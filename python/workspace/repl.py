from dataclasses import dataclass
from itertools import chain, count
from math import inf
from os import linesep
from tempfile import NamedTemporaryFile
from typing import Iterator, Optional, Sequence
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.nvim import Buffer
from pynvim_pp.api import (
    ExtMarkBase,
    ask_mc,
    buf_commentstr,
    buf_del_extmarks,
    buf_get_extmarks_base,
    buf_get_lines,
    buf_get_var,
    buf_set_extmarks_base,
    buf_set_var,
    clear_ns,
    create_ns,
    cur_buf,
    cur_win,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.lib import async_call, decode, encode, go
from pynvim_pp.operators import operator_marks
from std2.asyncio.subprocess import call

from ..registery import NAMESPACE, keymap, rpc

_NS = uuid4()
_SEP = "\x1f"
_TMUX_NS = "NVIM-"


@dataclass(frozen=True, order=True)
class _Pane:
    session_name: str
    window_index: int
    window_name: str
    pane_index: int
    pane_title: str

    uid: str

    def __str__(self) -> str:
        return f"S: {self.session_name} -> W: {self.window_index}:{self.window_name} -> {self.pane_index}:{self.pane_title}"


@rpc(blocking=True)
def _marks_clear(nvim: Nvim, visual: bool) -> None:
    ns = create_ns(nvim, ns=_NS)
    buf = cur_buf(nvim)
    if visual:
        (lo, _), (hi, _) = operator_marks(nvim, buf=buf, visual_type=None)
        clear_ns(nvim, id=ns, buf=buf, lo=lo, hi=hi + 1)
    else:
        clear_ns(nvim, id=ns, buf=buf)


_ = keymap.n("<leader>E") << f"<cmd>lua {NAMESPACE}.{_marks_clear.name}(false)<cr>"
_ = (
    keymap.v("<leader>E")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_marks_clear.name}(true)<cr>"
)


@rpc(blocking=True)
def _mark_set(nvim: Nvim, visual: bool) -> None:
    ns = create_ns(nvim, ns=_NS)
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    marks = tuple(buf_get_extmarks_base(nvim, id=ns, buf=buf))
    indices = {mark.idx for mark in marks}
    gen = (i for i in count(1) if i not in indices)
    lcs, rcs = buf_commentstr(nvim, buf=buf)
    cs = ((lcs + rcs) or "#") * 6

    def mk(r: int) -> ExtMarkBase:
        return ExtMarkBase(
            idx=next(gen),
            begin=(r, 0),
            meta={"virt_lines": (((cs, "NormalFloat"),),)},
        )

    if visual:
        (lo, _), (hi, _) = operator_marks(nvim, buf=buf, visual_type=None)

        def cont() -> Iterator[ExtMarkBase]:
            for mark in marks:
                r, _ = mark.begin
                if r <= hi and r >= lo:
                    yield mark

        existing = tuple(cont())
        if existing:
            buf_del_extmarks(nvim, buf=buf, id=ns, marks=existing)
        else:
            m1, m2 = mk(lo), mk(hi)
            buf_set_extmarks_base(nvim, buf=buf, id=ns, marks=(m1, m2))

    else:
        row, _ = win_get_cursor(nvim, win=win)
        for mark in marks:
            r, _ = mark.begin
            if r == row:
                buf_del_extmarks(nvim, buf=buf, id=ns, marks=(mark,))
                break
        else:
            mark = mk(row)
            buf_set_extmarks_base(nvim, buf=buf, id=ns, marks=(mark,))


_ = keymap.n("<leader>e") << f"<cmd>lua {NAMESPACE}.{_mark_set.name}(false)<cr>"
_ = (
    keymap.v("<leader>e")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_mark_set.name}(true)<cr>"
)


async def _ls_panes() -> Sequence[_Pane]:
    proc = await call(
        "tmux",
        "list-panes",
        "-a",
        "-F",
        _SEP.join(
            (
                "#{pane_id}",
                "#{session_name}",
                "#{window_index}",
                "#{window_name}",
                "#{pane_index}",
                "#{pane_title}",
            )
        ),
    )

    def cont() -> Iterator[_Pane]:
        for line in decode(proc.stdout).strip().splitlines():
            (
                pane_id,
                session_name,
                window_index,
                window_name,
                pane_index,
                pane_title,
            ) = line.split(_SEP)
            pane = _Pane(
                uid=pane_id,
                session_name=session_name,
                window_index=int(window_index),
                window_name=window_name,
                pane_index=int(pane_index),
                pane_title=pane_title,
            )
            yield pane

    return tuple(cont())


async def _pane(nvim: Nvim, buf: Buffer) -> Optional[str]:
    panes = sorted(await _ls_panes())

    def cont() -> None:
        answers = linesep.join(f"{idx} {pane}" for idx, pane in enumerate(panes))
        answer_key = {k: v for k, v in enumerate(panes)}
        pane = ask_mc(nvim, question="-->", answers=answers, answer_key=answer_key)
        if pane:
            buf_set_var(nvim, buf=buf, key=str(_NS), val=pane.uid)
            return pane.uid
        else:
            return pane

    await async_call(nvim, cont)


def _tmux_send(nvim: Nvim, buf: Buffer, text: str) -> None:
    pane = buf_get_var(nvim, buf=buf, key=str(_NS))

    async def cont() -> None:
        if t_pane := pane or await _pane(nvim, buf=buf):
            name = f"{_TMUX_NS}-{uuid4()}"
            with NamedTemporaryFile() as fd:
                fd.write(encode(text))
                fd.flush()
                await call("tmux", "load-buffer", "-b", name, "--", fd.name)
                await call("tmux", "paste-buffer", "-d", "-r", "-b", name, "-t", t_pane)

    go(nvim, aw=cont())


@rpc(blocking=True)
def _eval(nvim: Nvim, visual: bool) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    if visual:
        (begin, _), (end, _) = operator_marks(nvim, buf=buf, visual_type=None)
    else:
        ns = create_ns(nvim, ns=_NS)
        row, _ = win_get_cursor(nvim, win=win)
        marks = tuple(buf_get_extmarks_base(nvim, id=ns, buf=buf))
        begin, end = 0, None
        for mark in marks:
            r, _ = mark.begin
            if r < row:
                begin = max(begin, r)
            else:
                end = int(min(end or inf, r))

    lines = buf_get_lines(nvim, buf=buf, lo=begin, hi=end or -2 + 1)
    _tmux_send(nvim, buf=buf, text=linesep.join(lines))


_ = keymap.n("<leader>g") << f"<cmd>lua {NAMESPACE}.{_eval.name}(false)<cr>"
_ = keymap.v("<leader>g") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_eval.name}(true)<cr>"
