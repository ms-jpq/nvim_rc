from uuid import uuid4

from pynvim_pp.window import Window

from ..registry import NAMESPACE, autocmd, keymap, rpc

# fix cursor pos moving 1 back
_BUF_VAR_NAME = f"buf_cursor_col_{uuid4().hex}"

_ = keymap.n("i", nowait=True) << "zzi"

@rpc()
async def _record_pos() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    _, col = await win.get_cursor()
    await buf.vars.set(_BUF_VAR_NAME, val=col)


_ = (
    autocmd("InsertEnter", "CursorMovedI", "TextChangedP")
    << f"lua {NAMESPACE}.{_record_pos.method}()"
)


@rpc()
async def _restore_pos() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, _ = await win.get_cursor()
    col = await buf.vars.get(int, _BUF_VAR_NAME)

    if col is not None:
        await win.set_cursor(row=row, col=col)


_ = autocmd("InsertLeave") << f"lua {NAMESPACE}.{_restore_pos.method}()"
