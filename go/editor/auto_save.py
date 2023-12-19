from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Nvim

from ..registry import NAMESPACE, autocmd, keymap, rpc, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


# noskip backup
settings["backupskip"] = ""


_ = autocmd("FocusGained", "VimResume", "WinEnter") << "checktime"


@rpc()
async def _auto_save(local: bool) -> None:
    if local:
        buf = await Buffer.get_current()
        await Nvim.exec(f"checktime {buf.number}")
    else:
        await Nvim.exec("checktime")
    await Nvim.exec("silent! wall!")


_ = (
    autocmd("BufLeave", "FocusLost", "VimLeavePre")
    << f"lua {NAMESPACE}.{_auto_save.method}(false)"
)

_ = autocmd("CursorHold", "CursorHoldI") << f"lua {NAMESPACE}.{_auto_save.method}(true)"

# persistent undo
settings["undofile"] = True

_ = keymap.n("<c-s>") << "<cmd>w<cr>"
