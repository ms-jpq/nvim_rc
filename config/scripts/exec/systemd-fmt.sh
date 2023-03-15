#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O globstar

if [[ -t 0 ]]; then
  TMP="$(mktemp)"
  for FILE in "$PWD/"**/*; do
    case "$FILE" in
    *.link | *.netdev | *.network | *.socket | *.service | */systemd/**/*.conf)
      if [[ ! -L "$FILE" ]]; then
        printf -- '%s\n' "$FILE"
        "$0" <"$FILE" >"$TMP"
        mv -- "$TMP" "$FILE"
      fi
      ;;
    *) ;;
    esac
  done
else
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

  SKIP=0
  for LINE in "${LINES[@]}"; do
    if ((SKIP)); then

      case "$LINE" in
      *\\\\)
        SKIP=0
        ;;
      *\\)
        SKIP=1
        ;;
      *)
        SKIP=0
        ;;
      esac

      printf -- '%s\n' "$LINE"
    elif [[ "$LINE" =~ ^[[:space:]]*#[[:space:]]*(.*)$ ]]; then
      printf -- '%s\n' "# ${BASH_REMATCH[1]}"
    elif [[ "$LINE" =~ ^[[:space:]]*([^[:space:]]+)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
      L="${#BASH_REMATCH[1]}"
      RHS="${BASH_REMATCH[2]}"

      RHS="${RHS%"${RHS##*[![:space:]]}"}"

      case "$RHS" in
      *\\\\) ;;
      *\\)
        SKIP=1
        ;;
      esac

      if [[ -n "$RHS" ]]; then
        RHS=" $RHS"
      fi

      M=$((MAX - L))
      P=" "
      for ((i = 0; i < M; i++)); do
        P="$P "
      done

      printf -- '%s\n' "${BASH_REMATCH[1]}${P}=${RHS}"
    elif [[ "$LINE" =~ ^[[:space:]]*([^[:space:]]*)[[:space:]]*$ ]]; then
      printf -- '%s\n' "${BASH_REMATCH[1]}"
    else
      printf -- '%s\n' "unexpected --> $LINE" >&2
      exit 1
    fi
  done
fi
