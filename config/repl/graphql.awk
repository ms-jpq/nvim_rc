#!/usr/bin/env -S awk -f
BEGIN { OBS = "" }

NR != 1 { print " " }

{
  gsub(/^[[:space:]]+/, "")
  gsub(/[[:space:]]+/, " ")
  print
}

# <ctrl-q>
END { print "\x11" }
