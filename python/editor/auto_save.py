from asyncio.locks import Event
from asyncio.tasks import create_task, gather, sleep

from pynvim.api.nvim import Nvim
from pynvim_pp.lib import async_call, go
from std2.asyncio import race
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

autocmd("FocusLost", "VimLeavePre", modifiers=("*", "++nested")) << "silent! wa"

_EV = Event()
_EV.set()
_WAIT_TIME = 0.5


@rpc(blocking=True)
def _smol_save(nvim: Nvim) -> None:
    async def cont() -> None:
        _go, _, _ = await race(create_task(_EV.wait()), sleep(_WAIT_TIME, False))
        if _go.result() and _EV.is_set():
            _EV.clear()
            await gather(
                async_call(nvim, nvim.command, "silent! wa"), sleep(_WAIT_TIME)
            )
            _EV.set()

    go(cont())


autocmd(
    "CursorHold",
    "CursorHoldI",
    "TextChanged",
    "TextChangedI",
    modifiers=("*", "++nested"),
) << f"lua {_smol_save.name}()"


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000
