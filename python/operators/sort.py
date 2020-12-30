from locale import strxfrm

from pynvim.api import Buffer, Nvim

from ..nvim.operators import VisualTypes, operator_marks
from ..registery import keymap, rpc


@rpc(blocking=True)
def _sort_lines(nvim: Nvim, visual_type: VisualTypes = None) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    (row1, _), (row2, _) = operator_marks(nvim, buf=buf, visual_type=visual_type)
    # mixed indexing
    row1, row2 = row1 - 1, row2 - 1 + 1
    lines = nvim.api.buf_get_lines(0, row1, row2, True)
    new_lines = sorted(lines, key=strxfrm)
    nvim.api.buf_set_lines(0, row1, row2, True, new_lines)


keymap.n("gu") << f"<cmd>set opfunc=v:lua.{_sort_lines.lua_name}<cr>g@"
keymap.v("gu") << f"<esc><cmd>lua {_sort_lines.lua_name}()<cr>"
