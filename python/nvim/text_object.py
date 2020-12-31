from typing import MutableSequence, Set, Tuple


def is_word(c: str, unifying_chars: Set[str]) -> bool:
    return c.isalnum() or c in unifying_chars


def gen_lhs_rhs(
    line: str, col: int, unifying_chars: Set[str]
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    before, after = reversed(line[:col]), iter(line[col:])

    words_lhs: MutableSequence[str] = []
    syms_lhs: MutableSequence[str] = []
    words_rhs: MutableSequence[str] = []
    syms_rhs: MutableSequence[str] = []

    encountered_sym = False
    for char in before:
        is_w = is_word(char, unifying_chars=unifying_chars)
        if encountered_sym:
            if is_w:
                break
            else:
                syms_lhs.append(char)
        else:
            if is_w:
                words_lhs.append(char)
            else:
                syms_lhs.append(char)
                encountered_sym = True

    encountered_sym = False
    for char in after:
        is_w = is_word(char, unifying_chars=unifying_chars)
        if encountered_sym:
            if is_w:
                break
            else:
                syms_rhs.append(char)
        else:
            if is_w:
                words_rhs.append(char)
            else:
                syms_rhs.append(char)
                encountered_sym = True

    words = "".join(reversed(words_lhs)), "".join(words_rhs)
    syms = "".join(reversed(syms_lhs)), "".join(syms_rhs)
    return words, syms
