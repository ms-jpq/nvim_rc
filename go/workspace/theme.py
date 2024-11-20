from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType

from ..registry import NAMESPACE, atomic, autocmd, rpc, settings

# use 256 colours
settings["termguicolors"] = True

# remove welcome message
settings["shortmess"] += "I"
# always show status line
settings["laststatus"] = 3


# keep wrapped text indent
settings["breakindent"] = True
settings["showbreak"] = "↳"


# constant cursor styling
settings["guicursor"] = ""

# completion menu transparency
settings["pumblend"] = 5


# highlight yank
@rpc()
async def _hl_yank() -> None:
    await Nvim.lua.vim.highlight.on_yank(NoneType, {"higroup": "HighlightedyankRegion"})


atomic.command("highlight HighlightedyankRegion cterm=reverse gui=reverse")
_ = autocmd("TextYankPost") << f"lua {NAMESPACE}.{_hl_yank.method}()"
