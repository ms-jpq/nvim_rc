from ..registry import keymap

# dont shift move too much
_ = keymap.v("<s-up>") << "g<up>"
_ = keymap.v("<s-down>") << "g<down>"


# keep selected when indenting
_ = keymap.v("<") << "<gv"
_ = keymap.v(">") << ">gv"
