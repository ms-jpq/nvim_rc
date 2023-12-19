from pynvim_pp.lib import encode
from pynvim_pp.operators import set_visual_selection
from pynvim_pp.window import Window

from ..registry import NAMESPACE, keymap, rpc


@rpc()
async def _entire() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    count = await buf.line_count()
    last_line, *_ = await buf.get_lines(lo=-2, hi=-1)
    mark1 = (0, 0)
    mark2 = (count - 1, len(encode(last_line)))
    await set_visual_selection(win, mode="V", mark1=mark1, mark2=mark2)


_ = keymap.o("ie") << f"<cmd>lua {NAMESPACE}.{_entire.method}()<cr>"
_ = keymap.o("ae") << f"<cmd>lua {NAMESPACE}.{_entire.method}()<cr>"
_ = keymap.v("ie") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_entire.method}()<cr>"
_ = keymap.v("ae") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_entire.method}()<cr>"
