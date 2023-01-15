#!/usr/bin/env -S awk -f
!(NR == 1 && /^#/) { print }

END { print ";;" }
