from os.path import normpath

from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Nvim
from pynvim_pp.window import Window

from ..registry import NAMESPACE, keymap, rpc


@rpc()
async def _reset_buffer() -> None:
    win = await Window.get_current()

    buf = await win.get_buf()
    path = await buf.get_name()
    if (filetype := await buf.filetype()) and filetype == "CHADTree":
        return

    cursor = await win.get_cursor()
    lv = await win.opts.get(int, "foldlevel")

    scratch = await Buffer.create(
        listed=False, scratch=True, wipe=True, nofile=True, noswap=True
    )
    await win.set_buf(scratch)
    await buf.delete()

    if path:
        escaped = await Nvim.fn.fnameescape(str, normpath(path))
        await Nvim.exec(f"edit! {escaped}")
        await win.set_cursor(*cursor)
        await win.opts.set("foldlevel", lv)
        await Nvim.exec("norm! zz")


_ = keymap.n("<leader>r") << f"<cmd>lua {NAMESPACE}.{_reset_buffer.method}()<cr>"
