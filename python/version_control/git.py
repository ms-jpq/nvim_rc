from shutil import which

from pynvim import Nvim

from ..registery import keymap, rpc
from ..workspace.terminal import open_term


@rpc(blocking=True)
def _lazygit(nvim: Nvim) -> None:
    lg = which("lazygit")
    open_term(nvim, lg, opts={"env": {"LC_ALL": "C"}})


keymap.n("<leader>U") << f"<cmd>silent! wa! | lua {_lazygit.name}()<cr>"
