from pynvim import Nvim

from ..registery import keymap, rpc

# leave terminal
keymap.t("<c-g>") << "<c-\><c-n>"


@rpc()
def open_floating(nvim: Nvim, *args: str) -> None:
    pass


keymap.n("<leader>u") << "<cmd>" + open_floating.call_line() + "<cr>"
