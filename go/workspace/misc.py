from pynvim_pp.buffer import Buffer

from ..registry import NAMESPACE, atomic, rpc, settings

# do not exec arbitrary code
settings["nomodeline"] = True

# limit .vim exec rights
settings["secure"] = True

# use bash as shell
settings["shell"] = "bash"

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
        if not await buf.get_name():
            await buf.opts.set("buftype", val="nofile")


atomic.exec_lua(f"{NAMESPACE}.{_scratch_buffer.method}()", ())
