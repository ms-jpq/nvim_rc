from ..registery import NAMESPACE,  keymap

# dont shift move too much
keymap.v("<s-up>") << "g<up>"
keymap.v("<s-down>") << "g<down>"


# keep selected when indenting
keymap.v("<") << "<gv"
keymap.v(">") << ">gv"
