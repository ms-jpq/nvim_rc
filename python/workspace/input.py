from ..registery import keymap, settings

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


# normalize cursor pos
settings["virtualedit"] = ("onemore", "block")
keymap.nv("$") << "$<right>"


# use system clipboard
settings["clipboard"] = "unnamedplus"
# -- fake DISPLAY for xclip TODO TODO TODO
# env["DISPLAY"] = env["DISPLAY"] or "VIM_FAKE_DISPLAY"