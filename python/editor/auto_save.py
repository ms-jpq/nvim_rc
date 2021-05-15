from asyncio.events import Handle, get_running_loop
from typing import Optional

from pynvim.api.nvim import Nvim
from pynvim_pp.lib import async_call, go
from std2.sched import aticker

from ..consts import BACKUP_DIR
from ..registery import atomic, autocmd, rpc, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


@rpc(blocking=True)
def _check_time(nvim: Nvim) -> None:
    check = lambda: nvim.command("silent! checktime")

    async def cont() -> None:
        async for _ in aticker(3, immediately=False):
            go(async_call(nvim, check))

    go(cont())


atomic.call_function("luaeval", (f"{_check_time.name}()", ()))


# auto backup
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
settings["backup"] = True
settings["writebackup"] = True
settings["backupskip"] = ""
settings["backupdir"] = str(BACKUP_DIR)
settings["backupext"] = ".bak"

autocmd("BufLeave", "FocusLost", modifiers=("*", "++nested")) << "wa!"
autocmd("VimLeavePre") << "wa!"


_handle: Optional[Handle] = None


@rpc(blocking=True)
def _smol_save(nvim: Nvim) -> None:
    global _handle
    if _handle:
        _handle.cancel()

    def cont() -> None:
        go(async_call(nvim, nvim.command, "wa!"))

    loop = get_running_loop()
    _handle = loop.call_later(0.5, cont)


(
    autocmd(
        "CursorHold",
        "CursorHoldI",
        modifiers=("*", "++nested"),
    )
    << f"lua {_smol_save.name}()"
)


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000
