from ..registery import keymap

# {} scroll fixed lines
keymap.nv("{") << "<up>" * 5
keymap.nv("}") << "<down>" * 5

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
keymap.nv("<c-u>") << "<c-u>zz"
keymap.nv("<c-d>") << "<c-d>zz"
keymap.nv("<c-f>") << "<c-f>zz"
keymap.nv("<c-b>") << "<c-b>zz"
# centre on paragraph
keymap.nv("{") << "{zz"
keymap.nv("}") << "}zz"


# emacs arrow movements
keymap.nov("<m-left>") << "b"
keymap.nov("<m-right>") << "e"
keymap.i("<m-left>") << "<c-o>b"
keymap.i("<m-right>") << "<c-o>e"
keymap.c("<m-left>", silent=False) << "<s-left>"
keymap.c("<m-right>", silent=False) << "<s-right>"
