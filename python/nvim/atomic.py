from __future__ import annotations

from typing import Any, Iterator, MutableMapping, MutableSequence, Sequence, Tuple

from pynvim import Nvim, NvimError

_AtomicInstruction = Tuple[str, Sequence[Any]]


class _A:
    def __init__(self, name: str, parent: Atomic) -> None:
        self._name, self._parent = name, parent

    def __call__(self, *args: Any) -> int:
        self._parent._instructions.append((self._name, args))
        return len(self._parent._instructions)


class _NS:
    def __init__(self, parent: Atomic) -> None:
        self._parent = parent

    def __getattr__(self, name: str) -> Any:
        if self._parent._commited:
            raise RuntimeError()
        else:
            if name in self._parent._ns_mapping:
                return self._parent._resultset[self._parent._ns_mapping[name]]
            else:
                raise AttributeError()

    def __setattr__(self, key: str, val: int) -> None:
        if not self._parent._commited:
            raise RuntimeError()
        else:
            self._parent._ns_mapping[key] = val


class Atomic:
    def __init__(self) -> None:
        self._commited = False
        self._instructions: MutableSequence[_AtomicInstruction] = []
        self._resultset: MutableSequence[Any] = []
        self._ns_mapping: MutableMapping[str, int] = {}

    def __enter__(self) -> Tuple[Atomic, _NS]:
        return self, _NS(parent=self)

    def __exit__(self, *_: Any) -> None:
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

    def commit(self, nvim: Nvim) -> _NS:
        if self._commited:
            raise RuntimeError()
        else:
            self._commited = True
            inst = tuple(
                (f"nvim_{instruction}", args)
                for instruction, args in self._instructions
            )
            out, err = nvim.api.call_atomic(inst)
            if err:
                self._resultset[:] = []
                idx, _, err_msg = err
                raise NvimError(err_msg, self._instructions[idx])
            else:
                self._resultset[:] = out
                return _NS(self)
