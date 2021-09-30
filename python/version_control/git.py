from pynvim import Nvim

from ..registery import NAMESPACE, keymap, rpc
from ..workspace.terminal import open_term


@rpc(blocking=True)
def _lazygit(nvim: Nvim) -> None:
    open_term(nvim, "lazygit")


keymap.n("<leader>U") << f"<cmd>silent! wa! | lua {NAMESPACE}.{_lazygit.name}()<cr>"
