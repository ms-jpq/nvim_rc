from ..registery import settings, keymap


# dont show too many opts
settings["pumheight"] = 15  # TODO make this dynamic
# transparency
settings["pumblend"] = 5
# dont spam suggestions menu
settings["shortmess"] += "c"
# dont follow tags
settings["complete"] -= "i"
# complete menu
settings["completeopt"] = ("menuone", "preview", "noinsert", "noselect")


# cancel comp
keymap.i("<esc>", expr=True) << "pumvisible() ? '<c-e><esc>' : '<esc>'"
keymap.i("<bs>", expr=True) << "pumvisible() ? '<c-e><bs>' : '<bs>'"


# cua
keymap.i(
    "<cr>", expr=True
) << "pumvisible() ? (complete_info().selected == -1 ? '<c-e><cr>' : '<c-y>') : '<cr>'"
keymap.i("<tab>", expr=True) << "pumvisible() ? '<c-n>' : '<tab>'"
keymap.i("<s-tab>", expr=True) << "pumvisible() ? '<c-p>' : '<bs>'"


# previous
keymap.i("<c-p>") << "<c-x><c-p>"
# next
keymap.i("<c-n>") << "<c-x><c-n>"
# line
keymap.i("<c-l>") << "<c-x><c-l>"
# file
keymap.i("<c-f>") << "<c-x><c-f>"
# omnifunc
keymap.i("<c-o>") << "<c-x><c-o>"
# userfunc
keymap.nv("<c-space>") << ""
keymap.i("<c-space>") << "<c-x><c-u>"


# TODO -- remove this
settings["completefunc"] = "KoKomnifunc"
