from contextlib import suppress

from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Nvim
from pynvim_pp.preview import preview_windows
from pynvim_pp.rpc_types import NvimError
from pynvim_pp.tabpage import Tabpage
from pynvim_pp.types import NoneType
from pynvim_pp.window import Window

from ..registry import NAMESPACE, autocmd, keymap, rpc, settings

# hide background buffers
settings["hidden"] = True
# reuse buf
settings["switchbuf"] += ("useopen", "usetab")


# modern split direction
settings["splitright"] = True
settings["splitbelow"] = True

# move between windows
_ = keymap.n("<c-left>") << "<cmd>wincmd h<cr>"
_ = keymap.n("<c-up>") << "<cmd>wincmd k<cr>"
_ = keymap.n("<c-right>") << "<cmd>wincmd l<cr>"
_ = keymap.n("<c-down>") << "<cmd>wincmd j<cr>"

# swap windows
_ = keymap.n("<leader>'") << "<cmd>wincmd r<cr>"
_ = keymap.n("<leader>;") << "<cmd>wincmd R<cr>"

# move windows
_ = keymap.n("<s-m-left>") << "<cmd>wincmd H<cr>"
_ = keymap.n("<s-m-right>") << "<cmd>wincmd L<cr>"
_ = keymap.n("<s-m-up>") << "<cmd>wincmd K<cr>"
_ = keymap.n("<s-m-down>") << "<cmd>wincmd J<cr>"

# resize windows
_ = keymap.n("+") << "<cmd>wincmd =<cr>"
_ = keymap.n("<s-left>") << "<cmd>wincmd <<cr>"
_ = keymap.n("<s-right>") << "<cmd>wincmd ><cr>"
_ = keymap.n("<s-up>") << "<cmd>wincmd +<cr>"
_ = keymap.n("<s-down>") << "<cmd>wincmd -<cr>"


_ = autocmd("VimResized") << "wincmd ="


@rpc()
async def _new_window(vertical: bool) -> None:
    await Nvim.api.command(NoneType, "vnew" if vertical else "new")
    win = await Window.get_current()
    buf = await Buffer.create(
        listed=False, scratch=True, wipe=True, nofile=True, noswap=True
    )
    await win.set_buf(buf)


_ = keymap.n("<leader>=") << f"<cmd>lua {NAMESPACE}.{_new_window.method}(true)<cr>"
_ = keymap.n("<leader>-") << f"<cmd>lua {NAMESPACE}.{_new_window.method}(false)<cr>"


# kill current buf
_ = keymap.n("<leader>x") << "<cmd>bwipeout!<cr>"
# close self
_ = keymap.n("<leader>w") << "<cmd>close<cr>"
# close others
_ = keymap.n("<leader>W") << "<cmd>wincmd o<cr>"


# break window into tab
_ = keymap.n("<leader>k") << "<cmd>wincmd T<cr>"

# close tab
_ = keymap.n("<leader>q") << "<cmd>tabclose<cr>"

# split window
_ = keymap.n("<leader>t") << "<cmd>vsplit<cr>"


# create new tab
@rpc()
async def _new_tab() -> None:
    await Nvim.api.command(NoneType, "tabnew")
    buf = await Buffer.get_current()
    await buf.vars.set("buftype", val="nofile")


_ = keymap.n("<leader>n") << f"<cmd>lua {NAMESPACE}.{_new_tab.method}()<cr>"


# cycle between tabs
_ = keymap.n("<leader>[") << "<cmd>tabprevious<cr>"
_ = keymap.n("<leader>]") << "<cmd>tabnext<cr>"

_ = keymap.n("<leader>0") << "g<tab>"
for i in range(1, 10):
    _ = keymap.n(f"<leader>{i}") << f"<cmd>tabnext {i}<cr>"


# preview height
settings["previewheight"] = 11


# @rpc()
# async def _toggle_preview() -> None:
#     tab = await Tabpage.get_current()
#     if previews := await preview_windows(tab):
#         for win in previews:
#             await win.close()
#     else:
#         await Nvim.api.command(NoneType, "new")
#         win = await Window.get_current()
#         height = await Nvim.opts.get(int, "previewheight")
#         await win.opts.set("previewwindow", val=True)
#         await win.set_height(height)


# _ = keymap.n("<leader>h") << f"<cmd>lua {NAMESPACE}.{_toggle_preview.method}()<cr>"


# locallist
_ = keymap.n("<c-p>") << "<cmd>lprevious<cr>"
_ = keymap.n("<c-n>") << "<cmd>lnext<cr>"


# quickfix
_ = keymap.n("<c-j>") << "<cmd>cprevious<cr>"
_ = keymap.n("<c-k>") << "<cmd>cnext<cr>"


@rpc()
async def _toggle_qf() -> None:
    tab = await Tabpage.get_current()
    wins = await tab.list_wins()

    closed = False
    for win in wins:
        buf = await win.get_buf()
        ft = await buf.filetype()
        if ft == "qf":
            await win.close()
            closed = True
    if not closed:
        await Nvim.api.command(NoneType, "copen")
        win = await Window.get_current()
        height = await Nvim.opts.get(int, "previewheight")
        await win.set_height(height)


@rpc()
async def _clear_qf() -> None:
    await Nvim.fn.setqflist(NoneType, ())
    with suppress(NvimError):
        await Nvim.api.command(NoneType, "cclose")


_ = keymap.n("<leader>l") << f"<cmd>lua {NAMESPACE}.{_toggle_qf.method}()<cr>"
_ = keymap.n("<leader>L") << f"<cmd>lua {NAMESPACE}.{_clear_qf.method}()<cr>"
