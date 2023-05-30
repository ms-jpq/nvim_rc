from ..registery import keymap, settings

# search results shown on side
settings["inccommand"] = "nosplit"
# use ripgrep
settings["grepprg"] = r"rg\ --vimgrep"


# clear hlsearch result
_ = keymap.n("<leader>i") << "<cmd>nohlsearch<cr>"
_ = keymap.n("<leader><space>") << "<cmd>nohlsearch<cr>"


# search without moving
_ = keymap.n("*") << "*N"
_ = keymap.n("#") << "#N"
_ = keymap.n("g*") << "g*N"
_ = keymap.n("g#") << "g#N"
# centre on search result
_ = keymap.n("n") << "n"
_ = keymap.n("N") << "N"


# use no magic
_ = keymap.nv("/", silent=False) << r"/\V"
_ = keymap.nv("?", silent=False) << r"?\V"
