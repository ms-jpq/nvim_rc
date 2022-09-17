#!/usr/bin/env -S awk -f

{
  gsub(/[[:space:]]/, " ")
}

NR == 1 {
  match($0, /^[[:space:]]+/)
  DEDENT=RLENGTH
}

{
  if (!$0) { next }

  sub(/[[:space:]]+$/, "")
  print substr($0, DEDENT)
}

END {
  print
}
