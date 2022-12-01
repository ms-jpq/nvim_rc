#!/usr/bin/env -S awk -f
BEGIN { ORS = " " }

{
  gsub(/^[[:space:]]+|[[:space:]]+$/, "")
  print
}
