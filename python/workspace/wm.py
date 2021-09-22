from contextlib import suppress

from pynvim.api.nvim import Nvim, NvimError
from pynvim_pp.api import (
    buf_filetype,
    buf_set_var,
    create_buf,
    cur_buf,
    cur_tab,
    cur_win,
    tab_list_wins,
    win_close,
    win_get_buf,
    win_get_option,
    win_set_buf,
    win_set_option,
)

from ..registery import NAMESPACE, keymap, rpc, settings

# hide background buffers
settings["hidden"] = True
# reuse buf
settings["switchbuf"] += ("useopen", "usetab")


# modern split direction
settings["splitright"] = True
settings["splitbelow"] = True

# move between windows
keymap.n("<c-left>") << "<cmd>wincmd h<cr>"
keymap.n("<c-right>") << "<cmd>wincmd l<cr>"
keymap.n("<c-up>") << "<cmd>wincmd k<cr>"
keymap.n("<c-down>") << "<cmd>wincmd j<cr>"

# swap windows
keymap.n("<leader>'") << "<cmd>wincmd r<cr>"
keymap.n("<leader>;") << "<cmd>wincmd R<cr>"

# move windows
keymap.n("<s-m-left>") << "<cmd>wincmd H<cr>"
keymap.n("<s-m-right>") << "<cmd>wincmd L<cr>"
keymap.n("<s-m-up>") << "<cmd>wincmd K<cr>"
keymap.n("<s-m-down>") << "<cmd>wincmd J<cr>"

# resize windows
keymap.n("+") << "<cmd>wincmd =<cr>"
keymap.n("<s-left>") << "<cmd>wincmd <<cr>"
keymap.n("<s-right>") << "<cmd>wincmd ><cr>"
keymap.n("<s-up>") << "<cmd>wincmd +<cr>"
keymap.n("<s-down>") << "<cmd>wincmd -<cr>"


@rpc(blocking=True)
def _new_window(nvim: Nvim, vertical: bool) -> None:
    nvim.command("vnew" if vertical else "new")
    win = cur_win(nvim)
    buf = create_buf(
        nvim, listed=False, scratch=True, wipe=True, nofile=True, noswap=True
    )
    win_set_buf(nvim, win=win, buf=buf)


keymap.n("<leader>=") << f"<cmd>lua {NAMESPACE}.{_new_window.name}(true)<cr>"
keymap.n("<leader>-") << f"<cmd>lua {NAMESPACE}.{_new_window.name}(false)<cr>"


# kill current buf
keymap.n("<leader>x") << "<cmd>bwipeout!<cr>"
# close self
keymap.n("<leader>w") << f"<cmd>close<cr>"
# close others
keymap.n("<leader>W") << f"<cmd>wincmd o<cr>"


# break window into tab
keymap.n("<leader>k") << "<cmd>wincmd T<cr>"

# close tab
keymap.n("<leader>q") << "<cmd>tabclose<cr>"
# create new tab
@rpc(blocking=True)
def _new_tab(nvim: Nvim) -> None:
    nvim.command("tabnew")
    buf = cur_buf(nvim)
    buf_set_var(nvim, buf=buf, key="buftype", val="nofile")


keymap.n("<leader>t") << f"<cmd>lua {NAMESPACE}.{_new_tab.name}()<cr>"
keymap.n("<leader>n") << f"<cmd>lua {NAMESPACE}.{_new_tab.name}()<cr>"


# cycle between tabs
keymap.n("<leader>[") << "<cmd>tabprevious<cr>"
keymap.n("<leader>]") << "<cmd>tabnext<cr>"

keymap.n("<leader>0") << "g<tab>"
for i in range(1, 10):
    keymap.n(f"<leader>{i}") << f"<cmd>tabnext {i}<cr>"


# preview height
settings["previewheight"] = 11


@rpc(blocking=True)
def _toggle_preview(nvim: Nvim) -> None:
    tab = cur_tab(nvim)
    wins = tab_list_wins(nvim, tab=tab)
    closed = False
    for win in wins:
        is_preview: bool = win_get_option(nvim, win=win, key="previewwindow")
        if is_preview:
            win_close(nvim, win=win)
            closed = True
    if not closed:
        nvim.command("new")
        win = cur_win(nvim)
        win_set_option(nvim, win=win, key="previewwindow", val=True)
        height = nvim.options["previewheight"]
        nvim.api.win_set_height(win, height)


keymap.n("<leader>m") << f"<cmd>lua {NAMESPACE}.{_toggle_preview.name}()<cr>"


# quickfix
keymap.n("<c-j>") << "<cmd>cprevious<cr>"
keymap.n("<c-k>") << "<cmd>cnext<cr>"


@rpc(blocking=True)
def _toggle_qf(nvim: Nvim) -> None:
    tab = cur_tab(nvim)
    wins = tab_list_wins(nvim, tab=tab)
    closed = False
    for win in wins:
        buf = win_get_buf(nvim, win=win)
        ft = buf_filetype(nvim, buf=buf)
        if ft == "qf":
            win_close(nvim, win=win)
            closed = True
    if not closed:
        nvim.command("copen")
        win = cur_win(nvim)
        height = nvim.options["previewheight"]
        nvim.api.win_set_height(win, height)


@rpc(blocking=True)
def _clear_qf(nvim: Nvim) -> None:
    nvim.funcs.setqflist(())
    with suppress(NvimError):
        nvim.command("cclose")


keymap.n("<leader>l") << f"<cmd>lua {NAMESPACE}.{_toggle_qf.name}()<cr>"
keymap.n("<leader>L") << f"<cmd>lua {NAMESPACE}.{_clear_qf.name}()<cr>"


@rpc(blocking=True)
def _resize_secondary(nvim: Nvim) -> None:
    tab = cur_tab(nvim)
    wins = tab_list_wins(nvim, tab=tab)
    height = nvim.options["previewheight"]

    for win in wins:
        is_preview: bool = win_get_option(nvim, win=win, key="previewwindow")
        buf = win_get_buf(nvim, win=win)
        ft = buf_filetype(nvim, buf=buf)
        if is_preview or ft == "qf":
            nvim.api.win_set_height(win, height)


keymap.n("<leader>M") << f"<cmd>lua {NAMESPACE}.{_resize_secondary.name}()<cr>"
