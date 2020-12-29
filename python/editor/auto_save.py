from pynvim.api.nvim import Nvim
from ..registery import settings, autocmd

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


@autocmd("FocusGained", "BufEnter")
def reload_file(nvim: Nvim) -> None:
    nvim.command("checktime")


# auto backup
settings["backup"] = True


@autocmd("FocusLost", "VimLeavePre", modifiers=("nested",))
def auto_save(nvim: Nvim) -> None:
    nvim.command("silent! wa")


@autocmd(
    "CursorHold", "CursorHoldI", "TextChanged", "TextChangedI", modifiers=("nested",)
)
def smol_save(nvim: Nvim) -> None:
    auto_save(nvim)


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000
