from os import environ

from ..registery import atomic, keymap, settings

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
_ = keymap.nv("$") << "$<right>"


# use system clipboard
settings["clipboard"] = "unnamedplus"
# fake DISPLAY for xclip
atomic.call_function("setenv", ("DISPLAY", environ.get("DISPLAY", "VIM_FAKE_DISPLAY")))
