#!/usr/bin/env -S awk -f
BEGIN {
  ORS = " "
  COMMENTED = 1
}

{
  gsub(/^[[:space:]]+|[[:space:]]+$/, "")
  COMMENTING = (/^--.*/)

  if (COMMENTING && !COMMENTED) { printf("%s", "\n") }

  if ($0) { print }
  else { printf("%s", "\n") }

  if (COMMENTING) { printf("%s", "\n") }

  COMMENTED = COMMENTING
}
