from shutil import which

from ..registery import NAMESPACE, keymap, rpc
from ..workspace.terminal import open_term


@rpc()
async def _git_tui() -> None:
    if tui := which("lazygit"):
        await open_term(tui)


_ = (
    keymap.n("<leader>U")
    << f"<cmd>silent! wa! | lua {NAMESPACE}.{_git_tui.method}()<cr>"
)
