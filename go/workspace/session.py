from asyncio import Task, create_task, sleep
from os.path import normcase, normpath
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import quote

from pynvim_pp.nvim import Nvim
from std2.asyncio import cancel
from std2.cell import RefCell

from ..registry import NAMESPACE, autocmd, rpc

_CELL = RefCell[Optional[Task]](None)


async def _session_path() -> Tuple[Path, str]:
    state = await Nvim.fn.stdpath(str, "state")
    cwd = await Nvim.getcwd()
    path = Path(state) / "sessions" / quote(normcase(cwd.as_posix()), safe="")
    vim = path.with_suffix(".vim")
    escaped = await Nvim.fn.fnameescape(str, normpath(vim))
    return vim, escaped


async def restore() -> None:
    path, vim = await _session_path()
    if path.is_file():
        await Nvim.exec(f"source {vim}")


@rpc()
async def _save_session() -> None:
    if task := _CELL.val:
        _CELL.val = None
        await cancel(task)

    async def cont() -> None:
        await sleep(1.0)
        path, vim = await _session_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        await Nvim.exec(f"mksession! {vim}")

    _CELL.val = create_task(cont())


_ = autocmd("CursorHold") << f"lua {NAMESPACE}.{_save_session.method}()"
