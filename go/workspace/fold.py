from ..registry import autocmd, keymap, settings

# use buffer text for folds
settings["foldtext"] = ""

# close nested folds above this level
settings["foldlevel"] = 1

# auto open / close folds
settings["foldopen"] += ("insert", "jump")
# settings["foldclose"] = "all"

# toggle folds
_ = keymap.n("a", nowait=True) << "za"

_ = autocmd("CursorMoved") << "silent! foldopen"
_ = autocmd("InsertEnter") << "norm! zn"
_ = autocmd("InsertLeave") << "norm! zN"
