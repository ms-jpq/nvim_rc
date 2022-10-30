from dataclasses import dataclass
from operator import attrgetter
from os import linesep
from pathlib import Path
from types import NoneType
from typing import Any, Iterator, Mapping, Optional, Sequence, Union
from uuid import uuid4

from pynvim_pp.buffer import Buffer, ExtMark, ExtMarker
from pynvim_pp.nvim import Nvim
from std2.pickle.decoder import new_decoder

from ..registery import LANG, NAMESPACE, atomic, autocmd, keymap, rpc

_NS = uuid4()
_HL = "LspDiagnosticsDefaultInformation"

_CODE_ACTION = (
    Path(__file__).resolve(strict=True).parent / "code_action.lua"
).read_text("UTF-8")


@dataclass(frozen=True)
class _Error:
    message: str


@dataclass(frozen=True)
class _CodeActionReply:
    error: Optional[_Error] = None
    result: Optional[Any] = None


_CodeActionReplies = Union[Mapping[int, _CodeActionReply], Sequence[_CodeActionReply]]

_DECODER = new_decoder[_CodeActionReplies](_CodeActionReplies, strict=False)


@rpc()
async def _on_code_action_notif(line: int, values: Any) -> None:
    def parse() -> Iterator[_CodeActionReply]:
        vals = _DECODER(values)
        if isinstance(vals, Mapping):
            yield from vals.values()
        else:
            yield from vals

    actions = tuple(parse())

    if errs := tuple(err.message for action in actions if (err := action.error)):
        await Nvim.write(linesep.join(errs))

    buf = await Buffer.get_current()
    sign = ExtMark(
        buf=buf,
        marker=ExtMarker(1),
        begin=(line, 0),
        end=None,
        meta={
            "sign_text": LANG("code action"),
            "hl_mode": "combine",
            "sign_hl_group": _HL,
            "number_hl_group": _HL,
        },
    )
    extmarks = (sign,) if any(action.result for action in actions) else ()

    ns = await Nvim.create_namespace(_NS)
    await buf.clear_namespace(ns)
    await buf.set_extmarks(ns, extmarks=extmarks)


atomic.exec_lua(_CODE_ACTION, (NAMESPACE, _on_code_action_notif.method))


@rpc()
async def _on_hover() -> None:
    await attrgetter(NAMESPACE)(Nvim.lua).code_action(NoneType)


_ = autocmd("CursorHold", "CursorHoldI") << f"lua {NAMESPACE}.{_on_hover.method}()"


_ = keymap.n("gw") << f"<cmd>lua vim.lsp.buf.code_action()<cr>"
_ = keymap.v("gw") << f"<cmd>lua vim.lsp.buf.code_action()<cr>"
