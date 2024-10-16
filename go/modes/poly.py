from collections.abc import Iterator
from importlib.resources import files
from pathlib import Path

from ..registry import atomic, keymap

_move = files(__package__).joinpath("move.lua").read_text("UTF-8")

atomic.exec_lua(_move, ())

# for key, move in (("<up>", -1), ("<down>", +1), ("j", -1), ("k", +1)):
#     _ = keymap.nv(key, expr=True) << f"v:lua.Go.move('{key}', {move})"

# move w linewrap
for key in ("<up>", "<down>", "j", "k"):
    _ = keymap.nv(key, expr=True) << f"(v:count ? \"m'\" . v:count : 'g') . '{key}'"

# {} scroll fixed lines
_ = keymap.nv("{") << ("5g<up>zz")
_ = keymap.nv("}") << ("5g<down>zz")

# re-center
for key in ("d", "n", "N", "[c", "]c", "<c-f>", "<c-b>"):
    _ = keymap.nv(key) << f"{key}zz"

for key, remap in {"<c-u>": "<up>", "<c-d>": "<down>"}.items():
    _ = (
        keymap.nv(key, expr=True)
        << f"max([5, min([9, winheight(0) / 4])]) . 'g{remap}zz'"
    )


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
# _ = keymap.n("s") << '"_s'
# _ = keymap.n("S") << '"_S'
_ = keymap.n("x") << '"_x'
_ = keymap.n("X") << '"_X'

_ = keymap.nv("d") << '"_d'
_ = keymap.nv("D") << '"_D'
_ = keymap.nv("c") << '"_c'
_ = keymap.nv("C") << '"_C'


# leave cursor 1 behind instead of before
_ = keymap.nv("p") << "gp"
_ = keymap.nv("P") << "gP"


# emacs arrow movements
_ = keymap.nov("<m-left>") << "b"
_ = keymap.nov("<m-right>") << "e<right>"
_ = keymap.i("<m-left>") << "<c-o>b"
_ = keymap.i("<m-right>") << "<c-o>e<right>"
_ = keymap.c("<m-left>", silent=False) << "<s-left>"
_ = keymap.c("<m-right>", silent=False) << "<s-right>"
