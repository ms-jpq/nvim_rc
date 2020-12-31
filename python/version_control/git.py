from ..registery import keymap
from ..workspace.terminal import toggle_floating

keymap.n("<leader>U") << f"<cmd>lua {toggle_floating.remote_name}('lazygit')<cr>"
