from ..registery import NAMESPACE, keymap, rpc
from ..workspace.terminal import open_term


@rpc()
async def _lazygit() -> None:
    await open_term("lazygit")


_ = (
    keymap.n("<leader>U")
    << f"<cmd>silent! wa! | lua {NAMESPACE}.{_lazygit.method}()<cr>"
)
