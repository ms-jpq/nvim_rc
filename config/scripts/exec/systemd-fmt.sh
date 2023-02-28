#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

readarray -t -d $'\n' -- LINES </dev/stdin

MAX=1
for LINE in "${LINES[@]}"; do
  if [[ "$LINE" =~ ^[[:space:]]*# ]]; then
    true
  elif [[ "$LINE" =~ ^[[:space:]]*([^=]+)= ]]; then
    M="${#BASH_REMATCH[1]}"
    MAX=$((M > MAX ? M : MAX))
  fi
done

for LINE in "${LINES[@]}"; do
  if [[ "$LINE" =~ ^[[:space:]]*#(.*)$ ]]; then
    printf -- '%s\n' "#${BASH_REMATCH[1]}"
  elif [[ "$LINE" =~ ^[[:space:]]*([^[:space:]]+)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
    L="${#BASH_REMATCH[1]}"
    M=$((MAX - L))

    P=""
    for ((i = 0; i < M; i++)); do
      P="$P "
    done

    printf -- '%s\n' "${BASH_REMATCH[1]}${P}= ${BASH_REMATCH[2]}"
  else
    printf -- '%s\n' "$LINE"
  fi
done
