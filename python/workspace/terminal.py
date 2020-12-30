from pynvim import Nvim
from ..registery import keymap, rpc

from ..nvim.float_win import open_float_win


@rpc(blocking=True)
def open_floating(nvim: Nvim, *args: str) -> None:
    buf = nvim.api.create_buf(False, True)
    open_float_win(nvim, margin=1, relsize=0.9, buf=buf)


keymap.n("<leader>u") << f"<cmd>lua {open_floating.lua_name}()<cr>"
