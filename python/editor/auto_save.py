from pynvim.api.nvim import Nvim
from ..registery import settings, autocmd

# auto load changes
settings["autoread"] = True
# auto save file
settings["autowrite"] = True
settings["autowriteall"] = True


@autocmd("reload_file", events=("FocusGained", "BufEnter"))
def reload_file(nvim: Nvim) -> None:
    nvim.command("checktime")


# -- autosave
# local autosave = function ()

#   -- auto backup
#   -- bindings.set("backup")

#   local save = function ()
#     local bufs = api.nvim_list_bufs()
#     for _, buf in ipairs(bufs) do
#       local modified = api.nvim_buf_get_option(buf, "modified")
#       if modified ~= "nomodified" then
#         bindings.exec("silent! wa")
#         break
#       end
#     end
#   end

#   local smol_save = decorators.debounce(500, save)

#   registry.auto(
#     {"CursorHold", "CursorHoldI", "TextChanged", "TextChangedI"},
#     smol_save,
#     "*",
#     "nested")

#   registry.auto({"FocusLost", "VimLeavePre"}, save, "*", "nested")

# end
# registry.defer(autosave)


# persistent undo
settings["undofile"] = True
# maximum number of changes that can be undone
settings["undolevels"] = 1000
# maximum number lines to save for undo on a buffer reload
settings["undoreload"] = 1000
