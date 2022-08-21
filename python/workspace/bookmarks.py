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
    list_bookmarks,
    list_buf_bookmarks,
)

from ..registery import NAMESPACE, autocmd, rpc

_NS = uuid4()


@rpc(blocking=True)
def _bookmark_signs(nvim: Nvim) -> None:
    with suppress(NvimError):
        ns = create_ns(nvim, ns=_NS)
        buf = cur_buf(nvim)
        clear_ns(nvim, buf=buf, id=ns)

        def c1() -> Iterator[tuple[str, int]]:
            for name, (row, _) in list_buf_bookmarks(nvim, buf=buf).items():
                yield name, row
            for name, buf_nr, (row, _), _ in list_bookmarks(nvim):
                if buf_nr == buf.number:
                    yield name, row

        def c2() -> Iterator[ExtMarkBase]:
            for idx, (name, row) in enumerate(c1(), start=1):
                sign = ExtMarkBase(
                    idx=idx,
                    begin=(row, 0),
                    meta={
                        "sign_text": name,
                        "sign_hl_group": "IncSearch",
                    },
                )
                yield sign

        buf_set_extmarks_base(nvim, buf=buf, id=ns, marks=c2())


_ = (
    autocmd("BufEnter", "CursorHold", "CursorHoldI")
    << f"lua {NAMESPACE}.{_bookmark_signs.name}()"
)
