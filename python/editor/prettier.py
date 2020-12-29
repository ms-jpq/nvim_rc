from pynvim import Nvim
from pynvim.api.buffer import Buffer

from ..registery import keymap, rpc
from ..config.fmt import fmt_specs


@rpc()
def run_fmt(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()


keymap.n("M") << "<cmd>" + run_fmt.call_line() + "<cr>"
