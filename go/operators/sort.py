from locale import strxfrm

from pynvim_pp.buffer import Buffer
from pynvim_pp.operators import VisualTypes, operator_marks

from ..registery import NAMESPACE, keymap, rpc


@rpc()
async def _sort_lines(visual: VisualTypes) -> None:
    buf = await Buffer.get_current()
    if not await buf.modifiable():
        return
    else:
        (row1, _), (row2, _) = await operator_marks(buf, visual_type=visual)
        lines = await buf.get_lines(lo=row1, hi=row2 + 1)
        new_lines = sorted(lines, key=strxfrm)
        await buf.set_lines(lo=row1, hi=row2 + 1, lines=new_lines)


_ = keymap.n("gu") << f"<cmd>set opfunc={_sort_lines.method}<cr>g@"
_ = (
    keymap.v("gu")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_sort_lines.method}(vim.NIL)<cr>"
)
