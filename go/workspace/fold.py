from ..registry import keymap, settings

# use buffer text for folds
settings["foldtext"] = ""

# close nested folds above this level
settings["foldlevel"] = 5

# auto open / close folds
settings["foldopen"] += ("insert", "jump")
# settings["foldclose"] = "all"


# re-center
for key in ("o", "O", "c", "C", "a", "A", "v", "x", "X", "m", "M", "r", "R"):
    _ = keymap.n(f"z{key}") << f"z{key}zz"
