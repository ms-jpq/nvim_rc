from collections.abc import Iterator
from contextlib import suppress
from uuid import uuid4

from pynvim import Nvim, NvimError
from pynvim_pp.api import (
    ExtMarkBase,
    buf_set_extmarks_base,
    clear_ns,
    create_ns,
    cur_buf,
    list_buf_bookmarks,
)

from ..registery import NAMESPACE, autocmd, rpc

_NS = uuid4()


@rpc(blocking=True)
def _bookmark_signs(nvim: Nvim) -> None:
    with suppress(NvimError):
        ns = create_ns(nvim, ns=_NS)
        buf = cur_buf(nvim)
        marks = list_buf_bookmarks(nvim, buf=buf)
        clear_ns(nvim, buf=buf, id=ns)

        def cont() -> Iterator[ExtMarkBase]:
            for idx, (name, (row, _)) in enumerate(marks.items(), start=1):
                sign = ExtMarkBase(
                    idx=idx,
                    begin=(row, 0),
                    meta={"sign_text": name, "sign_hl_group": "IncSearch"},
                )
                yield sign

        buf_set_extmarks_base(nvim, buf=buf, id=ns, marks=cont())


_ = (
    autocmd("BufEnter", "CursorHold", "CursorHoldI")
    << f"lua {NAMESPACE}.{_bookmark_signs.name}()"
)
