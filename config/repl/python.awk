#!/usr/bin/env -S awk -f

BEGIN {
  DEDENT=-2
}

{
  gsub(/[[:space:]]/, " ")
  sub(/[[:space:]]+$/, "")
}

$0 && DEDENT == -2 {
  match($0, /^[[:space:]]+/)
  DEDENT=RLENGTH
}

$0 {
  print substr($0, DEDENT + 1)
}

END {
  print
}
