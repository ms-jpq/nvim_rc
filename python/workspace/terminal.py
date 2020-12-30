from pynvim import Nvim
from ..registery import keymap, rpc


@rpc(blocking=True)
def open_floating(nvim: Nvim, *args: str) -> None:
    pass


keymap.n("<leader>u") << f"<cmd>lua {open_floating.lua_name}()<cr>"
