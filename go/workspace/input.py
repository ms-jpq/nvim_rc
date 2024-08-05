from os import environ

from pynvim_pp.window import Window

from ..registry import NAMESPACE, atomic, autocmd, keymap, rpc, settings

# waiting time within a key sequence
settings["timeoutlen"] = 500
# cursor hold time
settings["updatetime"] = 300
# allow nav keys to wrap around
settings["whichwrap"] += ("h", "l", "<", ">", "[", "]")


# enable mouse
settings["mouse"] = "a"
# right click behaviour
settings["mousemodel"] = "popup_setpos"
# doubleclick time
settings["mousetime"] = 250


# scroll activation margin
settings["scrolloff"] = 0
settings["sidescrolloff"] = 10
settings["smoothscroll"] = True

_vcol = ("onemore", "block")
# normalize cursor pos
settings["virtualedit"] = _vcol
_ = keymap.nv("$") << "$<right>"


# show cursor
settings["cursorline"] = True


@rpc()
async def _ins_cursor() -> None:
    win = await Window.get_current()
    await win.opts.set("virtualedit", ",".join(_vcol))
    await win.opts.set("cursorline", False)
    await win.opts.set("cursorcolumn", False)


@rpc()
async def _norm_cursor() -> None:
    win = await Window.get_current()
    await win.opts.set("cursorline", True)


@rpc()
async def _vedit() -> None:
    win = await Window.get_current()
    col = await win.opts.get(bool, "cursorcolumn")
    if col:
        await win.opts.set("virtualedit", ",".join(_vcol))
        await win.opts.set("cursorcolumn", False)
    else:
        await win.opts.set("virtualedit", "all")
        await win.opts.set("cursorcolumn", True)


_ = autocmd("InsertEnter") << f"lua {NAMESPACE}.{_ins_cursor.method}()"
_ = autocmd("InsertLeave") << f"lua {NAMESPACE}.{_norm_cursor.method}()"
_ = keymap.n("<leader>f") << f"<cmd>lua {NAMESPACE}.{_vedit.method}()<cr>"


# use system clipboard
settings["clipboard"] = "unnamedplus"
# fake DISPLAY for xclip
atomic.call_function("setenv", ("DISPLAY", environ.get("DISPLAY", "VIM_FAKE_DISPLAY")))
