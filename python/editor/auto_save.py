from ..registery import autocmd, keymap, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


_ = autocmd("WinEnter") << "checktime"


# noskip backup
settings["backupskip"] = ""

_ = (
    autocmd("BufLeave", "FocusLost", "VimLeavePre", "CursorHold", "CursorHoldI")
    << "silent! wa!"
)


# persistent undo
settings["undofile"] = True

_ = keymap.n("<c-s>") << "<cmd>w<cr>"
