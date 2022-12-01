#!/usr/bin/env -S awk -f
BEGIN { ORS = " " }

{
  gsub(/^[[:space:]]+/, "")
  gsub(/[[:space:]]+$/, "")
  print
}

# <ctrl-q>
END {
  ORS = ""
  print "\x11"
}
