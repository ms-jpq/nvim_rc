#!/usr/bin/env -S awk -f

{
  gsub(/[[:space:]]/, " ")
  sub(/[[:space:]]+$/, "")
}

NR == 1 {
  match($0, /^[[:space:]]+/)
  DEDENT=RLENGTH
}

{
  if (!$0) { next }

  print substr($0, DEDENT)
}

END {
  print
}
