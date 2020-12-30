from asyncio.events import Handle, get_running_loop
from typing import Optional

from pynvim.api.nvim import Nvim
from python.nvim.lib import async_call, go

from ..registery import autocmd, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


@autocmd("FocusGained", "BufEnter", blocking=True)
def _reload_file(nvim: Nvim) -> None:
    nvim.command("checktime")


# auto backup
settings["backup"] = True


@autocmd(
    "FocusLost",
    "VimLeavePre",
    blocking=True,
    modifiers=("*", "nested"),
)
def _auto_save(nvim: Nvim) -> None:
    nvim.command("silent! wa")


_handle: Optional[Handle] = None


@autocmd(
    "CursorHold",
    "CursorHoldI",
    "TextChanged",
    "TextChangedI",
    blocking=False,
    modifiers=("*", "nested"),
)
def _smol_save(nvim: Nvim) -> None:
    global _handle
    if _handle:
        _handle.cancel()

    def cont() -> None:
        go(async_call(nvim, _auto_save, nvim))

    loop = get_running_loop()
    _handle = loop.call_later(0.5, cont)


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000
