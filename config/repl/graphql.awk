#!/usr/bin/env -S -- awk -f
BEGIN { ORS = " " }

{ gsub(/^[[:space:]]+|[[:space:]]*,?[[:space:]]*$/, "") }

$0 { print }

END {
  # <ctrl-q>
  print("\x11")
}
