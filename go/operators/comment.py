from typing import Iterable, Iterator, Optional, Sequence, Tuple

from pynvim_pp.buffer import Buffer
from pynvim_pp.operators import VisualTypes, operator_marks
from pynvim_pp.window import Window

from ..registery import NAMESPACE, keymap, rpc, settings

settings["commentstring"] = r"#\ %s"


def _p_indent(line: str) -> str:
    def cont() -> Iterator[str]:
        for c in line:
            if c.isspace():
                yield c
            else:
                break

    spaces = "".join(cont())
    return spaces


def _p_indents(lines: Iterable[str]) -> Iterator[Tuple[str, str]]:
    for line in lines:
        if line:
            enil = "".join(reversed(line))
            indent_f, indent_b = _p_indent(line), "".join(reversed(_p_indent(enil)))
            yield indent_f, indent_b


def _comm(
    lhs: str, rhs: str, lines: Sequence[str]
) -> Iterator[Tuple[Optional[bool], str, str, str]]:
    assert len((lhs + rhs).splitlines()) == 1
    assert lhs.lstrip() == lhs and rhs.rstrip() == rhs
    l, r = len(lhs), len(rhs)
    ll, rr = lhs.rstrip(), rhs.lstrip()

    indents = {front: back for front, back in _p_indents(lines)}
    indent_f = next(iter(sorted(indents.keys(), key=len)), "")
    indent_b = next(iter(sorted(indents.values(), key=len)), "")

    for line in lines:
        if not line:
            yield None, "", "", ""
        else:
            significant = line[len(indent_f) : len(line) - len(indent_b)]

            is_comment = significant.startswith(ll) and significant.endswith(rr)
            added = indent_f + lhs + significant + rhs + indent_b[r:]
            stripped = indent_f + significant[l : len(significant) - r] + indent_b

            yield is_comment, line, added, stripped


def _toggle_comment(lhs: str, rhs: str, lines: Sequence[str]) -> Sequence[str]:
    commented = tuple(_comm(lhs, rhs, lines=lines))
    if all(com for com, _, _, _ in commented if com is not None):
        return tuple(stripped for _, _, _, stripped in commented)
    elif any(com for com, _, _, _ in commented if com is not None):
        return tuple(
            original if com else added for com, original, added, _ in commented
        )
    else:
        return tuple(added for _, _, added, _ in commented)


@rpc()
async def _comment(visual: VisualTypes) -> None:
    buf = await Buffer.get_current()
    if not await buf.modifiable():
        return
    else:
        (row1, _), (row2, _) = await operator_marks(buf, visual_type=visual)
        lines = await buf.get_lines(lo=row1, hi=row2 + 1)
        if commentstr := await buf.commentstr():
            lhs, rhs = commentstr
            new_lines = _toggle_comment(lhs, rhs, lines=lines)
            await buf.set_lines(lo=row1, hi=row2 + 1, lines=new_lines)


_ = keymap.n("gc") << f"<cmd>set opfunc={_comment.method}<cr>g@"
_ = keymap.v("gc") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_comment.method}(vim.NIL)<cr>"


@rpc()
async def _comment_single() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    if not await buf.modifiable():
        return
    else:
        row, _ = await win.get_cursor()
        lines = await buf.get_lines(lo=row, hi=row + 1)
        if commentstr := await buf.commentstr():
            lhs, rhs = commentstr
            new_lines = _toggle_comment(lhs, rhs, lines=lines)
            await buf.set_lines(lo=row, hi=row + 1, lines=new_lines)


_ = keymap.n("gcc") << f"<cmd>lua {NAMESPACE}.{_comment_single.method}()<cr>"
