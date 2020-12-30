from string import whitespace
from typing import Literal, Tuple, Union

from pynvim import Nvim
from pynvim.api import Buffer

VisualTypes = Union[Literal["char"], Literal["line"], Literal["block"], None]


def operator_marks(
    nvim: Nvim, buf: Buffer, visual_type: VisualTypes
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    mark1, mark2 = ("[", "]") if visual_type else ("<", ">")
    row1, col1 = nvim.api.buf_get_mark(buf, mark1)
    row2, col2 = nvim.api.buf_get_mark(buf, mark2)
    return (row1, col1), (row2, col2)


def p_indent(line: str, tabsize: int) -> int:
    ws = {*whitespace}
    for idx, char in enumerate(line.expandtabs(tabsize), start=1):
        if char not in ws:
            return idx - 1
    else:
        return 0
