from pynvim import Nvim
from pynvim_pp.api import buf_get_lines, buf_line_count, cur_buf
from pynvim_pp.operators import set_visual_selection

from ..registery import keymap, rpc


@rpc(blocking=True)
def _entire(nvim: Nvim) -> None:
    buf = cur_buf(nvim)
    count = buf_line_count(nvim, buf=buf)
    last_line, *_ = buf_get_lines(nvim, buf=buf, lo=-2, hi=-1)
    mark1 = (0, 0)
    mark2 = (count - 1, len(last_line.encode()))
    set_visual_selection(nvim, buf=buf, mark1=mark1, mark2=mark2)
    nvim.command("norm! `<V`>")


keymap.o("ie") << f"<cmd>lua {_entire.name}()<cr>"
keymap.o("ae") << f"<cmd>lua {_entire.name}()<cr>"
keymap.v("ie") << f"<esc><cmd>lua {_entire.name}()<cr>"
keymap.v("ae") << f"<esc><cmd>lua {_entire.name}()<cr>"
