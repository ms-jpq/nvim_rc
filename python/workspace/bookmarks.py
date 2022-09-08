from asyncio import gather
from collections.abc import Iterator
from uuid import uuid4

from pynvim_pp.buffer import Buffer, ExtMark, ExtMarker
from pynvim_pp.nvim import Nvim

from ..registery import NAMESPACE, atomic, autocmd, rpc

_NS = uuid4()

_HL = "IncSearch"


@rpc(blocking=True)
async def _bookmark_signs() -> None:
    buf = await Buffer.get_current()
    local, glob = await gather(buf.list_bookmarks(), Nvim.list_bookmarks())

    def c1() -> Iterator[tuple[str, int]]:
        for l_marker, (row, _) in local.items():
            yield l_marker, row
        for g_marker, (_, b, (row, _)) in glob.items():
            if b == buf:
                yield g_marker, row

    def c2() -> Iterator[ExtMark]:
        for marker, (name, row) in enumerate(c1(), start=1):
            sign = ExtMark(
                buf=buf,
                marker=ExtMarker(marker),
                begin=(row, 0),
                end=None,
                meta={
                    "sign_text": name,
                    "hl_mode": "combine",
                    "sign_hl_group": _HL,
                    "number_hl_group": _HL,
                },
            )
            yield sign

    ns = await Nvim.create_namespace(_NS)
    await buf.clear_namespace(ns)
    await buf.set_ext_marks(ns, extmarks=c2())


_ = (
    autocmd("BufEnter", "CursorHold", "CursorHoldI")
    << f"lua {NAMESPACE}.{_bookmark_signs.name}()"
)

atomic.exec_lua(f"{NAMESPACE}.{_bookmark_signs.name}()", ())
