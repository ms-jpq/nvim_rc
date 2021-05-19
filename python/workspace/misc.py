from pynvim.api import Nvim
from pynvim_pp.api import buf_name, buf_set_option, list_bufs

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
    bufs = list_bufs(nvim, listed=False)
    for buf in bufs:
        name = buf_name(nvim, buf=buf)
        if not name:
            buf_set_option(nvim, buf=buf, key="buftype", val="nofile")


atomic.exec_lua(f"{_scratch_buffer.name}()", ())
