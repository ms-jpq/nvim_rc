from os import environ
from shutil import which

from pynvim_pp.nvim import Nvim
from std2.asyncio.subprocess import call

from ..registry import LANG, NAMESPACE, atomic, keymap, rpc


@rpc()
async def open_term(*args: str) -> None:
    if "TMUX" in environ and (tmux := which("tmux")):
        cwd = await Nvim.getcwd()
        await call(
            tmux,
            "display-popup",
            "-EE",
            "-d",
            cwd,
            "-w",
            "95%",
            "-h",
            "90%",
            "--",
            *args,
            check_returncode=set(),
        )
    else:
        await Nvim.write(LANG("cannot tmux"))


atomic.command(f"command! -nargs=* FCmd lua {NAMESPACE}.{open_term.method}(<f-args>)")
_ = keymap.n("<leader>u") << f"<cmd>lua {NAMESPACE}.{open_term.method}()<cr>"
