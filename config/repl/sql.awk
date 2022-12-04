#!/usr/bin/env -S awk -f
BEGIN {
  ORS = " "
  COMMENTED = 1
  SKIPPED = 0
}

{
  gsub(/^[[:space:]]+|[[:space:]]+$/, "")
  COMMENTING = (/^--.*/)

  if (COMMENTING && !COMMENTED) { printf("%s", "\n") }

  if (!$0) { SKIPPED = 1 }
  else {
    if (SKIPPED) { printf("%s", "\n") }

    SKIPPED = 0

    print

    if (COMMENTING) { printf("%s", "\n") }
  }

  COMMENTED = COMMENTING
}
