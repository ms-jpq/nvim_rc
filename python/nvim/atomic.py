from __future__ import annotations

from os import name
from typing import Any, ContextManager, Iterator, MutableSequence, Sequence, Tuple, cast

from pynvim import Nvim, NvimError

_AtomicInstruction = Tuple[str, Sequence[Any]]


class _A:
    def __init__(self, name: str, parent: Atomic) -> None:
        self._name, self._parent = name, parent

    def __call__(self, *args: Any) -> None:
        self._parent._instructions.append((name, args))


class Atomic(ContextManager["Atomic"]):
    def __init__(self) -> None:
        self._instructions: MutableSequence[_AtomicInstruction] = []

    def __exit__(self, _: Any) -> None:
        return None

    def __iter__(self) -> Iterator[_AtomicInstruction]:
        return iter(self._instructions)

    def __add__(self, other: Atomic) -> Atomic:
        new = Atomic()
        new._instructions.extend(self._instructions)
        new._instructions.extend(other._instructions)
        return new

    def __getattr__(self, fn_name: str) -> _A:
        return _A(name=fn_name, parent=self)

    def execute(self, nvim: Nvim) -> Sequence[Any]:
        inst = tuple(
            (f"nvim_{instruction}", args) for instruction, args in self._instructions
        )
        out, err = nvim.api.call_atomic(inst)
        if err:
            idx, _, err_msg = err
            raise NvimError(err_msg, self._instructions[idx])
        else:
            return cast(Sequence[Any], out)
