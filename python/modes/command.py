from ..registery import keymap

# dont go into ex mode
keymap.c("<c-f>") << ""

# quit
keymap.c("<c-q>") << "<esc>"

# enable paste
keymap.c("<c-v>", silent=False) << '<c-r>"'
