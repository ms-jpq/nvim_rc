from ..registry import keymap, settings

_ = settings["foldlevel"] = 3
# auto close folds
_ = settings["foldclose"] = "all"

_ = keymap.n("<leader>F", nowait=True) << "<cmd>set foldenable!<cr>"

_ = keymap.n("a", nowait=True) << "za"
