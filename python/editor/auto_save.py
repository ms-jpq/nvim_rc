from asyncio.events import Handle, get_running_loop
from typing import Optional

from pynvim.api.nvim import Nvim

from ..nvim.lib import async_call, go
from ..registery import autocmd, rpc, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


autocmd("FocusGained", "BufEnter") << "checktime"


# auto backup
settings["backup"] = True


autocmd("FocusLost", "VimLeavePre", modifiers=("*", "nested")) << "silent! wa"


_handle: Optional[Handle] = None


@rpc(blocking=True)
def _smol_save(nvim: Nvim) -> None:
    global _handle
    if _handle:
        _handle.cancel()

    def cont() -> None:
        go(async_call(nvim, nvim.command, "silent! wa"))

    loop = get_running_loop()
    _handle = loop.call_later(0.5, cont)


autocmd(
    "CursorHold",
    "CursorHoldI",
    "TextChanged",
    "TextChangedI",
    modifiers=("*", "nested"),
) << f"lua {_smol_save.lua_name}()<cr>"


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000
