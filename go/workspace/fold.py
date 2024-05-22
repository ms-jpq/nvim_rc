from ..registry import keymap, settings

# use buffer text for folds
settings["foldtext"] = ""

# close nested folds above this level
settings["foldlevel"] = 1

# auto open / close folds
settings["foldopen"] += ("insert", "jump")
# settings["foldclose"] = "all"

_ = keymap.n("<leader>F", nowait=True) << "<cmd>set foldenable!<cr>"

_ = keymap.n("a", nowait=True) << "za"
