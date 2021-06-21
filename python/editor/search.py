from ..registery import keymap, settings

# find result during search
settings["incsearch"] = True
# search results shown on side
settings["inccommand"] = "nosplit"
# use ripgrep
settings["grepprg"] = r"rg\ --vimgrep"


# clear hlsearch result
keymap.n("<leader>i") << "<cmd>nohlsearch<cr>"


# search without moving
keymap.n("*") << "*N"
keymap.n("#") << "#N"
keymap.n("g*") << "g*N"
keymap.n("g#") << "g#N"
# centre on search result
keymap.n("n") << "n"
keymap.n("N") << "N"


# use no magic
keymap.nv("/", silent=False) << r"/\V"
keymap.nv("?", silent=False) << r"?\V"

