#!/usr/bin/env -S awk -f

BEGIN {
  DEDENT=-2
  SKIPPED=0
}

{
  # Trim Trailing Spaces
  sub(/[[:space:]]+$/, "")
  # Standardize Indent
  gsub(/[[:space:]]/, " ")
}

# Dedent @ First Non-Empty Line
$0 && DEDENT == -2 {
  match($0, /^[[:space:]]+/)
  DEDENT=RLENGTH
}

# Skip Empty Line
!$0 {
  SKIPPED=1
}

$0 {
  # Ensure Single Newline
  if (SKIPPED) {
    printf "\n"
  }
  SKIPPED=0
  print substr($0, DEDENT + 1)
}
