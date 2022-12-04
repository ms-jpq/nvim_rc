#!/usr/bin/env -S awk -f
BEGIN {
  DEDENT = -2
  SKIPPED = 0
}

{
  gsub(/[[:space:]]+$/, "")
  gsub(/^[[:space:]]/, " ")
}

DEDENT == -2 && $0 {
  match($0, /^[[:space:]]+/)
  DEDENT = RLENGTH
}

{
  if (!$0) { SKIPPED = 1 }
  else {
    if (SKIPPED) { print "" }

    SKIPPED = 0

    print substr($0, DEDENT + 1)
  }
}
