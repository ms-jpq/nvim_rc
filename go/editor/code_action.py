from contextlib import suppress
from dataclasses import dataclass
from functools import cache
from itertools import count
from operator import attrgetter
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from pynvim_pp.buffer import Buffer, ExtMark, ExtMarker
from pynvim_pp.nvim import Nvim
from pynvim_pp.rpc_types import NvimError
from pynvim_pp.types import NoneType
from std2.cell import RefCell
from std2.pickle.decoder import new_decoder

from ..registry import LANG, NAMESPACE, atomic, autocmd, keymap, rpc

_NS = uuid4()
_HL = "LspDiagnosticsDefaultInformation"

_CODE_ACTION = (
    Path(__file__).resolve(strict=True).parent / "code_action.lua"
).read_text("UTF-8")


@dataclass(frozen=True)
class _Error:
    message: str


_DECODER = new_decoder[Optional[_Error]](Optional[_Error], strict=False)
_COUNTER = count()
_NOW = RefCell(next(_COUNTER))


@cache
def prefix() -> str:
    return LANG("code action")


@rpc()
async def _on_code_action_notif(
    uid: int, line: int, error: Optional[Any], actionable: bool
) -> None:
    now = _NOW.val

    if uid >= now:
        _NOW.val = uid

        if err := _DECODER(error):
            msg = f"{prefix()} {err.message}"
            await Nvim.write(msg, error=True)

        ns = await Nvim.create_namespace(_NS)
        buf = await Buffer.get_current()

        sign = ExtMark(
            buf=buf,
            marker=ExtMarker(uid),
            begin=(line, 0),
            end=None,
            meta={
                "sign_text": prefix(),
                "hl_mode": "combine",
                "sign_hl_group": _HL,
                "number_hl_group": _HL,
            },
        )

        extmarks = (sign,) if actionable else ()
        if uid > now:
            await buf.clear_namespace(ns)
        with suppress(NvimError):
            await buf.set_extmarks(ns, extmarks=extmarks)


atomic.exec_lua(_CODE_ACTION, (NAMESPACE, _on_code_action_notif.method))


@rpc()
async def _on_hover() -> None:
    await attrgetter(NAMESPACE)(Nvim.lua).code_action(NoneType, next(_COUNTER))


_ = autocmd("CursorHold", "CursorHoldI") << f"lua {NAMESPACE}.{_on_hover.method}()"


_ = keymap.nv("gw") << "<cmd>lua vim.lsp.buf.code_action()<cr>"
