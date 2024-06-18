from ..registry import keymap

for key in ("<left>", "<right>"):
    _ = keymap.i(key, expr=True) << f"pumvisible() ? '<C-e>{key}' : '{key}'"
