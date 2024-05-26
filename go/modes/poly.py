from collections.abc import Iterator
from pathlib import Path

from ..registry import atomic, keymap

_move = Path(__file__).parent.joinpath("move.lua").read_text("UTF-8")

atomic.exec_lua(_move, ())

# move w linewrap
for key in ("<up>", "<down>", "j", "k"):
    _ = keymap.nv(key, expr=True) << f"v:lua.Go.move('{key}')"

# {} scroll fixed lines
_ = keymap.nv("{") << ("5g<up>zz")
_ = keymap.nv("}") << ("5g<down>zz")

# re-center
for key in ("d", "n", "N", "[c", "]c"):
    _ = keymap.nv(key) << f"{key}zz"


def _redraw(wrapped: str) -> Iterator[str]:
    yield "<cmd>set lazyredraw<cr>"
    yield "<cmd>set noincsearch<cr>"
    yield wrapped
    yield "<cmd>nohlsearch<cr>"
    yield "<cmd>set incsearch<cr>"
    yield "<cmd>set nolazyredraw<cr>"


# () search next paren
_ = keymap.nv(")") << "".join(_redraw(r"/)\|]\|}<cr>"))
_ = keymap.nv("(") << "".join(_redraw(r"?(\|[\|{<cr>"))


# add emacs key binds
_ = keymap.i("<c-a>") << "<c-o>^"
_ = keymap.i("<c-x><c-a>") << "<c-a>"
_ = keymap.i("<c-e>", expr=True) << "pumvisible() ? '<c-e><End>' : '<End>'"

_ = keymap.c("<c-a>", silent=False) << "<Home>"
_ = keymap.c("<c-x><c-a>", silent=False) << "<c-a>"
_ = keymap.c("<c-e>", silent=False) << "<End>"


# delete dont copy
_ = keymap.n("s") << '"_s'
_ = keymap.n("S") << '"_S'
_ = keymap.n("x") << '"_x'
_ = keymap.n("X") << '"_X'

_ = keymap.nv("d") << '"_d'
_ = keymap.nv("D") << '"_D'
_ = keymap.nv("c") << '"_c'
_ = keymap.nv("C") << '"_C'


# leave cursor 1 behind instead of before
_ = keymap.nv("p") << "gp"
_ = keymap.nv("P") << "gP"


# centre on up down
_ = keymap.nv("<c-u>") << "<c-u>"
_ = keymap.nv("<c-d>") << "<c-d>"
_ = keymap.nv("<c-f>") << "<c-f>"
_ = keymap.nv("<c-b>") << "<c-b>"


# emacs arrow movements
_ = keymap.nov("<m-left>") << "b"
_ = keymap.nov("<m-right>") << "e<right>"
_ = keymap.i("<m-left>") << "<c-o>b"
_ = keymap.i("<m-right>") << "<c-o>e<right>"
_ = keymap.c("<m-left>", silent=False) << "<s-left>"
_ = keymap.c("<m-right>", silent=False) << "<s-right>"
