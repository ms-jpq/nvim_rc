from ..registery import keymap

# move w linewrap
keymap.nv("<up>") << "g<up>"
keymap.nv("<down>") << "g<down>"

# {} scroll fixed lines
keymap.nv("{") << ("5<up>")
keymap.nv("}") << ("5<down>")

# add emacs key binds
keymap.i("<c-a>") << "<c-o>^"
keymap.i("<c-x><c-a>") << "<c-a>"
keymap.i("<c-e>", expr=True) << "pumvisible() ? '<c-e><End>' : '<End>'"

keymap.c("<c-a>", silent=False) << "<Home>"
keymap.c("<c-x><c-a>", silent=False) << "<c-a>"
keymap.c("<c-e>", silent=False) << "<End>"


# delete dont copy
keymap.n("s") << '"_s'
keymap.n("S") << '"_S'
keymap.n("x") << '"_x'
keymap.n("X") << '"_X'

keymap.nv("d") << '"_d'
keymap.nv("D") << '"_D'
keymap.nv("c") << '"_c'
keymap.nv("C") << '"_C'


# leave cursor 1 behind instead of before
keymap.nv("p") << "gp"
keymap.nv("P") << "gP"


# centre on up down
keymap.nv("<c-u>") << "<c-u>"
keymap.nv("<c-d>") << "<c-d>"
keymap.nv("<c-f>") << "<c-f>"
keymap.nv("<c-b>") << "<c-b>"


# emacs arrow movements
keymap.nov("<m-left>") << "b"
keymap.nov("<m-right>") << "e<right>"
keymap.i("<m-left>") << "<c-o>b"
keymap.i("<m-right>") << "<c-o>e<right>"
keymap.c("<m-left>", silent=False) << "<s-left>"
keymap.c("<m-right>", silent=False) << "<s-right>"
