from typing import Sequence

from pynvim.api.nvim import Buffer, Nvim, Tabpage, Window

from ..registery import keymap, rpc, settings

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


@rpc()
def new_window(nvim: Nvim, vertical: bool) -> None:
    nvim.command("vnew" if vertical else "new")
    win: Window = nvim.api.get_current_win()
    buf: Buffer = nvim.api.create_buf(False, True)
    nvim.api.win_set_buf(win, buf)


keymap.n("<leader>=", unique=True) << "<cmd>" + new_window.call_line("true") + "<cr>"
keymap.n("<leader>-", unique=True) << "<cmd>" + new_window.call_line("false") + "<cr>"


# kill current buf
keymap.n("<leader>x") << "<cmd>bwipeout!<cr>"
# kill current win
keymap.n("<leader>w") << "<cmd>close<cr>"


@rpc()
def close_others(nvim: Nvim) -> None:
    tab: Tabpage = nvim.api.get_current_tabpage()
    win: Window = nvim.api.get_current_win()
    wins: Sequence[Window] = nvim.api.tabpage_list_wins(tab)
    for w in wins:
        if w != win:
            nvim.api.win_close(win, False)


keymap.n("<leader>W") << "<cmd>" + close_others.call_line() + "<cr>"


# break window into tab
keymap.n("<leader>k") << "<cmd>wincmd T<cr>"

# close tab
keymap.n("<leader>q") << "<cmd>tabclose<cr>"
# create new tab
@rpc()
def new_tab(nvim: Nvim) -> None:
    nvim.command("tabnew")
    buf: Buffer = nvim.api.get_current_buf()
    nvim.api.buf_set_var(buf, "buftype", "nofile")


keymap.n("<leader>t") << "<cmd>" + new_tab.call_line() + "<cr>"
keymap.n("<leader>n") << "<cmd>" + new_tab.call_line() + "<cr>"


# cycle between tabs
keymap.n("<leader>[") << "<cmd>tabprevious<cr>"
keymap.n("<leader>]") << "<cmd>tabnext<cr>"

keymap.n("<leader>0") << "g<tab>"
for i in range(1, 10):
    keymap.n(f"<leader>{i}") << f"<cmd>tabnext {i}<cr>"


# preview height
settings["previewheight"] = 11


@rpc()
def toggle_preview(nvim: Nvim) -> None:
    tab: Tabpage = nvim.api.get_current_tabpage()
    wins: Sequence[Window] = nvim.api.tabpage_list_wins(tab)
    closed = False
    for win in wins:
        is_preview = nvim.api.win_get_option(win, "previewwindow")
        if is_preview:
            nvim.api.win_close(win, True)
            closed = True
    if not closed:
        nvim.command("new")
        win = nvim.api.get_current_win()
        nvim.api.win_set_option(win, "previewwindow", True)
        height = nvim.options["previewheight"]
        nvim.api.win_set_height(win, height)


keymap.n("<leader>m") << "<cmd>" + toggle_preview.call_line() + "<cr>"


# quickfix
keymap.n("<c-j>") << "<cmd>cprevious<cr>"
keymap.n("<c-k>") << "<cmd>cnext<cr>"


@rpc()
def toggle_qf(nvim: Nvim) -> None:
    tab: Tabpage = nvim.api.get_current_tabpage()
    wins: Sequence[Window] = nvim.api.tabpage_list_wins(tab)
    closed = False
    for win in wins:
        buf: Buffer = nvim.api.win_get_buf(win)
        ft = nvim.api.buf_get_option(buf, "filetype")
        if ft == "qf":
            nvim.api.win_close(win, True)
            closed = True
    if not closed:
        nvim.command("copen")
        win = nvim.api.get_current_win()
        height = nvim.options["previewheight"]
        nvim.api.win_set_height(win, height)


@rpc()
def clear_qf(nvim: Nvim) -> None:
    nvim.funcs.setqflist(())
    nvim.command("cclose")


keymap.n("<leader>l") << "<cmd>" + toggle_qf.call_line() + "<cr>"
keymap.n("<leader>L") << "<cmd>" + clear_qf.call_line() + "<cr>"


@rpc()
def resize_secondary(nvim: Nvim) -> None:
    tab: Tabpage = nvim.api.get_current_tabpage()
    wins: Sequence[Window] = nvim.api.tabpage_list_wins(tab)
    height = nvim.options["previewheight"]

    for win in wins:
        is_preview = nvim.api.win_get_option(win, "previewwindow")
        buf: Buffer = nvim.api.win_get_buf(win)
        ft = nvim.api.buf_get_option(buf, "filetype")
        if is_preview or ft == "qf":
            nvim.api.win_set_height(win, height)


keymap.n("<leader>M") << "<cmd>" + resize_secondary.call_line() + "<cr>"
