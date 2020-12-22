from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, MutableMapping, Tuple

from .rpc import RPC_FUNCTION


@dataclass(frozen=True)
class _AuParams:
    name: str
    events: Iterable[str]
    filters: Iterable[str]
    modifiers: Iterable[str]
    args: Iterable[str]


class AutoCMD:
    def __init__(self) -> None:
        self._finalized = False
        self._autocmds: MutableMapping[_AuParams, RPC_FUNCTION] = {}

    def __call__(
        self,
        name: str,
        *,
        events: Iterable[str],
        filters: Iterable[str] = ("*",),
        modifiers: Iterable[str] = (),
        args: Iterable[str] = (),
    ) -> Callable[[RPC_FUNCTION], RPC_FUNCTION]:
        param = _AuParams(
            name=name, events=events, filters=filters, modifiers=modifiers, args=args
        )

        def decor(rpc_f: RPC_FUNCTION) -> RPC_FUNCTION:
            self._autocmds[param] = rpc_f
            return rpc_f

        return decor

    def finalize(self, chan_id: int) -> None:
        if self._finalized:
            raise RuntimeError()
        else:
            self._finalized = True

            def instructions() -> Iterator[str]:
                for param, func in self._autocmds.items():
                    events = ",".join(param.events)
                    filters = " ".join(param.filters)
                    modifiers = " ".join(param.modifiers)
                    args = ", ".join(param.args)
                    group = f"augroup ch_{chan_id}_{param.name}"
                    cls = "autocmd!"
                    rpc_args = f"{chan_id}, {param.name}, {{{args}}}"
                    cmd = f"autocmd {events} {filters} {modifiers} lua vim.rpcnotify({rpc_args})"
                    group_end = "augroup END"
