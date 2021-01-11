from typing import Sequence

from pynvim.api import Buffer, Nvim

from ..registery import atomic, rpc, settings

# do not exec arbitrary code
settings["nomodeline"] = True

# limit .vim exec rights
settings["secure"] = True

# use bash as shell
settings["shell"] = "bash"

# vim session state
settings["shada"] += "!"

# min lines changed to report
settings["report"] = 0

# no swap files
settings["noswapfile"] = True

# wrap
settings["wrap"] = True

# line wrap follow indent
settings["breakindent"] = True

# open with scratch buffer, like emacs
@rpc(blocking=True)
def _scratch_buffer(nvim: Nvim) -> None:
    bufs: Sequence[Buffer] = nvim.api.list_bufs()
    for buf in bufs:
        name = nvim.api.buf_get_name(buf)
        if not name:
            nvim.api.buf_set_option(buf, "buftype", "nofile")


atomic.exec_lua(f"{_scratch_buffer.name}()", ())