from ..registery import keymap, settings

# waiting time within a key sequence
settings["timeoutlen"] = 500
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
