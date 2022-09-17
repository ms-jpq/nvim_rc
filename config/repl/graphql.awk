#!/usr/bin/env -S awk -f

{
  print $0
}

END {
  printf("%s", "\x11")
}
