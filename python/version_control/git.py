from ..registery import keymap
from ..workspace.terminal import open_floating

keymap.n("<leader>U") << "<cmd>" + open_floating.call_line("lazygit") << "<cr>"
