from ..registry import keymap, settings

# use buffer text for folds
_ = settings["foldtext"] = ""

_ = settings["foldlevel"] = 6

# auto open / close folds
_ = settings["foldopen"] = "all"
_ = settings["foldclose"] = "all"

_ = keymap.n("<leader>F", nowait=True) << "<cmd>set foldenable!<cr>"

_ = keymap.n("a", nowait=True) << "za"
