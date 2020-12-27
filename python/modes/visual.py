from ..registery import keymap

# dont shift move too much
keymap.v("<s-up>") << "<up>"
keymap.v("<s-down>") << "<down>"


# keep selected when indenting
keymap.v("<") << "<gv"
keymap.v(">") << ">gv"
