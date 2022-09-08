from types import NoneType

from pynvim_pp.nvim import Nvim
from pynvim_pp.window import Window

from ..registery import NAMESPACE, atomic, autocmd, rpc, settings

# use 256 colours
settings["termguicolors"] = True

# remove welcome message
settings["shortmess"] += "I"
# always show status line
settings["laststatus"] = 3
# always show tabline
settings["showtabline"] = 2


# always show issues column
settings["signcolumn"] = "yes"
# show line count
settings["number"] = True
# dont show eob lines
settings["fillchars"] = r"eob:\ "


# keep wrapped text indent
settings["breakindent"] = True
# settings["showbreak"] = "↳"

# show cursor
settings["cursorline"] = True
# constant cursor styling
settings["guicursor"] = ""

# completion menu transparency
settings["pumblend"] = 5
# light background
settings["background"] = "light"


@rpc(blocking=True)
async def _ins_cursor() -> None:
    win = await Window.get_current()
    await win.opts.set("cursorline", False)


@rpc(blocking=True)
async def _norm_cursor() -> None:
    win = await Window.get_current()
    await win.opts.set("cursorline", True)


_ = autocmd("InsertEnter") << f"lua {NAMESPACE}.{_ins_cursor.name}()"
_ = autocmd("InsertLeave") << f"lua {NAMESPACE}.{_norm_cursor.name}()"


# highlight yank
@rpc(blocking=True)
async def _hl_yank() -> None:
    await Nvim.lua.vim.highlight.on_yank(NoneType, {"higroup": "HighlightedyankRegion"})


atomic.command("highlight HighlightedyankRegion cterm=reverse gui=reverse")
_ = autocmd("TextYankPost") << f"lua {NAMESPACE}.{_hl_yank.name}()"
