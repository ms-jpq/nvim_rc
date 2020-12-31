from ..registery import keymap
from ..workspace.terminal import open_floating

keymap.n("<leader>U") << f"<cmd>lua {open_floating.remote_name}('lazygit')<cr>"
