from ..registery import atomic, settings

# use 256 colours
settings["termguicolors"] = True
# always show status line
settings["laststatus"] = 2
# always show issues column
settings["signcolumn"] = "yes"
# dont show eob lines
settings["fillchars"] = "eob:\ "
# always show tabline
settings["showtabline"] = 2
# show line count
settings["number"] = True


# show cursor
settings["cursorline"] = True
# constant cursor styling
settings["guicursor"] = ""


# light theme
settings["background"] = "light"
atomic.command("colorscheme edge")
