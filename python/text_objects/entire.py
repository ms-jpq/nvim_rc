from pynvim import Nvim
from pynvim.api import Buffer
from pynvim_pp.operators import set_visual_selection

from ..registery import keymap, rpc


@rpc(blocking=True)
def _entire(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    count: int = nvim.api.buf_line_count(buf)
    last_line, *_ = nvim.api.buf_get_lines(buf, -2, -1, True)
    set_visual_selection(nvim, buf=buf, mark1=(1, 1), mark2=(count, len(last_line)))
    nvim.command("norm! `<V`>")


keymap.o("ie") << f"<cmd>lua {_entire.name}()<cr>"
keymap.o("ae") << f"<cmd>lua {_entire.name}()<cr>"
keymap.v("ie") << f"<esc><cmd>lua {_entire.name}()<cr>"
keymap.v("ae") << f"<esc><cmd>lua {_entire.name}()<cr>"
