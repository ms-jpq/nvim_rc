from ..consts import BACKUP_DIR
from ..registery import autocmd, settings

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


autocmd("WinEnter") << "checktime"


# auto backup
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
settings["backup"] = True
settings["writebackup"] = True
settings["backupskip"] = ""
settings["backupdir"] = str(BACKUP_DIR)
settings["backupext"] = ".bak"

(
    autocmd("BufLeave", "FocusLost", "VimLeavePre", "CursorHold", "CursorHoldI")
    << "silent! wa!"
)


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000

