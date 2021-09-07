from ..registery import autocmd, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


autocmd("WinEnter") << "checktime"


# noskip backup
settings["backupskip"] = ""

(
    autocmd("BufLeave", "FocusLost", "VimLeavePre", "CursorHold", "CursorHoldI")
    << "silent! wa!"
)


# persistent undo
settings["undofile"] = True
