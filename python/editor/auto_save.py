from ..registery import NAMESPACE, autocmd, keymap, rpc, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


_ = autocmd("WinEnter") << "checktime"


# noskip backup
settings["backupskip"] = ""

_ = autocmd("BufLeave", "FocusLost", "VimLeavePre") << "silent! wall!"


@rpc()
async def _auto_save() -> None:
    ...


_ = autocmd("CursorHold", "CursorHoldI") << f"lua {NAMESPACE}.{_auto_save.method}()"

# persistent undo
settings["undofile"] = True

_ = keymap.n("<c-s>") << "<cmd>w<cr>"
