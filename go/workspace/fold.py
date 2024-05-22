from uuid import uuid4

from pynvim_pp.nvim import Nvim
from pynvim_pp.window import Window

from ..registry import NAMESPACE, autocmd, keymap, rpc, settings

_BUF_VAR_NAME = f"buf_cursor_row_{uuid4().hex}"

# use buffer text for folds
settings["foldtext"] = ""

# close nested folds above this level
settings["foldlevel"] = 1

# auto open / close folds
settings["foldopen"] += ("insert", "jump")
# settings["foldclose"] = "all"

# toggle folds
_ = keymap.n("a", nowait=True) << "za"


@rpc()
async def _open_fold() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, _ = await win.get_cursor()
    r = row + 1
    lo = await Nvim.fn.foldclosed(int, r)
    if lo == r:
        await Nvim.exec(f"silent! foldopen")
        if (prev := await buf.vars.get(int, _BUF_VAR_NAME)) and prev > row:
            await Nvim.exec(f"norm! ]z")

    await buf.vars.set(_BUF_VAR_NAME, val=row)


_ = autocmd("CursorMoved") << f"lua {NAMESPACE}.{_open_fold.method}()"

# _ = autocmd("InsertEnter") << "norm! zn"
# _ = autocmd("InsertLeave") << "norm! zN"
