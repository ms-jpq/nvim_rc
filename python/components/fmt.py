from pynvim import Nvim
from pynvim.api.buffer import Buffer


def run_fmt(nvim: Nvim) -> None:
    buf: Buffer = nvim.api.get_current_buf()
