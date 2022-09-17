#!/usr/bin/env -S awk -f

BEGIN {
  DEDENT=-2
  BLANKED=0
}

{
  sub(/[[:space:]]+$/, "")
  gsub(/[[:space:]]/, " ")
}

NF && DEDENT == -2 {
  match($0, /^[[:space:]]+/)
  DEDENT=RLENGTH
}

!NF {
  BLANKED++
}

NF || BLANKED > 2 {
  print substr($0, DEDENT + 1)
  BLANKED=0
}

END {
  printf "\n"
}
