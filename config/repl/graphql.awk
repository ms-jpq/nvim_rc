#!/usr/bin/env -S awk -f

{ print }

# <ctrl-q>
END { printf("%s", "\x11") }
