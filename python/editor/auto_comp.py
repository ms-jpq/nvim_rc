from ..registery import keymap, settings

# dont follow tags
settings["complete"] -= "i"


# previous
keymap.i("<c-p>") << "<c-x><c-p>"
# next
keymap.i("<c-n>") << "<c-x><c-n>"
# line
keymap.i("<c-l>") << "<c-x><c-l>"
# file
keymap.i("<c-f>") << "<c-x><c-f>"
# omnifunc
keymap.i("<c-o>") << "<c-x><c-o>"
