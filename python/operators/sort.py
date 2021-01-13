from locale import strxfrm

from pynvim.api import Nvim
from pynvim_pp.api import buf_get_lines, buf_set_lines, cur_buf
from pynvim_pp.operators import VisualTypes, operator_marks, writable

from ..registery import keymap, rpc


@rpc(blocking=True)
def _sort_lines(nvim: Nvim, visual_type: VisualTypes = None) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        (row1, _), (row2, _) = operator_marks(nvim, buf=buf, visual_type=visual_type)
        lines = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)
        new_lines = sorted(lines, key=strxfrm)
        buf_set_lines(nvim, buf=buf, lo=row1, hi=row2 + 1, lines=new_lines)


keymap.n("gu") << f"<cmd>set opfunc=v:lua.{_sort_lines.name}<cr>g@"
keymap.v("gu") << f"<esc><cmd>lua {_sort_lines.name}()<cr>"
