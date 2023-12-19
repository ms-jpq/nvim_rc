from pynvim_pp.nvim import Nvim
from pynvim_pp.operators import operator_marks, set_visual_selection
from pynvim_pp.window import Window

from ..registry import NAMESPACE, keymap, rpc


@rpc()
async def _norm_mv(up: bool) -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, _ = await win.get_cursor()
    lines = await buf.line_count()

    if not await buf.modifiable():
        return
    else:
        if up:
            if row:
                await Nvim.exec("move -2")
        else:
            if row < lines - 1:
                await Nvim.exec("move +1")


_ = keymap.n("<m-up>") << f"<cmd>lua {NAMESPACE}.{_norm_mv.method}(true)<cr>"
_ = keymap.n("<m-down>") << f"<cmd>lua {NAMESPACE}.{_norm_mv.method}(false)<cr>"


@rpc()
async def _visual_mv(up: bool) -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    (row1, col1), (row2, col2) = await operator_marks(buf, visual_type=None)
    lines = await buf.line_count()

    if not await buf.modifiable():
        return
    else:
        if up:
            if row1 <= 0:
                await Nvim.exec("norm! gv")
            else:
                await Nvim.exec(f"{row1 + 1},{row2 + 1}move {row1 - 1}")
                await set_visual_selection(
                    win,
                    mode="v",
                    mark1=(row1 - 1, col1),
                    mark2=(row2 - 1, col2),
                    reverse=True,
                )

        else:
            if row2 >= lines - 1:
                await Nvim.exec("norm! gv")
            else:
                await Nvim.exec(f"{row1 + 1},{row2 + 1}move {row2 + 2}")
                await set_visual_selection(
                    win,
                    mode="v",
                    mark1=(row1 + 1, col1),
                    mark2=(row2 + 1, col2),
                )


_ = (
    keymap.v("<m-up>")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_visual_mv.method}(true)<cr>"
)
_ = (
    keymap.v("<m-down>")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_visual_mv.method}(false)<cr>"
)
