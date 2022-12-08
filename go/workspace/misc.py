from shutil import which

from pynvim_pp.buffer import Buffer
from std2.platform import OS, os

from ..registery import NAMESPACE, atomic, rpc, settings

if os is OS.windows and (cmd := which("cmd.exe")):
    settings["shell"] = cmd

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
@rpc()
async def _scratch_buffer() -> None:
    bufs = await Buffer.list(listed=False)
    for buf in bufs:
        name = await buf.get_name()
        if not name:
            await buf.opts.set("buftype", val="nofile")


atomic.exec_lua(f"{NAMESPACE}.{_scratch_buffer.method}()", ())
