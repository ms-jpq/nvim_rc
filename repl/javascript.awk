#!/usr/bin/env -S -- awk -f
BEGIN {
  DEDENT = -2
  PRINTED = 0
  SKIPPED = 0

  printf("%s", "exec ")
}

{
  gsub(/^[[:space:]]/, " ")
  gsub(/[[:space:]]+$/, "")
}

DEDENT == -2 && $0 {
  match($0, /^[[:space:]]+/)
  DEDENT = RLENGTH
}

{
  if (!$0) { SKIPPED = 1 }
  else {
    if (SKIPPED && PRINTED) { printf("%s", ";") }

    SKIPPED = 0
    PRINTED = 1

    printf("%s;", substr($0, DEDENT + 1))
  }
}

END { printf("%c", 0) }
