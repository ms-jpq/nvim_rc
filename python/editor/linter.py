from pynvim import Nvim
from pynvim.api.buffer import Buffer

from ..registery import keymap, rpc
from ..config.linter import linter_specs


@rpc()
def run_linter(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()


keymap.n("gq", nowait=True) << "<cmd>" + run_linter.call_line() + "<cr>"