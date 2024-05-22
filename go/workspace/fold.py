from ..registry import keymap, settings

_ = settings["foldlevel"] = 3

_ = keymap.n("a", nowait=True) << "za"
