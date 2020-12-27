from ..registery import keymap

# which key
keymap.n("<leader>") << "<cmd>WhichKey '<space>'<cr>"
keymap.n("[") << "<cmd>WhichKey '['<cr>"
keymap.n("]") << "<cmd>WhichKey ']'<cr>"
