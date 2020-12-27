from ..registery import settings, atomic

atomic.command("filetype on")

# do not exec arbitrary code
settings["nomodeline"] = True

# limit .vim exec rights
settings["secure"] = True

# use bash as shell
settings["shell"] = "bash"

# vim session state
settings["shada"] += "!"

# min lines changed to report
settings["report"] = 0

# no swap files
settings["noswapfile"] = True

# wrap
settings["wrap"] = True

# line wrap follow indent
settings["breakindent"] = True
