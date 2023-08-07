#!/usr/bin/env -S -- awk -f
BEGIN {
  ORS = " "
  COMMENTED = 1
  SKIPPED = 0

  # <ctrl-c>
  print("\x03")
}

{
  gsub(/^[[:space:]]+|[[:space:]]+$/, "")
  COMMENTING = (/^--.*/)

  if (COMMENTING && !COMMENTED) { print "" }

  if (!$0) { SKIPPED = 1 }
  else {
    if (SKIPPED) { print "" }

    SKIPPED = 0

    print

    if (COMMENTING) { print "" }
  }

  COMMENTED = COMMENTING
}