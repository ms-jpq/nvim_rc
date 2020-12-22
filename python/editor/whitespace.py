from ..registery import keymap, settings

tabsize = 2

# how big are tabs ?
settings["tabstop"] = tabsize
# spaces remove on deletion
settings["softtabstop"] = tabsize
# manual indentation width
settings["shiftwidth"] = tabsize


# insert spaces instead of tabs
settings["expandtab"] = True


# smart indentation level
settings["autoindent"] = True
settings["smarttab"] = True
