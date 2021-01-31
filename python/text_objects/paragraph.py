from ..registery import keymap

for key in ("v", "y", "d", "c"):
    for mod in ("i", "a"):
        keymap.n(f"{key}{mod}<space>") << f"{key}{mod}p"
