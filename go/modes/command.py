from ..registry import keymap

# dont go into ex mode
_ = keymap.c("<c-f>") << ""

# quit
_ = keymap.c("<c-q>") << "<esc>"

# enable paste
_ = keymap.c("<c-v>", silent=False) << '<c-r>"'
