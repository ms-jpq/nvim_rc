#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

readarray -t -d $'\n' -- LINES </dev/stdin

MAX=0
for LINE in "${LINES[@]}"; do
  if [[ "$LINE" =~ ^[[:space:]]*#.*$ ]]; then
    :
  elif [[ "$LINE" =~ ^[[:space:]]*([^[:space:]]+)[[:space:]]*=.*$ ]]; then
    M="${#BASH_REMATCH[1]}"
    MAX=$((M > MAX ? M : MAX))
  fi
done

for LINE in "${LINES[@]}"; do
  if [[ "$LINE" =~ ^[[:space:]]*#[[:space:]]*(.*)$ ]]; then
    printf -- '%s\n' "# ${BASH_REMATCH[1]}"
  elif [[ "$LINE" =~ ^[[:space:]]*([^[:space:]]+)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
    L="${#BASH_REMATCH[1]}"
    M=$((MAX - L))

    P=" "
    for ((i = 0; i < M; i++)); do
      P="$P "
    done

    printf -- '%s\n' "${BASH_REMATCH[1]}${P}= ${BASH_REMATCH[2]}"
  elif [[ "$LINE" =~ ^[[:space:]]*([^[:space:]]*)[[:space:]]*$ ]]; then
    printf -- '%s\n' "${BASH_REMATCH[1]}"
  else
    printf -- '%s\n' "unexpected --> $LINE" 2>&1
    exit 1
  fi
done
