from ..registery import keymap
from ..workspace.terminal import open_term

keymap.n("<leader>U") << f"<cmd>lua {open_term.name}('lazygit')<cr>"
