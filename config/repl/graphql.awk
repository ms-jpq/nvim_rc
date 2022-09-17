#!/usr/bin/env -S awk -f

{ print }
END { printf("%s", "\x11") }
