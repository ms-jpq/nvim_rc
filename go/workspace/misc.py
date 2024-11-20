from os import environ

from ..registry import keymap, settings

# Prevent macro recording
_ = keymap.n("q") << "<nop>"

# do not exec arbitrary code
settings["nomodeline"] = True

# limit .vim exec rights
settings["secure"] = True

# use bash as shell
settings["shell"] = environ.get("COMSPEC", "bash")

# min lines changed to report
settings["report"] = 0

# no swap files
settings["noswapfile"] = True

# wrap
settings["wrap"] = True

# no hex or binary parsing
settings["nrformats"] = ""
