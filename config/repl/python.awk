#!/usr/bin/env -S awk -f

BEGIN {
  DEDENT=-2
}

{
  sub(/[[:space:]]+$/, "")
  gsub(/[[:space:]]/, " ")
}

$0 && DEDENT == -2 {
  match($0, /^[[:space:]]+/)
  DEDENT=RLENGTH
}

$0 {
  print substr($0, DEDENT + 1)
}

END {
  printf "\n"
}
