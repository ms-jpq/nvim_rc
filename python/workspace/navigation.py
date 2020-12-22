from ..registery import settings, keymap

# ui for cmd auto complete
settings["wildmenu"] = True
settings["wildmode"] = "list:longest,full"
settings["wildignorecase"] = True
settings["wildoptions"] = "tagfile"


# more history
settings["history"] = 10000


# ignore case
settings["ignorecase"] = True


# use [ ] to navigate various lists, ie quickfix
keymap.n("[b") << "<cmd>bprevious<cr>"
keymap.n("]b") << "<cmd>bnext<cr>"