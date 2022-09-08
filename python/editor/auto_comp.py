from ..registery import keymap, settings

# dont follow tags
settings["complete"] -= "i"


# previous
_ = keymap.i("<c-p>") << "<c-x><c-p>"
# next
_ = keymap.i("<c-n>") << "<c-x><c-n>"
# line
_ = keymap.i("<c-l>") << "<c-x><c-l>"
# file
# keymap.i("<c-f>") << "<c-x><c-f>"
# omnifunc
_ = keymap.i("<c-o>") << "<c-x><c-o>"
