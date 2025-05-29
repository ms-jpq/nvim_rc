from asyncio import sleep
from collections.abc import Mapping
from typing import cast

from pynvim_pp.buffer import Buffer
from pynvim_pp.logging import suppress_and_log
from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType

from ..registry import NAMESPACE, autocmd, keymap, rpc, settings, tasks

# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


# noskip backup
settings["backupskip"] = ""


_ = autocmd("FocusGained", "VimResume", "WinEnter") << "silent! checktime"


@rpc()
async def _check_time(local: bool) -> None:
    if local:
        buf = await Buffer.get_current()
        if await buf.get_name():
            await Nvim.exec(f"checktime {buf.number}")
    else:
        await Nvim.exec("silent! checktime")
    await Nvim.exec("silent! wall!")


_ = (
    autocmd("BufLeave", "FocusLost", "VimLeavePre")
    << f"lua {NAMESPACE}.{_check_time.method}(false)"
)

_ = (
    autocmd("CursorHold", "CursorHoldI")
    << f"lua {NAMESPACE}.{_check_time.method}(true)"
)


async def _check_times() -> None:
    while True:
        await sleep(0.6)
        with suppress_and_log():
            info = cast(Mapping[str, str], await Nvim.api.get_mode(NoneType))
            mode = info["mode"]

            if not mode.startswith("i"):
                await _check_time(local=True)


tasks.append(_check_times())

# persistent undo
settings["undofile"] = True

_ = keymap.n("<c-s>") << "<cmd>w<cr>"
